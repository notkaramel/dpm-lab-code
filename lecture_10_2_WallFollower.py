#!/usr/bin/python3
"""DPM Hands on Example 5 (Lecture 10) - WallFollower

A striaghtforward implementation of the Wall Follower described in the slides for Lecture 12.
The program prompts the user to override default values of wall distance, forward speed,
and delta speed and then proceedsd to execute the BangBang controller. Program runs until interrupted
with ^C.

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

import time
from utils import brick
from utils.brick import BP, EV3UltrasonicSensor, Motor, TouchSensor, wait_ready_sensors

SAMPLING_INTERVAL = 0.2    # Sampling Interval 200ms or 5Hz
DEFAULT_WALL_DIST = 0.15    # Default distance from wall = 15cm
DEADBAND = 0.02            # Deadband is 2cm
DEFAULT_SPEED = 150        # Default speed = 150dps
DEFAULT_DELTA_SPEED = 100   # Default delta change in speed = 100dps
US_OUTLIER = 200           # Ignore ultrasonic readings > 200

POWER_LIMIT = 80           # Motor Power limit = 80%
SPEED_LIMIT = 720          # Motor Speed limit = 720dps

LEFT_MOTOR = Motor("A")             # Left motor on Port A
RIGHT_MOTOR = Motor("D")            # Right motor on Port D
T_SENSOR = TouchSensor(1)           # Touch sensor on Port S1
US_SENSOR = EV3UltrasonicSensor(2)  # Ultrasonic on Port S2


# Initialization

try:
    print('Wall Follower Demo')
    wait_ready_sensors()                             # Wait for sensor initialization
    # Set motor power and speed limits
    LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
    RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
    # Reset motor encoders to 0 value
    LEFT_MOTOR.reset_encoder()
    RIGHT_MOTOR.reset_encoder()

    """Allow user to override default parameters, of speed, wall distance, and delta speed"""

    fwd_speed = DEFAULT_SPEED
    wall_dist = DEFAULT_WALL_DIST
    delta_speed = DEFAULT_DELTA_SPEED

    resp = input('Enter speed (default:{:0.2f})'.format(fwd_speed))
    if resp.isnumeric():
        fwd_speed = int(resp)

    resp = input('Enter wall distance (default:{:0.2f})'.format(wall_dist))
    if resp.isnumeric():
        wall_dist = int(resp)

    resp = input('Enter delta speed (default:{:0.2f})'.format(delta_speed))
    if resp.isnumeric():
        delta_speed = int(resp)

    print('Starting wall follower!')

    LEFT_MOTOR.set_dps(fwd_speed)  # Set the motor speeds to start them
    RIGHT_MOTOR.set_dps(fwd_speed)

    while True:

        # End if the wall follower bumps the wall
        if T_SENSOR.is_pressed():
            print("Contact - wall follower terminated.")
            BP.reset_all()
            exit()

        dist = US_SENSOR.get_cm()  # Get distance reading from wall
        if dist >= US_OUTLIER:    # If error or too far, no error correction
            dist = wall_dist
        dist = dist / 100.0       # Convert to meters
        error = wall_dist - dist  # Get error difference
        print('dist: {:0.2f}'.format(dist))
        print('error: {:0.2f}'.format(error))

        # Error within Deadband: wheels rotate same speed, go forward
        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(fwd_speed)
            RIGHT_MOTOR.set_dps(fwd_speed)
            print('reaction: no correction')

        # Error negative (and outside deadband): move closer to wall
        elif error < 0:
            LEFT_MOTOR.set_dps(fwd_speed)
            RIGHT_MOTOR.set_dps(fwd_speed+delta_speed)
            print('reaction: move closer to wall')

        # Error positive (and outside deadband): move away from wall
        else:
            LEFT_MOTOR.set_dps(fwd_speed+delta_speed)
            RIGHT_MOTOR.set_dps(fwd_speed)
            print('reaction: move away from wall')

        time.sleep(SAMPLING_INTERVAL) # Sleep for sampling interval

except (KeyboardInterrupt, OSError): # Program exit on ^C (Ctrl + C)
    BP.reset_all()
