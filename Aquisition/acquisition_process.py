import sys
import multiprocessing
import visa
import time
import os
from agilent_u2542a import AgilentU2542A, AI_Channels
from multiprocessing import *



class AcquisitionProcess(Process):
    def __init__(self, idx, data_queue,  resource):
        super(AcquisitionProcess,self).__init__()
        
        self.exit = Event()
        self.idx = idx
        self.queue = data_queue
        self.resource = resource
        sys.stdout = open(str(os.getpid()) + ".txt", "w")

    def stop(self):
        self.exit.set()

    def configure(self):
        print("configured")

    def return_name(self):
        return "Process idx=%s is called '%s'" % (self.idx, self.name)
    
    def run(self):
        d = AgilentU2542A(self.resource)
        init_time = time.time()
        counter = 0
        try:
            d.daq_reset()
            d.daq_setup(500000,50000)
            d.daq_enable_channels([AI_Channels.AI_1,AI_Channels.AI_2,AI_Channels.AI_3,AI_Channels.AI_4])
            d.daq_run()
            print("started")
            while (not self.exit.is_set()) and counter < 100:
                try:
                    if d.daq_is_data_ready():
                        print("data ready")
                        counter += 1
                        t = time.time()-init_time
                        data = d.daq_read_data()
                        self.queue.put((t,data))
                except:
                    print("exception")
                    self.stop()
                    counter = 100
                
                    
        except:
            pass
        finally:
            d.daq_stop()
            d.daq_reset()
            



if __name__ == '__main__':
    q = Queue()

    a = AcquisitionProcess(data_queue = q, idx = 10,resource = 'ADC')

    a.start()

    a.configure()
    counter = 0

    
    while True:
        try:
            print("before get")
            print(q.get(timeout=10))
        
            print("after get\n\r")

            counter +=1
            
        except:
            print("Exception")
            break

    print ("loop is over")    
    a.stop()
    a.terminate()
    a.join()

    print("joined")

    
    
