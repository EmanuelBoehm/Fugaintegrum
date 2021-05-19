from io import BytesIO

from PIL import Image

from Simulation.Server import UdpServer as udp, TcpServer as tcp
import numpy as np
import json


class Drone:
    def __init__(self, udpIP="127.0.0.1", portTX=8000, portRX=8001):
        self.pos = None
        self.pic = None
        self.angle = 0.
        self.tcp_server = tcp.TcpServer()
        self.udp_server = udp.UdpServer(udpIP, portTX, portRX, enableRX=True, suppressWarnings=True)

    def receive_data(self):
        """
        Returns the received positional data from unity
        :return:
        """
        return self.udp_server.ReadReceivedData()

    def receive_picture(self):
        """
        Returns the last received depth_frame from unity
        returned value cant be read again because it will be deleted from buffer after accessing this method
        :return:
        """

        pic_data = None
	img_bytes = self.tcp_server.ReadReceivedData()
        if img_bytes != None:
            try:
                pic_data = Image.open(BytesIO(img_bytes)))
            except UnidentifiedImageError:
                print("image was not send correctly")
                
        if pic_data is None:
            return self.pic

        pic = np.array([[i[0] for i in j] for j in np.array(pic_data))])

        # 15.4 -> Unity cam frame max dist
        # 0.2 -> Unity min dist
        pic = (pic / 255) * 15.4 + 0.2

        # Set everything with max dist (white pixels) to 0 for easier removal
        pic[pic == 15.6] = 0

        self.pic = pic  # Safe last pic

        return pic

    def fly_forward(self, dist=0.):
        data = {
            "name": "fly_forward",
            "dist": dist,
        }
        self.udp_server.SendData(str(data))

    def move_to(self, dest):
        data = {
            "name": "move_to",
            "x": dest[0],
            "y": dest[2],
            "z": dest[1],  # unity weird -> switch z,y
        }
        # print(str(data))
        self.udp_server.SendData(str(data))

    # Dont use, unlike drone features
    def move_to_relative(self, x=0., y=0., z=0.):
        # x,y,z = self.float_cs(x,y,z)
        # print(x)
        data = {
            "name": "move_to_relative",
            "x": x,
            "y": y,
            "z": z,
        }
        self.udp_server.SendData(str(data))

    # Rotates relative to current drone angle
    # E.g Drone looks East (90 deg) and we call (rotate_by(90))
    # Drone will then be facing South (180 deg)
    # Pos input -> clockwise
    # Neg input -> counter clock
    def rotate_by(self, angle=0.):
        data = {
            "name": "rotate_by",
            "angle": angle
        }
        self.udp_server.SendData(str(data))

    def get_pos(self):
        temp = self.receive_data()
        if temp is not None:
            pos = np.array(json.loads(temp)["pos"])
            # Unity weird again (¬_¬ )
            pos = [pos[0], pos[2], pos[1]]
            self.pos = pos  # Safe last pos
            # print(pos)
            return pos
        return self.pos

    def get_angle(self):
        temp = self.receive_data()
        if temp is not None:
            angle = np.array(json.loads(temp)["angle"])
            self.angle = angle  # Safe last pos
            return self.angle
        return self.angle


# Test zeug
"""
time.sleep(0.5)
at_dest = False
s = drone.receive_data()
data = json.loads(s)
while not at_dest:
    temp = drone.receive_data()
    if temp is not None:
        data = json.loads(temp)
        pos = np.array(data["pos"])
        dis = sum(((dest - pos) ** 2)) ** 0.5
        if dis < 0.25:
            print("Yay, wir sind da")
            at_dest = True
            print(drone.receive_picture())

        else:
            print(dis)




def main():
    drone = Drone()
    from pynput import keyboard

    def on_release(key):
        if key == keyboard.Key.esc:
            return False  # stop listener
        try:
            k = key.char  # single-char keys
        except:
            k = key.name
        if k == 'left':
            drone.rotate_by(-15.)
        if k == 'right':
            drone.rotate_by(15.)
        if k == 'up':
            drone.fly_forward(0.5)
        if k == 'down':
            drone.move_by_relative(10., 0., 3.)

    listener = keyboard.Listener(on_press=on_release)
    listener.start()  # start to listen on a separate thread
    listener.join()  # remove if main thread is polling self.keys

    #### just for testing
    from PIL import Image
    import numpy as np
    from io import BytesIO
    i = 0
    while True:
        i = (i + 1) % 5

        data = drone.receive_data()  # read data
        pic = drone.receive_picture()
        if data != None:  # if NEW data has been received since last ReadReceivedData function call
            print(data)
        if pic != None and i == 0:
            ar = np.array(Image.open(BytesIO(pic)))
            # print(ar)


if __name__ == '__main__':
    main()
"""
