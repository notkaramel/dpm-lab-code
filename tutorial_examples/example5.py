"Examples on dictionaries"

# Basic Dictionary creation
x = {} # empty
d = {
    'a':1,
    'b':2,
    'c':None,
    'd':'meh'
}

print('a' in d) # 'in' checks keys
print('b' in d.keys()) # also check keys
print(2 in d.values()) # to check values

# To loop through all keys and values
for key, value in dict.items():
    print(key, ':', value)

# To loop through sorted keys
for key in sorted(dict.keys()):
    print(key)

# THIS IS NOT A DICT
# it's called a Set actually...
s = {1,2,3,4,4}
# sets behave like math sets
# --they only keep unique elements
print(s) # {1,2,3,4}
# --also no order present, s[0] fails
s[0]