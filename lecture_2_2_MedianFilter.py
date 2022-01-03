import math

def median(arr):
    N = len(arr) # length of array
    arr = sorted(arr)
    if N%2==1:
        return arr[ math.ceil(N/2) ]
    else:
        return (arr[N//2] + arr[N//2 + 1]) / 2

def median_filter(samples, width):
    N = len(samples)
    
    result = []
    for i in range(0, N, width):
        m = median(samples[i:i+width])
        for j in range(min(width, N-i)):
            result.append(m)
    
    return result
        