from scipy import signal
from scipy.signal import decimate
from scipy.signal import periodogram
import numpy as np
import matplotlib.pyplot as plt
import timeit
import math



def main():
    n = 10
    nsamples = 50000
    fs = 500000
    new_fs = 10000

    f1_max = 3000

    decimation_factor = int( fs/new_fs)
    new_fs = int(fs/decimation_factor)
    print("sampling rate = {0}".format(fs))
    print("decimation factor = {0}".format(decimation_factor))
    print("new sampling rage= {0}".format(new_fs))

    total_array = np.zeros(fs)
    second_range = None
    first_range = None
    freq_2 = None
    freq_1 = None
    aver_counter = 0
    fill_value = 0

    for i in range(n):
        t = np.linspace(0, 1, nsamples, endpoint=False)
        arr = np.random.random(nsamples)
        arr = arr + 0.1*signal.square(2 * np.pi * 100 * t)
        #sig = np.sin(2 * np.pi * t)
        #arr = arr + signal.square(2 * np.pi * 30 * t, duty=(sig + 1)/2)
        #arr = signal.square(2 * np.pi * 1 * t)
        #arr = np.sin(2 * np.pi * t)
        arr = arr + np.sin(np.pi*f1_max*t)
        aver_counter += 1 
        new_fill_value = fill_value+nsamples
        total_array[fill_value:new_fill_value] = arr
        fill_value = new_fill_value % fs
        if second_range is None:
            freq_2, second_range = periodogram(arr, fs)
        else:
            f, psd = periodogram(arr, fs)
            #np.average((self.average, data['p']), axis=0, weights=(self.average_counter - 1, 1))
            second_range = np.average((second_range,psd),axis=0,weights=(aver_counter - 1, 1))        
        
    
    decimated = decimate(total_array,decimation_factor,n=8,ftype="iir",zero_phase=True)
    print("decimated length = {0}".format(len(decimated)))
    print(decimated)
    freq_1, first_range = periodogram(decimated, new_fs)
    
    df1 = freq_1[1]
    df2 = freq_2[1]



    freq1_idx = math.floor(f1_max/df1)+1
    freq2_idx = math.ceil(f1_max/df2)+1

    print(freq_1)
    print(first_range)
    print(freq_2)
    print(second_range)

    res_freq  = np.hstack((freq_1[1:freq1_idx],freq_2[freq2_idx:]))
    res = np.hstack((first_range[1:freq1_idx],second_range[freq2_idx:]))
    print("result length = {0}".format(len(res)))
    print(res_freq)
    
    #plt.loglog(freq_1,first_range,'r', freq_2, second_range,'k', res_freq,res, 'g')
    #plt.show()
    return (res_freq, res)




def analyze_timetrace():
    fname = "F:\\Noise data_000.dat"
    
    n = 10
    nsamples = 50000
    fs = 500000
    new_fs = 10000

    f1_max = 3000
    decimation_factor = int( fs/new_fs)
    new_fs = int(fs/decimation_factor)


    total_array = np.zeros(fs)

    second_range = None
    first_range = None
    freq_2 = None
    freq_1 = None
    f1_aver_counter = 0
    f2_aver_counter = 0
    fill_value = 0

    #arr = np.zeros(fs)

    counter = 0
    line_counter = 0
    with open(fname) as timetrace:
        print(timetrace.readline())
        print(timetrace.readline())
        for line in timetrace:
            time,volt = line.split('\t')
            total_array[counter+fill_value]= float(volt)
            line_counter += 1
            #print(line_counter)
            counter += 1
            if counter == nsamples:
                counter = 0
                f2_aver_counter += 1
                new_fill_value = fill_value+nsamples
                arr = total_array[fill_value:new_fill_value]
                fill_value = new_fill_value % fs
                if second_range is None:
                    freq_2, second_range = periodogram(arr, fs)
                else:
                    f, psd = periodogram(arr, fs)
                    #np.average((self.average, data['p']), axis=0, weights=(self.average_counter - 1, 1))
                    second_range = np.average((second_range,psd),axis=0,weights=(f2_aver_counter - 1, 1))   

                

                #perform small fft
               
        
            if line_counter%fs ==0:
                fill_value = 0
                decimated = decimate(total_array,decimation_factor,n=8,ftype="iir",zero_phase=True)
                #print("decimated length = {0}".format(len(decimated)))
                #print(decimated)
                f1_aver_counter += 1
                print(f1_aver_counter)
                if first_range is None:
                    freq_1, first_range = periodogram(decimated, new_fs)
                else:
                    f,psd = periodogram(decimated,new_fs)
                    first_range = np.average((first_range,psd),axis=0,weights=(f1_aver_counter - 1, 1))   
    

        df1 = freq_1[1]
        df2 = freq_2[1]



        freq1_idx = math.floor(f1_max/df1)+1
        freq2_idx = math.ceil(f1_max/df2)+1

        #print(freq_1)
        #print(first_range)
        #print(freq_2)
        #print(second_range)

        res_freq  = np.hstack((freq_1[1:freq1_idx],freq_2[freq2_idx:]))
        res = np.hstack((first_range[1:freq1_idx],second_range[freq2_idx:]))
        #print("result length = {0}".format(len(res)))
        #print(res_freq)
        plt.loglog(res_freq,res,'r')
        plt.show()
                #perform big fft
  
