###########################
### Power-based Control ###
###########################

from utils.brick import Motor

motor_left = Motor("A")

motor_left.set_power(50)
input("Press any key to continue...")

motor_left.set_limits(power=20)
motor_left.set_power(70) # limited to 20% instead
input("Press any key to continue...")

motor_left.set_power(0) # always do 0% to stop motor
input("Press any key to continue...")

##############################
### Position-based Control ###
##############################

from utils.brick import Motor

motor_left = Motor("A")

# set target speed first, 40 deg/sec
motor_left.set_dps(40)

# set current position to absolute pos 0deg
motor_left.reset_encoder()

# command to move to absolute pos 270deg
motor_left.set_position(270)
input("Press any key to continue...")

# command to rotate 90deg away from current position
motor_left.set_position_relative(90)
input("Press any key to continue...")