from utils import telemetry, dummy
import threading, time

motor = dummy._FakeMotor()

telemetry.start()
telemetry.resize(500,500)

def execution():
    while True:
        try:
            print(eval(input('>>> ')))
            ...
            time.sleep(0.1)
        except Exception as e:
            print(e)

t = threading.Thread(target=execution, daemon=True)
t.start()

try:
    motor.start()
    while True:
        telemetry.label("position", motor.position, True)
        telemetry.label("speed", motor.speed, True)
        telemetry.label("position_goal", motor.position_goal, True)
        telemetry.label("power", motor.power, True)
        telemetry.label("speed_limit", motor.speed_limit, True)
        telemetry.label("power_limit", motor.power_limit, True)
        telemetry.update()
except:
    pass