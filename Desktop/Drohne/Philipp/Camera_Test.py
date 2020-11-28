import os
import Main
import camera
import pyrealsense2
import time
import numpy as np

def test():
    cam = camera.Realsense_Camera()
    print('cam connected')
    diffs = []
    print('starting test. use ctrl+c to interrupt')
    try:
        for n in range(10):
            frame, timestamp = cam.get_depth_frame()
            grid = Main.analyze_depth_frame(frame, rowstep=3, colstep=3)
            etime = time.time()
            timediff = etime - (timestamp/1000)
            diffs.append(timediff)
            print('c_time={}, timestamp={}, grid[0][0]={}, diff={}'.format(etime, timestamp, grid[0][0], timediff))
            #qtime.sleep(1)
    except KeyboardInterrupt:
        print('Interrupted after {} reads'.format(n))
    
    cam.close()
    print('test done')
    print("Mean Time Diff = {:.3f}".format(np.mean(diffs)))

if __name__ == '__main__':
    print('Running camera test')
    test()
