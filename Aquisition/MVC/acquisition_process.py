import sys
import numpy as np
from PyQt4 import QtCore
from multiprocessing import Process, Event, JoinableQueue
from agilent_u2542a import *
from scipy.signal import periodogram
from scipy.signal import decimate
import math

"""
This class implements acquisition from hardware and fourier tranform
Need to implement amount of samples to acquire    
"""
class Acquisition(Process):
    """sample_rate is acquisition sample rate, points per shot - how much points would be acquired each time, total samples = acquiring time*sample_rate"""
    def __init__(self, visa_resource, data_queue, sample_rate, points_per_shot, total_samples):# child_pipe):
        super().__init__()
        self.exit = Event()
        self.visa_resource = visa_resource
        self.data_queue = data_queue
        
        self.sample_rate = sample_rate
        self.points_per_shot = points_per_shot
        self.total_samples = total_samples
        
    def stop(self):
        self.exit.set()

    def fill_array(self,a,res_array,counter, fill_value_start, fill_value_end):
        for i,idx in enumerate(range(fill_value_start,fill_value_end)):
            res_array[counter.index][idx] = a[i]
        counter.increment()


    def run_new(self):
        sys.stdout = open("log.txt", "w")
        data_queue = self.data_queue
        
        try:
            d = AgilentU2542A(self.visa_resource)
            d.daq_init_channels()
            nchan = len(d.enabled_ai_channels)
            counter = 0

            row_counter = Counter()

            fs = self.sample_rate
            npoints = self.points_per_shot
            max_count = self.total_samples
            
            d.daq_run()
            print("started")
            init_time = time.time()
            

            #functions for reducing dot anmount in cycle below
            need_exit = self.exit.is_set
            is_data_ready = d.daq_is_data_ready
            read_data = d.daq_read_data
            
            f1_max = 3000
            new_fs = 10000
            decimation_factor = int( fs/new_fs)
            new_fs = int(fs/decimation_factor)
            total_array = np.zeros((nchan,fs))

            second_range = None
            first_range = None
            freq_2 = None
            freq_1 = None
            #f1_aver_counter = 0
            f2_aver_counter = 0
            fill_value = 0
            
               

            while (not need_exit()) and counter < max_count:
                try:
                    if is_data_ready():
                        
                        f2_aver_counter += 1
                        new_fill_value = fill_value+npoints
                        data = read_data()
                        print("data have been read")
                        
                        #for i,idx in enumerate(range(fill_value, new_fill_value)):
                        #    for j in range(nchan):
                        #        total_array[j,idx] = data[j,i]
                        #        print("i,j,idx")
                        #        print(i)
                        #        print(j)
                        #        print(idx)
                            
                            
                        
                        total_array[:,fill_value:new_fill_value] = data
                        print("slice was taken")
                        print(arr)
                        fill_value = new_fill_value % fs

                        if second_range is None:
                            freq_2, second_range = periodogram(data, fs)
                        else:
                            f, psd = periodogram(data, fs)
                            #np.average((self.average, data['p']), axis=0, weights=(self.average_counter - 1, 1))
                            second_range = np.average((second_range,psd),axis=0,weights=(f2_aver_counter - 1, 1))   


                        if new_fill_value%fs == 0:
                            #fill_value = 0
                            decimated = decimate(total_array,decimation_factor,n=8,ftype="iir",axis = 1 ,zero_phase=True)
                            #print("decimated length = {0}".format(len(decimated)))
                            #print(decimated)
                            #f1_aver_counter += 1
                            #print(f1_aver_counter)
                            #if first_range is None:
                            freq_1, first_range = periodogram(decimated, new_fs)
                            #else:
                            #    f,psd = periodogram(decimated,new_fs)
                            #    first_range = np.average((first_range,psd),axis=0,weights=(f1_aver_counter - 1, 1)) 
                            #counter += npoints
                            t = time.time()-init_time

                            df1 = 1/fs
                            df2 = 1/new_fs

                            freq1_idx = math.floor(f1_max/df1)+1
                            freq2_idx = math.ceil(f1_max/df2)+1

                            res_freq  = np.hstack((freq_1[1:freq1_idx],freq_2[freq2_idx:]))
                            res = np.hstack((first_range[:,1:freq1_idx],second_range[:,freq2_idx:]))


                            #data = read_data()
                            print(t)
    ##                        print(len(data))
                            print(data)
                            freq, psd = periodogram(data,fs) 
    ##                        decimated_data = 
                            block = {
                                     "t": t,
                                     "d": np.copy(total_array),
                                     "f": res_freq , #np.delete(freq,1,0),
                                     "p": res  #np.delete(psd,1,1)
                                     }
                            data_queue.put(block)
                            print(psd)
                        
                except Exception as e:
                    err = str(e)
                    print(err)
                    if err== 'overload':
                        counter = max_count
                        break
                                    
        except Exception as e:
            print ("exception"+str(e))
        finally:
            d.daq_stop()
##            data_queue.close()
            print("finished") 


    

#    def run_new(self):
#        sys.stdout = open("log.txt", "w")
#        data_queue = self.data_queue
        
#        try:
#            d = AgilentU2542A(self.visa_resource)
#            d.daq_init_channels()
#            counter = 0
#            fs = self.sample_rate
#            npoints = self.points_per_shot
#            max_count = self.total_samples
            
#            d.daq_run()
#            print("started")
#            init_time = time.time()
            

#            #functions for reducing dot anmount in cycle below
#            need_exit = self.exit.is_set
#            is_data_ready = d.daq_is_data_ready
#            read_data = d.daq_read_data
            
            
#            while (not need_exit()) and counter < max_count:
#                try:
#                    if is_data_ready():
                        
