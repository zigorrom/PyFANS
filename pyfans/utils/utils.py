import os
import sys
from queue import Queue
from PyQt4 import QtCore


def check_if_script_executed_with_console():
    executable = sys.executable
    basename = os.path.basename(executable)
    filename, file_extention = os.path.splitext(basename)
    if filename == "pythonw":
        return False
    else:
        return True


def open_folder_in_explorer(folder):
    print("opening folder")
    request = 'explorer "{0}"'.format(folder)#self._settings.working_directory)
    print(request)
    os.system(request)

def open_folder_with_file_selected(filename):
    print("opening folder")
    request = 'explorer /select, "{0}"'.format(filename)#self._settings.working_directory)
    print(request)
    os.system(request)


# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!
class WriteStream(object):
    def __init__(self,queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)
        sys.stdout.write(text)

    def flush(self):
        sys.stdout.flush()

# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal 
class MyReceiver(QtCore.QObject):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self,queue,*args,**kwargs):
        QtCore.QObject.__init__(self,*args,**kwargs)
        self.queue = queue

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)



