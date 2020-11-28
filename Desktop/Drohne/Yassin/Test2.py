import numpy as np
import pyrealsense2 as rs
from areas import DepthArea as da
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

x = da(0, 0, 0, 0)
x.print()


pipe = rs.pipeline()

config = rs.config()

config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

profile = pipe.start(config)


depth_sensor = profile.get_device().first_depth_sensor()
# Set high accuracy for depth sensor
depth_scale = depth_sensor.get_depth_scale()


for i in range(0, 1000):
    frames = pipe.wait_for_frames()

    depth = frames.get_depth_frame()

    color_frame = frames.get_color_frame()

    width = depth.get_width()
    height = depth.get_height()

    color = np.asanyarray(color_frame.get_data())
    print(color)

    #plt.rcParams["axes.grid"] = False
    #plt.rcParams['figure.figsize'] = [12, 6]
    plt.imshow(color)
    plt.show()


    dist = depth.get_distance(int(width / 2), int(height / 2))

    print(dist)
   # print(width,height)

pipe.stop()
