"""
--Telemetry Window with Threads--
Telemetry can have issues/bugs when using telemtry.update() so instead,
we use telemetry.mainloop() at the end. Mainloop uses its own while True 
loop, meaning we need to use 'threads' do any other actions during the 
program execution.

telemetry.mainloop will be run without threads:

1. Open telemtry window
2. (optional) Resize if desired
3. Start any primary/control threads, such as 'main()' [Use daemon=True]
4. Run telemetry.mainloop()

Author: Ryan Au
"""


from utils import telemetry
from threading import Thread
import os
import time


def main():
    """
    A main method which has a while True loop 
    and does the main things we want it to.
    """
    try:
        i = 1
        while True:
            telemetry.add('text', '.'*i)
            print(i, ".")
            time.sleep(1)
            i += 1
    except KeyboardInterrupt:
        os._exit(0)


if __name__ == '__main__':
    telemetry.start()  # open and create telemetry window
    telemetry.resize(200, 100)

    t = Thread(target=main, daemon=True)
    t.start()

    telemetry.mainloop()
