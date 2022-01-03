from utils import sound
import brickpi3
import time
import contextlib

# Constants for remembering what you assigned.
BP = brickpi3.BrickPi3()
TOUCH_SENSOR = BP.PORT_1
US_SENSOR = BP.PORT_2

BP.set_sensor_type(TOUCH_SENSOR, BP.SENSOR_TYPE.TOUCH)
BP.set_sensor_type(US_SENSOR, BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)

print("Waiting for sensors to turn on...")
time.sleep(5)
print("Done waiting.")

def main():
    print("Program start.")
    try:
        output_file = open('test_data.csv', 'w')
        output_file.write('Ultrasonic Measurement (cm)\n')
        while True:
            try:
                touch_data = BP.get_sensor(TOUCH_SENSOR) # Integer value 0 or 1
                us_data = BP.get_sensor(US_SENSOR) # Float value in centimeters 0 to 255 limits

                if touch_data != 0:
                    """Insert Code Querying the Ultrasonic sensor"""
                    print(us_data)
                    output_file.write(str(us_data) + '\n')

                    sound.play_note(note_name='A4', seconds=0.3, vol_factor=0.4).wait_done()
            except brickpi3.SensorError as error:
                print(error)
    except KeyboardInterrupt: # Ctrl-C will stop the program
        BP.reset_all()
    finally:
        output_file.close()
        BP.reset_all()

if __name__=='__main__':
    main()