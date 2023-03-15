"""
--The With Style--

This file demonstrates using the With Style (Python Context Manager).

It involves the code "with wait_ready_sensors():" to handle exiting the
code automatically for you.

Author: Ryan Au
"""


from utils.brick import wait_ready_sensors, EV3UltrasonicSensor, Motor, BP
import time

# Create robot objects
color = EV3UltrasonicSensor(1)
motor = Motor("A")


with wait_ready_sensors(): # Exits with KeyboardInterrupt
    # One-time Initial Actions
    motor.set_limits(dps=180)

    while True:
        # Main Thread Loop Actions
        print(color.get_value())
        time.sleep(1)

print("Done with program")
