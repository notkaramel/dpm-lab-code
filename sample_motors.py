"""

--Motor Examples--

Demonstrates usage of the motors.

Every motor.set_*() function returns immediately, it does not "wait"
to complete. You can use time.sleep(seconds) or input("msg") to wait
until the motor finishes its movement.

Author: Ryan Au
January 24th, 2022
"""

###########################
### Power-based Control ###
###########################

from utils.brick import Motor

motor_left = Motor("A")


motor_left.set_dps(180) # Motor starts to rotate 180 deg/sec constantly without stopping
print("motor_left.set_dps(180)")
input("# Press any key to continue...")

motor_left.set_power(50) # Set power to 50% of maximum voltage input, constant rotation starts
print("motor_left.set_power(50)")
input("# Press any key to continue...")

# limits are used for position movement, not power movement
motor_left.set_limits(power=20)

motor_left.set_power(70) # increase to 70% instead of 20%
print("motor_left.set_power(70)")
input("# Press any key to continue...")

motor_left.set_power(0) # always do 0% to stop motor
print("motor_left.set_power(0)")
input("# Press any key to continue...")

# float_motor lets it move freely. 0% power resists movement.
motor_left.float_motor()
print("motor_left.float_motor()")
input("# Press any key to continue...")

##############################
### Position-based Control ###
##############################

from utils.brick import Motor
import time

motor_left = Motor("A")

# Set target speed first, 360 deg/sec
# Reset power limit to limitless with 0, default values:(power=0, dps=0)
motor_left.set_limits(dps=360)

# set current position to absolute pos 0deg
motor_left.reset_encoder()

# command to move to absolute pos 270deg
motor_left.set_position(270)
print("motor_left.set_position(270)")
input("# Press any key to continue...")

# command to rotate 90deg away from current position
motor_left.set_position_relative(90)
print("motor_left.set_position_relative(90)")
input("Press any key to continue...")

"""Tests 3 different speeds. set_dps overrides set_limits.
dps=180, rotation_dist=720
dps=360, rotation_dist=1080
dps=540, rotation_dist=1440
"""
for i, speed in enumerate([180, 360, 180*3]):
    motor_left.set_position_relative(360 * (i+2))
    motor_left.wait_is_moving()
    while motor_left.is_moving():
        time.sleep(0.1)
        print("actual speed=", motor_left.get_dps(), "actual power=", motor_left.get_power(), "status=", motor_left.get_status())
