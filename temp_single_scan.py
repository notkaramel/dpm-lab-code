from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors
from scratch.temp_color import RGBData
import time
import sys

color = EV3ColorSensor(2)
touch = TouchSensor(1)
marker = TouchSensor(3)

wait_ready_sensors(True)

try:
    while True:
        if marker.is_pressed():
            print("---")
            while marker.is_pressed(): time.sleep(0.1)
        if touch.is_pressed():
            dat = RGBData.poll(color)
            print(f"{dat} <= {[round(c, 3) for c in dat.hsv]}")
            time.sleep(0.5)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
