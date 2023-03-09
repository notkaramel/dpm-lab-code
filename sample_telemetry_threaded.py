"""
--Telemetry Window with Threads--
Telemetry can have issues/bugs when using telemtry.update() so instead,
we use telemetry.mainloop() at the end. Mainloop uses its own while True 
loop, meaning we need to use 'threads' do any other actions during the 
program execution.

1. Open telemetry window
2. (optional) Resize if desired
3. Start any primary/control threads, such as 'main()' [Use daemon=True]
4. Run telemetry.mainloop()

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