import time
import numpy as np
from Simulation.Server import drone
from Pathfinding import simPathMap, aStar
from Simulation.simCam import simCam

d = drone.Drone()

time.sleep(4)  # Time to start Unity Simulation

pixel_size = 0.4
dest = np.array([4.6, 0.71, 1.0])  # Position of flag
path_map = simPathMap.simPathMap(d.get_pos(), dest, radius=5, pixel_size=pixel_size)
# path_map.plot_map()

pos_points = [dest]
drone_pos = d.get_pos()

while simPathMap.getDist(d.get_pos(), dest) > pixel_size:

    for i in pos_points:
        time.sleep(0.5)
        drone_pos = d.get_pos()
        print("Moving to:", i, "| From:", drone_pos)
        angle_between_points = path_map.get_angle(drone_pos, i)
        print("Angle:", angle_between_points)

        check_reached = False
        can_go = simCam.can_go_further(d.receive_picture())

        # print(can_go)

        # initial check if drone can start
        if not can_go:
            drone_angle = d.get_angle()

            # Unity wählt Winkel negativ wenn sie >180 sind
            if drone_angle < 0:
                drone_angle = 360 + drone_angle
            print("Angle between:", angle_between_points, "| Drone angle:", drone_angle)
            rotate_deg = angle_between_points - d.get_angle()
            print("Drone is now rotating by", rotate_deg, "degrees")
            d.rotate_by(rotate_deg)

            time.sleep(0.75)

        # update can_go after turning
        time.sleep(1)
        can_go = simCam.can_go_further(d.receive_picture())

        # try moving after turning
        if can_go:
            d.move_to(i)

        while can_go:
            time.sleep(0.25)  # Time till next check

            # dist check
            drone_pos = d.get_pos()
            dist = simPathMap.getDist(drone_pos, i)
            # print(dist, can_go)

            can_go = simCam.can_go_further(d.receive_picture())

            # check if a checkpoint has been reached
            if dist < pixel_size:
                # Stop drone
                d.fly_forward(0)
                # Set Flag -> maybe unnecessary - need to think about it
                check_reached = True
                # Delete current checkpoint from list
                np.delete(pos_points, 0)
                # Move on to next checkpoint
                can_go = False

        # Find new path
        if not check_reached:
            d.fly_forward(0)  # Stop!
            break

    time.sleep(0.5)  # wait for new input
    drone_pos = d.get_pos()

    # papath_map.drone_pos ändert sich nicht
    path_map.change_drone_pos(drone_pos)
    time.sleep(0.5)  # wait for new input
    yaw = d.get_angle()
    # print(path_map.drone_pos, drone_pos, yaw)
    time.sleep(0.5)  # wait for new input
    # path_map.plot_map()
    path_map.add_vac_arr(simCam.to_cord(d.receive_picture(), cam_yaw=yaw))

    # Drohne steckt im Sicherheitsrand
    path_map.drone_illegal()

    path_map.plot_map()

    path = aStar.aStar(path_map.path_map, path_map.drone_pos, path_map.dest_pos)
    checkpoints = aStar.create_checkpoints(path)
    pos_points = np.append(path_map.checkpoints_to_pos(checkpoints, drone_pos), np.array([dest]), axis=0)
    # print(pos_points)

    path_map.visualize_path(path)

