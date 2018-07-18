import sys
import math
import numpy as np

from enum import Enum
from PyQt4 import QtCore

class HandlersEnum(Enum):
    normal = 0
    back_forth = 1
    center_start = 2
    center_start_back_forth = 3

class RangeInfo(QtCore.QObject):
    def __init__(self, **kwargs):
        """
        Initializes range info:

        """
        super().__init__()
        self._start = kwargs.get("start", 0)
        self._end = kwargs.get("end", 0)
        self._step = kwargs.get("step", 0)
        

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
    
class CenteredRangeInfo(RangeInfo):
    def __init__(self,**kwargs):
        self._span = span = kwargs.get("span", None)
        self._center = center = kwargs.get("center", None)
        start = kwargs.setdefault("start",0)
        end = kwargs.setdefault("end", 0)

        if span is not None and center is not None:
            kwargs["start"] = center - span/2
            kwargs["end"] = center + span/2
         

        super().__init__(**kwargs)
    
    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        self._center = value

    @property
    def span(self):
        return self._span

    @span.setter
    def span(self, value):
        self._span = value

    def __str__(self):
        strRepresentation = """
        CenteredRangeInfo:
           start:\t{0}
           end:\t{1}
           step:\t{2}

        """.format(self.start, self.end, self.step)
        return strRepresentation

class CustomRangeInfo(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        if isinstance(args[0],(tuple, list)):
            self._list_of_values = list_of_values
        elif isinstance(args,(tuple, list)):
            if all(isinstance(x, (int,float)) for x in args):
                self._list_of_values = args
            else:
                self._list_of_values = list()    
        else:
            self._list_of_values = list()

    @property
    def values(self):
        return self._list_of_values

    def __getitem__(self, idx):
        return self._list_of_values[idx]

    def __setitem__(self, idx, value):
        self._list_of_values[idx] = value

    def __len__(self):
        return len(self._list_of_values)

    def __str__(self):
        return self._list_of_values.__str__()

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

    def checkHitRangeEdge(self, direction, range_edge, current_value):
        if direction >= 0:
            if current_value <= range_edge:
                return False
        else:
            if current_value >= range_edge:
                return False

        return True
        



        # if math.copysign(1,range_edge - current_value) == direction:
        #     return False
        # else:
        #     return True


    def checkCondition(self):   
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def next(self):
        if self.checkCondition():
            current = self.currentValue
            self.nextValue()
            self.incrementCount()
            self.incrementTotalIterations()
            return current
        else:
            raise StopIteration()

class NormalRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, RangeInfo):
            raise TypeError("This range handler supports only RangeInfo ranges")

        super().__init__(rangeInfo)

    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True
                    
            elif not self.checkHitRangeEdge(self.currentDirection, self.rangeInfo.end, self.currentValue):
                return True
            
            elif self.__next_repetition():
                return True
            else:
                return False

            # elif self.currentDirection >= 0:
            #     if self.currentValue <= self.rangeInfo.end:
            #         return True
            #     elif self.__next_repetition():
            #         return True
            #     else:
            #         return False

            # else:
            #     if self.currentValue >= self.rangeInfo.end:
            #         return True
            #     elif self.__next_repetition():
            #         return True
            #     else:
            #         return False
             
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
        if not isinstance(rangeInfo, RangeInfo):
            raise TypeError("This range handler supports only RangeInfo ranges")

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
            
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True
            
            elif not self.checkHitRangeEdge(self.currentDirection, end_value, self.currentValue):
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
        if self.currentRepeat>0:
            self.nextValue()

        if self.currentRepeat < self.rangeInfo.repeats:
            return True

        return False
  
class CenterStartEndRangeHandler(RangeHandler):
    LEFT_SECTION, RIGHT_SECTION = SECTIONS = ("left", "right")

    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, CenteredRangeInfo):
            raise TypeError("This range handler supports only CenteredRangeInfo ranges")

        super().__init__(rangeInfo)
        self._current_section = self.LEFT_SECTION
        
    
    @property
    def currentSection(self):
        return self._current_section

    @currentSection.setter
    def currentSection(self, value):
        self._current_section = value
    
    def __condition_function__(self, current_value, start, end, section, direction):
        if not self.checkHitRangeEdge(direction, end, current_value):
            return True

        elif self.__change_to_right_section():
            return True

        elif self.__next_repetition():
            return True
        
        return False

        
    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True

            elif self.currentSection == self.LEFT_SECTION:
                return self.__condition_function__(self.currentValue,self.rangeInfo.center, self.rangeInfo.start, self.currentSection, self.currentDirection)
            
            elif self.currentSection == self.RIGHT_SECTION:
                return self.__condition_function__(self.currentValue,self.rangeInfo.center, self.rangeInfo.end, self.currentSection, self.currentDirection)

            else:
                return False

        return False

    def __change_to_right_section(self):
        if self.currentSection == self.LEFT_SECTION:
            self.currentSection = self.RIGHT_SECTION
            self.currentValue = self.rangeInfo.center
            self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.end)
            # self.nextValue()
            return True

        return False

    def __estimate_direction(self, start, end):
        return math.copysign(1, end - start)

    def __initialize_repetition(self):
        self.currentCount = 0
        self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.start)
        self.currentValue = self.rangeInfo.center
        self.currentSection = self.LEFT_SECTION

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


