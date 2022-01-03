import time
from utils import brick
from utils.brick import BP, EV3UltrasonicSensor, Motor, TouchSensor, wait_ready_sensors

SAMPLING_INTERVAL = 0.2 # seconds?
DEFAULT_WALL_DIST = 0.2 # meters?
DEADBAND = 0.02
DEFAULT_SPEED = 150
DEFAULT_DELTA_SPEED = 100
US_OUTLIER = 200

LEFT_MOTOR = Motor("A")
RIGHT_MOTOR = Motor("D")
T_SENSOR = TouchSensor(1)
US_SENSOR = EV3UltrasonicSensor(2)

POWER_LIMIT = 80
SPEED_LIMIT = 720

# Initialization
wait_ready_sensors()
LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
LEFT_MOTOR.reset_encoder()
RIGHT_MOTOR.reset_encoder()

try:
    print('Wall Follower Demo')
    fwd_speed = DEFAULT_SPEED
    wall_dist = DEFAULT_WALL_DIST
    delta_speed = DEFAULT_DELTA_SPEED
    
    resp = input('Enter speed (default:{0.2f})'.format(fwd_speed))
    if resp.isnumeric():
        fwd_speed = int(resp)
    
    resp = input('Enter wall distance (default:{0.2f})'.format(wall_dist))
    if resp.isnumeric():
        wall_dist = int(resp)

    resp = input('Enter delta speed (default:{0.2f})'.format(delta_speed))
    if resp.isnumeric():
        delta_speed = int(resp)
    
    print('Starting wall follower!')

    LEFT_MOTOR.set_dps(fwd_speed)
    RIGHT_MOTOR.set_dps(fwd_speed)
    last = wall_dist

    while True:
        if T_SENSOR.is_pressed():
            print("Contact - wall follower terminated.")
            BP.reset_all()
            break

        dist = US_SENSOR.get_cm()
        if dist >= US_OUTLIER:
            dist = last
        dist = dist / 100.0
        error = wall_dist - dist
        print('dist: {:0.2f}'.format(dist))
        print('error: {:0.2f}'.format(error))

        if abs(error) <= DEADBAND:
            LEFT_MOTOR.set_dps(fwd_speed)
            RIGHT_MOTOR.set_dps(fwd_speed)
            print('reaction: no correction')
        elif error < 0:
            LEFT_MOTOR.set_dps(fwd_speed)
            RIGHT_MOTOR.set_dps(fwd_speed+delta_speed)
            print('reaction: move closer to wall')
        else:
            LEFT_MOTOR.set_dps(fwd_speed+delta_speed)
            RIGHT_MOTOR.set_dps(fwd_speed)
            print('reaction: move away from wall')

        time.sleep(SAMPLING_INTERVAL)
        
except KeyboardInterrupt:
    BP.reset_all()