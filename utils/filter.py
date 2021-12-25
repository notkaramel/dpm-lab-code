import math

def MaximumFilter(samples:list[float], N:int):
    "Returns the maximum values found in the N-size slices of samples."
    for i in range(N):
        yield max(samples[i:i+N])

def MinimumFilter(samples:list[float], N:int):
    "Returns the maximum values found in the N-size slices of samples."
    for i in range(N):
        yield min(samples[i:i+N])

def MeanFilter(samples: list[float], N:int):
    "Return the mean of the N-size slices of samples"
    for i in range(N):
        yield sum(samples[i:i+N]) / N

def LowPassFilter(samples: list[float], cutoff:float):
    pass