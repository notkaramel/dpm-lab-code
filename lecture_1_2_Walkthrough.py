from utils.brick import BP, Motor, TouchSensor, EV3ColorSensor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 30           # speed constant = 30% power
SENSOR_POLL_SLEEP = 0.05     # Polling rate = 50 msec

T_SENSOR = TouchSensor(1)    # Touch Sensor in Port S1
C_SENSOR = EV3ColorSensor(2) # Color Sensor in Port S2

LEFT_MOTOR = Motor("A")      # Left motor in Port A
RIGHT_MOTOR = Motor("D")     # Right motor in Port D

try:
    f = open("colorSensor.txt", "w+")             # Open a file for writing
    f.write("Data logged from color sensor.\n")   # Print a header

    wait_ready_sensors()                  # Wait for sensors to initialize
    LEFT_MOTOR.set_power(FORWARD_SPEED)   # Start left motor
    RIGHT_MOTOR.set_power(FORWARD_SPEED)  # Simultaneously start right motor

    while True:
        try:
            if T_SENSOR.is_pressed():     # Press touch sensor to stop robot
                BP.reset_all()

            # Retrieve the color values the Color sensor
            red, gre, blu, lum = C_SENSOR.get_value()

            # Write color values to the file
            f.write('R={:d},G={:d},B={:d},L={:d}\n'.format(red, gre, blu, lum))
            
            time.sleep(SENSOR_POLL_SLEEP)  # Use sensor polling interval here
        except SensorError as error:
            print(error)                   # On exception or error, print error code

except KeyboardInterrupt:                  # Allows program to be stopped on keyboard interrupt
    f.close()
    BP.reset_all()
