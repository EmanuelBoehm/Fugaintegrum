#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
from pymavlink import mavutil  # Needed for command message definitions
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import math
import bb




def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    print("Vehicle is in GUIEDED mode")
    print("#####CAUTION: Arming motors...#####")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for vehicle being fully armed...")
        time.sleep(1)
    print("Vehicle is armed")
    print("Taking off to target altitude: ", aTargetAltitude)
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print("Current altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def landAndDisarmAndClose():
    print("Vehicle is in LAND mode")
    vehicle.mode = VehicleMode("LAND")
    while abs(vehicle.location.global_relative_frame.alt) > 1:
            time.sleep(1)
            
    time.sleep(5)
    while abs(vehicle.location.global_relative_frame.alt) > 0.3:
        print("vehicle alt: ", vehicle.location.global_relative_frame.alt)
        set_velocity_body(vehicle,0,0,0.1)
        time.sleep(1)
        
    print("disarming motors now!")
    print("vehicle alt: ", vehicle.location.global_relative_frame.alt)
    vehicle.armed = False
    while vehicle.armed:
        time.sleep(0.5)
    vehicle.close()
    print("Landed and disarmed vehicle! Goodbye :)")
    

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
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobal(newlat, newlon,original_location.alt)


def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
   

def setSpeed(aSpeed):
    vehicle.groundspeed = aSpeed
    vehicle.airspeed = aSpeed
    
def printVehicleInfos():
    print("Gathering vehicle information...")
    print("Armed: ", vehicle.armed)
    print("System status: ", vehicle.system_status.state)
    print("GPS: ", vehicle.gps_0)
    print("Alt: ", vehicle.location.global_relative_frame.alt)
    print("Downloading home location...")
    while not vehicle.home_location:
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready()
        if not vehicle.home_location:
            print("Waiting for home location...")
            time.sleep(1)
        print("Home location: ", vehicle.home_location)
        print("Actual location: ", vehicle.location.global_relative_frame)
        
def landOnObstacle():
    obstacleDist = bb.getDist("front")
    if not obstacleDist or obstacleDist < 200:
        print("Aborting mission, obstacle found at: ", obstacleDist, " cm")
        landAndDisarmAndClose()
        bb.cleanAndExit()
        
        
# Connect to the Vehicle
print("Connecting to vehicle...")
vehicle = connect("/dev/ttyS0", wait_ready=True, baud=921600)
printVehicleInfos()
print("Setting up sensors...")
bb.setupPins()


altitude = 1
startLocation = vehicle.location.global_relative_frame
startLocation.alt = altitude
point1 = get_location_metres(startLocation, 5, 0)
point2 = get_location_metres(point1, 0, -5)
point3 = get_location_metres(point2, -5, 0)


arm_and_takeoff(altitude)
speed = 1
print("Setting speed to ", speed)
setSpeed(speed)

for p in [point1, point2, point3, startLocation]:
    dist = get_distance_metres(vehicle.location.global_relative_frame, p)
    print("distance to ", p, ": ", dist)
    obstacleDist = bb.getDist("front")
    landOnObstacle()
    vehicle.simple_goto(p, groundspeed=speed)
    while dist > 1:
        print("flying to waypoint, dist: ", dist)
        landOnObstacle()
        time.sleep(0.1)
        dist = get_distance_metres(vehicle.location.global_relative_frame, p)
    print("reached waypoint!")
    time.sleep(3)


print("Landing...")
landAndDisarmAndClose()

