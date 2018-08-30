import numpy as np
from os.path import join, isfile, dirname, basename
import math
import sys
import argparse
import tqdm
import time


def eps(current,appearence_radius,i,j):
    d = math.hypot(current[i]-current[j],current[i+1]-current[j+1])#euclidean_distance(current,i,j)
    return 1 if d<=appearence_radius else 0

vect_eps = np.vectorize(eps,otypes=[int])


MEAS_DATA_FN_COL = 3
MEAS_DATA_HEADER_ROWS = 2

def perform_rts_transition_analysis():
    pass

def perform_tlp_analysis():
    pass


def perform_analysis(fn, ns, s, e, sigma):
    if not isfile(fn):
        print("No such file to analyze")
        return

    if ns == 0:
        print("Nothing to process =) You asked to process 0 samples")
        return

    if s < 0:
        print("Start index must be equal or larger than 0")
        return

    if e < s and e>0:
        print("End index cannot be smaller than start index")
        return

    file_directory = dirname(fn)
    print(fn)
    print(file_directory)
    data = list()
    
    with open(fn) as file:
        ## possibly use filter here
        for line in file:
            line = line.strip('\n')
            if len(line) <1:
                continue
            words = line.split('\t')
            data.append(words)
            
    if len(data) > MEAS_DATA_HEADER_ROWS:
        data = data[MEAS_DATA_HEADER_ROWS:]
    else:
        print("no data to analyze")
        return

        
    n_files = len(data)
    n_files_counter = 0
    for i in range(s,e):
        meas = data[i]
        n_files_counter += 1
        print("File: {0}/{1}".format(n_files_counter,n_files))
        short_filename = meas[MEAS_DATA_FN_COL]
        filename = join(file_directory,short_filename)
        if not isfile(filename):
            print("No such file")
            continue

        print("Start loading data from file.")
        time,current = np.loadtxt(filename).transpose()
        print("Data loaded.")
        N = len(current)-1
        window_size =  ns if ns>0 else N
        appearence_radius = sigma * 1e-6
        result = np.zeros(window_size)
        ## possibly walk along the array with window size
        for i in tqdm.tqdm(range(window_size)):
            values = list(map(lambda j: eps(current,appearence_radius,i,j) ,range(window_size)))
            result[i] = np.sum(values)
    
        res = np.vstack((current[:window_size],current[1:window_size+1],result)).transpose()
        res_file_name = join(file_directory,"{0}_{1}.dat".format(basename(short_filename),"rts"))
        np.savetxt(res_file_name,res)
        print("Result was saved in the file: {0}".format(res_file_name))



def main():
    parser = argparse.ArgumentParser(description='Process timetraces in order to check RTS appearance using TLP method')
    parser.add_argument('-fn', metavar='f', type=str, nargs='?', default = "MeasurDataCapture.dat",
                    help='The name of main file where all measured data is stored')

    parser.add_argument('-ns', metavar='Number of Samples', type = int, nargs='?' , default = -1,
                        help = 'The number of samples to be analyzed')
    
    parser.add_argument('-s', metavar='Start index', type = int, nargs='?' , default = 0,
                        help = 'The index where to start analyzing measured data')

    parser.add_argument('-e', metavar='End index', type = int, nargs='?' , default = -1,
                        help = 'The inclusive index where to stop measured data analysis')

    parser.add_argument('-sigma', metavar='Sigma value', type = int, nargs='?' , default = 1,
                        help = 'The sigma value for the current measurement data distribution')

    
    args = parser.parse_args()
##    print(args)
    perform_analysis(**vars(args))

if __name__ == "__main__":
    main()
