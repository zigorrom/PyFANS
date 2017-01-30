import numpy as np
from os.path import join, isfile, dirname, basename
import math
import sys
import argparse
from tqdm import tqdm
import time
from itertools import zip_longest

##filepath = "G:\\Study\\PhD\\Measurements\\2016\\SiNW\\SOI#18\\Chip19\\2016.12.13\\VacuumPot\\Noise\\T=300K"
##filename = "t16-100x100nm_noise_8.dat"
##
##f = join(filepath,filename)
##file = np.loadtxt(f)
##
##time,current = file.transpose()
##N_half_wnd = 5
##r_weights = [1,1,0.9,0.8,0.7]
##l_weights = r_weights.reverse()
##
##sigma = 1e-5
##L = len(current)#10000
##dt = current[1]
##
##avg_wnd = 3
####
##avg = current[:L].copy()#np.zeros(L)
###avg2 = current[:L].copy()
####result = np.zeros(L)
##
##
##for i in range(1,L-1):
##    point_aver = (avg[i-1]+avg[i+1])/2
##    if abs(point_aver - avg[i]):
##        avg[i] = point_aver
##    
##
##
##
##
####for i in range(avg_wnd, L):
####    avg2[i] = np.average(avg2[i-avg_wnd:i])
##def calc_levels(current_arr,L):
##    result = np.zeros(L)
##    left_avg = 0
##    right_arv = 0
##    prev_val = 0
####    prev_time = 0
####    time_counter = 0
##    for i in range(N_half_wnd,L-N_half_wnd):
##        left_avg = np.average(current_arr[i-N_half_wnd:i],weights=l_weights)
##        right_avg= np.average(current_arr[i:i+N_half_wnd],weights=r_weights)
##        diff = right_avg - left_avg
##        abs_diff = abs(diff)
##        if abs_diff > sigma or abs(right_avg - prev_val) > sigma:
####            if time_counter >1:
####                amplitude_time_list.append([prev_val,prev_time])
##            prev_val = right_avg
####            prev_time =0
####            time_counter =0 
##
##        result[i] = prev_val
####        prev_time += dt
####        time_counter += 1
####        print(i)
##
##    return result
##
##
##
##def write_levels(amplitudes):
##    res_file_name = join(filepath,"{0}_{1}.dat".format(basename(filename),"rts_rec"))
##    np.savetxt(res_file_name,amplitudes)
##
##def calc_times(calculated_amplitudes, level):
##    calculated_amplitudes = calculated_amplitudes - level
##    length = len(calculated_amplitudes)
##    lower_time_list = []
##    higher_time_list = []
##    current_time =0 
##    for i in range(length-1):
##        if calculated_amplitudes[i]*calculated_amplitudes[i+1]<0:
##            if calculated_amplitudes[i]<calculated_amplitudes[i+1]:
##                lower_time_list.append(current_time)
##            else:
##                higher_time_list.append(current_time)
##            
##            current_time = 0
##        current_time += dt
##    time_list = list(zip_longest(lower_time_list,higher_time_list))
##    return time_list
##        
##    
##    
##def write_times(amplitude_time_list):
##    amplitides_time_filename = join(filepath,"{0}_{1}.dat".format(basename(filename),"rts_times"))
##    np.savetxt(amplitides_time_filename,amplitude_time_list)
####res = np.vstack((time[:L],current[:L],avg,result)).transpose()
####res = np.vstack((time[:L],current[:L],avg,calc1(current,L),calc1(avg,L))).transpose()
##
##
##amplitudes = calc_levels(current,L)
##amplitudes_avg = calc_levels(avg,L)
##res = np.vstack((time[:L],current[:L],avg,amplitudes,amplitudes_avg)).transpose()
##write_levels(res)
##
<<<<<<< HEAD
def perform_parse():
    pass
=======
##def perform_parse():
##    pass
>>>>>>> origin/master



def main():
    parser = argparse.ArgumentParser(description='Process timetrace and search transitions')
    parser.add_argument('fn', metavar='f', type=str, nargs='?', default = "",
                    help='The name of file where timetrace is stored')
    parser.add_argument('-wnd_name', metavar='window name', type=str, nargs='?', default = "r",
                    help='The name of window function to be applied')

    parser.add_argument('-wnd_len', metavar='window length', type=int, nargs='?', default = 4,
                    help='The length of window function to be applied')

    parser.add_argument('-wnd', metavar='custom window', type=float, nargs='+', default = 0,
                    help='Custom window coefficients')

    parser.add_argument('-tr', metavar='transition treshold', type=float, nargs='?', default = 0.0,
                    help='Treshold value for counting peaks')
    

    parser.add_argument('--rempk', action = 'store_true',default = False,  help='remove pickups')
    
    

    args = parser.parse_args()
    print(args)
    

if __name__ == "__main__":
    main()

