
class DepthAreaCreator:
    count = 1

    def __init__(self, count):
        super().__init__()
        self.count = count


class DepthArea:
    pos_x = 0
    pos_y = 0
    w = 0
    h = 0

    def __init__(self, pos_x, pos_y, w, h):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.w = w
        self.h = h

    def print(self):
        print("[PosX:", self.pos_x, ",PosY:", self.pos_y, ",Width:", self.w, ",Height:", self.h, "]")


