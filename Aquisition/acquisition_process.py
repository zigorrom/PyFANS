import sys
import numpy as np
from PyQt4 import QtCore
from multiprocessing import Process, Event, JoinableQueue
from agilent_u2542a import *
from scipy.signal import periodogram

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

    
        
    def run(self):
        sys.stdout = open("log.txt", "w")
        data_queue = self.data_queue
        
        try:
            d = AgilentU2542A(self.visa_resource)
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
                        block = {"t": t,
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
                print("data received")
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

def main():
    pass
    
    
if __name__ == '__main__':
  main()

    
    
