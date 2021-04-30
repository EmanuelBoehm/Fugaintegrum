import matplotlib.pyplot as plt
import numpy as np
from math import atan, degrees


def getDist(pos_drone, pos_dest):
    return sum((pos_drone - pos_dest) ** 2) ** 0.5  # 6366 -> Earth radius at ~50° lat


class simPathMap:

    def __init__(self, pos_drone, pos_dest, radius=5, pixel_size=1.0):
        self.root = pos_drone
        self.cord_drone = pos_drone
        self.pixel_size = pixel_size

        # Entfernungen auf die pixel size anpassen
        height = self.horiDist(pos_drone, pos_dest)
        width = self.vertDist(pos_drone, pos_dest)

        # print("Before", width, height)

        # Kann zusammengefasst werden, aber unübersichtlich
        width = round(width + (2 * radius * width) / (abs(width) * pixel_size))
        height = round(height + (2 * radius * height) / (abs(height) * pixel_size))
        # print("After", height, width)

        # 0 und 1 tauschen ? - ! -done
        self.drone_pos = [int(round(-height * (radius / pixel_size) / abs(height))),
                          int(round(width * (radius / pixel_size) / abs(width)))]
        self.dest_pos = [int(round(height * (radius / pixel_size) / abs(height))),
                         int(round(-width * (radius / pixel_size) / abs(width)))]

        self.width = int(abs(width))
        self.height = int(abs(height))

        # Anpassen der negativen werte auf richtige Positionen
        if self.dest_pos[0] < 0:
            self.dest_pos[0] = self.height + self.dest_pos[0]
        if self.dest_pos[1] < 0:
            self.dest_pos[1] = self.width + self.dest_pos[1]
        if self.drone_pos[0] < 0:
            self.drone_pos[0] = self.height + self.drone_pos[0]
        if self.drone_pos[1] < 0:
            self.drone_pos[1] = self.width + self.drone_pos[1]

        # print(self.drone_pos, self.dest_pos)

        self.path_map = np.array([
            [0.5 if ((i != 0) and (i != self.width - 1) and (j != 0) and (j != self.height - 1)) else 1 for i in
             range(self.width)] for j in range(self.height)])

        # range normalisieren ([0,1]), damit der Plot die Farben richtig anfängt
        self.path_map[0][0] = 0

        # Farbe des Ziels und der Drohne setzen
        self.path_map[self.drone_pos[0]][self.drone_pos[1]] = 0.75
        self.path_map[self.dest_pos[0]][self.dest_pos[1]] = 0.25
        # print(len(self.path_map), len(self.path_map[0]))

    def vertDist(self, pos_root, pos_dest):
        return int(round((pos_dest[0] - pos_root[0]) / self.pixel_size))

    def horiDist(self, pos_root, pos_dest):
        return int(round((pos_dest[1] - pos_root[1]) / self.pixel_size))

    def get_angle(self, pos_root, pos_dest):
        hd = self.horiDist(pos_root, pos_dest)
        vd = self.vertDist(pos_root, pos_dest)

        if vd == 0:
            if hd > 0:
                return 0
            else:
                return 180

        if vd < 0:
            return 270 - degrees(atan(hd / vd))

        return 90 - degrees(atan(hd / vd))

    def change_drone_pos(self, pos_new):
        """
        Ändert die Position der Drohne auf der Karte
        :param pos_new: Neue Koordinate der Drohne (lat, log)
        """
        vDist = self.vertDist(self.cord_drone, pos_new)
        hDist = self.horiDist(self.cord_drone, pos_new)

        # print("vertical and horizontal distances:", vDist, hDist)

        if (0 < (self.drone_pos[0] - hDist) < self.height) and (0 < (self.drone_pos[1] + vDist) < self.width):
            self.cord_drone = pos_new

            # remove current drone point
            self.path_map[self.drone_pos[0]][self.drone_pos[1]] = 0.5

            # add new drone point
            self.path_map[self.drone_pos[0] - hDist][self.drone_pos[1] + vDist] = 0.75

            # update pos_drone
            self.drone_pos = [self.drone_pos[0] - hDist, self.drone_pos[1] + vDist]

    def add_vec(self, vec, label=1):
        """
        Fügt ein vector hinzu. Der Vektor enthält die x/y Abstände des Punkten im Verhältnis zur Drohne
        :param vec: Vektor mit (x,y) Abstände in Metern
        :param label: Label der Koordinate (1 = Hinderniss, 0.75 = Drohne, 0.25 = Ziel)
        """
        x = self.drone_pos[1] + int(round(vec[0] / self.pixel_size))
        y = self.drone_pos[0] - int(round(vec[1] / self.pixel_size))

        # Point
        p = None

        if (0 < y < self.height) and (0 < x < self.width):
            if self.path_map[y][x] == 0.5:
                self.path_map[y][x] = label
                p = (y, x)

        return p

    def add_vac_arr(self, array, label=1):
        p = []
        for i in array:
            t = self.add_vec(i, label)
            if t is not None:
                p.append(t)

        # Fügt den Sicherheitsrand für alle Punkte ein, die nicht vollständig von anderen umgeben sind
        for i, j in p:
            # Nachbar check
            if not ((i + 1, j) in p and (i - 1, j) in p and (i, j - 1) in p and (i, j + 1) in p):
                self.mark_boarder(vec=(i, j), radius=1.3 / self.pixel_size)

    def visualize_path(self, path):
        temp_map = self.path_map.copy()
        # [1:-1] nicht erstes und letztes element
        for i in path[1:-1]:
            temp_map[i[0]][i[1]] = 0.15
        plt.imshow(temp_map, cmap='twilight_shifted')
        plt.xticks(())
        plt.yticks(())
        plt.show()

    def plot_map(self):
        plt.imshow(self.path_map, cmap='twilight_shifted')
        plt.xticks(())
        plt.yticks(())
        plt.show()

    def checkpoints_to_pos(self, checkpoints, drone_cord):
        pos_points = []
        for i in checkpoints:
            t = np.array([self.drone_pos[1] - i[1], i[0] - self.drone_pos[0], 0])
            pos_points.append(np.array(drone_cord) - t * self.pixel_size)
        return np.array(pos_points)

    def drone_illegal(self):
        self.path_map[self.drone_pos[0]][self.drone_pos[1]] = 0.75
        for j in [[1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]]:
            self.path_map[self.drone_pos[0] + j[0]][self.drone_pos[1] + j[1]] = 0.5

    def mark_boarder(self, vec, radius):
        array = self.path_map
        dist_array = np.array(
            [[np.sum((np.array((j, i)) - vec) ** 2) ** 0.5 for i in range(len(array[0]))] for j in range(len(array))])
        self.path_map[np.logical_and(dist_array < radius, self.path_map == 0.5)] = 0.9
