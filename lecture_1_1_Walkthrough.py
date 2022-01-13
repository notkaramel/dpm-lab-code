from utils.brick import BP, TouchSensor, Motor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 30          # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05    # Polling rate = 50 msec

T_SENSOR = TouchSensor(1)   # Touch Sensor in Port S1
LEFT_MOTOR = Motor("A")     # Left motor in Port A
RIGHT_MOTOR = Motor("D")    # Right motor in Port D

try:
    wait_ready_sensors()                  # Wait for sensors to initialize
    LEFT_MOTOR.set_power(FORWARD_SPEED)   # Start left motor
    RIGHT_MOTOR.set_power(FORWARD_SPEED)  # Simultaneously start right motor

    while True:
        try:
            if T_SENSOR.is_pressed():      # Press touch sensor to stop robot
                BP.reset_all()
            time.sleep(SENSOR_POLL_SLEEP)  # Use sensor polling interval here
        except SensorError as error:
            print(error)                   # On exception or error, print error code

except KeyboardInterrupt:                  # Allows program to be stopped on keyboard interrupt
    BP.reset_all()