#                        t = time.time()-init_time
#                        data = read_data()
                        
                        
                        
#                        #freq, psd = periodogram(data,fs) 
###                        decimated_data = 
#                        block = None
#                        #block = {
#                        #         "t": t,
#                        #         "d": data,
#                        #         "f": np.delete(freq,1,0),
#                        #         "p": np.delete(psd,1,1)
#                        #         }
#                        data_queue.put(block)
                        
                        
#                except Exception as e:
#                    err = str(e)
#                    print(err)
#                    if err== 'overload':
#                        counter = max_count
#                        break
                                    
#        except Exception as e:
#            print ("exception"+str(e))
#        finally:
#            d.daq_stop()
###            data_queue.close()
#            print("finished")




        #Previous version
    def run(self):
        sys.stdout = open("log.txt", "w")
        data_queue = self.data_queue
        
        try:
            d = AgilentU2542A(self.visa_resource)
            d.daq_init_channels()
            counter = 0
            fs = self.sample_rate
            npoints = self.points_per_shot
            max_count = self.total_samples
            
            d.daq_run()
            print("started")
            init_time = time.time()
            

            #functions for reducing dot anmount in cycle below
            need_exit = self.exit.is_set
            is_data_ready = d.daq_is_data_ready
            read_data = d.daq_read_data
            
            
            while (not need_exit()) and counter < max_count:
                try:
                    if is_data_ready():
                        counter += npoints
                        t = time.time()-init_time
                        data = read_data()
                        print(t)
##                        print(len(data))
                        print(data)
                        freq, psd = periodogram(data,fs) 
##                        decimated_data = 
                        block = {
                                 "t": t,
                                 "d": data,
                                 "f": np.delete(freq,1,0),
                                 "p": np.delete(psd,1,1)
                                 }
                        data_queue.put(block)
                        print(psd)
                        
                except Exception as e:
                    err = str(e)
                    print(err)
                    if err== 'overload':
                        counter = max_count
                        break
                                    
        except Exception as e:
            print ("exception"+str(e))
        finally:
            d.daq_stop()
##            data_queue.close()
            print("finished") 


class AcquisitionProcess(QtCore.QThread):
    threadStarted = QtCore.pyqtSignal()
    threadStopped = QtCore.pyqtSignal()

    def __init__(self, data_storage, data_queue,nchan = 1, npoints = 100, parent=None):
        super().__init__(parent)
        self.data_storage = data_storage
        self.data_queue = data_queue
        self.alive = False
        self.nchan = nchan
        self.npoints = npoints
        self.arr = np.zeros((nchan,npoints))
        

    def stop(self):
        self.alive = False
        self.wait()

    def parse_output(self, data,counter):
        print(data)
##        np.savetxt("file_{0}.txt".format(counter),data)
        
    def run(self):
        self.alive = True
        self.threadStarted.emit()
        data_queue = self.data_queue
        parse = self.parse_output
        counter = 0
        data_storage = self.data_storage
##        file_tt = open("data_tt.txt", 'wb')
##        file_psd = open("data_psd.txt", 'wb')
##        file_ave_psd = open("data_psd_ave.txt", 'wb')
##        average = None
        
        
        while self.alive or (not data_queue.empty()):
            try:
                print("wait for data")
                data = data_queue.get(timeout=1)
                data_queue.task_done()
                #print("data received")
                #print(data["d"])
##                parse(data.transpose(),counter)
##                parse(data,counter)
                data_storage.update(data)
##                d = data["d"].transpose()
##                np.savetxt(file_tt,d,fmt='%e',delimiter='\t', newline='\r\n')
##                self.arr += data['p']
##                p = np.vstack((data["f"], data["p"])).transpose()
##                np.savetxt(file_psd,p,fmt='%e',delimiter='\t', newline='\r\n')

                counter += 1
                
            except EOFError as e:
                print("error raised")
                break
            except:
                print("exception")
                pass

        self.alive = False
##        file_tt.close()
##        file_psd.close()

##        np.divide(self.arr,counter)

##        np.savetxt(file_ave_psd,self.arr.transpose(),fmt='%e',delimiter='\t', newline='\r\n')
##        file_ave_psd.close()
        self.threadStopped.emit()


class Counter:
    def __init__(self):
       self._index = 0

    def increment(self):
        self._index+=1

    def reset(self):
        self._inde = 0

    @property
    def index(self):
        return self._index

def fill_array(a,res_array,counter, fill_value_start, fill_value_end):
    print(np.shape(res_array))
    for i,idx in enumerate(range(fill_value_start,fill_value_end)):
        res_array[idx] = a[i]
    counter.increment()


def multiply_by_coef(a, counter):
    print(counter.index)
    res = a*counter.index
    counter.increment()
    return res

def main():

    width = 4
    len = 20
    nsamp = 5
    ds = int(len/nsamp)
    total_arr = np.ones((width,len))
    fill_val =0

    for i in range(0,ds):
        arr = np.ones((width,nsamp))*i
        new_fill_val = fill_val + nsamp
        total_arr[:,fill_val:new_fill_val] = arr
        fill_val = new_fill_val
     
    print(total_arr)

    #counter = Counter()
    #arr = np.ones((4,10)) #np.random.randn(4,10)
    #np.apply_along_axis(fill_array,1, arr, res_arr, counter, 2,8)
    #print(arr)
    #print(res)
    
    
if __name__ == '__main__':
  main()

    
    
