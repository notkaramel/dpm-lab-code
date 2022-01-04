"""
Module for providing access to a single, simple, GUI that can easily display data.

Author: Ryan Au
"""

from tkinter import ttk, StringVar, TclError

import tkinter as tk

WINDOW: tk.Tk = None
LABELS = {}
_EXIT_FLAG = True


def _on_closing():
    """Private method: cleans up internal values on window destruction"""
    global WINDOW, _EXIT_FLAG, LABELS
    _EXIT_FLAG = True
    WINDOW.destroy()
    WINDOW = None
    LABELS = {}


def start():
    """Open the telemetry window"""
    global WINDOW, _EXIT_FLAG
    _EXIT_FLAG = False
    if WINDOW is None:
        WINDOW = tk.Tk()
    WINDOW.protocol("WM_DELETE_WINDOW", _on_closing)
    update()


def isopen():
    """Determines if the telemtry window has been opened or closed"""
    return not _EXIT_FLAG


def resize(width, height):
    """Resize telemtry to a set width and height in pixels"""
    if WINDOW is None:
        return
    WINDOW.geometry("{}x{}".format(width, height))


def stop():
    """Closes window"""
    global WINDOW
    if WINDOW is not None:
        WINDOW.quit()
        WINDOW = None


def add(key, data, showkey=False):
    """Adds/Sets data by a key to the telemetry window"""
    if WINDOW is None:
        return
    key = str(key)
    data = str(data)
    if showkey:
        data = "{} : {}".format(key, data)
    if key in LABELS:
        LABELS[key][1].set(data)
    else:
        var = StringVar()
        var.set(data)
        LABELS[key] = (tk.Label(WINDOW, textvariable=var), var)
        LABELS[key][0].pack()


def update(retries=1):
    """Updates display with latest telemetry values"""
    global WINDOW
    if WINDOW is not None:
        try:
            for i in range(retries):
                WINDOW.update()
        except TclError as e:
            err = str(e)
            if err == 'can\'t invoke "update" command: application has been destroyed':
                WINDOW = None


def clear():
    """Destroy and remove all LABELS of telemetry"""
    global LABELS
    for i, widget in LABELS.items():
        try:
            widget[0].destroy()
        except TclError:
            pass
    LABELS = {}


def mainloop():
    if WINDOW is not None and isopen():
        WINDOW.mainloop()


if __name__ == '__main__':
    import time
    start()
    resize(500, 200)
    i = 0
    add("word", "heyo this is the start")
    update()
    while True:
        time.sleep(1)

        ### Test clearing window despite still updating ###
        if i == 10:
            clear()
            if not isopen():
                start()

        # Adding data
        add("color", "red", True)
        i = i + 2 if i < 40 else 0

        print(i, isopen())
        add("counter", "*"*i)

        # Must update window to see changes
        update()
