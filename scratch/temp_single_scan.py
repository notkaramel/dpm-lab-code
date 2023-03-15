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

"""

Red    - 358.8 to 6.757,     0.833 to 0.875, 0.966 to 0.971
Yellow - 8.926 to 12.0,      0.823 to 0.857, 0.945 to 0.952
Orange - 52.224 to 56.176,   0.786 to 0.815, 0.730 to 0.735
Green  - 115.0 to 125.6,     0.643 to 0.696, 0.878 to 0.915
Blue   - 220.0 to 224.706,   0.659 to 0.718, 0.836 to 0.879
Purple - 340.678 to 349.853, 0.772 to 0.843, 0.906 to 0.934  
White  - 90.0 to 266.25,     0.036 to 0.223, 0.582 to 0.657

"""