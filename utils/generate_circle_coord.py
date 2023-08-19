import math
import numpy
import numpy as np


def generate_circle_coordinates(center, radius, height, num_points, group=0):
    groups = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = round(center[0] + radius * math.cos(angle))
        y = round(center[1] + radius * math.sin(angle))
        groups.append(np.array([[x, y, height]]))
    return groups
