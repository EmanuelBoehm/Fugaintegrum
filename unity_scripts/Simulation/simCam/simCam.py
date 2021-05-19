from math import sin, cos, radians
import numpy as np


def min_reBin(a, shape):
    sh = shape[0], a.shape[0] // shape[0], shape[1], a.shape[1] // shape[1]
    return a.reshape(sh).min(axis=3).min(axis=1)


def mean_reBin(a, shape):
    sh = shape[0], a.shape[0] // shape[0], shape[1], a.shape[1] // shape[1]
    return a.reshape(sh).mean(axis=3).mean(axis=1)


def max_reBin(a, shape):
    sh = shape[0], a.shape[0] // shape[0], shape[1], a.shape[1] // shape[1]
    return a.reshape(sh).max(axis=3).max(axis=1)

# todo medain rebin


def can_go_further(dist_array):
    """
    Decides if the drone can still move further
    if every point in a certain part is far enough away
    :param dist_array: depth frame
    :return: boolean
    """
    # [39:80, 39:120] middle third of height and center half of width
    dist_array = max_reBin(dist_array, (120, 160))[9:110, 19:140]
    return (dist_array[dist_array != 0.0] > 1).all()


def to_cord(dist_array, cam_pitch=0, cam_yaw=0, cam_position=None, z_range=0.15):
    """
    realSense d435 depthcam -> 86°x57° FOV
    :param z_range: distance from center in which the possible collision points are
    :param dist_array: array of distances in mm
    :param cam_pitch: camara pitch/drone tilt
    :param cam_yaw: yaw of camera/drone
    :param cam_position: gps location of camera
    :return array with coordinates
    """

    if cam_position is None:
        cam_position = [0, 0, 0]

    cam_yaw = 90 - cam_yaw
    # reducing the size of the array to conserve computing power
    dist_array = max_reBin(dist_array, (120, 160))

    # Array we will put the coordinates in
    vec_arr = []
    for j in range(120):
        for i in range(160):
            if dist_array[j][i] != 0.0:
                alpha = (47.0 + (2 * i + 1) * (43.0 / 160))  # Grad X|Y
                beta = (28.5 - (2 * j + 1) * (28.5 / 120))  # Grad Y|Z
                r = dist_array[j][i]
                vec_arr.append(np.array([r * cos(radians(beta)) * sin(radians(alpha)),
                                         r * cos(radians(beta)) * cos(radians(alpha)),
                                         r * sin(radians(beta))]))
    trans_yaw = np.array([
        [cos(radians(cam_yaw)), -sin(radians(cam_yaw)), 0],
        [sin(radians(cam_yaw)), cos(radians(cam_yaw)), 0],
        [0, 0, 1]
    ])
    trans_pitch = np.array([
        [cos(radians(cam_pitch)), 0, sin(radians(cam_pitch))],
        [0, 1, 0],
        [-sin(radians(cam_pitch)), 0, cos(radians(cam_pitch))],
    ])

    # np.matmul statt @, damit wir nicht abhängig von Python 3.5+ sind
    res = [np.matmul(np.matmul(trans_yaw, trans_pitch), x) + cam_position for x in vec_arr if
           (-z_range < np.matmul(np.matmul(trans_yaw, trans_pitch), x)[2] < z_range)]
    # Nur die Punkte die +-15cm von der Mitte entfernt sind
    return np.array(res)
