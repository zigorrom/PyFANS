import os
from PyQt4 import QtCore

class SoundPlayer(QtCore.QRunnable):
    def __init__(self, filename):
        self._filename = filename
        super().__init__()

    @QtCore.pyqtSlot()
    def run(self):
        from playsound import playsound
        if os.path.isfile(self._filename):
            playsound(self._filename)
