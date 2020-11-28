# -*- coding: utf-8 -*-

from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command, Vehicle
from pymavlink import mavutil  # Needed for command message definitions
import time
import math
import sys

class Drone:

    _CRITICAL_DISTANCE = 3.0 # in m
    _ALT_TOLERANCE = 0.4 # in m, tolerated difference to target height
    _POSITION_TOLERANCE = 0.6 # in m, tolerated difference to target position


    def __init__(self, depth_data, port='/dev/serial0'):
        self.vehicle = connect(port, wait_ready=True, baud=921600)
        self._depth_data = depth_data
        self.cmds = self.vehicle.commands
        self.cmds.download()
        self.cmds.wait_ready()
        print('Drone connected')

    def send_body_ned_velocity(self, velocity_x, velocity_y, velocity_z, duration=0):
        # duration in seconds
        # velocitys in m/s
        # y > 0 => vorwaerts, y < 0 => Rueckwaerts
        # x > 0 => rechts, x < 0 => links
        # z fuer hoehe, z > 0 => runter fliegen
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            # frame Needs to be MAV_FRAME_BODY_NED for forward/back left/right control.
            0b0000111111000111,  # type_mask
            0, 0, 0,  # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z,  # m/s
            0, 0, 0,  # x, y, z acceleration
            0, 0)
        for x in range(0, duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)

    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

        print("Vehicle armed. Waiting 3 secs")
        time.sleep(3)

        print("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude - Drone._ALT_TOLERANCE:  # Trigger just below target alt.
                print("Reached target altitude")
                break
            time.sleep(1)

    # change yaw of vehicle counter clockwise
    # relative=  True changes relative to actual heading
    # relative = False changes heading absolute
    # absolute: 0=North, 90=East, 180=South, 270=West
    def condition_yaw(self, heading, relative=False):
        if relative:
            is_relative = 1  # yaw relative to direction of travel
        else:
            is_relative = 0  # yaw is an absolute angle
        # create the CONDITION_YAW command using command_long_encode()
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
            0,  # confirmation
            heading,  # param 1, yaw in degrees
            0,  # param 2, yaw speed deg/s
            1,  # param 3, direction -1 ccw, 1 cw
            is_relative,  # param 4, relative offset 1, absolute angle 0
            0, 0, 0)  # param 5 ~ 7 not used
        # send command to vehicle
        self.vehicle.send_mavlink(msg)

    # not necessary.. when chaning vehicle into land mode, it will land safely
    def landAndDisarm(self):
        print("Setting LAND mode...")
        self.vehicle.mode = VehicleMode("LAND")
        while abs(self.vehicle.location.global_relative_frame.alt) > 1:
            time.sleep(1)

        time.sleep(5)
        while abs(self.vehicle.location.global_relative_frame.alt) > 0.3:
            print("vehicle alt: ", self.vehicle.location.global_relative_frame.alt)
            self.set_velocity_body(0, 0, 0.1)
            time.sleep(1)

        print("vehicle alt: ", self.vehicle.location.global_relative_frame.alt)
        time.sleep(4)
        if self.vehicle.armed:
            print("Vehicle is still armed. Disarming now..")
            self.vehicle.armed = False
            while self.vehicle.armed:
                time.sleep(0.5)

    # sets the velocity in each of x, y and z directions
    def set_velocity_body(self, vx, vy, vz):
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111,  # -- BITMASK -> Consider only the velocities
            0, 0, 0,  # -- POSITION
            vx, vy, vz,  # -- VELOCITY
            0, 0, 0,  # -- ACCELERATIONS
            0, 0)
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()

    def stop_here(self):
        self.set_velocity_body(0, 0, 0)
        print('Drone stopped')

    def goto(self, dNorth, dEast, gotoFunction=None):
        currentLocation = self.vehicle.location.global_relative_frame
        targetLocation = get_location_metres(currentLocation, dNorth, dEast)
        targetDistance = get_distance_metres(currentLocation, targetLocation)
        if gotoFunction == None:
            self.vehicle.simple_goto(targetLocation)
        else:
            gotoFunction(targetLocation)

        while self.vehicle.mode.name == "GUIDED":  # Stop action if we are no longer in guided mode.
            remainingDistance = get_distance_metres(self.vehicle.location.global_frame, targetLocation)
            print("Distance to target: ", remainingDistance)
            if remainingDistance <= Drone._POSITION_TOLERANCE:  # Just below target, in case of undershoot.
                print("Reached target")
                break
            time.sleep(1)


    def safe_goto(self, dNorth, dEast, gotoFunction=None):
        """
        Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
        Uses depth information to stop in when facing obstacles

        The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for
        the target position. This allows it to be called with different position-setting commands.
        By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().
        """
        if self._depth_data == None:
            print('no camera data, switching to normal goto')
            self.goto(dNorth, dEast, gotoFunction)
        currentLocation = self.vehicle.location.global_relative_frame
        targetLocation = get_location_metres(currentLocation, dNorth, dEast)
        targetDistance = get_distance_metres(currentLocation, targetLocation)
        if gotoFunction == None:
            self.vehicle.simple_goto(targetLocation)
        else:
            gotoFunction(targetLocation)

        # print "DEBUG: targetLocation: %s" % targetLocation
        # print "DEBUG: targetLocation: %s" % targetDistance

        while self.vehicle.mode.name == "GUIDED":  # Stop action if we are no longer in guided mode.
            # print "DEBUG: mode: %s" % vehicle.mode.name
            remainingDistance = get_distance_metres(self.vehicle.location.global_relative_frame, targetLocation)
            print("Distance to target: ", remainingDistance)
            if remainingDistance <= Drone._POSITION_TOLERANCE:  # Just below target, in case of undershoot.
                print("Reached target")
                break
            if not self._dodgeObstacles():
                print("Obstacle detected, stopping drone ...")
                self.stop_here()
                break
            time.sleep(0.5)

    def _dodgeObstacles(self):
        """ returns True when there is no obstacle, False when it needed to stop """
        grid = self._depth_data
        vmid_free = min(grid[0][1], grid[1][1], grid[2][1]) > self._CRITICAL_DISTANCE
        #vright_free = min(grid[0][2], grid[1][2], grid[2][2]) > self._CRITICAL_DISTANCE
        #vleft_free = min(grid[0][0], grid[1][0], grid[2][0]) > self._CRITICAL_DISTANCE
        front_free = min(grid[0][0], grid[0][1], grid[0][2],
                         grid[1][0], grid[1][1], grid[0][2]) > self._CRITICAL_DISTANCE

        return front_free


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
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation = LocationGlobal(newlat, newlon, original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation = LocationGlobalRelative(newlat, newlon, original_location.alt)
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
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5


