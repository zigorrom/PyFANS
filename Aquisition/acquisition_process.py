import sys
import multiprocessing
import visa
import time
from agilent_u2542a import AgilentU2542A, AI_Channels
from multiprocessing import *

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

    a = AcquisitionProcess(data_queue = q, idx = 10,resource = 'ADC')
    a.start()
    a.configure()
    counter = 0
    while counter<600:
        print(q.get())
        counter +=1
    a.stop()
    
    a.join()
    print("joined")

    
    
