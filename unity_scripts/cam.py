import camera
import build_grid


def test():
    cam = camera.Realsense_Camera()
    if cam is not None:
        print 'connected to camera'
    print('starting test. use ctrl+c to interrupt')
    try:
        for n in range(1):
            frame = cam.get_depth_frame()
            grid = build_grid.build(frame, shape=(12, 16))
    except KeyboardInterrupt:
        print('Interrupted after {} reads'.format(n))

    cam.close()
    print('test done')


if __name__ == '__main__':
    print('Running camera test')
    test()
