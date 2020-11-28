import Drone_Control
import DephtAnalyzer
import time

def takeoffAndLand():
    # init camera
    analyzer = DephtAnalyzer.Analyzer(rows=3, cols=3, rowstep=3, colstep=3)
    analyzer.start()
    analyzer.waitReady()

    # connect to drone
    drone = Drone_Control.Drone(analyzer.datagrid)

    input('press enter to arm and takeoff')
    drone.arm_and_takeoff(1.5)

    input('press enter to land and disarm')
    drone.landAndDisarm()

    analyzer.stop()
    drone.vehicle.close()
    print('finished')

def takeoffGoAndStop():
    # init camera
    analyzer = DephtAnalyzer.Analyzer(rows=3, cols=3, rowstep=3, colstep=3)
    analyzer.start()
    analyzer.waitReady()

    # connect to drone
    drone = Drone_Control.Drone(analyzer.datagrid)

    input('press enter to arm and takeoff')
    drone.arm_and_takeoff(1.5)
    analyzer.waitNextFrame(n=2) # wait till camera has air data
    drone.vehicle.airspeed = 0.4

    input('press enter to go')
    drone.safe_goto(10, 0)
    time.sleep(1)

    drone.goto(5, 3)
    drone.stop_here()
    time.sleep(1)

    drone.goto(3, -1)

    input('press enter to land and disarm')
    drone.landAndDisarm()

    analyzer.stop()
    drone.vehicle.close()
    print('finished')

if __name__ == '__main__':
    takeoffAndLand()
