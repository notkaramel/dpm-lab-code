from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors
from .temp_color import RGBData
import time
import sys

color = EV3ColorSensor(2)
touch = TouchSensor(1)

wait_ready_sensors(True)

try:
    while True:
        if touch.is_pressed():
            dat = RGBData.poll(color)
            print(f"{dat} <= {dat._dat}")
            time.sleep(0.5)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
