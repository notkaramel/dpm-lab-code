
f = open('testfile.txt', 'w')

f.write('{},{},{}\n'.format(1, 2, 3))
f.write(','.join(['4', '5', '6']) + '\n')
f.write(f'{7+1},{8+1},{9+1}\n')

f.close()

with open('testfile.txt','w') as f:
    f.write('{},{},{}\n'.format(1, 2, 3))
    f.write(','.join(['4', '5', '6']) + '\n')
    f.write(f'{7+1},{8+1},{9+1}\n')

with open('testfile.txt', 'r') as f:
    print(f.read())
"""
1,2,3
4,5,6
8,9,10
"""

result = []
with open('testfile.txt', 'r') as f:
    for line in f.readlines():
        result.append(line.split(','))

print(result)
"""result:
[
    ['1', '2', '3\n'], 
    ['4', '5', '6\n'], 
    ['8', '9', '10\n']
]

# Note:
# Remove whitespace with str.strip()
# ('3\n'.strip()) -> '3'
"""

