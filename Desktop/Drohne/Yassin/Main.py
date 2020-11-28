import Drone_Control
import pyrealsense2
import camera
import time
import dronekit
import numpy as na


cam = None

def analyze_depth_frame(df, rows=3, cols=3):
    assert isinstance(df, pyrealsense2.depth_frame)
    width, height = df.get_width(), df.get_height()
    row_height, column_width = int(height/rows), int(width/cols)
    # prepare grid
    grid = [[99 for i in range(cols)] for j in range(rows)]
    # calculate
    for i in range(0, width, 3):
        for j in range(0, height, 3):
            dist = df.get_distance(i, j)
            x = min(rows-1, int(i/row_height))
            y = min(cols-1, int(j/column_width))
            c = grid[x][y]
            if dist > 0 and c > dist:
                grid[x][y] = dist
    return grid


def get_minimum_dist(depth):
    assert isinstance(depth, pyrealsense2.depth_frame)
    #if not isinstance(depth, pyrealsense2.depth_frame):
    #   return 0.0
    width = depth.get_width()
    height = depth.get_height()
    halfWidth = width / 2
    halfHeight = height / 2

    h0 = depth.get_distance(int(halfWidth), int(halfHeight))
    h1 = depth.get_distance(int(halfWidth / 2), int(halfHeight))
    # h2 = depth.get_distance(int(halfWidth+(halfWidth/2)), int(halfHeight))
    h3 = depth.get_distance(int(halfWidth), int(halfHeight / 2))
    h4 = depth.get_distance(int(halfWidth / 2), int(halfHeight / 2))
    h5 = depth.get_distance(int(halfWidth + (halfWidth / 2)), int(halfHeight / 2))
    # h6 = depth.get_distance(int(halfWidth), int(halfHeight+(halfHeight/2)))
    h7 = depth.get_distance(int(halfWidth / 2), int(halfHeight + (halfHeight / 2)))
    # h8= depth.get_distance(int(halfWidth+(halfWidth/2)), int(halfHeight+(halfHeight/2)))
    not_zero = list(filter(lambda x: x != 0, [h0, h1, h3, h4, h5, h7]))
    if(len(not_zero)!= 0):
        mindar = na.nanmin(not_zero)
    else:
        mindar = 0.0
    return mindar

def detect_collision(vehicle):
    global cam
    assert cam is not None 
    depthframe, timestamp = cam.get_depth_frame()
    if depthframe is None:
        print('no depthframe')
        return 0.0
    mini = get_minimum_dist(depthframe)
    return mini

def detect_obstacles():
    global cam
    assert cam is not None and isinstance(cam, camera.Realsense_Camera)
    depthframe, timestamp = cam.get_depth_frame()
    ctime = time.time()
    if ctime - timestamp > 10:
        print("Timestamp Warning: frame=", timestamp, " current=", ctime)
    return analyze_depth_frame(depthframe)

def main():
    global cam
    cam = camera.Realsense_Camera()
    print("Camera connected")
    drone = Drone_Control.Drone(detect_collision)
    #print("Drone connected")
    #print('Drone Battery = {}'.format(drone.vehicle.battery))
    time.sleep(5)
    drone.arm_and_takeoff(0.7)
    print("Holding altitude for 5 seconds...")
    time.sleep(5)
    #print("crash")
    drone.vehicle.mode = dronekit.VehicleMode("GUIDED")
    
   
   # drone.vehicle.groundspeed=0.1
    #drone.goto(1,0)
    print("Landing...")
    drone.landAndDisarm()
    time.sleep(1)
    drone.vehicle.close()
    print("Landed and disarmed vehicle! Goodbye :)")
    #cam.close()
    
    
if __name__ == '__main__':
    main()
