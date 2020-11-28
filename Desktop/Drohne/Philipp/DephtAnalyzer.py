from camera import Realsense_Camera
from threading import Thread
from pyrealsense2 import depth_frame
import time

class Analyzer(Thread):
    def __init__(self, rows=3, cols=3, rowstep=1, colstep=1):
        Thread.__init__(self)
        self.name = 'Camera Analyzer'
        self.cam = Realsense_Camera()
        self._force_stop = False
        self._frame_wait = False # run method will set this false after every finished frame
        self._rows, self._columns = rows, cols
        self.datagrid = [[99 for i in range(cols)] for j in range(rows)]
        self._rowheight, self._colwidth = -1, -1
        self._boundsset = False
        self._rowstep, self._colstep = rowstep, colstep

    def __del__(self):
        self.stop()
        if self.cam != None:
            self.cam.close()

    def run(self):
        print('starting to analyze depth data', flush=True)
        while not self._force_stop:
            df, timestamp = self.cam.get_depth_frame()
            if not self._boundsset:
                self._rowheight = int(df.get_height() / self._rows)
                self._colwidth = int(df.get_width() / self._columns)
                self._boundsset = True
            if isinstance(df, depth_frame):
                self._analyze_depthframe(df)
                self._frame_wait = False
        print('depth data analysis stopped', flush=True)

    def _analyze_depthframe(self, frame):
        for i in range(self._rows):
            for j in range(self._columns):
                self._analyze_area(frame, i, j, i*self._colwidth, j*self._rowheight,
                                   (i+1)*self._colwidth, (j+1)*self._rowheight)

    def _analyze_area(self, frame, row, col, x1, y1, x2, y2):
        assert isinstance(frame, depth_frame)
        minimum = 99  # sensor values are < 10.0
        for i in range(y1, y2, self._rowstep):
            for j in range(x1, x2, self._colstep):
                v = frame.get_distance(j, i)
                if v > 0 and v < minimum:
                    minimum = v
        if minimum < 99:
            self.datagrid[row][col] = minimum
        else:
            self.datagrid[row][col] = 0

    def stop(self):
        self._force_stop = True

    def waitNextFrame(self, n=1):
        for i in range(n):
            self._frame_wait = True
            while self._frame_wait:
                time.sleep(0.1)

    def waitReady(self):
        """ wait till first depthframe is fully analyzed """
        # last entry of datagrid gets != 99 when first depthframe is fully analyzed
        while self.datagrid[self._rows-1][self._columns-1] == 99:
            time.sleep(0.1)
