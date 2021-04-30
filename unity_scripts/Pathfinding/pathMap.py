from math import cos, sqrt, pi, asin
import matplotlib.pyplot as plt


def getDist(cord_drone, cord_dest):
    """
    https://en.wikipedia.org/wiki/Haversine_formula
    """
    lat1, lon1, lat2, lon2 = cord_drone[0], cord_drone[1], cord_dest[0], cord_dest[1]
    p = pi / 180
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 2 * 6366 * asin(sqrt(a)) * 1000  # 6366 -> Earth radius at ~50° lat


def vertDist(cord_root, cord_dest):
    temp = (cord_dest[0], cord_root[1])
    if cord_root[0] < cord_dest[0]:
        return getDist(cord_root, temp)
    else:
        return -getDist(cord_root, temp)


def horiDist(cord_root, cord_dest):
    temp = (cord_root[0], cord_dest[1])
    if cord_root[1] < cord_dest[1]:
        return getDist(cord_root, temp)
    else:
        return -getDist(cord_root, temp)


class PathMap:

    def __init__(self, cord_drone, cord_dest, radius=5, pixel_size=1):
        self.root = cord_drone
        self.cord_drone = cord_drone
        self.pixel_size = pixel_size

        width = horiDist(cord_drone, cord_dest) / pixel_size
        height = vertDist(cord_drone, cord_dest) / pixel_size
        # Kann zusammengefasst werden, aber unübersichtlich
        width = round(width + (2 * radius * width) / (abs(width) * pixel_size))
        height = round(height + (2 * radius * height) / (abs(height) * pixel_size))

        # 0 und 1 tauschen ? - ! -done
        self.drone_pos = [round(-height * (radius / pixel_size) / abs(height)),
                          round(width * (radius / pixel_size) / abs(width))]
        self.dest_pos = [round(height * (radius / pixel_size) / abs(height)),
                         round(-width * (radius / pixel_size) / abs(width))]

        # print(self.drone_pos, self.dest_pos)

        self.width = abs(width)
        self.height = abs(height)

        # Anpassen der negativen werte auf richtige Positionen
        if self.dest_pos[0] < 0:
            self.dest_pos[0] = self.height + self.dest_pos[0]
        if self.dest_pos[1] < 0:
            self.dest_pos[1] = self.width + self.dest_pos[1]
        if self.drone_pos[0] < 0:
            self.drone_pos[0] = self.height + self.drone_pos[0]
        if self.drone_pos[1] < 0:
            self.drone_pos[1] = self.width + self.drone_pos[1]

        self.path_map = [
            [0.5 if ((i != 0) and (i != self.width - 1) and (j != 0) and (j != self.height - 1)) else 1 for i in
             range(self.width)] for j in range(self.height)]

        # range normalisieren ([0,1]), damit der Plot die Farben richtig anfängt
        self.path_map[0][0] = 0

        # Farbe des Ziels und der Drohne setzen
        self.path_map[self.drone_pos[0]][self.drone_pos[1]] = 0.75
        self.path_map[self.dest_pos[0]][self.dest_pos[1]] = 0.25
        # print(len(self.path_map), len(self.path_map[0]))

    def add_cord(self, cord, lable):
        """
        Füngt eine Koordinate (lat, lon) der map hinzu, wenn diese innerhalb des Rahmens liegt
        :param cord: Koordinate des Punktes der hinzugefügt werden soll
        :param lable: Label der Koordinate (0 = Hinderniss, 0.75 = Drohne, 0.25 = Ziel)

        Wahrscheinlich nur nützlich um mehrere Ziele hinzuzufügen, bzw für Checkpoints o.Ä
        """
        vDist = round(vertDist(self.root, cord) / self.pixel_size)
        hDist = round(horiDist(self.root, cord) / self.pixel_size)

        if (0 < (self.drone_pos[0] - vDist) < self.height) and (0 < (self.drone_pos[1] + hDist) < self.width):
            self.path_map[self.drone_pos[0] - vDist][self.drone_pos[1] + hDist] = lable

    def change_drone_pos(self, cord_new):
        """
        Ändert die Position der Drohne auf der Karte
        :param cord_new: Neue Koordinate der Drohne (lat, log)
        """
        vDist = round(vertDist(self.cord_drone, cord_new) / self.pixel_size)
        hDist = round(horiDist(self.cord_drone, cord_new) / self.pixel_size)
        if (0 < (self.drone_pos[0] - vDist) < self.height) and (0 < (self.drone_pos[1] + hDist) < self.width):
            self.cord_drone = cord_new

            # remove current drone point
            self.path_map[self.drone_pos[0]][self.drone_pos[1]] = 0.5

            # add new drone point
            self.path_map[self.drone_pos[0] - vDist][self.drone_pos[1] + hDist] = 0.75

            # update pos_drone
            self.drone_pos = [self.drone_pos[0] - vDist, self.drone_pos[1] + hDist]

    def add_vec(self, vec, lable):
        """
        Fügt ein vector hinzu. Der Vektor enthält die x/y Abstände des Punkten im Verhältnis zur Drohne
        :param vec: Vektor mit (x,y) Abstände in Metern
        :param lable: Label der Koordinate (0 = Hinderniss, 0.75 = Drohne, 0.25 = Ziel)
        """
        x = round(vec[0] / self.pixel_size)
        y = round(vec[1] / self.pixel_size)
        if (0 < (self.drone_pos[0] - y) < self.height) and (0 < (self.drone_pos[1] + x) < self.width):
            self.path_map[self.drone_pos[0] - y][self.drone_pos[1] + x] = lable

    def visualize_path(self, path):
        temp_map = self.path_map.copy()
        for i in path:
            temp_map[i[0]][i[1]] = 0.15
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        plt.imshow(temp_map, cmap='twilight_shifted')
        plt.xticks(())
        plt.yticks(())
        plt.show()

    def plot_map(self):
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        plt.imshow(self.path_map, cmap='twilight_shifted')
        plt.xticks(())
        plt.yticks(())
        plt.show()
