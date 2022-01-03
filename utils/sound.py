#!/usr/bin/env python3
# Written by Ryan Au and Younes Boubekaur

from typing import Iterable, SupportsIndex, Tuple, overload
from time import time
from typing import Tuple
import simpleaudio as sa
import math
import functools
import array

@functools.lru_cache()
def sin(x):
    return math.sin(x)

# @functools.lru_cache()
def cos(x):
    return math.cos(x)

def _parse_freq(value):
    if type(value) == str:
        if value in NOTES:
            return NOTES[value]
    if type(value) == int or type(value) == float:
        return float(value)
    return 0

def gen_wave(duration=1, volume=0.2, pitch="A4", mod_f=0, mod_k=0, amp_f=0, amp_ka=0, amp_ac=1, cutoff=0.01, fs=8000):
    # Process frequencies, factors
    pitch = _parse_freq(pitch)
    mod_f = _parse_freq(mod_f)
    amp_f = _parse_freq(amp_f)
    
    return _gen_wave(duration, volume, pitch, mod_f, mod_k, amp_f, amp_ka, amp_ac, cutoff, fs )

def _gen_wave(duration, volume, pitch, mod_f, mod_k, amp_f, amp_ka, amp_ac, cutoff, fs ):
    n = int(duration * fs)
    t = [ 0 for i in range(n)] # comprehension faster than append
    maximum =  -2**31
    for i in range(0,n):
        x = i / fs
        # create carrier wave (float division is faster)
        c = (2 * math.pi * x * pitch)
        # frequncy modulate
        m = mod_k * sin(2 * math.pi * mod_f * x)
        y = cos(c + m)
        # amplitude modulate
        a = amp_ac * (1 + (amp_ka * sin(2 * math.pi * amp_f * x)))
        y = y * a
        if maximum < (_abs := abs(y)):
            maximum = _abs
        # no append (which is marginally slow)
        t[i] = y

    # do volume and cutoff calculation
    max16 = (2**15 - 1)
    cutoff = min(int(n/2), int(fs * cutoff))
    k = (1/3) * (1/math.log(2))
    for i in range(len(t)):
        # apply volume
        y = t[i] * volume

        # # apply cutoff
        if  0 <= i and i < cutoff:
            y *= math.log(i / cutoff * 7 + 1) * k
        elif n - cutoff <= i and i < n:
            j = n - i - 1
            y *= math.log(j / cutoff * 7 + 1) * k

        # pull down value to int16
        t[i] = int(y * max16 / maximum)

    # convert to array.array('h')

    return array.array('h', t)

class Sound:
    def __init__(self, duration=1, volume=0.2, pitch="A4", mod_f=0, mod_k=0, amp_f=0, amp_ka=0, amp_ac=1, cutoff=0.01, fs=8000):
        self.player = None
        self.fs = fs # needs a default value
        self.set_volume(volume)
        self.set_pitch(pitch)
        self.set_cutoff(cutoff)
        self.set_frequency_modulation(mod_f, mod_k)
        self.set_amplitude_modulation(amp_f, amp_ka, amp_ac)
        self.update_duration(duration, fs)

    def set_volume(self, volume):
        self.volume = volume
    def set_pitch(self, pitch):
        self.pitch = pitch
    def set_cutoff(self, cutoff):
        self.cutoff = cutoff
    def set_frequency_modulation(self, mod_f, mod_k):
        self.mod_f = mod_f
        self.mod_k = mod_k
    def set_amplitude_modulation(self, amp_f, amp_ka, amp_ac):
        self.amp_f = amp_f
        self.amp_ka = amp_ka
        self.amp_ac = amp_ac
    def update_duration(self, duration, fs=None):
        if fs is not None:
            self.fs = fs
        self.duration = duration

        if not self.is_playing():
            self.update_audio(True)
        else:
            raise RuntimeError("Cannot change duration or sample rate while playing sound.")
    def update_audio(self, overwrite=False):
        arr = gen_wave(self.duration, self.volume, self.pitch, self.mod_f, self.mod_k, self.amp_f, self.amp_ka, self.amp_ac, self.cutoff, self.fs)
        if not overwrite:
            for i in range(len(arr)):
                self.audio[i] = arr[i]
        else:
            self.audio = arr
    def alter_wave(self, func):
        for i in range(len(self.audio)):
            self.audio[i] = func(i/fs, self.audio[i]) # func(x:float, y:int16) -> y:int16
    def play(self):
        self.stop()
        self.player = sa.play_buffer(self.audio, 1, 2, self.fs)
    def stop(self):
        if self.is_playing():
            self.player.stop()
    def is_playing(self):
        return self.player is not None and self.player.is_playing()
    def wait_done(self):
        if self.is_playing():
            self.player.wait_done()
