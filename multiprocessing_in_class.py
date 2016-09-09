from multiprocessing import Process,Queue

class DAQ:
    def __init__(self,queue,idx):
        self.queue = queue
        self.idx = idx
        self.proc = Process(target = self.run)
        
    def run(self):
         self.queue.put(self.return_name())

    def start(self):
        self.proc.start()

    def test(self):
        pass

    def stop(self):
        self.proc.join()
        

    
        
    def return_name(self):
        ## NOTE: self.name is an attribute of multiprocessing.Process
        return "Process idx=%s is called '%s'" % (self.idx, self.proc.name)



if __name__ == "__main__":
    q = Queue()
    idx = 10
    d = DAQ(q,idx)
    d.start()
    print("started")
    d.test()
    print("passed")
    d.stop()
    print("stopped")
    print ("RESULT: %s" % q.get())
    
    
