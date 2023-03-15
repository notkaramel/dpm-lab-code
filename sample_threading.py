import threading
import time
from utils.brick import EV3ColorSensor, EV3UltrasonicSensor, Motor, wait_ready_sensors

# Preapre Motor and Sensors
COLOR_SENSOR = EV3ColorSensor(1)   # Port S1
US_SENSOR = EV3UltrasonicSensor(2)  # Port S2
MOTOR = Motor("A")                 # Motor in Port MA

# Wait for Sensor Initialization
wait_ready_sensors(True)

# Create a dictionary to store sensor data.
SHARED_DATA = {'us': None, 'color': None}


def read_ultrasonic():
    """Runs in background, polling the ultrasonic sensor"""
    global SHARED_DATA

    while True:
        SHARED_DATA['us'] = US_SENSOR.get_cm()
        time.sleep(0.01)


def read_color():
    """Runs in background, polling the color sensor"""
    global SHARED_DATA

    while True:
        SHARED_DATA['color'] = COLOR_SENSOR.get_rgb()
        time.sleep(0.01)


def main():
    """Your main() function is the Main Thread.
    t1 and t2 are Child Threads (daemon threads)

    When Main Thread finishes/exits, then Child Deamon Threads exit automatically also.
    """
    global SHARED_DATA

    print("starting sensor readings")
    t1 = threading.Thread(target=read_ultrasonic, daemon=True)
    t2 = threading.Thread(target=read_color,      daemon=True)
    t1.start()  # must start threads also
    t2.start()

    MOTOR.set_dps(0)  # Stops motor movement
    while True:
        # Always pull out a value from the dictionary first
        dist = SHARED_DATA['us']
        color = SHARED_DATA['color']

        speed = 0
        if dist is not None:
            speed = dist + 90

        if color[0] > 100:
            speed = -speed

        MOTOR.set_dps(speed)

        time.sleep(0.1)  # This time is different from the sensors' times


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