NOTES = {
    "C0": 16.35,
    "D0": 18.35,
    "E0": 20.60,
    "F0": 21.83,
    "G0": 24.50,
    "A0": 27.50,
    "B0": 30.87,
    "C1": 32.70,
    "D1": 36.71,
    "E1": 41.20,
    "F1": 43.65,
    "G1": 49.00,
    "A1": 55.00,
    "B1": 61.74,
    "C2": 65.41,
    "D2": 73.42,
    "E2": 82.41,
    "F2": 87.31,
    "G2": 98.00,
    "A2": 110.00,
    "B2": 123.47,
    "C3": 130.81,
    "D3": 146.83,
    "E3": 164.81,
    "F3": 174.61,
    "G3": 196.00,
    "A3": 220.00,
    "B3": 246.94,
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
    "F5": 698.46,
    "G5": 783.99,
    "A5": 880.00,
    "B5": 987.77,
    "C6": 1046.50,
    "D6": 1174.66,
    "E6": 1318.51,
    "F6": 1396.91,
    "G6": 1567.98,
    "A6": 1760.00,
    "B6": 1975.53,
    "C7": 2093.00,
    "D7": 2349.32,
    "E7": 2637.02,
    "F7": 2793.83,
    "G7": 3135.96,
    "A7": 3520.00,
    "B7": 3951.07,
    "C8": 4186.01,
    "D8": 4698.63,
    "E8": 5274.04,
    "F8": 5587.65,
    "G8": 6271.93,
    "A8": 7040.00,
    "B8": 7902.13,
    "C#0": 17.32,
    "Db0": 17.32,
    "D#0": 19.45,
    "Eb0": 19.45,
    "F#0": 23.12,
    "Gb0": 23.12,
    "G#0": 25.96,
    "Ab0": 25.96,
    "A#0": 29.14,
    "Bb0": 29.14,
    "C#1": 34.65,
    "Db1": 34.65,
    "D#1": 38.89,
    "Eb1": 38.89,
    "F#1": 46.25,
    "Gb1": 46.25,
    "G#1": 51.91,
    "Ab1": 51.91,
    "A#1": 58.27,
    "Bb1": 58.27,
    "C#2": 69.30,
    "Db2": 69.30,
    "D#2": 77.78,
    "Eb2": 77.78,
    "F#2": 92.50,
    "Gb2": 92.50,
    "G#2": 103.83,
    "Ab2": 103.83,
    "A#2": 116.54,
    "Bb2": 116.54,
    "C#3": 138.59,
    "Db3": 138.59,
    "D#3": 155.56,
    "Eb3": 155.56,
    "F#3": 185.00,
    "Gb3": 185.00,
    "G#3": 207.65,
    "Ab3": 207.65,
    "A#3": 233.08,
    "Bb3": 233.08,
    "C#4": 277.18,
    "Db4": 277.18,
    "D#4": 311.13,
    "Eb4": 311.13,
    "F#4": 369.99,
    "Gb4": 369.99,
    "G#4": 415.30,
    "Ab4": 415.30,
    "A#4": 466.16,
    "Bb4": 466.16,
    "C#5": 554.37,
    "Db5": 554.37,
    "D#5": 622.25,
    "Eb5": 622.25,
    "F#5": 739.99,
    "Gb5": 739.99,
    "G#5": 830.61,
    "Ab5": 830.61,
    "A#5": 932.33,
    "Bb5": 932.33,
    "C#6": 1108.73,
    "Db6": 1108.73,
    "D#6": 1244.51,
    "Eb6": 1244.51,
    "F#6": 1479.98,
    "Gb6": 1479.98,
    "G#6": 1661.22,
    "Ab6": 1661.22,
    "A#6": 1864.66,
    "Bb6": 1864.66,
    "C#7": 2217.46,
    "Db7": 2217.46,
    "D#7": 2489.02,
    "Eb7": 2489.02,
    "F#7": 2959.96,
    "Gb7": 2959.96,
    "G#7": 3322.44,
    "Ab7": 3322.44,
    "A#7": 3729.31,
    "Bb7": 3729.31,
    "C#8": 4434.92,
    "Db8": 4434.92,
    "D#8": 4978.03,
    "Eb8": 4978.03,
    "F#8": 5919.91,
    "Gb8": 5919.91,
    "G#8": 6644.88,
    "Ab8": 6644.88,
    "A#8": 7458.62,
    "Bb8": 7458.62,
}

_note_order = {
    'b': 'x', '': 'y', '#': 'z',
    'C': '0', 'D': '1', 'E': '2', 'F': '3', 'G': '4', 'A': '5', 'B': '6', }

NOTE_NAMES = sorted(list(NOTES.keys()), key=lambda x: x[-1] + _note_order[x[0]] + _note_order[x[1:-1]])

# NOTE_SOUNDS = {key:gen_wave(pitch=key) for key in NOTE_NAMES}

SAMPLE_RATES = [
    8000,
    11025,
    16000,
    22050,
    24000,
    32000,
    44100,
    48000,
    88200,
    96000,
    192000,
]

if __name__=='__main__':
    sec = .1
    fs = 8000
    x = [ i/fs for i in range(int(sec * fs))]
    y = gen_wave(pitch="A4", duration=sec, fs = fs, mod_f=110, mod_k=1, cutoff=0.2)
    print(len(y))
    s = Sound(duration=10)
    s1 = Sound(duration=10, pitch="G4")
    s.play()
    input(">> Press Enter to play next note(s)")
    s.set_pitch("B4")
    s.update_audio()
    s1.play()
    input(">> Press Enter to play next note(s)")
    s.alter_wave(lambda x,y : int(y*0.5))
    # s.update_audio()
    input(">> Press Enter to play next note(s)")
    for key in ["A4", "B4", "C5", "D5"]:
        y = gen_wave(volume=0.4, pitch=key, duration=sec, fs = fs, cutoff=0.03, amp_f=10, amp_ac=0.5, amp_ka=1)
        sa.play_buffer(y, 1, 2, fs).wait_done()