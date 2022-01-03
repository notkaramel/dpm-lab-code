from utils.brick import BP, Motor, TouchSensor, EV3ColorSensor, wait_ready_sensors, SensorError
import time

FORWARD_SPEED = 30
SENSOR_POLL_SLEEP = 0.05

T_SENSOR = TouchSensor(1)
C_SENSOR = EV3ColorSensor(2)

LEFT_MOTOR = Motor("A")
RIGHT_MOTOR = Motor("D")

try:
    wait_ready_sensors()  # Initialize sensors
    
    f = open("colorSensor.csv", "w")
    f.write("Data logged from color sensor.\n")
    print("Data acquisition commencing.")

    LEFT_MOTOR.set_power(FORWARD_SPEED)
    RIGHT_MOTOR.set_power(FORWARD_SPEED)

    while True:
        try:
            if T_SENSOR.is_pressed():
                print("Data acquisition complete.")
                f.close()
                BP.reset_all()
            red, gre, blu, lum = C_SENSOR.get_value()
            f.write('{:d},{:d},{:d},{:d}\n'.format(red, gre, blu, lum))
            time.sleep(SENSOR_POLL_SLEEP)
        except SensorError as error:
            print(error)

except KeyboardInterrupt:
    print("Data acquisition interrupted.")
    f.close()
    BP.reset_all()
