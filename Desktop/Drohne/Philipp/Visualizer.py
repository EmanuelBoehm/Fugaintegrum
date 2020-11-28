import pyrealsense2 as realsense
import numpy as np
from tkinter import Tk, Canvas


class ui:

    width, height = 1280, 720

    def __init__(self, n=6, m=6):
        assert isinstance(n, int) and n in range(0, 100)
        assert isinstance(m, int) and m in range(0, 100)
        self.n, self.m = n, m
        self.window = Tk()
        self.canvas = Canvas(self.window, width=ui.width, height=ui.height)
        self.canvas.pack()
        self.generate_rectangles(self.canvas)

    def set_color(self, x, y, color):
        assert isinstance(x, int) and x in range(self.n)
        assert isinstance(y, int) and y in range(self.m)
        assert isinstance(color, str)
        self.canvas.itemconfig(self.rectangles[y][x], fill=color)

    def generate_rectangles(self, c):
        self.rectangles = []
        recs = self.rectangles
        for i in range(self.n):
            recs.append([])
            for j in range(self.m):
                x = i * self.width / self.n
                y = j * self.height / self.m
                recs[i].append(c.create_rectangle(x, y, x + ui.width / self.n - 5, y + ui.height / self.m - 5, fill='green',
                                                  outline=""))

    def _from_rgb(self, rgb):
        """
        translates an rgb tuple of int to a tkinter friendly color code
        """
        return "#%02x%02x%02x" % rgb

    def analyze_depth_data(self, a, n, m):
        for i in range(n):
            for j in range(m):
                c = a[i][j]
                if c <= 0:
                    self.set_color(i, j, self._from_rgb((255, 255, 255)))
                    continue
                if c >= 5:
                    red = 255 - int(255 * (c - 5) / 5)
                    green = 255
                else:
                    red = 255
                    green = int(255 * c / 5)
                self.set_color(i, j, self._from_rgb((red, green, 0)))

    def start(self):
        w = self.window
        w.mainloop()


test_data = [[10, 9, 8, 7, 6, 5, 4, 3, 2],
             [0.01, 1, 2, 0, 0, 0, 9, 9, 9],
             [0, 3, 0, 0, 0, 0, 9, 9, 9],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 2, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 3, 0, 0, 0, 0, 0, 2, 3],
             [0, 0, 0, 0, 0, 0, 4, 0, 1]]

#t = ui(9, 9)
#t.analyze_depth_data(test_data, len(test_data), len(test_data[0]))
#t.start()