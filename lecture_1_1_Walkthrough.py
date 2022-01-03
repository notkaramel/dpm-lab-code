from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 30  # 30% power
SENSOR_POLL_SLEEP = 0.05

T_SENSOR = TouchSensor(1)
LEFT_MOTOR = Motor("A")
RIGHT_MOTOR = Motor("D")

try:
    wait_ready_sensors()  # Initialize sensors
    LEFT_MOTOR.set_power(30)
    RIGHT_MOTOR.set_power(30)

    while True:
        try:
            if T_SENSOR.is_pressed():
                BP.reset_all()
                exit()
            time.sleep(SENSOR_POLL_SLEEP)
        except SensorError as error:
            print(error)

except KeyboardInterrupt:
    BP.reset_all()
