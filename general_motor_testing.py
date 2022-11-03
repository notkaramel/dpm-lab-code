from utils.brick import Motor
from utils import telemetry, remote
import time

motor = Motor("A")

def open_window():
    telemetry.start()
    telemetry.resize(500,500)

    telemetry.label("Motor Speed", 0, True)
    telemetry.label("Motor Position", 0, True)


try:
    server = remote.RemoteBrickServer("password")
    open_window()
    while True:
        if not telemetry.isopen():
            break
        telemetry.label("Motor Speed", motor.get_dps(), True)
        telemetry.label("Motor Position", motor.get_position(), True)
        telemetry.update()
        time.sleep(0.010)
except KeyboardInterrupt:
    pass
