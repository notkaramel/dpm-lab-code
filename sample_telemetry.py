from utils import telemetry
from time import sleep

"""First start and open the telemetry window:"""
telemetry.start()

"""Then you can resize it:"""
telemetry.resize(500, 200)  # pixels, width, height

"""Then add data to the display:"""
i = 0
while True:

    # if window close, leave loop. Optional.
    if not telemetry.isopen():
        break

    i = i + 1 if i < 30 else 0
    telemetry.add("counter", i, showboth=True)

    # telemetry.add(key, value, showboth=False)
    telemetry.add("something", "Hello Robots")

    # can change existing text, by using same key
    telemetry.add("replaceable", "Hello World!")
    telemetry.add("replaceable", "No no no no!")

    if i == 25:
        telemetry.clear()  # and you can clear all text!

    """MUST UPDATE TO SEE RESULTS!"""
    telemetry.update()
    sleep(0.25)

    # telemetry.stop()
