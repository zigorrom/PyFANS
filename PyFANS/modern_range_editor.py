import sys
import math
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
        #self._count = kwargs.get("count", 0)
        self._handler = kwargs.get("handler", HandlersEnum.normal)
        self._repeats = kwargs.get("repeats", 1)
        
    # when handler = zero start -> we start from zero -> move to start ->move to zero -> move to end
    # when handler zero start back and forth -> repeat previous statement in reverse direction

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

    # @property
    # def count(self):
    #     return self._count

    # @count.setter
    # def count(self, value):
    #     self._count = value

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
        """.format(self.start, self.end, self.step)
        return strRepresentation
    

    

class RangeHandler(QtCore.QObject):
    def __init__(self, rangeInfo):
        super().__init__()
        self._rangeInfo = rangeInfo
        self._currentValue = None
        self._currentCount = 0
        self._currentDirection = 1
        self._currentRepeat = 0
        self._totalIterationsMade = 0

    @property
    def totalIterationsMade(self):
        return self._totalIterationsMade

    def incrementTotalIterations(self):
        self._totalIterationsMade+=1

    @property
    def currentDirection(self):
        return self._currentDirection

    @currentDirection.setter
    def currentDirection(self, value):
        self._currentDirection = value

    def toggleDirection(self):
        self.currentDirection = -self.currentDirection

    @property
    def currentRepeat(self):
        return self._currentRepeat

    @currentRepeat.setter
    def currentRepeat(self, value):
        self._currentRepeat = value

    def incrementRepeat(self):
        self._currentRepeat += 1 #math.copysign(1, self._currentDirection)

    def decrementRepeat(self):
        self._currentRepeat -= 1#math.copysign(1, self._currentDirection)


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
        self._currentCount += 1 #math.copysign(1, self._currentDirection)

    def decrementCount(self):
        self._currentCount -= 1#math.copysign(1, self._currentDirection)

    def nextValue(self):
        self._currentValue += math.copysign(self.rangeInfo.step, self._currentDirection)
        return self.currentValue

    def prevValue(self):
        self._currentValue -= math.copysign(self.rangeInfo.step, self._currentDirection)
        return self.currentValue

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
    def checkCondition(self):   
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def next(self):
        if self.checkCondition():
            current = self.currentValue
            self.nextValue()
            self.incrementTotalIterations()
            return current
        else:
            raise StopIteration()

    


class NormalRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)

    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            if self.currentDirection >= 0:
                if self.currentValue <= self.rangeInfo.end:
                    return True
                elif self.__next_repetition():
                    return True
                else:
                    return False

            else:
                if self.currentValue >= self.rangeInfo.end:
                    return True
                elif self.__next_repetition():
                    return True
                else:
                    return False
             
        return False

    def __initialize_repetition(self):
        self.currentCount = 0
        self.currentDirection = math.copysign(1, self.rangeInfo.end - self.rangeInfo.start)
        self.currentValue = self.rangeInfo.start

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()
        if self.currentRepeat < self.rangeInfo.repeats:
            return True

        return False



    
            
      
class BackAndForthHandler(RangeHandler):
    def __init__(self, rangeInfo):
        super().__init__(rangeInfo)
        self._directionChanged = False

    @property
    def directionChanged(self):
        return self._directionChanged

    @directionChanged.setter
    def directionChanged(self, value):
        self._directionChanged = value

    def changeDirection(self):
        prev_value = self.directionChanged
        self.directionChanged = True
        self.toggleDirection()
        self.nextValue()
        self.nextValue()
        if not prev_value:
            return True
        
        return False

    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            start_value = self.rangeInfo.start
            end_value = self.rangeInfo.end
            
            if self.directionChanged:
                start_value, end_value = end_value, start_value

            if self.currentDirection >= 0:
                if self.currentValue <= end_value:
                    return True

                elif self.changeDirection():
                    return True

                elif self.__next_repetition():
                    return True

                else:
                    return False

            else:
                if self.currentValue >= end_value:
                    return True
                
                elif self.changeDirection():
                    return True
   
                elif self.__next_repetition():
                    return True
                else:
                    return False
             
        return False

    def __initialize_repetition(self):
        self.currentCount = 0
        self.directionChanged = False
        self.currentDirection = math.copysign(1, self.rangeInfo.end - self.rangeInfo.start)
        self.currentValue = self.rangeInfo.start

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()
        if self.currentRepeat < self.rangeInfo.repeats:
            return True

        return False

    



    

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
    ri = RangeInfo(start = 10, end = -10, step = 1, handler = HandlersEnum.normal, repeats = 3)
    print(ri)
    print("NORMAL HANDLER")
    rh = RangeHandlerFactory.createHandler(ri)
    lst = list(rh)
    print(lst)
    print(rh.totalIterationsMade)

    print("Back Forth HANDLER")
    ri.handler = HandlersEnum.back_forth
    ri.repeats = 2
    rh = RangeHandlerFactory.createHandler(ri)
    lst = list(rh)
    print(lst)
    print(rh.totalIterationsMade)
    

if __name__ == "__main__":
    sys.exit(test_range())
    # test_smth()

    
