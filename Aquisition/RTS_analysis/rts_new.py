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
##def perform_parse():
##    pass
def remove_peakups_rts(timetrace):
    for i in range(1,len(timetrace)-1):
        if timetrace[i-1]==timetrace[i+1] and timetrace[i-1] != timetrace[i]:
            timetrace[i] = timetrace[i-1]
    return timetrace

def remove_peeks(array, treshold = 1e-6):
    L = len(array)
    result = np.zeros(L)
    for i in range(1,L-1):
        point_aver = (array[i-1]+array[i+1])/2
        if abs(point_aver - array[i])>treshold:
            result[i] = point_aver
    return result

def create_window(name,length):
    pass

def get_level_by_amplitude(level_items, amplitude, treshold):
    res = (None,0)
    if not level_items:
        return res

    for i in range(len(level_items)):
        if abs(level_items[i]["amp"]-amplitude)<treshold :
            res = (level_items[i], i)

    return res

def eps(current,appearence_radius,i,j):
##    current,i = a
    d = math.hypot(current[i]-current[j],current[i+1]-current[j+1])#euclidean_distance(current,i,j)
    return 1 if d<=appearence_radius else 0

vect_eps = np.vectorize(eps,otypes=[int])
    
def calculate_levels(current_arr,treshold, wnd):

   
    L = len(current_arr)
    iqr = iqr = np.subtract(*np.percentile(current_arr, [75, 25]))
##    peak_to_peak = np.ptp*(current_arr)
    min_value = np.amin(current_arr)
    max_value = np.amax(current_arr)
    bin_width = 2 * iqr * math.pow(L,-1.0/3)
    print("max = {0}".format(max_value))
    print("min = {0}".format(min_value))
    
    print("bin_width = {0}".format(bin_width))
    bin_number = int((max_value-min_value)/bin_width)
    print("bin_number = {0}".format(bin_number))
    histogram_levels,step = np.linspace(min_value,max_value,num=bin_number+1,retstep=True)
    count_array = np.zeros(bin_number)
    index_array = np.arange(0,bin_number,dtype = int)
    histogram_levels = histogram_levels[1:]
    half_step = step/2
    bin_centers = histogram_levels - half_step

    result = np.zeros(len(current_arr),dtype=np.uint8)
    for i,val in enumerate(current_arr):
##        print("next index")
        print(i)

        bin_idx = 0
        for j, bin_level in enumerate(histogram_levels):
##            print("val = {0}, level = {1}".format(val,bin_level))
            if val < bin_level:
##                print("accepted {0}".format(j))
                bin_idx = j
                break
        result[i] = bin_idx
        count_array[bin_idx] += 1

##    print(len(bin_centers))
##    print(len(count_array))
##    print(len(index_array))
    
    levels = np.vstack((bin_centers,count_array,index_array))
    return (levels,result)
    
        


## OLD VERSION
## ######################################################################################
##
##             L = len(current_arr)
##    wnd_len = len(wnd)
##    if wnd_len % 2 >0:
##        return 
##    half_wnd_len = int(wnd_len/2)
##
##    print("half wnd len {0}".format(half_wnd_len))
##    l_weights = wnd[:half_wnd_len]
##    r_weights = wnd[half_wnd_len:]
##    
##    result = np.zeros(L,dtype=np.uint8)
##    left_avg = 0
##    right_arv = 0
##    prev_val = 0
##
##    level_items = []
##
##    prev_index =0
##
##    index_delay = 1
##    
##    for i in tqdm(range(half_wnd_len,L-half_wnd_len)):
##        left_avg = np.average(current_arr[i-half_wnd_len:i],weights=l_weights)
##        right_avg= np.average(current_arr[i:i+half_wnd_len],weights=r_weights)
##
##        item = None
####        index = 0
##        if abs(right_avg - left_avg) > treshold or abs(right_avg - prev_val) > treshold:
##            prev_val = right_avg
##            (item, prev_index) = get_level_by_amplitude(level_items, prev_val, treshold)
##            if item:
##                item["amp"] = (item["amp"]+prev_val)/2
##                item["count"] += 1
##                
##                
##            else:
##                prev_index = len(level_items)
##                item = {"amp": prev_val,"count": 1,"idx": prev_index}
##                level_items.append(item)
##            
##        result[i+index_delay] = prev_index
    ####################################################################################

##Check the shift
##        if abs(right_avg - prev_val) > sigma:
##            prev_val = right_avg
##    return (level_items,result)


def calc_times(calculated_amplitudes, level,dt):
    calculated_amplitudes = calculated_amplitudes - level
    length = len(calculated_amplitudes)
    lower_time_list = []
    higher_time_list = []
    current_time =0 
    for i in range(length-1):
        if calculated_amplitudes[i]*calculated_amplitudes[i+1]<0:
            if calculated_amplitudes[i]<calculated_amplitudes[i+1]:
                lower_time_list.append(current_time)
            else:
                higher_time_list.append(current_time)
            
            current_time = 0
        current_time += dt
    time_list = list(zip_longest(lower_time_list,higher_time_list,fillvalue= 0))
    return time_list


##def get_clusters(amplitudes, estimated_means):
MAX_ITERATIONS = 100000
def should_stop(oldCentroids, centroids, iterations):
    if iterations>MAX_ITERATIONS: return True
    return np.array_equal(oldCentroids,centroids)

def get_random_centroids(data, k):
    amps, counts, index = data #np.transpose(data)
    min_amp = min(amps)
    max_amp = max(amps)
    return np.linspace(min_amp,max_amp,k)
    
