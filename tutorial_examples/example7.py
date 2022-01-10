"""Defining functions"""


"""Functions return None by default"""
def func1():
    x = 89

print(func1()) # prints None

"""Functions don't need a return type specified"""
def func2():
    return "words"

"""Functions can also return tuples using commas"""
def func3():
    return 8, 9, 10

print(func3()) # prints (8, 9, 10)
a, b, c = func3() # multi-assignment works too
print(b) # prints 9

"""y is a default value, overloading does not exist.
def func4(x=4, y): cannot work, because optional params
    must come after normal parameters
"""
def func4(x, y=4):
    return x + y

func4(8) # 12
func4(8,9) # 17

"""Type hinting doesn't give any warning or errors.
But it's useful for you to read, and IDEs to use.
"""
def func5_1(lst):
    return len(lst)

def func5_2(lst:list) -> int:
    return len(lst)


"""We can also import any functions present in other files/modules"""
from .library import ceil, action
print(action(5))
print(ceil(6/7))

