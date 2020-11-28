import Drone_Control
import pyrealsense2
import camera
import time


cam = None

def analyze_depth_frame(df, rows=3, cols=3):
    assert isinstance(df, pyrealsense2.depth_frame)
    width, height = df.get_width(), df.get_height()
    row_height, column_width = height/rows, width/cols
    # prepare grid
    grid = [[99 for i in range(cols)] for j in range(rows)]
    # calculate
    for i in range(height):
        for j in range(width):
            dist = df.get_distance(i, j)
            c = grid[int(i/row_height)][int(j/column_width)]
            if dist > 0 and (c > dist or c < 0):
                grid[int(i/row_height)][int(j/column_width)] = dist
    return grid

def analyze_depth_frameT(df, rows=3, cols=3):
    width, height = len(df[0]), len(df)
    row_height, column_width = height/rows, width/cols
    # prepare grid
    grid = [[-1 for i in range(cols)] for j in range(rows)]
    # calculate
    for i in range(height):
        for j in range(width):
            dist = df[i][j]
            c = grid[int(i/row_height)][int(j/column_width)]
            if dist > 0 and (c > dist or c < 0):
                grid[int(i/row_height)][int(j/column_width)] = dist
    return grid



def get_minimum_dist(depth):
    assert isinstance(depth, pyrealsense2.depth_frame)
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
    mindar = na.nanmin(not_zero)
    return mindar

def detect_collision(vehicle):
    global cam
    assert cam is not None and isinstance(cam, camera.Realsense_Camera)
    depthframe, timestamp = cam.get_depth_frame()
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
    drone = Drone_Control.Drone(detect_collision)
    print('Drone Battery = {}'.format(drone.vehicle.battery))

if __name__ == '__main__':
    main()
