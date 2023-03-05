"More on list operations"

# Check if list contains element:
print( 4 in [ 1, 2, 3, 4 ] ) # True
print( 5 in [ 1, 2, 3, 4 ] ) # False

# Indexes can be negative!
lst = [0 , 1, 2, 3, 4]
print( lst[2] == lst[-3] ) # True! Both are 2
print( lst[-3] == lst[len(lst) - 3] ) # True also

# Slices of lists are very versatile
lst = [0, 1, 2, 3, 4, 5]
# lst[start : stop : step]
print(lst[1:])    # [1, 2, 3, 4, 5]
print(lst[:2:-1]) # [5, 4, 3]
print(lst[-3::2]) # [3, 5]
print(lst[2:4])   # [2, 3]


#|  range(stop)
#|  range(start, stop[, step])
range(4) # [0,1,2,3]
range(1,4) # [1,2,3]
range(1,7,2) # [1,3,5,7]
for i in range(1,4,2):
    print(i)


# Initialize lists with multiplication too
lst = [0] * 3   # [0, 0, 0]
lst = [1,2] * 2 # [1, 2, 1, 2]

# (Extra) These functions may also be helpful!
all([True, True, 1, "hi"])        # True
all([True, True, 1, "hi", False]) # False now
any([False, "", [], None])        # False
any([False, "", [], None, 1])     # True now

# (Extra) filter and map methods, but not necessary
def action(x):
    return x*2
list(map(action, [1,2,3,4]))
# output: [2,4,6,8]

def check(x):
    return x > 2
list(filter(check, [1,2,3,4]))
# output: [3,4]