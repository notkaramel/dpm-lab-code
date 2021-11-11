from threading import Thread
from time import time, sleep
from utils.brick import EV3ColorSensor, EV3UltrasonicSensor, Sensor, Motor


SHARED_DATA = {'us': None, 'color': None}
COLOR_SENSOR = EV3ColorSensor(1) # Port S1
US_SENSOR = EV3UltrasonicSensor(2) # Port S2
MOTOR = Motor("A") # Motor in Port MA

print("waiting for sensors")
COLOR_SENSOR.wait_ready()
US_SENSOR.wait_ready()
print("sensors ready")

def read_ultrasonic(shared):
    try:
        while True:
            shared['us'] = US_SENSOR.get_value()
            sleep(0.2)
    except Exception:
        return

def read_color(shared):
    try:
        while True:
            rgb = COLOR_SENSOR.get_value()
            if rgb is not None and len(rgb) >= 3:
                shared['color'] = rgb[0]
            sleep(0.2)
    except Exception:
        return

def main():
    print("starting sensor readings")
    t1 = Thread(target=read_ultrasonic, args=[SHARED_DATA])
    t2 = Thread(target=read_color, args=[SHARED_DATA])
    t1.start() # will update SHARED_DATA['us'] in the background
    t2.start() # will update SHARED_DATA['color'] in the background

    motor_power = 0 # power value 0.0 to 1.0
    while True:

        # always sets motor_power to either 0.5 or 0
        if SHARED_DATA['us'] is not None and SHARED_DATA['us'] < 5:
            motor_power = 50
        else:
            motor_power = 0

        # either leaves the motor_power to normal direction, or switches it to negative
        if SHARED_DATA['color'] is not None and SHARED_DATA['color'] > 100:
            motor_power = -motor_power

        # Motors keep the power that they were last given
        # In this case, we always set power of motor to the newest
        # motor_power value
        MOTOR.set_power(motor_power)
        print("Data:", motor_power, SHARED_DATA)
        sleep(0.2)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass # catch all
