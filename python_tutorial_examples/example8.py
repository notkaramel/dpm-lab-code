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

try:
    f = open('testfile.txt', 'w')
    f.write(None)
    g = open('srcfile.txt','r')
except (IOError, FileNotFoundError) as error:
    print("File Error!")
finally:
    f.close() # on sucess(try) or fail(except), close file