def multichannel_acquisition():
    nchan = 4
    counter = 0
    fs = 500000
    npoints = 50000
    max_count = fs*1000
    
    print("started")
    #init_time = time.time()
            
    f1_max = 3000
    new_fs = 10000
    decimation_factor = int( fs/new_fs)
    new_fs = int(fs/decimation_factor)
    total_array = np.zeros((nchan,fs))

    second_range = None
    first_range = None
    freq_2 = None
    freq_1 = None
    f1_aver_counter =0
    f2_aver_counter = 0
    fill_value = 0
            
       

    while counter < max_count:
        f2_aver_counter += 1
        new_fill_value = fill_value+npoints
        data = np.random.randn(nchan,npoints)
        #print("data have been read")
                        
        total_array[:,fill_value:new_fill_value] = data
        #print("slice was taken")
        
        fill_value = new_fill_value % fs

        if second_range is None:
            freq_2, second_range = periodogram(data, fs)
        else:
            f, psd = periodogram(data, fs)
            #np.average((self.average, data['p']), axis=0, weights=(self.average_counter - 1, 1))
            second_range = np.average((second_range,psd),axis=0,weights=(f2_aver_counter - 1, 1))   


        if new_fill_value%fs == 0:
            counter+= fs
            #fill_value = 0
            decimated = decimate(total_array,decimation_factor,n=8,ftype="iir",axis = 1 ,zero_phase=True)
            #print("decimated length = {0}".format(len(decimated)))
            #print(decimated)
            f1_aver_counter += 1
            #print(f1_aver_counter)
            if first_range is None:
                freq_1, first_range = periodogram(decimated, new_fs)
            else:
                f,psd = periodogram(decimated,new_fs)
                first_range = np.average((first_range,psd),axis=0,weights=(f1_aver_counter - 1, 1)) 
            #counter += npoints
            #t = time.time()-init_time

    df1 = 1
    df2 = fs/npoints
    print(df1)
    print(df2)


    freq1_idx = math.floor(f1_max/df1)+1
    freq2_idx = math.ceil(f1_max/df2)+1
    print(freq1_idx)
    print(freq2_idx)

    res_freq  = np.hstack((freq_1[1:freq1_idx],freq_2[freq2_idx:]))
    res = np.hstack((first_range[:,1:freq1_idx],second_range[:,freq2_idx:]))             
    return (res_freq,res)

if __name__ == "__main__":
    #analyze_timetrace()
    #res_freq, res = multichannel_acquisition()
    #print(res_freq)
    #print(res)
    #r1,r2,r3,r4 = res
    #plt.loglog(res_freq, r1,"r",res_freq, r2,"g",res_freq, r3,"b",res_freq, r4,"c")
    #plt.show()

    #result = None
    #freq = None
    #n_repeats = 100

    #for i in range(n_repeats):
    #    if result is None:
    #        freq,result = main()
    #    else:
    #        f,psd = main()
    #        result = np.average((result,psd),axis=0,weights=(i, 1))        

    #plt.loglog(freq,result,'r')
    ##plt.semilogy(freq,result,'r')
    #plt.show()  

    print(timeit.Timer(multichannel_acquisition).timeit(number=1))
    #print(timeit.Timer(main).timeit(number=1))
    
    #main()