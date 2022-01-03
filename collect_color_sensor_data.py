#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

from utils import sound
from utils.brick import EV3ColorSensor, TouchSensor, configure_ports


COLOR_SENSOR_DATA_FILE = "../data_analysis/color_sensor.csv"

TOUCH_SENSOR, COLOR_SENSOR = configure_ports(PORT_1=TouchSensor, PORT_3=EV3ColorSensor)


def collect_color_sensor_data():
    try:
        output_file = open(COLOR_SENSOR_DATA_FILE, "w")
        while True:
            color_data = COLOR_SENSOR.get_value()
            if TOUCH_SENSOR.is_pressed():
                print(color_data)
                output_file.write(f"{color_data}\n")  # r,g,b format
                sound.play_note(note_name='A4', seconds=0.3, vol_factor=0.4)
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        output_file.close()
        exit()


if __name__ == "__main__":
    collect_color_sensor_data()
