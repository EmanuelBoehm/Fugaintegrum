import pyrealsense2 as rs
import numpy as na

class Realsense_Camera:
    def __init__(self):
        self.pipe = rs.pipeline()
        self.profile = self.pipe.start()

    def get_depth_frame(self):
        frames = self.pipe.wait_for_frames()
        for f in frames:
            if f.is_depth_frame():
                return f.as_depth_frame(), f.timestamp

    def close(self):
        self.pipe.stop()
