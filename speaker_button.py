#!/usr/bin/env python3
 
from utils import sound
from utils.brick import TouchSensor, configure_ports


TOUCH_SENSOR = configure_ports(PORT_1=TouchSensor)


def play_sound():
    "Play a single note."
    sound.play_note(note_name='A4', seconds=1, vol_factor=0.4)


def play_sound_on_button_press():
    "In an infinite loop, play a single note when the touch sensor is pressed."
    try:
        while True:
            touch_data = TOUCH_SENSOR.get_value()
            print(touch_data)
            if touch_data:
                play_sound()
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        exit()


if __name__=='__main__':
    play_sound()

    # TODO Implement this function
    play_sound_on_button_press()
