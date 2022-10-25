from utils import brick, dummy
import time

try:
    import spidev
except (ModuleNotFoundError, OSError, TypeError):
    brick.BP = dummy.BrickPi3()

ultra1 = brick.EV3UltrasonicSensor(1)
ultra2 = brick.EV3UltrasonicSensor(2)
touch1 = brick.TouchSensor(3)
color1 = brick.EV3ColorSensor(4)

motor1 = brick.Motor("A")
motor2 = brick.Motor("A")
motor3 = brick.Motor("C")

brick.wait_ready_sensors(True)

try:
    while True:
        print(ultra1.get_value(), motor1.get_position())
        time.sleep(0.1)
except:
    pass