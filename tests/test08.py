from utils.brick import Motor, TouchSensor, wait_ready_sensors, busy_sleep
from utils.sound import Sound
import simpleaudio
import time
import threading
import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file("thesong.wav")

sounds = [
    Sound(volume=100, pitch='C4'),
    Sound(volume=100, pitch='B4'),
    Sound(volume=100, pitch='D4'),
    Sound(volume=100, pitch='E4')
    ]

motor = Motor('A')
motor.set_limits(dps=180) # 90 deg / sec max limit = goal

touches = [
    TouchSensor(1),
    TouchSensor(2),
    TouchSensor(3),
    TouchSensor(4)
]

drumming = False

wait_ready_sensors(True)

def drum_function():
    while True:
        if drumming:
            motor.set_position_relative(-90)
            busy_sleep(0.5)
            motor.set_position_relative(90)
            busy_sleep(0.5)
        else:
            motor.set_position_relative(0)
            busy_sleep(0.01)


drum_thread = threading.Thread(target=drum_function, daemon=True)
drum_thread.start()

try:
    while True:
        if touches[3].is_pressed(): # Emergency Stop
            exit()

        if touches[0].is_pressed() or touches[1].is_pressed() or touches[2].is_pressed():
            busy_sleep(0.25)
            if touches[0].is_pressed() and touches[1].is_pressed() and touches[2].is_pressed():
                drumming = not drumming
                busy_sleep(0.5)
            elif touches[0].is_pressed() and touches[1].is_pressed():
                play_obj = wave_obj.play()
                play_obj.wait_done()
            elif touches[0].is_pressed():
                sounds[0].play().wait_done()
            elif touches[1].is_pressed():
                sounds[1].play().wait_done()
            elif touches[2].is_pressed():
                sounds[2].play().wait_done()

        busy_sleep(0.2)

except KeyboardInterrupt:
    exit()