import numpy as np
from os.path import join, isfile, dirname, basename

filename = "D:\\PhD\\Measurements\\2016\\SiNW\\SOI#18\\Chip19\\2016.12.13\\VacuumPot\\Noise\\T=300K\\t16-100x100nm_noise_2_times.dat"
t1,t2 = np.loadtxt(filename).transpose()

t1_hist, t1_bin_edges = np.histogram(t1,bins = "fd")
t2_hist, t2_bin_edges = np.histogram(t2,bins = "fd")



print(t1_hist)

print(t2_hist)


