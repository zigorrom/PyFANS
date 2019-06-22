import numpy as np
from os.path import join, isfile, dirname, basename
import math
import sys
import argparse
import tqdm
import time
import multiprocessing
import functools
from contextlib import contextmanager
###  New Weighted Time Lag Method for the Analysis of Random Telegraph Signals

def phiFunction(i, data, coeff1, coeff2):
    data_len = len(data)-1
    values = np.array(list(map(lambda j: coeff1*math.exp(-math.hypot(data[i]-data[j],data[i+1]-data[j+1])/coeff2), range(data_len))))
    phi = np.sum(values)
    return phi #  values


def epsFunction(i, data, appearance_radius):
    data_len = len(data)-1
    values = np.array(list(map(lambda j: 1 if math.hypot(data[i]-data[j],data[i+1]-data[j+1]) <= appearance_radius else 0, range(data_len))))
    s = np.sum(values)
    return s #  values

@contextmanager    
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

class TimeLapHistogram2DBuilder:
    def __init__(self, xStart, xEnd, xBinCount, yStart, yEnd, yBinCount):
        self._x_start = xStart
        self._x_end = xEnd
        self._x_bin_count = xBinCount
        self._x_bin_size = (xEnd-xStart)/xBinCount

        
        self._y_start = yStart
        self._y_end = yEnd
        self._y_bin_count = yBinCount
        self._y_bin_size = (yEnd - yStart)/yBinCount
      
        self.reset()
        
    
    def reset(self):
        self._histogram_array = np.zeros((self._x_bin_count, self._y_bin_count))


    def assign_data(self, x,y,z):
        if x < self._x_start or x > self._x_end:
            return
        
        if y < self._y_start or y > self._y_end:
            return 

        x_idx = math.floor((x-self._x_start)/self._x_bin_size)
        y_idx = math.floor((y-self._y_start)/self._y_bin_size)

        self._histogram_array[x_idx, y_idx] += z

        

    def append_data(self, data):
        stDev = np.std(data)
        doubleStDevSqr = 2*stDev*stDev
        coeff = 1/(math.pi*doubleStDevSqr)
        data_len = len(data) - 1
        result = np.zeros(data_len)

        # for i in tqdm.tqdm(range(data_len)):
        #     val = epsFunction(i, data, stDev)
        #     result[i] = val #np.sum(values)
        #     self.assign_data(data[i], data[i+1], val)
        
        for i in tqdm.tqdm(range(data_len)):
            phi = phiFunction(i, data, coeff, doubleStDevSqr)
            result[i] = phi #np.sum(values)
            self.assign_data(data[i], data[i+1], phi)


        #max_phi = np.max(result)
        #result = np.divide(result, max_phi)
        #result = np.vstack((data[:data_len],data[1:data_len+1],result)).transpose()


        #return result

    def get_histogram(self):
        m = np.amax(self._histogram_array)
        hist = np.divide(self._histogram_array, m)
        xBinEdges = np.linspace(self._x_start, self._x_end, self._x_bin_count+1, endpoint=True)
        yBinEdges = np.linspace(self._y_start, self._y_end, self._y_bin_count+1, endpoint=True)
        return hist, xBinEdges, yBinEdges


class TimeLagPlotCalculator:
    def __init__(self):
        pass
    
    @staticmethod
    def calculate_tlp(data):
        stDev = np.std(data)
        doubleStDevSqr = 2*stDev*stDev
        coeff = 1/(math.pi*doubleStDevSqr)
        data_len = len(data) - 1
        result = None #np.zeros(data_len)
        
        ncores = multiprocessing.cpu_count() 
        ncores = ncores-1 if ncores>1 else 1
        with poolcontext(processes=ncores) as pool:
            result = np.array(pool.map(functools.partial(phiFunction, data=data, coeff1=coeff, coeff2=doubleStDevSqr), range(data_len)))
        
    
        # for i in tqdm.tqdm(range(data_len)):
        #     phi = phiFunction(data, i, coeff, doubleStDevSqr)
        #     result[i] = phi #np.sum(values)

        max_phi = np.max(result)
        result = np.divide(result, max_phi)
        result = np.vstack((data[:data_len],data[1:data_len+1],result)).transpose()
        return result

       
    @staticmethod
    def calculate_tlp_using_histogram(data, block_length = None):
        pass

    

    
    

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
    # test_tlp()