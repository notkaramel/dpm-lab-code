#!/usr/bin/python3
"""
A simple median filter (Python)

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

import math

def simple_median_filter(samples, width):
    """width must be an odd number"""
    N = len(samples)
    
    result = []
    for i in range(0, N-width):
        sv = sorted(samples[i:i+width])
        med_i = math.floor(width/2)
        result.append(sv[med_i])
    
    return result

print("Median Example", simple_median_filter([1,2,3,4,5,6,7,8,9,10,11], 5))

from utils import brick
import time
ultra = brick.EV3UltrasonicSensor(2)

result = []
try:
    while True:
        time.sleep(0.8)
        print(ultra.get_value())
        result.append(ultra.get_value())
except KeyboardInterrupt:
    pass

"""
A simple median filter (Python)

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

"""
from statistics import median

def median_filter(samples, width):
    N = len(samples)
    
    result = []
    for i in range(0, N-width):
        m = median(samples[i:i+width])
        result.append(m)
    
    return result

print(median_filter([1,2,3,4,5,6,7,8,9,10,11], 3))


"""