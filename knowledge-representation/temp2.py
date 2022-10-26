r, y, d, w = [int(x) for x in input().split()]

total = 0
for i in range(y):
    total += d
    total += total * (1 + r / 100)

