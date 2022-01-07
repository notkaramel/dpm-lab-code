import math
from typing import List, Tuple, Union

# Converting Numbers, float/int division, string conversion, other math,
# color ratio formula, max filtering


def normalize_rgb_reading(red: int, green: int, blue: int) -> Tuple[int, int, int]:
    """
    Perform math operations to return the normalized color value of each color
    Using the ratio-based formula.

    >>> normalize_rgb_reading(6,3,11)
    (0.3, 0.15, 0.55)
    """
    nred, ngreen, nblue = red, green, blue

    # TODO: Change any code within this function!

    ### SOLUTION ###
    s = red + green + blue
    nred, ngreen, nblue = red/s, green/s, blue/s
    ### END SOLUTION ###

    return nred, ngreen, nblue


def outlier_filtering(samples: List[float], cutoff: float, replacement: float) -> List[float]:
    """
    Remove the maximum value outliers from a given list of samples
    Use the cutoff value as the highest value you will accept
    Use the replacement value as the value to switch out in place of the outlier

    >>> incoming = [1,4,8,23,7,100,2e4]
    >>> cutoff = 20
    >>> replacement = -1
    >>> outlier_filtering(incoming, cutoff, replacement)
    [1, 4, 8, -1, 7, -1, -1]


    Note: Length of incoming samples list, should match length of result list. 
    DO NOT ALTER INCOMING LIST
    """
    result = samples.copy()

    # TODO: Change any code within this function!

    ### SOLUTION ###
    result = [num if num <= cutoff else replacement for num in result]
    ### END SOLUTION ###

    return result


def mean_of_strings(arguments: List[str]) -> float:
    """
    Given a list of strings, where each string may be a integer or 
    a word, take the integers and calculate the mean.

    >>> samples = [ 'hello', '1','2', '.', 'Hello world!', '4', '3' ]
    >>> mean_of_strings(samples)
    2.5


    Expected output: (1 + 4 + 3 + 2) / 4 = 10 / 4 = 2.5

    [Hint: use math.isclose to check float equivalence]
    """
    result = 0
    counter = 0

    # TODO: Change any code within this function!

    ### SOLUTION ###
    result = list(map(int, filter(str.isnumeric, arguments)))
    result = sum(result) / len(result)
    ### END SOLUTION ###

    return result

# Typing in Python


def accepted_float_convert(value: Union[int, float, str, bool]) -> float:
    """
    Convert the given value to a specfic float value, for potentially more useful data/graphing purposes.

    float -> return the same value
    int   -> divide by 10
    str   -> try to convert, return -1 on failure
    bool  -> True = 1, False = 0
    any other type -> raise a ValueError (see example for details)

    >>> accepted_float_convert(1.1)
    1.1
    >>> accepted_float_convert(1)
    0.1
    >>> accepted_float_convert("hello")
    -1
    >>> accepted_float_convert("2.2")
    2.2
    >>> accepted_float_convert(True)
    1
    >>> accepted_float_convert(5 - 2j) # complex unacceptable
    Traceback (most recent call last):
    ...
    ValueError: Invalid value type

    Hint: Use isinstance(value, class).
    """

    ### SOLUTION ###
    if type(value) == float:
        return value
    elif type(value) == int:
        return value/10
    elif type(value) == str:
        try:
            return float(value)
        except ValueError:
            return -1
    elif type(value) == bool:
        return 1 if value else 0

    raise ValueError("Invalid value type")
    ### END SOLUTION ###

    return -1

# List operations, for loops



# Dictionary operations

# File operations

# Exceptions

# Start one class, simple methods, no special methods

# Simple Grader file and Assignment file


if __name__ == "__main__":
    import doctest
    doctest.testmod()
