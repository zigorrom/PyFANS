import sys
from PyQt4 import QtCore

class RangeInfo(QtCore.QObject):
    def __init__(self, **kwargs):
        super().__init__()
        self._start = kwargs.get("start", None)
        self._end = kwargs.get("stop", None)
        self._step = kwargs.get("step", None)
        self._count = kwargs.get("count",None)
        self._handler = kwargs.get("handler", None)

def test_range():
    pass

if __name__ == "__main__":
    sys.exit(test_range())


    
