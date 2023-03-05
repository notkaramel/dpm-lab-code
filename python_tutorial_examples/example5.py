"Examples on dictionaries"

# Basic Dictionary creation
x = {}  # empty
d = {
    'a': 1,
    'b': 2,
    'c': None,
    'd': 'meh'
}
print(isinstance(d, dict))  # True

print('a' in d)  # 'in' checks keys, True
print('b' in d.keys())  # also check keys
print(2 in d.values())  # to check values
print(d['a'])  # prints 1
print(getattr(d, 'b', None))  # prints 2
print(getattr(d, 'z', None))  # prints None

# Normal for-loop loops the keys
for key in d:
    print(key, d[key])

# To loop through all keys and values
for key, value in d.items():
    print(key, ':', value)

# To loop through sorted keys
for key in sorted(d.keys()):
    print(key, d[key])

# To loop through sorted values
for value in sorted(d.values()):
    print(value)

# THIS IS NOT A DICT NOR A LIST
# it's called a Set actually
s = {1, 2, 3, 4, 4}
# sets behave like math sets
# --they only keep unique elements
print(s)  # {1,2,3,4}
# --also no order present, s[0] fails
s[0]  # Throws error: 'not subscriptable'

s = {1, 2, 3, 4, 4}  # This is a Set
print(s)  # {1,2,3,4}
s[0]  # Throws error: 'not subscriptable'

t1 = (9,) # These are tuples
t2 = (7,'k',None)
print(t1[0]) # just fine. prints 9
t1[0] = 0 # Throws error: no item assignment
t1.append(0) # Throws error: 'no method exists'

