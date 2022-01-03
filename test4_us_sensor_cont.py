from utils import sound, brick
import time
import contextlib

# Constants for remembering what you assigned.
BP = brick.BrickPi3()
TOUCH_SENSOR = brick.TouchSensor(BP, 1)
US_SENSOR = brick.EV3UltrasonicSensor(BP, 2)

print("Waiting for sensors to turn on...")
while US_SENSOR.get_status() != 'VALID_DATA':
    ...
print("Done waiting.")

def main():
    print("Program start.")
    try:
        output_file = open('test_data.csv', 'w')
        output_file.write('Ultrasonic Measurement (cm)\n')
        while True:
            touch_data = TOUCH_SENSOR.get_value() # Integer value 0 or 1
            us_data = US_SENSOR.get_value() # Float value in centimeters 0 to 255 limits
            
            if touch_data != 0:
                """Insert Code Querying the Ultrasonic sensor"""
                print(us_data)
                output_file.write(str(us_data) + '\n')

                sound.play_note(note_name='A4', seconds=0.3, vol_factor=0.4).wait_done()
            
    except KeyboardInterrupt: # Ctrl-C will stop the program
        BP.reset_all()
    finally:
        output_file.close()
        BP.reset_all()

if __name__=='__main__':
    main()