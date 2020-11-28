#import Drone_Control
import time
import pyrealsense2 as rs
from dronekit import Vehicle
from threading import Thread
import DephtAnalyzer
import numpy as na
import Main
from Visualizer import ui as vui

test = None

class visualizerUIThread(Thread):
    def __init__(self, ui, analyzer):
        Thread.__init__(self)
        self._ui = ui
        self.an = analyzer

    def run(self):
        assert isinstance(self._ui, vui)
        assert isinstance(self.an, DephtAnalyzer.Analyzer)
        while self.an.is_alive():
            if self._ui.window.winfo_exists(): # if windows is still open
                self._ui.analyze_depth_data(self.an.datagrid, 6, 6)

def collsion_detection(vehicle):
    assert isinstance(vehicle, dronekit.Vehicle)

def test2():
    test_data = [[0, 0, 0, 0, 0, 0, 9, 9, 9],
                 [0, 1, 2, 0, 0, 0, 9, 9, 9],
                 [0, 3, 0, 0, 0, 0, 9, 9, 9],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 2, 0, 0, 1, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 3, 0, 0, 0, 0, 0, 2, 3],
                 [0, 0, 0, 0, 0, 0, 4, 0, 1]]
    res = Main.analyze_depth_frame(test_data, isArray=True)
    print(res)

def test3():
    r, c = 6, 6
    a = DephtAnalyzer.Analyzer(rows=r, cols=c)
    u = vui(n=r, m=c)
    vut = visualizerUIThread(u, a)

    a.start()
    vut.start()

    u.start()

    a.stop()
    a.join()
    del a

def test4():
    input('Press Enter to start')
    print('starting ...')
    input('press enter to finish')

def main():
    pipe = rs.pipeline()

    pipe.start()
    profile = pipe.get_active_profile()

    for i in range(100):
        frames = pipe.wait_for_frames()
        for f in frames:
            if f.is_depth_frame():
                df = f.as_depth_frame()
                print(df.get_distance(100, 100))
    pipe.stop()
    drohne = Drone_Control.Drone(collsion_detection)

if __name__ == '__main__':
    test = 'abc'
    test3()
    # main()