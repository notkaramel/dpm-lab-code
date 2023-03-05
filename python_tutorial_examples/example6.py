"""String examples."""

s1 = 'hello' # Both are valid strings
s2 = "world" # There is no difference
s3 = '8'     # Also a string, not char

# Index and slice work on strings
print(s1[0]) # Prints 'h'
print(s1[1:4]) # Prints 'ell'
"hello world".index('w') # index 6

ord('5') # get ascii value, 53
chr(53)  # get character, '5'

lst = str([5,6,7]) # acts like .toString()
lst # '[5, 6, 7]'
list("hi") # makes list ['h', 'i']

# Use for-loops on words too
word = " learning something "
for letter in word:
    print(letter)

# Other string methods
print(word.upper()) # Uppercase version
print(word.strip()) # Remove spaces on ends

# check if string is all numbers
print("80".isnumeric()) # True
print("8.0".isnumeric()) # False

# make list of parts, split by given string
print(word.split("g"))

# List of strings combined to one string
# Each element separated by '--'
word = '--'.join(['smith', 'jar'])
print(word) # 'smith--jar'

