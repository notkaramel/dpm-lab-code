from utils import sound
import threading
import time

VOLUME = 40
duration1 = 0.4
SOUND1 = [
    sound.Sound(duration=duration1, pitch="A4", volume=VOLUME),
    sound.Sound(duration=duration1, pitch="B4", volume=VOLUME),
    sound.Sound(duration=duration1, pitch="C5", volume=VOLUME),
    sound.Sound(duration=duration1, pitch="D5", volume=VOLUME),
    ]

duration2 = 1.6
SOUND2 = [
    sound.Sound(duration=duration2, pitch="A4", volume=VOLUME),
    sound.Sound(duration=duration2, pitch="B4", volume=VOLUME),
    sound.Sound(duration=duration2, pitch="C5", volume=VOLUME),
    sound.Sound(duration=duration2, pitch="D5", volume=VOLUME),
    ]

def play_sound1():
    i = 0
    n = len(SOUND1)
    try:
        while True:
            SOUND1[i].play()
            SOUND1[i].wait_done()
            i = (i+1) % n
    except KeyboardInterrupt:
        return

def play_sound2():
    i = 0
    n = len(SOUND2)
    try:
        while True:
            SOUND2[i].play()
            SOUND2[i].wait_done()
            i = (i+1) % n
    except KeyboardInterrupt:
        return

if __name__=='__main__':
    t1 = threading.Thread(target=play_sound1, daemon=True)
    t2 = threading.Thread(target=play_sound2, daemon=True)

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass