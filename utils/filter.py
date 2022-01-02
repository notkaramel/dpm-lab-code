import math

def mean(ls: list):
    """Takes the mean or average of a list of numerical values"""
    return sum(ls) / len(ls)

def range_limit(value:float, lower:float, upper:float) -> float:
    """Prevents the value from going beyond the upper or lower values.
    
    Example:
    range_limit(40,30,50)->40 (within bounds)
    range_limit(60,30,50)->50 (upper limit)
    range_limit(20,30,50)->30 (lower limit)
    """
    return min(max(value, lower), upper)

def ZeroFilter(samples: list, zero_offsets: list):
    """Returns a list of the samples minus zero_offsets. Acts circularly on zero_offsets.

    Example:
    if samples = [1,2,3,4,5,6], zero_offsets = [1,2,3] then
    result => [1-1, 2-2, 3-3, 4-1, 5-2, 6-3]
    or [0,0,0,3,3,3]
    """
    z = len(zero_offsets)
    result = []
    for i in range(samples):
        result.append(samples[i] - zero_offsets[i % z])
    return result


def SumFilter(samples: list, N: int):
    """Returns the summed values found in the N-size slices of samples.

    Example:
    if samples = [1,2,3,4,5,6] and N = 2 then
    result => [3,3,7,7,11,11]
    """
    result = []
    for i in range(0, len(samples), N):
        m = sum(samples[i:i+N])
        n = len(samples[i:i+N])
        for j in range(n):
            result.append(m)
    return result


def MaximumFilter(samples: list, N: int):
    """Returns the maximum values found in the N-size slices of samples.

    Example:
    if samples = [1,2,3,4,5,6] and N = 2
    result => [2, 2, 4, 4, 6, 6]
    """
    result = []
    for i in range(0, len(samples), N):
        m = max(samples[i:i+N])
        n = len(samples[i:i+N])
        for j in range(n):
            result.append(m)
    return result


def MinimumFilter(samples: list, N: int):
    """Returns the minimum values found in the N-size slices of samples.

    Example:
    if samples = [1,2,3,4,5,6] and N=2
    result => [1, 1, 3, 3, 5, 5]
    """
    result = []
    for i in range(0, len(samples), N):
        m = min(samples[i:i+N])
        n = len(samples[i:i+N])
        for j in range(n):
            result.append(m)
    return result


def ModulusFilter(samples: list, mod: int):
    """Returns a copy of samples, with each value applied a modulus.

    Example:
    samples = [1,2,3,4,5,6] and mod=4
    result => [1,2,3,0,1,2]
    """
    return [val % mod for val in samples]




def MeanFilter(samples: list, N: int):
    "Return the mean of the N-size slices of samples"
    result = []
    for i in range(0, len(samples), N):
        ls = samples[i:i+N]
        m = mean(ls)
        n = len(samples[i:i+N])
        for j in range(n):
            result.append(m)
    return result


def IntegrationFilter(samples: list, delta_time=1):
    """Returns the trapezoidal integration of the samples, given a constant sample time interval.

    Example:
    samples = [0,1,2,3,4] and delta_time=1
    result => [0, 0.5, 2, 4.5, 8]
    (Equivalent of f(x)=x integrated to g(x)=x^2/2)

    delta_time can be a float or a list of floats (the list must be length N-1 as samples N)
    """
    if type(delta_time) == list:
        if not all([type(d) == float or type(d) == int for d in delta_time]):
            return None
        if len(delta_time) != len(samples)-1:
            return None
    elif type(delta_time) == int or type(delta_time) == float:
        m = float(delta_time)
        delta_time = [m for m in range(len(samples)-1)]
    else:
        return None

    N = len(samples)
    result = 0
    ls = [0]
    for i in range(N-1):
        j = i + 1
        result += (samples[i] + samples[j]) * delta_time[i] * 0.5
        ls.append(result)
    return ls


def RangeLimitFilter(samples: list, lower: float, upper: float):
    "Creates a copy of samples, with values limited by a lower and upper bound (inclusive)."
    return [range_limit(val, lower, upper) for val in samples]


def MaxLimitFilter(samples: list, cutoff: float):
    "Creates a copy of samples, making values match a cutoff if they are greater than it."
    return RangeLimitFilter(samples, -math.inf, cutoff)


def MinLimitFilter(samples: list, cutoff: float):
    "Creates a copy of samples, making values match a cutoff if they are lesser than it."
    return RangeLimitFilter(samples, cutoff, math.inf)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    ls = list(range(50))
    print(ls)
    print(IntegrationFilter(ls))
    print(MaximumFilter(ls, 3))
    print(MinimumFilter(ls, 3))
    print(MeanFilter(ls, 3))
    plt.plot(ls, ls)
    plt.plot(ls, MaximumFilter(ls, 3))
    plt.plot(ls, MinimumFilter(ls, 3))
    plt.plot(ls, MeanFilter(ls, 3))
    plt.plot(ls, MinLimitFilter(MaxLimitFilter(IntegrationFilter(ls), 70), 5))
    plt.plot(ls, RangeLimitFilter(IntegrationFilter(ls), 20, 50))
    plt.show()
