import math

var = True     # boolean
var = 0        # int
var = 0x50     # int (hex form)
var = 0.22     # float
var = 0.1 + 5j  # complex number
var = "hello"  # string
var = 'world'  # string

# type checking
print( type(var) == str ) # prints True
print( isinstance(var, str)) # prints True

# multiple assignment
a, b, c = 1, 2, 3
print(f"multiple assignment a:{a}, b:{b}, c:{c}")

# variable swapping
a, b = b, a
print(f"variable swapping a:{a}, b:{b}")

print("float division", 10 / 4)    # 2.5
print("integer division", 10 // 4)  # 2

word = "56"
type(word) # type is 'str'
number = int(word)
type(number)
print(number + 4)

a, b, c = 1, 2, 1
if a == b:
    print("a == b")
elif a == c:
    print("a == c")
else:
    print("I don't know")

if a == 10:
    if b == 11:
        if c == 12:
            print("well that's unlikely.")

# single line if statement
if a == 1: print("heyyy")

# ternary if statement
b = (5 if a == 1 else 6) + 1

i = 5
while i > 0:
    i -= 1
    print("...")

1_000_000_002.3 # 1 billion 2 and 3 tenths
0x90f           # hexadecimal integer
0b1101101       # binary integer
2.0             # float
1 + 5.9j        # complex number