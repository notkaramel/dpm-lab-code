import time

try:
    time.sleep(1)
except BaseException as error:
    print("something is wrong, i dont know")
    print(error)

from brickpi3 import SensorError
try:
    time.sleep(1)
except SensorError as error:
    print("Sensor messed up, probably off.")
    print(error)

try:
    time.sleep(1)
except KeyboardInterrupt as error:
    print("Guess you want to say goodbye...")
    print(":(")
    print(error)
    exit(0) # exit this thread execution

