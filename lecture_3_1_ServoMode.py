#!/usr/bin/python3
"""DPM Hands On Example 3 (Lecture 10) - MotorDemo

A simple interactive program that allows the user to specify the rotation and 
speed for an EV3 Large Motor. Prgoram operates a loop until ^C entered.

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

from utils.brick import BP, Motor
import time

AUX_MOTOR = Motor("C") # Auxilliary Motor used for test
POWER_LIMIT = 80       # Power limit = 80%
SPEED_LIMIT = 720      # Speed limit = 720 deg per sec (dps)

try:
    print("Motor Position Control Demo")

    # Encoder keeps a record of degrees turned
    AUX_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    AUX_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    AUX_MOTOR.set_power(0)

    while True:
        speed = int(input('Enter speed:'))                        # Get the speed from user input
        rotation = int(input('Enter rotation change (deg +/-):')) # Get the degrees to rotate from user input 
        try:
            AUX_MOTOR.set_dps(speed)                              # Set the speed for the motor
            AUX_MOTOR.set_limits(POWER_LIMIT, speed)
            AUX_MOTOR.set_position_relative(rotation)             # Rotate the desired amount of degrees
        except IOError as error:
            print(error)

except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
    BP.reset_all()
