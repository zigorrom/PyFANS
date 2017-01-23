import numpy as np
from os.path import join
import math
import sys

##
##filepath = "F:\\T=300K"
##filename = "t16-100x100nm_noise_2.dat"
##
##name = join(filepath,filename)
##
##print(name)
##
##file = np.loadtxt(name)
##
##
##time,current = file.transpose()
##
####current_pp = current[1:]
##
##N = len(current)-1
##
##print("N")
##print(N)
##
##print("time")
##print(time)
##print("curernt")
##print(current)
####
####print("current pp")
####print(current_pp)
##
##window_size = 1000
##sigma = 1
##appearence_radius = sigma * 1e-6
##
##def euclidean_distance(i,j):
##    return math.hypot(current[i]-current[j],current[i+1]-current[j+1])
##
##
##def eps(i,j):
##    d = euclidean_distance(i,j)
##    return 1 if d<=appearence_radius else 0
##
##vect_eps = np.vectorize(eps,otypes=[int])
##
##
##print("start calculation")
##
##result = np.zeros(window_size)
##
##for i in range(window_size):
####    arr = vect_eps(i,range(N))
####    print(arr)
##    result[i] = np.sum(vect_eps(i,range(window_size)))
##    print(i)
####
##
##res = np.vstack((current[:window_size],current[1:window_size+1],result)).transpose()
##
##np.savetxt("result4.dat",res)
##

def main():
    print(sys.argv)


if __name__ == "__main__":
    main()
