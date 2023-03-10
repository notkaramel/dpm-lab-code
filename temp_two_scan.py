from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors
from scratch.temp_color import RGBData, ColorProfile, ColorGroup, ColorDetector
import time
import sys

detector = ColorDetector(None, ColorGroup.gaussian_dist, ColorDetector.by_min_value)
profiles_list = detector.color_group.profiles
profiles_list.append(ColorProfile.UNKNOWN)
profiles_list.append(ColorProfile.UNKNOWN)

samples1 = []
samples2 = []

color = EV3ColorSensor(2)
touch1 = TouchSensor(1)
touch2 = TouchSensor(3)

wait_ready_sensors(True)

try:
    while True:
        dat = RGBData.poll(color)
        if touch1.is_pressed():
            print(f"Color 1: {dat} <= {[round(c, 3) for c in dat.normalized]}")

            samples1.append(dat)
            try:
                profiles_list[0] = ColorProfile.from_data("Color 1", samples1)
            except:
                pass

            time.sleep(0.5)
        if touch2.is_pressed():
            print(f"Color 2: {dat} <= {[round(c, 3) for c in dat.normalized]}")

            samples2.append(dat)
            try:
                profiles_list[1] = ColorProfile.from_data("Color 2", samples2)
            except:
                pass

            time.sleep(0.5)

        print(detector.determine(dat))
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
