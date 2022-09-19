#!/usr/bin/python3
"""DPM Hands On Example 2 (Lecture 7) - Scan2File

This program builds on the StopOnSw example to include scanning with the color sensor
and writing the results to a data file, colorSensor.txt

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

from utils.brick import BP, Motor, TouchSensor, EV3ColorSensor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 20           # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05     # Polling rate = 50 msec

T_SENSOR = TouchSensor(1)    # Touch Sensor in Port S1
C_SENSOR = EV3ColorSensor(3) # Color Sensor in Port S2

LEFT_MOTOR = Motor("A")      # Left motor in Port A
RIGHT_MOTOR = Motor("D")     # Right motor in Port D

try:
    f = open("colorSensor.txt", "w+")             # Open a file for writing
    f.write("Data logged from color sensor.\n")   # Print a header

    wait_ready_sensors()                  # Wait for sensors to initialize
    LEFT_MOTOR.set_power(FORWARD_SPEED)   # Start left motor
    RIGHT_MOTOR.set_power(FORWARD_SPEED)  # Simultaneously start right motor

    while True:
        try:
            if T_SENSOR.is_pressed():     # Press touch sensor to stop robot
                BP.reset_all()
                exit()

            # Retrieve the color values the Color sensor
            red, gre, blu, lum = C_SENSOR.get_value()

            # Write color values to the file
            f.write('R={:d},G={:d},B={:d},L={:d}\n'.format(red, gre, blu, lum))

            time.sleep(SENSOR_POLL_SLEEP)  # Use sensor polling interval here
        except SensorError as error:
            # On exception or error, print error code
            print(error)
            exit()

except KeyboardInterrupt:                  # Allows program to be stopped on keyboard interrupt
    f.close() # SAVE THE FILE
    BP.reset_all()
