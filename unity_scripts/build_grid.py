import pyrealsense2
import numpy as np


def build(df, shape=(3, 4)):
    assert isinstance(df, pyrealsense2.depth_frame)
    grid = np.array(df.get_data())
    grid = reBin(grid, (12, 16))
    return grid


def reBin(a, shape):
    sh = shape[0], a.shape[0]//shape[0], shape[1], a.shape[1]//shape[1]
    return a.reshape(sh).mean(axis=3).mean(axis=1)
