#!/usr/bin/python3
"""DPM Hands On Example 4 (Lecture 10) - SquareDriver

A simple program that drives a two-wheeled robot along a square trajectory
with size specified by the suer. Program will execute prompt-drive loop
until hated with ^C.

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

from cmath import isclose
import time
import math
from utils import brick
from utils.brick import BP, Motor

MOTOR_POLL_DELAY = 0.05

SQUARE_LENGTH = 0.5     # (meters) Side length of square in
WHEEL_RADIUS = 0.028    # (meters) Radius of one wheel
AXLE_LENGTH = 0.11      # (meters) Distance between wheel contact with ground

DIST_TO_DEG = 180/(math.pi*WHEEL_RADIUS)   # (degrees / meter) Convert distance to wheel degrees
ORIENT_TO_DEG = AXLE_LENGTH / WHEEL_RADIUS # Convert whole robot rotation to wheel rotation

FWD_SPEED = 100  # (deg per sec) Moving forward speed
TRN_SPEED = 180   # (deg per sec) Turning a corner speed

LEFT_MOTOR = Motor("A")  # Left motor in Port A
RIGHT_MOTOR = Motor("D") # Right motor in Port D
POWER_LIMIT = 80         # Power limit = 80%
SPEED_LIMIT = 720        # Speed limit = 720dps


def wait_for_motor(motor: Motor):
    "Function to block until motor completion"
    while math.isclose(motor.get_speed(), 0):    # Wait for motor to spin up   (start)
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(), 0):    # Wait for motor to spin down (stop)
        time.sleep(MOTOR_POLL_DELAY)

def init_motor(motor: Motor):
    "Function to initialize a motor"
    try:
        motor.reset_encoder()                      # Reset encoder to 0 value
        motor.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set power and speed limits
        motor.set_power(0)                         # Stop the motor as well
    except IOError as error:
        print(error)


def move_dist_fwd(distance, speed):  # meters, dps
    "Function to move forward by user-specified distance and speed"
    try:
        # Set speed of motors
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))  # Rotate wheels
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))

        wait_for_motor(RIGHT_MOTOR)
        # sleep_for_motor(int(distance * DIST_TO_DEG), speed)
    except IOError as error:
        print(error)


def rotate_bot(angle, speed):
    "Function to rotate in place by a user specified angle and speed"
    try:
        # Set speeds of motors
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG))   # Rotate L Wheel +ve
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG)) # Rotate R Wheel -ve

        wait_for_motor(RIGHT_MOTOR)
        # sleep_for_motor(int(distance * DIST_TO_DEG), speed)
    except IOError as error:
        print(error)


def do_square(side_length):
    for i in range(4):
        move_dist_fwd(side_length, FWD_SPEED) # Do side of square
        rotate_bot(90, TRN_SPEED)             # Rotate 90 degrees
    LEFT_MOTOR.set_power(0)                   # Motors off, square done
    RIGHT_MOTOR.set_power(0)

if __name__=='__main__':
    try:
        print('Square Driving Demo') # Banner
        init_motor(LEFT_MOTOR)       # Initialize L Motor
        init_motor(RIGHT_MOTOR)      # Initialize R Motor

        # Prompt for drive loop
        while True:
            side_length = SQUARE_LENGTH # Assume default side length
            resp = input('Override default side length {:0.2f}m? y/n (q for quit): '.format(side_length))
            if resp.lower() == 'y':
                AXLE_LENGTH = float(input('Enter square side length (m): '))
            if resp.lower() == 'q':
                BP.reset_all()
                exit()
            print('Starting sqaure driver with side length = {:0.2f}m'.format(
                side_length))
            
            do_square(side_length) # Drive in a square shape, with designated side_length

    except KeyboardInterrupt: # Abort program using ^C (Ctrl+C)
        BP.reset_all()
