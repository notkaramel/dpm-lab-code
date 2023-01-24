#!/usr/bin/python3
"""DPM Sensor and Filtering (Lecture 8) - SimpleLog.py

A simple program to poll the color sensor and write the results to a log file (colorSensorLog.csv).
Graceful termination when Touch sensor pressed.
Abort on ^C.

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

from utils.brick import BP, Motor, TouchSensor, EV3ColorSensor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 20           # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05     # Polling rate = 50 msec

T_SENSOR = TouchSensor(1)    # Touch Sensor in Port S1
C_SENSOR = EV3ColorSensor(3) # Color Sensor in Port S3

switch_sensor = TouchSensor(2) # Touch Sensor in Port S2

try:
    f = open("temp_calibration.csv", "w")              # Open a file for writing
    # f.write("Data logged from color sensor.\n")   # Print a header

    print('Waiting for sensors to initialize...')
    wait_ready_sensors()                          # Wait for sensors to initialize
    print("Data acquisition commencing...")
    index = 0
    while True:
        try:
            if T_SENSOR.is_pressed():             # End data acquisition if sensor pressed
                print("Data acquisition complete. Closing log file.")
                f.close()                         # Close file (save contents)
                BP.reset_all()                    # Stop robot
                exit()

            if switch_sensor.is_pressed():
                print(f"Switching to Next Index {index} -> {index+1}")
                print(f"Pausing execution...")
                index += 1
                while switch_sensor.is_pressed():
                    time.sleep(1)
                print(f"Resuming execution...")
            
            # Retrieve the color values the Color sensor
            red, gre, blu, lum = C_SENSOR.get_value()

            if red != 0 and gre != 0 and blu != 0:
                # Write color values to the file
                f.write('{:d},{:d},{:d},{:d}\n'.format(red, gre, blu, index))

            time.sleep(SENSOR_POLL_SLEEP)         # Use sensor polling interval here
        except SensorError as error:
            print(error)                          # On exception or error, print error code

except KeyboardInterrupt:                         # Allows program to be stopped on keyboard interrupt
    print("Data acquisition aborted.")
    BP.reset_all()
