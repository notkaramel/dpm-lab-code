from tkinter import ttk, StringVar, TclError

import tkinter as tk

WINDOW = None
LABELS = {}
_EXIT_FLAG = True


def _on_closing():
    global WINDOW, _EXIT_FLAG, LABELS
    _EXIT_FLAG = True
    WINDOW.destroy()
    WINDOW = None
    LABELS = {}


def start():
    global WINDOW, _EXIT_FLAG
    _EXIT_FLAG = False
    if WINDOW is None:
        WINDOW = tk.Tk()
    WINDOW.protocol("WM_DELETE_WINDOW", _on_closing)
    update()


def isopen():
    return not _EXIT_FLAG


def resize(width, height):
    if WINDOW is None:
        return
    WINDOW.geometry("{}x{}".format(width, height))


def stop():
    global WINDOW
    if WINDOW is not None:
        WINDOW.quit()
        WINDOW = None


def add(key, data, showboth=False):
    if WINDOW is None:
        return
    key = str(key)
    data = str(data)
    if showboth:
        data = "{} : {}".format(key, data)
    if key in LABELS:
        LABELS[key][1].set(data)
    else:
        var = StringVar()
        LABELS[key] = (tk.Label(WINDOW, textvariable=var), var)
        LABELS[key][0].pack()


def update():
    global WINDOW
    if WINDOW is not None:
        try:
            WINDOW.update()
        except TclError as e:
            err = str(e)
            if err == 'can\'t invoke "update" command: application has been destroyed':
                WINDOW = None


def clear():
    global LABELS
    for i, widget in LABELS.items():
        widget[0].destroy()
    LABELS = {}


if __name__ == '__main__':
    import time
    start()
    resize(500, 200)
    i = 0
    while True:
        time.sleep(0.5)
        if i == 10:
            clear()
            if not isopen():
                start()

        add("color", "red")
        i = i + 2 if i < 40 else 0

        print(i, isopen())
        add("counter", "*"*i)
        update()