class CenterStartEndBackForthRangeHandler(RangeHandler):
    LEFT_SECTION, RIGHT_SECTION = SECTIONS = ("left", "right")

    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, CenteredRangeInfo):
            raise TypeError("This range handler supports only CenteredRangeInfo ranges")

        super().__init__(rangeInfo)
        self._current_section = self.LEFT_SECTION
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

    @property
    def currentSection(self):
        return self._current_section

    @currentSection.setter
    def currentSection(self, value):
        self._current_section = value
    
    def __condition_function__(self, current_value, start, end, section, direction):
        if not self.checkHitRangeEdge(direction, end, current_value):
            return True

        elif self.changeDirection():
            return True

        elif self.__change_to_right_section():
            
            return True

        elif self.__next_repetition():
            return True
        
        return False

        
    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True

            elif self.currentSection == self.LEFT_SECTION:
                start_value = self.rangeInfo.center
                end_value = self.rangeInfo.start
                if self.directionChanged:
                    start_value, end_value = end_value, start_value

                return self.__condition_function__(self.currentValue,start_value, end_value, self.currentSection, self.currentDirection)
            
            elif self.currentSection == self.RIGHT_SECTION:
                start_value = self.rangeInfo.center
                end_value = self.rangeInfo.end
                if self.directionChanged:
                    start_value, end_value = end_value, start_value

                return self.__condition_function__(self.currentValue,start_value, end_value, self.currentSection, self.currentDirection)

            else:
                return False

        return False

    def __change_to_right_section(self):
        if self.currentSection == self.LEFT_SECTION:
            self.currentSection = self.RIGHT_SECTION
            # self.currentValue = self.rangeInfo.center
            self.directionChanged = False
            self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.end)
            self.nextValue()
            self.nextValue()
            return True

        return False

    def __estimate_direction(self, start, end):
        return math.copysign(1, end - start)

    def __initialize_repetition(self):
        self.currentCount = 0
        self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.start)
        self.currentValue = self.rangeInfo.center
        self.currentSection = self.LEFT_SECTION
        self.directionChanged = False

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()

        if self.currentRepeat>0:
            self.nextValue()

        if self.currentRepeat < self.rangeInfo.repeats:
            return True
        
        return False

class CustomRangeHandler(QtCore.QObject):
    def __init__(self, rangeInfo):
        super().__init__()
        self._rangeInfo = rangeInfo
        self._totalIterationsMade = 0
     
    @property
    def totalIterationsMade(self):
        return len(self._rangeInfo)

    @property
    def rangeInfo(self):
        return self._rangeInfo

    def __len__(self):
        return self.totalIterationsMade

    def __iter__(self):
        return iter(self.rangeInfo.values)
        
class RangeHandlerFactory(QtCore.QObject):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def createHandler(rangeInfo):
        if isinstance(rangeInfo, RangeInfo):
            if rangeInfo.handler is HandlersEnum.normal:
                return NormalRangeHandler(rangeInfo)

            elif rangeInfo.handler is HandlersEnum.back_forth:
                return BackAndForthHandler(rangeInfo)

            elif rangeInfo.handler is HandlersEnum.center_start:
                return CenterStartEndRangeHandler(rangeInfo)
                #return ZeroStartRangeHandler(rangeInfo)

            elif rangeInfo.handler is HandlersEnum.center_start_back_forth:
                return CenterStartEndBackForthRangeHandler(rangeInfo)
                #return ZeroStartBackAndForthRangeHandler(rangeInfo)

            else:
                raise ValueError("handler is not specified in range info")

        elif isinstance(rangeInfo, CustomRangeInfo):
            return CustomRangeHandler(rangeInfo)

        else:
            raise TypeError("rangeInfo has wrong data type")




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
    ri = RangeInfo(start=-3, end=3, step=1, handler=HandlersEnum.normal, repeats=2)
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
    
    print("Center start Handler")
    ri = CenteredRangeInfo(start=-3, end=3, center=1, step=1, handler=HandlersEnum.center_start, repeats=2)
    rh = RangeHandlerFactory.createHandler(ri)
    lst = list(rh)
    print(lst)
    print(rh.totalIterationsMade)

    print("Center start back forth Handler SPAN")
    ri = CenteredRangeInfo(span = 6, center=1, step=1, handler=HandlersEnum.center_start_back_forth, repeats=2)#start=-2, end=2
    rh = RangeHandlerFactory.createHandler(ri)
    lst = list(rh)
    print(lst)
    print(rh.totalIterationsMade)

    print("Center start back forth Handler START-STOP")
    ri = CenteredRangeInfo(start=-3, end=3, center=1, step=1, handler=HandlersEnum.center_start_back_forth, repeats=2)#start=-2, end=2
    rh = RangeHandlerFactory.createHandler(ri)
    lst = list(rh)
    print(lst)
    print(rh.totalIterationsMade)


    print("Custom range handler")
    ri = CustomRangeInfo(1,2,3,4,5)
    rh = RangeHandlerFactory.createHandler(ri)
    lst = list(rh)
    print(lst)
    print(rh.totalIterationsMade)


if __name__ == "__main__":
    sys.exit(test_range())
    # test_smth()

    
