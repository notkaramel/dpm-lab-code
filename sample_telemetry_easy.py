"""
--Telemetry Window (Easy Version)--

Telemetry displays live up-to-date information, like a 'print()' statement.
Also allows input via sliders (integers) and buttons (true/false)

Author: Ryan Au
"""


from utils import telemetry
from threading import Thread
import os
import time

telemetry.start_threaded()  # open and create telemetry window
telemetry.resize(200, 100)
SLIDER = telemetry.create_slider(0, 100, 51)
BUTTON = telemetry.create_button("Ok")

def main():
    """
    A main method which has a while True loop 
    and does the main things we want it to.
    """
    try:
        i = 1
        while telemetry.isopen():
            telemetry.label('text', '.'*i)
            telemetry.label('slider', SLIDER.get_value(), showkey=True)

            print(i, "|", SLIDER.get_value(), BUTTON.is_pressed())
            time.sleep(1)
            i += 1
    except KeyboardInterrupt:
        exit(0)

if __name__ == '__main__':
    main()