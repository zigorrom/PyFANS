import math
from enum import IntEnum, unique
#from n_enum import enum

#RANGE_HANDLERS = ["normal","back_forth","zero_start","zero_start_back_forth"]
#NORMAL_RANGE_HANDLER, BACK_FORTH_RANGE_HANDLER, ZERO_START_RANGE_HANDLER, ZERO_START_BACK_FORTH = RANGE_HANDLERS
@unique
class RANGE_HANDLERS(IntEnum):
   NORMAL_RANGE_HANDLER = 0
   BACK_FORTH_RANGE_HANDLER = 1
   ZERO_START_RANGE_HANDLER = 2
   ZERO_START_BACK_FORTH = 3

def index_to_range_handler_converter(index):
    return RANGE_HANDLERS(index)

class RangeObject:
    def __init__(self, rng = None):
        self._float_range = None
        self.floatRange = rng
        self._range_handler = RANGE_HANDLERS.NORMAL_RANGE_HANDLER
        self._repeats = 1

    @property
    def floatRange(self):
        return self._float_range

    @floatRange.setter
    def floatRange(self,value):
        assert isinstance(value, (float_range, type(None)))
        self._float_range = value

    @property
    def rangeHandler(self):
        return self._range_handler
    
    @rangeHandler.setter
    def rangeHandler(self, value):
        assert isinstance(value, RANGE_HANDLERS)
        self._range_handler = value

    @property
    def rangeRepeats(self):
        return self._repeats

    @rangeRepeats.setter
    def rangeRepeats(self,value):
        assert isinstance(value, int)
        assert value > 0
        self._repeats = value

    def total_iterations(self):
        return self.rangeRepeats * self.floatRange.length

    def copy_object(self):
        rng = None
        if self.floatRange:
            rng = self.floatRange.copy_range()
        ro = RangeObject(rng)
        ro.rangeHandler = self.rangeHandler
        ro.rangeRepeats = self.rangeRepeats
        return ro

    @staticmethod
    def empty_object():
        rng = float_range(0,1)
        ro = RangeObject(rng)
        return ro

    def __iter__(self):
        rng = self.floatRange
        if not rng:
            return None
        if self.rangeHandler == RANGE_HANDLERS.NORMAL_RANGE_HANDLER:
            return normal_range_handler(rng, self.rangeRepeats) #rng.start,rng.stop, rng.step, rng.length, self.rangeRepeats)
        elif self.rangeHandler == RANGE_HANDLERS.BACK_FORTH_RANGE_HANDLER:
            return back_forth_range_handler(rng, self.rangeRepeats)#rng.start,rng.stop, rng.step, rng.length, self.rangeRepeats)
        elif self.rangeHandler == RANGE_HANDLERS.ZERO_START_RANGE_HANDLER:
            return zero_start_range_handler(rng, self.rangeRepeats) #rng.start,rng.stop, rng.step, rng.length, self.rangeRepeats)
        elif self.rangeHandler == RANGE_HANDLERS.ZERO_START_BACK_FORTH:
            return zero_start_back_forth(rng, self.rangeRepeats) #rng.start,rng.stop, rng.step, rng.length, self.rangeRepeats)
    
    

class float_range:
    def __init__(self, start, stop, step = 1, length = -1):
        self.__start = start
        self.__stop = stop
        self.__step = step
        self.__length = length
        self.__calculate_length_step()
      
    def __calculate_length_step(self):
        value_difference = math.fabs(self.__stop - self.__start)
        if self.__length > 1:
            #self.__length = len
            self.__step = value_difference / (self.__length - 1)
        elif self.__length == 1:
            self.__step = 0
        elif self.__step > 0:
            self.__length = math.floor(value_difference / self.__step)
            if self.__length>1:
                self.__step = value_difference / (self.__length - 1)
            else: 
                self.__step = 0
        else:
            raise AttributeError("length or step is not set correctly")
          
    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, value):
        assert isinstance(value, (int, float))
        self.__start = value
        self.__calculate_length_step()

    @property       
    def stop(self):
        return self.__stop

    @stop.setter
    def stop(self, value):
        assert isinstance(value, (int, float))
        self.__stop = value
        self.__calculate_length_step()

    @property
    def step(self):
        return self.__step

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self,value):
        assert isinstance(value,int)
        self.__length = value
        self.__calculate_length_step()

    def copy_range(self):
        rng = float_range(0,0)
        rng.__start = self.start
        rng.__stop = self.stop
        rng.__length = self.length
        rng.__step = self.step
        return rng

