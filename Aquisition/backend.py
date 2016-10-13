import subprocess, math

import numpy as np
from PyQt4 import QtCore

class DAQthread(QtCore.QThread):
    threadStarted = QtCore.pyqtSignal()
    threadStopped = QtCore.pyqtSignal()
    threadProgressChanged = QtCore.pyqtSignal()
    threadTaskDone = QtCore.pyqtSignal()

    def __init__(self,data_storage, parent = None):
        super().__init__(parent)
        self.data_storage = data_storage
        self.alive = False
        self.process = None

    def process_start(self):
        pass

    def process_stop(self):
        pass

    def process_terminate(self):
        pass

    def enqueue_task(self):
        pass
    


def main():
    pass

if __name__ == "__main__":
    main()
