import multiprocessing
from multiprocessing import Process

class AquisitionProcess(Process):
    def __init__(self, queue):
        Process.__init__(self)
        self.exit = Event()
        self.queue = queue

    def daq_openPort(self):
        pass

    def daq_closePort(self):
        pass

    def run(self):
        pass

    

    
    
