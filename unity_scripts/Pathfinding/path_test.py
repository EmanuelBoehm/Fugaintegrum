import time
import numpy as np
from Simulation.Server import drone
from Pathfinding import simPathMap, aStar
from Simulation.simCam import simCam

d = drone.Drone()

time.sleep(4)  # Time to start Unity Simulation

pixel_size = 1
dest = np.array([4.0, 5.4, 1.0])  # Position of flag
path_map = simPathMap.simPathMap(d.get_pos(), dest, radius=5, pixel_size=pixel_size)
pos_points = [dest]

time.sleep(0.5)

# path_map.plot_map()
a = simCam.to_cord(d.receive_picture(), cam_yaw=d.get_angle())
path_map.add_vac_arr(a)

# Drohne steckt im Sicherheitsrand
path_map.drone_illegal()

path_map.plot_map()
