from utils.brick import BP, Motor, TouchSensor, EV3ColorSensor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 30
SENSOR_POLL_SLEEP = 0.05

T_SENSOR = TouchSensor(1)
C_SENSOR = EV3ColorSensor(2)

LEFT_MOTOR = Motor("A")
RIGHT_MOTOR = Motor("D")

try:
    f = open("colorSensor.txt", "w+")
    f.write("Data logged from color sensor.\n")

    wait_ready_sensors()  # Initialize sensors

    LEFT_MOTOR.set_power(FORWARD_SPEED)
    RIGHT_MOTOR.set_power(FORWARD_SPEED)

    while True:
        try:
            if T_SENSOR.is_pressed():
                BP.reset_all()
            red, gre, blu, lum = C_SENSOR.get_value()
            f.write('R={:d},G={:d},B={:d},L={:d}\n'.format(red, gre, blu, lum))
            time.sleep(SENSOR_POLL_SLEEP)
        except SensorError as error:
            print(error)

except KeyboardInterrupt:
    f.close()
    BP.reset_all()
