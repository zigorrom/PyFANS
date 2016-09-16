import sys
import multiprocessing
import visa
import time
from agilent_u2542a import AgilentU2542A, AI_Channels
from multiprocessing import *

class ProcessingProcess(Process):
    def __init__(self,input_queue, output_queue):
        super(ProcessingProcess,self).__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.exit = Event()

    def stop(self):
        self.exit.set()
        
    def run(self):
        try:
            while not self.exit.is_set():
                val = input_queue.get()
                l = len(val)
                self.output_queue.put(l)
        except:
                raise
        finally:
                 pass   
        
            

class AcquisitionProcess(Process):
    def __init__(self, idx, data_queue,  resource):
        super(AcquisitionProcess,self).__init__()
        self.exit = Event()
        self.idx = idx
        self.queue = data_queue
        self.resource = resource

    def stop(self):
        self.exit.set()

    def configure(self):
        print("configured")

    def return_name(self):
        return "Process idx=%s is called '%s'" % (self.idx, self.name)
    
    def run(self):
        d = AgilentU2542A(self.resource)
        init_time = time.time()
        try:
            d.daq_reset()
            d.daq_setup(500000,50000)
            d.daq_enable_channels([AI_Channels.AI_1,AI_Channels.AI_2,AI_Channels.AI_3,AI_Channels.AI_4])
            d.daq_run()
            while not self.exit.is_set():
                try:
                    if d.daq_is_data_ready():
                        t = time.time()-init_time
                        data = d.daq_read_data()
                        self.queue.put((t,data))
                except:
                    pass
        except:
            raise
        finally:
            d.daq_stop()
            d.daq_reset()
            



if __name__ == '__main__':
    q = Queue()
##    rq = Queue()
    a = AcquisitionProcess(data_queue = q, idx = 10,resource = 'ADC')
##    p = ProcessingProcess( input_queue = q,output_queue = rq)
    a.start()
##    p.start()
    a.configure()
    counter = 0
    while counter<1000:
        
        print(q.get())
        print("\n\r")
##        print(rq.get())
        counter +=1
    a.stop()
##    p.stop()
    
    
    a.join()
##    p.join()
    print("joined")

    
    
