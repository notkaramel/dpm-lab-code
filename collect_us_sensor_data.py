#!/usr/bin/env python3

"""
This test is used to collect continuous and discrete data from the ultrasonic sensor.
It must be run on the robot.
"""

from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, configure_ports, reset_brick
from time import sleep


DELAY_SEC = 0.01  # seconds of delay between measurements
US_SENSOR_DATA_FILE = "../data_analysis/us_sensor.csv"

print("Program start.\nWaiting for sensors to turn on...")

TOUCH_SENSOR, US_SENSOR = configure_ports(PORT_1=TouchSensor, PORT_2=EV3UltrasonicSensor)

print("Done waiting.")


def collect_continuous_us_data():
    "Collect continuous data from the ultrasonic sensor between two button presses."
    try:
        output_file = open(US_SENSOR_DATA_FILE, "w")
        while not TOUCH_SENSOR.is_pressed():
            pass  # do nothing while waiting for first button press
        print("Touch sensor pressed")
        sleep(1)
        print("Starting to collect US distance samples")
        while not TOUCH_SENSOR.is_pressed():
            us_data = US_SENSOR.get_value()  # Float value in centimeters 0, capped to 255 cm
            print(us_data)
            output_file.write(f"{us_data}\n")
            sleep(DELAY_SEC)
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        print("Done collecting US distance samples")
        output_file.close()
        exit()


def collect_discrete_us_data():
    "Collect discrete data from the ultrasonic sensor at each button presse."
    print("Program start.")
    try:
        output_file = open(US_SENSOR_DATA_FILE, "w")
        while True:
            us_data = US_SENSOR.get_value()  # Float value in centimeters 0 to 255 limits
            if TOUCH_SENSOR.is_pressed():
                print(us_data)
                output_file.write(str(us_data) + '\n')
                sound.play_note(note_name='A4', seconds=0.3, vol_factor=0.4)
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        output_file.close()
        exit()


if __name__ == "__main__":
    # collect_continuous_us_data()
    collect_discrete_us_data()
