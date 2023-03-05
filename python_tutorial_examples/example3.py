import math

lst = list()

# Empty lists
lst = []
# Filled list
lst = [0,1,2,3,4]
print(lst[0])   # get item
print(lst[-2])  # get item from back
print(lst[1:3])  # slice
print(lst[1:])   # 
print(lst[::-1]) # reverse slice
lst.append(5)
print(lst) # [0, 1, 2, 3, 4, 5]

lst = ['a',"b",56,True]
for num in lst:
    print(num)

for i, num in enumerate(lst):
    print(i, num)

N = len(lst)
for i in range(N):
    print(i, lst[i])