def get_labels(data,centroids):
    amps, counts, index = data  #np.transpose(data)
    
    labels = np.zeros(len(amps),dtype = int)
##    k = len(centroids)
    global_max_diff= abs(centroids[0]-centroids[-1])
    
    for i, amplitude in enumerate(amps):
        min_distance = global_max_diff
        centroid_idx = 0
        for j, mean in enumerate(centroids):
            diff = abs(amplitude-mean)
            if diff < min_distance:
                min_distance = diff
                centroid_idx = j
        labels[i] = centroid_idx
    return labels


def get_centroids(data,labels,k):
    amps, counts, index = data  #np.transpose(data)

    count_arr = np.ones(k, dtype=int)
    cumulative_arr = np.zeros(k)
##    n_all_counts = np.sum(count_arr)

    for i, centroid_idx in enumerate(labels):
        count_arr[centroid_idx] += counts[i]
        cumulative_arr[centroid_idx] += amps[i]*counts[i]

    centroids = cumulative_arr/count_arr
    return centroids
    

def k_means_levels_classification(data, k):
    amps, counts, index = data #np.transpose(data)

    centroids = get_random_centroids(data,k)
    print("in k means centroids")
    print(centroids)
    iterations = 0
    oldCentroids = None

    while not should_stop(oldCentroids, centroids, iterations):

        oldCentroids = centroids
        iterations +=1

        labels = get_labels(data, centroids)

        centroids = get_centroids(data, labels,k)
        print(centroids)
        

    dictionary_result = dict((int(idx), centroids[labels[i]]) for i,idx in enumerate(index))
    return (centroids, dictionary_result)

    
    
    

def perform_analysis(fn, wnd_name, wnd_len, wnd, tr, rempk,postfix ):
    if not isfile(fn):
        print(fn)
        print("No such file for analysis")
        return

    if len(wnd)>0:
        print("using of custom window")
    elif wnd_name and wnd_len >0:
        print("using window {0}".format(wnd_name))
        wnd = create_window(wnd_name,wnd_len)
    else:
        print("please select window and set its length")
        return 

    time, current = np.loadtxt(fn).transpose()
    
    if rempk:
        print("removing peekups")
        current = remove_peeks(current)
    print("start analysis")
    l = 200000
    dt = current[1]
    current = current[:l]
    time = time[:l]
    tr = 1e-6

    levels, result = calculate_levels(current,tr, wnd)
    print(levels)
    print(result)

##    iterable = ([item["amp"],item["count"]] for item in levels)
##    arr = [[item["amp"],item["count"], item["idx"]] for item in levels]
##    arr  = np.fromiter(iterable)
##    amps, counts = np.transpose(arr)

    estimated_k_levels = 2
    centroids, k_values_dictionary = k_means_levels_classification(levels,estimated_k_levels)
    print("k_values_dictionary")
    print(k_values_dictionary)

    arr = np.transpose(levels)
    print(levels)
##    print(arr)
    _histogram_filename = join(dirname(fn),"{0}_hist.dat".format(basename(fn).split('.')[0]))
    np.savetxt(_histogram_filename,arr)

    print("write resulting current")
    
    iterable = (k_values_dictionary[i] for i in result)
    resulting_current = np.fromiter(iterable, np.float)
    resulting_current = remove_peakups_rts(resulting_current)
    _result_filename = join(dirname(fn),"{0}_rts.dat".format(basename(fn).split('.')[0]))
    np.savetxt(_result_filename, np.vstack((time,current,resulting_current)).transpose())

    times = []
    for a,b in zip(centroids[:-1],centroids[1:]):
        level = (a+b)/2
        times.extend(calc_times(resulting_current,level,dt))

    print("times")
    print(times)
    _times_filename = join(dirname(fn),"{0}_times.dat".format(basename(fn).split('.')[0]))
    np.savetxt(_times_filename, times)

def main():
    parser = argparse.ArgumentParser(description='Process timetrace and search transitions')
    parser.add_argument('fn', metavar='f', type=str, nargs='?', default = "",
                    help='The name of file where timetrace is stored')
    parser.add_argument('-wnd_name', metavar='window name', type=str, nargs='?', default = None,
                    help='The name of window function to be applied')

    parser.add_argument('-wnd_len', metavar='window length', type=int, nargs='?', default = 0,
                    help='The length of window function to be applied')

    parser.add_argument('-wnd', metavar='custom window', type=float, nargs='+', default = [],
                    help='Custom window coefficients')

    parser.add_argument('-tr', metavar='transition treshold', type=float, nargs='?', default = 1e-6,
                    help='Treshold value for counting peaks')
    
    parser.add_argument('--rempk', action = 'store_true',default = False,  help='remove pickups')
    
    parser.add_argument('-postfix', metavar='postfix for processed file', type=str, nargs='?', default = "rts",
                    help='Treshold value for counting peaks')
    args = parser.parse_args("D:\\PhD\\Measurements\\2016\\SiNW\\SOI#18\\Chip19\\2016.12.13\\VacuumPot\\Noise\\T=300K\\t16-100x100nm_noise_8.dat -wnd 0.7 0.8 0.9 1 1 1 1 0.9 0.8 0.7".split(" "))
##    args = parser.parse_args("F:\\Noise\\T=300K\\t16-100x100nm_noise_8.dat -wnd 0.7 0.8 0.9 1 1 1 1 0.9 0.8 0.7".split(" "))
##    print(args)
    perform_analysis(**vars(args))

if __name__ == "__main__":
    main()

