

#name, priority, range

# for key, value in sorted(mydict.iteritems(), key=lambda (k,v): (v,k)):
#     print "%s: %s" % (key, value)

from io import StringIO
NAME_OPTION = "name"
PRIORITY_OPTION = "priority"
RANGE_OPTION = "rang"

class ParameterItem:
    def __init__(self, name, **kwargs):
        self._name = name
        self._priority_level = kwargs.setdefault(PRIORITY_OPTION)
        self._range_handler = kwargs.setdefault(RANGE_OPTION, None)

    @property
    def priority_level(self):
        return self._priority_level

    @priority_level.setter
    def priority_level(self, value):
        self._priority_level = value

    @property
    def name(self):
        return self._name

    @property
    def range_handler(self):
        return self._range_handler
   
    @range_handler.setter
    def range_handler(self, value):
        self._range_handler = value

    def __str__(self):
        return "Name: {0}; Level: {1}; Range: {2}".format(self.name, self.priority_level, self.range_handler)

class ParamGenerator(object):
    def __init__(self, *args, **kwargs):
        self._all_params = []
        self.clear()
        self.opts = kwargs
        #self._max_priority_level = 0
        #self._total_iterations = 1
        self.populate_params(*args, **kwargs)
    
    def populate_params(self, *args, **kwargs):
        for item in args:
            self.append_parameter(item)
 

    def append_parameter(self, parameter_item, **kwargs):
        if isinstance(parameter_item, str):
            parameter_item = ParameterItem(parameter_item, **kwargs)
        if isinstance(parameter_item, ParameterItem):
            parameter_item.priority_level = self._max_priority_level
            self._max_priority_level += 1
            self._all_params.append(parameter_item) 
            try:
                self._total_iterations *= len(parameter_item.range_handler)
            except TypeError:
                #self._total_iterations *= 1
                pass
            return parameter_item
        else:
            raise TypeError("Unexpected parameter_item type")

    
    def clear(self):
        self._all_params.clear()
        self._max_priority_level = 0
        self._total_iterations = 1
        self._current_index = 0

    @property
    def parameter_items(self):
        return self._all_params

    @property
    def current_index(self):
        return self._current_index

    def __iter__(self):
        self._current_index = 0
        return self.build_generator()

    def build_generator(self):
        return self.recursive_level_iteration(0, **self.opts)      
        
    def recursive_level_iteration(self, level, **kwargs):
        if self._max_priority_level == 0:
            return None
        current_level_parameters = self._all_params[level]
        try:
            for value in current_level_parameters.range_handler:
                kwargs[current_level_parameters.name] = value
                if level < self._max_priority_level-1:
                    yield from self.recursive_level_iteration(level+1, **kwargs)
                else:
                    yield kwargs
                    self._current_index += 1

        except TypeError:
            kwargs[current_level_parameters.name] = current_level_parameters.range_handler
            if level < self._max_priority_level-1:
                yield from self.recursive_level_iteration(level+1, **kwargs)
            else:
                yield kwargs
                self._current_index += 1
                
            

    def __str__(self):
        sio = StringIO()
        sio.write("ParamGenerator:\n")
        for item in iter(self._all_params):
            sio.write(str(item))
            sio.write("\n")
        sio.write("Total iterations: {0}".format(self.total_iterations))
        return sio.getvalue()
    
    def __getitem__(self, i):
        if isinstance(i, int):
            return self._all_params[i]
        else:
            raise IndexError()

    @property
    def total_iterations(self):
        return self._total_iterations


def dummy_function(transistor, temperature, drain_source_voltage, gate_source_voltage, *args, **kwargs):
    print("t:{0}-T:{1}-Vds:{2}-Vgs:{3}".format(transistor, temperature, drain_source_voltage, gate_source_voltage))


if __name__ == "__main__":
    m = ParamGenerator(test_param = False)
    m.append_parameter("temperature", rang = [1,2,3,4])
    m.append_parameter("transistor", rang = [1,2,3])
    m.append_parameter(ParameterItem("drain_source_voltage", rang = None)) #[1,2,3,4]))
    m.append_parameter(ParameterItem("gate_source_voltage", rang = [1]))
    #m.recursive_level_iteration(0)
    for idx, item in enumerate(m):
        print("IDX: {0}; CONFIRM: {1}; Item: {2}".format(idx,m.current_index, item))

        #dummy_function(**i)
    
    print(m)
    
    # m = ParamGenerator({NAME_OPTION:"vlg", PRIORITY_OPTION:0, RANGE_OPTION: 1})
    