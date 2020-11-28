import os
import Main
import camera
import pyrealsense2
import time

def test():
    cam = camera.Realsense_Camera()
    print('cam connected')
    
    print('starting test. use ctrl+c to interrupt')
    n = 0
    try:
        while n < 20:
            frame, timestamp = cam.get_depth_frame()
            grid = Main.analyze_depth_frame(frame)
            etime = time.time()
            print('c_time={}, timestamp={}, grid[0][0]={}, diff={}'.format(etime, timestamp, grid[0][0],(etime - (timestamp/1000))))
            #qtime.sleep(1)
            n += 1
    except KeyboardInterrupt:
        print('Interrupted after {} reads'.format(n))
    
    cam.close()
    print('test done')

if __name__ == '__main__':
    print('Running camera test')
    test()