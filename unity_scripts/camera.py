import pyrealsense2 as rs


class Realsense_Camera:
    def __init__(self):
        self.pipe = rs.pipeline()
        self.profile = self.pipe.start()

    def get_depth_frame(self):
        return self.pipe.wait_for_frames().get_depth_frame()

    def close(self):
        self.pipe.stop()