POSITIVE_DIRECTION, NEGATIVE_DIRECTION = (1,-1)       
class range_handler():
    def __init__(self, value_range, n_repeats, round_n_digits = -1):
        if not isinstance(value_range, float_range):
            raise TypeError("range parameter is of wrong type!")
        if n_repeats < 1:
            raise ValueError("n_repeats should be greater than one")

        
        self.__round_n_digits = round_n_digits
        self.__range = value_range
        self.__repeats = n_repeats

        self.__direction = POSITIVE_DIRECTION
        self.__comparison_function = self.__positive_comparator

        self.define_direction(self.__range.start,self.__range.stop)
        
    
    @property
    def comparison_function(self):
        return self.__comparison_function
    
    @property
    def number_of_repeats(self):
        return self.__repeats

    @property
    def woking_range(self):
        return self.__range
    
    @property
    def direction(self):
        return self.__direction
    
    def reset(self):
        self.__current_value = self.woking_range.start

     

    def increment_value(self, value_to_increment):
        result = value_to_increment + self.__direction * self.__range.step
        if self.__round_n_digits>0:
            result = round(result,self.__round_n_digits)

        return result
        
    def define_direction(self, start_value, stop_value):
        if stop_value > start_value:
            self.__direction = POSITIVE_DIRECTION
            self.__comparison_function = self.__positive_comparator
        else:
            self.__direction = NEGATIVE_DIRECTION
            self.__comparison_function = self.__negative_comparator

    def __positive_comparator(self, val1,val2):
        if val2 >= val1:
            return True
        return False

    def __negative_comparator(self,val1,val2):
        if val2 <= val1:
            return True
        return False

    def __iter__(self):
        return self

class normal_range_handler(range_handler):
    def __init__(self, rng, repeats):# start,stop,step=1,len=-1,repeats = 1):
        super().__init__(rng, repeats,6) #float_range(start,stop,step,len),repeats,6)
        self.__current_value = self.woking_range.start
        self.__current_round = 0 

    def __next__(self):
        if not self.comparison_function(self.__current_value, self.woking_range.stop):
            self.__current_round += 1
            self.reset()
        
        if self.__current_round >= self.number_of_repeats:
            raise StopIteration        

        #print("current round: {0}".format(self.__current_round))
        value = self.__current_value
        self.__current_value = self.increment_value(value)
        return value

class back_forth_range_handler(range_handler):
    def __init__(self, rng, repeats):# start,stop,step=1,len=-1,repeats = 1):
        super().__init__(rng, repeats,6)#(float_range(start,stop,step,len), repeats, 6) 
        self.__current_value = start
        self.__current_round = 0
        self.__left_value = self.woking_range.start
        self.__right_value = self.woking_range.stop
        self.__change_dir_point = 0

        
    def __next__(self):
        if not self.comparison_function(self.__current_value, self.__right_value):
            value = self.__left_value
            self.__left_value = self.__right_value
            self.__right_value = value
            self.define_direction(self.__left_value,self.__right_value)
            self.__change_dir_point += 1
            if self.__change_dir_point == 2:
                self.__change_dir_point = 0
                self.__current_round += 1
                self.reset()
                

        if self.__current_round >= self.number_of_repeats:
            raise StopIteration        

        value = self.__current_value
        if self.__change_dir_point == 1:
            value = self.increment_value(self.__current_value)
            self.__current_value = self.increment_value(value)
        else:
            self.__current_value = self.increment_value(value)
            
        
        return value

class zero_start_range_handler(range_handler):
    def __init__(self, rng, repeats):# start,stop,step=1,len=-1,repeats = 1):
        assert isinstance(rng, float_range)
        if rng.start * rng.stop >= 0:
            raise ValueError("Zero start range handler interval should cross zero")
        super().__init__(rng, repeats,6)#(float_range(start,stop,step,len), repeats, 6)


    def __next__(self):
        pass

class zero_start_back_forth(range_handler):
    def __init__(self, rng, repeats):# start,stop,step=1,len=-1,repeats = 1):
        assert isinstance(rng, float_range)
        if rng.start * rng.stop >= 0:
            raise ValueError("Zero start range handler interval should cross zero")
        return super().__init__(rng, repeats,6)#(float_range(start,stop,step,len), repeats, 6) 


if __name__ == "__main__":
    ro = RangeObject(None)
    ro.floatRange = float_range(0,1,length = 11)
    ro.rangeRepeats = 2
    ro.rangeHandler = RANGE_HANDLERS.BACK_FORTH_RANGE_HANDLER
    for i in ro:
        print(i)
    #nr = normal_range_handler(-2,2,step = 0.1)
    #for i in nr:
    #    print(i)

    #pass