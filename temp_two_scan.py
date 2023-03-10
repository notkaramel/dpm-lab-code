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
    print([ (p.color_mean, p.color_stdev) for p in profiles_list])


"""
Red -    0.97 0.17 0.14 | 0.0046 0.0203 0.0357
Orange - 0.96 0.26 0.13 | 0.0065 0.0199 0.0251
Purple - 0.93 0.17 0.33 | 0.0131 0.0199 0.0383
Blue -   0.30 0.47 0.83 | 0.0368 0.0293 0.0218
Yellow - 0.73 0.67 0.11 | 0.0182 0.0209 0.0068
Green -  0.29 0.92 0.26 | 0.0160 0.0116 0.0261

Red -    
Orange - 
Purple - 
Blue -   
Yellow - 
Green  - 
"""