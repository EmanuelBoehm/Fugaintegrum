from Simulation.Server import drone
import time

d = drone.Drone()

time.sleep(4)

d.rotate_by(185)
time.sleep(8)
d.rotate_by(20)
