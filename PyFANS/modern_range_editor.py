import sys
import numpy as np

from enum import Enum
from PyQt4 import QtCore

class HandlersEnum(Enum):
    normal = 0
    back_forth = 1
    zero_start = 2
    zero_start_back_forth = 3

class RangeInfo(QtCore.QObject):
    def __init__(self, **kwargs):
        """
        Initializes range info:

        """
        super().__init__()
        self._start = kwargs.get("start", None)
        self._end = kwargs.get("end", None)
        self._step = kwargs.get("step", None)
        self._log_scale = kwargs.get("log_scale", False)
        self._count = kwargs.get("count", 0)
        self._handler = kwargs.get("handler", HandlersEnum.normal)
        self._repeats = kwargs.get("repeats", 1)
        
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

    @log_scale.setter
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

    def __str__(self):
        strRepresentation = """
        RangeInfo:
           start:\t{0}
           end:\t{1}
           step:\t{2}
           count:\t{3}
        """.format(self.start, self.end, self.step, self.count)
        return strRepresentation
    

class RangeHandler(QtCore.QObject):
    def __init__(self, rangeInfo):
        super().__init__()
        self._rangeInfo = rangeInfo
        self._currentValue = None
        self._currentCount = 0

    @property
    def rangeInfo(self):
        return self._rangeInfo

    @property
    def currentValue(self):
        return self._currentValue

    @currentValue.setter
    def currentValue(self,value):
        self._currentValue = value

    @property
    def currentCount(self):
        return self._currentCount

    @currentCount.setter
    def currentCount(self, value):
        self._currentCount = value

    def incrementCount(self):
        self._currentCount += 1

    def decrementCount(self):
        self._currentCount -= 1

    def __iter__(self):
        self.reset()
        return self

    def __next__(self):
        return self.next()
        # try:
        #     return iter(self.iterator())
        # except TypeError as te:
        #     print ("some_object is not iterable")
        #     raise

    def reset(self):
        pass

    def next(self):
        raise StopIteration()

    # def iterator(self):
    #     raise NotImplementedError()



class NormalRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)

    def continueCondition(self):
        return self.currentCount < self.rangeInfo.end

    def next(self):
        if self.continueCondition():
            current, self.currentValue = self.currentValue, self.currentValue + self.rangeInfo.step
        
        else:
            raise StopIteration()
            
        # if self.currentCount < self.rangeInfo.count:
        #     current, self.currentValue = self.currentValue, self.currentValue + self.rangeInfo.step
        #     return current
        # else:
        #     raise StopIteration()

    # def iterator(self):
    #     rngInfo = self.rangeInfo
    #     currentValue = rngInfo.start

        

    #     # for repeat in range(rngInfo.repeats):
    #     #     for i in range(rngInfo.count):
    #     #         currentValue.handler 
    #     print("From range info")
    #     print(rngInfo)
    #     if rngInfo.log_scale:
    #         start = np.log10(rngInfo.start)
    #         end = rngInfo.end
                 


    #     else:
    #         return np.linspace(rngInfo.start, rngInfo.end, rngInfo.count, endpoint = True)
            
        
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
    def createHandler(rangeInfo):
        if not isinstance(rangeInfo, RangeInfo):
            raise TypeError("rangeInfo has wrong data type")

        if rangeInfo.handler is HandlersEnum.normal:
            return NormalRangeHandler(rangeInfo)

        elif rangeInfo.handler is HandlersEnum.back_forth:
            return BackAndForthHandler(rangeInfo)

        elif rangeInfo.handler is HandlersEnum.zero_start:
            return ZeroStartRangeHandler(rangeInfo)

        elif rangeInfo.handler is HandlersEnum.zero_start_back_forth:
            return ZeroStartBackAndForthRangeHandler(rangeInfo)

        else:
            raise ValueError("handler is not specified in range info")





def test_smth():
    class firstn(object):
        def __init__(self, n):
            self.n = n
            self.num, self.nums = 0, []

        def __iter__(self):
            return self

        # Python 3 compatibility
        def __next__(self):
            return self.next()

        def next(self):
            if self.num < self.n:
                cur, self.num = self.num, self.num+1
                return cur
            else:
                raise StopIteration()

    sum_of_first_n = sum(firstn(1000000))
    print(sum_of_first_n)
    sum_of_first_n = sum(firstn(1000))
    print(sum_of_first_n)


def test_range():
    ri = RangeInfo(start = -10, end = 10, count = 100, handler = HandlersEnum.normal)
    print(ri)
    rh = RangeHandlerFactory.createHandler(ri)
    print(rh)
    lst = list(rh)
    print(lst)

if __name__ == "__main__":
    sys.exit(test_range())
    # test_smth()

    
