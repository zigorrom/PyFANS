import sys
import numpy as np
from PyQt4 import QtCore

class RangeInfo(QtCore.QObject):
    def __init__(self, **kwargs):
        super().__init__()
        self._start = kwargs.get("start", None)
        self._end = kwargs.get("stop", None)
        self._step = kwargs.get("step", None)
        self._log_scale = kwargs.get("log_scale", False)
        self._count = kwargs.get("count",None)
        self._handler = kwargs.get("handler", None)
        self._repeats = kwargs.get("repeats", None)
        
    # when handler = zero start -> we start from zero -> move to start ->move to zero -> move to end
    # when handler zero start back and forth -> repeat previous statement in reverse direction


    # def __calculate_step(self, start, end, count, end_point = True):
    #     try:
    #         step = 0

    #         if count < 1:
    #             count = 0
    #         elif count < 2:
    #             count = 1
    #         else:
    #             if end_point:
    #                 rnd = end
    #             else:
    #                 pass
            
    #     except:
    #         raise
    
    # def __calculate_count(self, start, end, step, end_point = True):
    #     pass

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value

    @property
    def log_scale(self):
        return self._log_scale

    @log_scale.state
    def log_scale(self,value):
        self._log_scale = value


    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value

    @property
    def handler(self):
        return self._handler

    @handler.setter
    def handler(self, value):
        self._handler = value

    @property
    def repeats(self):
        return self._repeats

    @repeats.setter
    def repeats(self, value):
        self._repeats = value


class RangeHandler(QtCore.QObject):
    def __init__(self, rangeInfo):
        super().__init__()
        self._rangeInfo = rangeInfo

    @property
    def rangeInfo(self):
        return self._rangeInfo

    def __iter__(self):
        try:
            return iter(self.iterator())
        except TypeError as te:
            print ("some_object is not iterable")
            raise

    def iterator(self):
        raise NotImplementedError()

class NormalRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)

    def iterator(self):
        rngInfo = self.rangeInfo
        if rngInfo.log_scale:
            pass

        else:
            return np.linspace(rngInfo.start, rngInfo.stop, rngInfo.count, endpoint = True)
        
class BackAndForthHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)

    def iterator(self):
        pass

class ZeroStartRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)

    def iterator(self):
        pass


class ZeroStartBackAndForthRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)

    def iterator(self):
        pass

class CustomRangeHandler(RangeHandler):
    pass

    
class RangeHandlerFactory(QtCore.QObject):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def createHandler(self, rangeInfo):
        pass






def test_range():
    pass

if __name__ == "__main__":
    sys.exit(test_range())


    
