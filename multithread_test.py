from multiprocessing import Process, Queue
class Processor(Process):

    def __init__(self, queue, idx):
        super(Processor, self).__init__()
        self.queue = queue
        self.idx = idx

    def return_name(self):
        ## NOTE: self.name is an attribute of multiprocessing.Process
        return "Process idx=%s is called '%s'" % (self.idx, self.name)

    def run(self):
        self.queue.put(self.return_name())

## Create a list to hold running Processor objects
processes = list()

if __name__ == "__main__":

    q = Queue()
    for i in range(0,5):
        p=Processor(queue=q, idx=i)
        processes.append(p)
        p.start()
    for proc in processes:
        proc.join()
        ## NOTE: You cannot depend on the results to queue / dequeue in the
        ## same order
        print ("RESULT: %s" % q.get())
