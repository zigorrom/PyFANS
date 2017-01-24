import numpy as np
from os.path import join
import matplotlib.pyplot as plt
import math
sigma = 10e-7

filepath = "G:\\Study\\PhD\\Measurements\\2016\\SiNW\\SOI#18\\Chip19\\2016.12.13\\VacuumPot\\Noise\\T=300K"
filename = join(filepath,"t16-100x100nm_noise_4.dat")
f = np.loadtxt(filename).transpose()

current = f[1]
cpp = current[1:]
c = current[:-1]
print(len(current))
print(len(cpp))
print(len(c))
##plt.scatter(c,cpp)
##plt.show()
N = len(current)-2
print(N)


def eps_from_distanse(d):
    if d <= sigma:
        return 1
    else:
        return 0


def distanse(i,j):
##    print("i={0}".format(i))
##    print("j={0}".format(j))
##    print()
    ci = c[i]
    cipp = c[i+1]
    cj = cpp[j]
    cjpp = cpp[j+1]
    return math.hypot(ci-cipp,cj-cjpp)


vect_distanse = np.vectorize(distanse)
vect_eps_from_distanse = np.vectorize(eps_from_distanse, otypes=[int])
indexes = np.arange(N)

generator = (i for i in range(N))

appearanse_function = np.zeros(N)

print("start calculation")

for i in generator:
    distanses = vect_distanse(i,indexes)
    eps = vect_eps_from_distanse(distanses)
    appearanse_function[i] = np.sum(eps)
    print("progress: {0}%".format(i*100.0/N))
    


result = np.vstack((c,cpp,appearanse_function)).transpose()

np.savetxt("test.dat",result)


##print(appearanse_function)


##def distanse(i):
##    np.apply
##    print(i)
##    print(j)
##    return math.hypot(c[i]-c[i+1],cpp[j]-cpp[j+1])




##v = [eps(current,0,j) for j in range(N-1)]
##print(v)
    


##print(current)


    



