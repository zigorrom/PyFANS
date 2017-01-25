import numpy as np
from os.path import join, isfile, dirname, basename
import math
import sys
import argparse
import tqdm
import time

filepath = "H:\\Study\\PhD\\Measurements\\2016\\SiNW\\SOI#18\\Chip19\\2016.12.13\\VacuumPot\\Noise\\T=300K"
filename = "t16-100x100nm_noise_8.dat"

f = join(filepath,filename)
file = np.loadtxt(f)

time,current = file.transpose()
N_half_wnd = 5
r_weights = [1,1,0.9,0.8,0.7]
l_weights = r_weights.reverse()

sigma = 1e-5
L = 10000

avg_wnd = 10

avg = np.zeros(L)
#avg2 = current[:L].copy()
##result = np.zeros(L)

for i in range(L-avg_wnd):
    avg[i] = np.average(current[i:i+avg_wnd])

##for i in range(avg_wnd, L):
##    avg2[i] = np.average(avg2[i-avg_wnd:i])
def calc1(current_arr,L):
    result = np.zeros(L)
    left_avg = 0
    right_arv = 0
    prev_val = 0
    for i in range(N_half_wnd,L-N_half_wnd):
        left_avg = np.average(current_arr[i-N_half_wnd:i],weights=l_weights)
        right_avg= np.average(current_arr[i:i+N_half_wnd],weights=r_weights)
        diff = right_avg - left_avg
        abs_diff = abs(diff)
        if abs_diff > sigma:
            prev_val = right_avg

        if abs(right_avg - prev_val) > sigma:
            prev_val = right_avg
            
        result[i] = prev_val
        print(i)

    return result

##res = np.vstack((time[:L],current[:L],avg,result)).transpose()
res = np.vstack((time[:L],current[:L],avg,calc1(current,L),calc1(avg,L))).transpose()
res_file_name = join(filepath,"{0}_{1}.dat".format(basename(filename),"rts_rec"))
np.savetxt(res_file_name,res)

