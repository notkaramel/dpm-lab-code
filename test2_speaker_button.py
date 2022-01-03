from utils import sound
import brickpi3

# Constants for remembering what you assigned.
BP = brickpi3.BrickPi3()
TOUCH_SENSOR = BP.PORT_1
BP.set_sensor_type(TOUCH_SENSOR, BP.SENSOR_TYPE.TOUCH)

def main():
    try:
        while True:
            try:
                touch_data = BP.get_sensor(TOUCH_SENSOR)
                print(touch_data)
                if touch_data != 0:
                    sound.play_note(note_name='A4', seconds=0.5, vol_factor=0.4).wait_done()
            except brickpi3.SensorError as error:
                print(error)
    except KeyboardInterrupt: # Ctrl-C will stop the program
        BP.reset_all()


if __name__=='__main__':
    main()