import math
from math import pi, sin

# almost like:
import math
pi = math.pi
sin = math.sin

print("> python3 example1.py")
print("Hello World.")

hypotenuse_of_triangle = 2 / sin(pi * 2/3)
print("using sin", hypotenuse_of_triangle)
print("using cos:", math.cos(math.radians(60)))


def action():
    print("hi i'm a function")


action()

if __name__ == "__main__":
    action()

