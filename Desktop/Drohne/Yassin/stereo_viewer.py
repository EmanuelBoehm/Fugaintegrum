import pyrealsense2 as rs
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


# Setup:
root = tk.Tk()
root.title('Tiefen Aufnahme')
canvas = tk.Canvas(root, width=1280, height=720)

pipe = rs.pipeline()

config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
#config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

profile = pipe.start(config)


# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(20):
    pipe.wait_for_frames()
    

i = -1
while True:
    i+=1

    # Store next frameset for later processing:
    frameset = pipe.wait_for_frames()
    color_frame = frameset.get_color_frame()
    depth_frame = frameset.get_depth_frame()
    
    depth = frameset.get_depth_frame()

    width = depth.get_width()
    height = depth.get_height()

    colorizer = rs.colorizer()
    colorized_depth = np.array(colorizer.colorize(depth_frame).get_data())

    if i == 0:
        canvas = tk.Canvas(root, width=width, height=height)
        root.update()


    array = colorized_depth
    try:
        img = ImageTk.PhotoImage(image=Image.fromarray(array), master=root)
    except Exception:
        break
    canvas.delete("all")
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.update()


# Cleanup:
pipe.stop()
print("Frames Captured")
