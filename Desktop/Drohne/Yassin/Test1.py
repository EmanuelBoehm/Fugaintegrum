#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
from pymavlink import mavutil  # Needed for command message definitions
import time
import math
import sys
import bb


print("Connecting to vehicle...")
vehicle = connect("/dev/ttyS0", wait_ready=True, baud=921600)

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
#    while not vehicle.is_armable:
#        print(" Waiting for vehicle to initialise...")
#        time.sleep(1)

        
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)

# change yaw of vehicle counter clockwise
# relative=  True changes relative to actual heading
# relative = False changes heading absolute
def condition_yaw(heading, relative=False):
    if relative:
        is_relative = 1 #yaw relative to direction of travel
    else:
        is_relative = 0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)
    
# not necessary.. when chaning vehicle into land mode, it will land safely
def landAndDisarm():
    print("Vehicle is in LAND mode")
    vehicle.mode = VehicleMode("LAND")
    while abs(vehicle.location.global_relative_frame.alt) > 1:
            time.sleep(1)
            
    time.sleep(5)
    while abs(vehicle.location.global_relative_frame.alt) > 0.3:
        print("vehicle alt: ", vehicle.location.global_relative_frame.alt)
        set_velocity_body(vehicle,0,0,0.1)
        time.sleep(1)
        
    
    print("vehicle alt: ", vehicle.location.global_relative_frame.alt)
    time.sleep(4)
    if vehicle.armed:
        print("Vehicle is still armed. Disarming now..")
        vehicle.armed = False
        while vehicle.armed:
            time.sleep(0.5)

# returns true, if sensor reads distance < minDist
# when distance was None maxMeasures times, it returns true
def isFacingObstacle(minDist=150, maxMeasures=1):
    obstacleDist = bb.getDist("front")
    result = not obstacleDist or obstacleDist < minDist
    actualMeasure = 0
    while result and actualMeasure < maxMeasures:
        print("Facing obstacle at dist(" + str(maxMeasures) + "): ", obstacleDist)
        time.sleep(0.1)
        obstacleDist = bb.getDist("front")
        result = not obstacleDist or obstacleDist < minDist
        actualMeasure = actualMeasure + 1
    if result:
        print("Facing obstacle at dist(" + str(maxMeasures) + "): ", obstacleDist)
    print("AUsweichen?", result)
    return result

            
# sets the velocity in each of x, y and z directions
def set_velocity_body(vehicle, vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
    0,
    0, 0,
    mavutil.mavlink.MAV_FRAME_BODY_NED,
    0b0000111111000111,  # -- BITMASK -> Consider only the velocities
    0, 0, 0,  # -- POSITION
    vx, vy, vz,  # -- VELOCITY
    0, 0, 0,  # -- ACCELERATIONS
    0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.

    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
    else:
        raise Exception("Invalid Location object passed")
        
    return targetlocation;


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


  
        
    
        
def goto(dNorth, dEast, depth=0, maxDepth=3, gotoFunction=vehicle.simple_goto):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.

    The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for 
    the target position. This allows it to be called with different position-setting commands. 
    By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().
    """
    if depth >= maxDepth:
        print("Max recursive depth reached! Aborting this goto() call")
        return
    currentLocation = vehicle.location.global_relative_frame
    targetLocation = get_location_metres(currentLocation, dNorth, dEast)
    targetDistance = get_distance_metres(currentLocation, targetLocation)
    gotoFunction(targetLocation)
    
    #print "DEBUG: targetLocation: %s" % targetLocation
    #print "DEBUG: targetLocation: %s" % targetDistance

    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        #print "DEBUG: mode: %s" % vehicle.mode.name
        remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
        print("Distance to target: ", remainingDistance)
        if remainingDistance <= 1: #Just below target, in case of undershoot.
            print("Reached target")
            break
        time.sleep(2)
        # very primitive way of preventing flying into obstacles
        if isFacingObstacle():
            #landAndDisarm()
            #break
            #vehicle.mode = VehicleMode("land")
            remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
            currentLocation1 = vehicle.location.global_relative_frame
            if dNorth > 0 and dEast == 0:
                goto(0, -5, depth + 1)
                goto(remainingDistance, 5, depth +  1)
            break
            #elif dNorth < 0:
            #    goto(0, 5, depth +  1)
            #    goto(remainingDistance, -5, depth +  1)
            #elif dEast > 0:
            #    goto(5, 0, depth +  1)
            #    goto(-5, remainingDistance, depth +  1)
            #else:
            #    goto(-5, 0, depth +  1)
            #    goto(5, remainingDistance, depth +  1)
            #break

        
        
#printVehicleInfos()
print("Setting up sensors...")
bb.setupPins() # sets up sensors




arm_and_takeoff(1)
print("Holding altitude for 5 seconds...")
time.sleep(5)
vehicle.mode = VehicleMode("GUIDED")
vehicle.groundspeed=1
meters = 7
print("Moving north")
goto(meters + 3, 0)

print("Moving west")
goto(0, meters)


print("Moving south")
goto(-meters - 3, 0)

print("Position east")
goto(0, -meters)
print("done")


print("Landing...")
vehicle.airspeed = 1
landAndDisarm()
time.sleep(1)
vehicle.close()
print("Landed and disarmed vehicle! Goodbye :)")


