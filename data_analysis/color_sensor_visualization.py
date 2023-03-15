#!/usr/bin/env python3

"""
--Color Sensor Data Visualization--

Use to plot RGB data collected from the color sensor.

It should be run on your computer/laptop, not on the robot.

(before running this script for the first time, you must install the dependencies
as explained in README.md)
"""

from ast import literal_eval
from math import sqrt, e, pi
from statistics import mean, stdev

from matplotlib import pyplot as plt
import numpy as np


COLOR_SENSOR_DATA_FILE = "color_sensor.csv"
X_RESOLUTION = 1000


def gaussian(x, values):
    "Return a gaussian function from the given values."
    sigma = stdev(values)
    return (1 / (sigma * sqrt(2 * pi))) * e ** (-((x - mean(values)) ** 2) / (2 * sigma ** 2))


def ratio_normalization(r, g, b):
    """ RATIO METHOD """
    denominator = r + g + b
    return r/denominator, g/denominator, b/denominator


def vector_normalization(r, g, b):
    """ UNIT-VECTOR METHOD """
    denominator = sqrt(r**2 + g**2 + b**2)
    return r/denominator, g/denominator, b/denominator


def main(normalization_function):
    red, green, blue = [], [], []
    with open(COLOR_SENSOR_DATA_FILE, "r") as f:
        for line in f.readlines():
            r, g, b = literal_eval(line)  # convert string to 3 floats
            # normalize the values to be between 0 and 1

            r, g, b = normalization_function(r, g, b)

            red.append(r)
            green.append(g)
            blue.append(b)

    # 255 evenly spaced values between 0 and 1
    x_values = np.linspace(0, 1, X_RESOLUTION)
    plt.plot(x_values, gaussian(x_values, red), color="r")
    plt.plot(x_values, gaussian(x_values, green), color="g")
    plt.plot(x_values, gaussian(x_values, blue), color="b")
    plt.xlabel("Normalized intensity value")
    plt.ylabel("Normalized intensity's PDF by color")

    print(sum(gaussian(x_values, red)/X_RESOLUTION))
    plt.show()


def help_msg():
    print("\nRun this program on your computer.\n")
    print("These are your options:\n")
    print("python color_sensor_visualization")
    print("\t**Default Visualization Type**\n")
    print("python color_sensor_visualization ratio")
    print("\t**Ratio Visualization Type**\n")
    print("python color_sensor_visualization vector")
    print("\t**Unit Vector-Based Visualization Type**\n")


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1 or sys.argv[1] == 'ratio':
        main(ratio_normalization)
    elif sys.argv[1] == 'vector':
        main(vector_normalization)
    else:
        help_msg()
