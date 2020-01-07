import math

A = 13000
r = 0.1
n = 25
print('P = ' + str(round((A/r) * (1 - 1/((1 + r) ** n)), 0)))
