import time, math
from utils import brick
from utils.brick import BP, Motor

MOTOR_POLL_DELAY = 0.05

SQUARE_LENGTH = 0.5 # meters
WHEEL_RADIUS = 0.028 # meters
AXEL_LENGTH = 0.09 # meters

DIST_TO_DEG = 180/(math.pi*WHEEL_RADIUS) # degrees / meter
ORIENT_TO_DEG = AXEL_LENGTH / WHEEL_RADIUS

FWD_SPEED = 180 # deg per sec
TRN_SPEED = 90  # dps

LEFT_MOTOR = Motor("A")
RIGHT_MOTOR = Motor("D")
POWER_LIMIT = 80
SPEED_LIMIT = 720

def wait_for_motor(motor: Motor):
    while motor.get_speed() == 0:
        time.sleep(MOTOR_POLL_DELAY)
    while motor.get_speed() != 0:
        time.sleep(MOTOR_POLL_DELAY)

def init_motor(motor:Motor):
    try:
        motor.reset_encoder()
        motor.set_limits(POWER_LIMIT, SPEED_LIMIT)
        motor.set_power(0)
    except IOError as error:
        print(error)

def move_dist(distance, speed): # meters, dps
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)

def rotate_bot(angle, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG))
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG))
        
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)

def do_square(side_length):
    for i in range(4):
        move_dist(side_length, FWD_SPEED)
        rotate_bot(90, TRN_SPEED)
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)

try:
    print('Square Driving Demo')
    init_motor(LEFT_MOTOR)
    init_motor(RIGHT_MOTOR)
    while True:
        side_length = SQUARE_LENGTH
        resp = input('Override default side length 0.5m? y/n')
        if resp.lower() == 'y':
            side_length = int(input('Enter square side length (m): '))
        print('Starting sqaure driver with side length = {:0.2f}m'.format(side_length))
        do_square(side_length)

except KeyboardInterrupt:
    BP.reset_all()

