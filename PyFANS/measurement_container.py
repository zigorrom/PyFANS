

#name, priority, range

# for key, value in sorted(mydict.iteritems(), key=lambda (k,v): (v,k)):
#     print "%s: %s" % (key, value)

from io import StringIO
NAME_OPTION = "name"
PRIORITY_OPTION = "priority"
RANGE_OPTION = "range"

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
        self._max_priority_level = 0
        self.populate_params(*args, **kwargs)
    
    def populate_params(self, *args, **kwargs):
        for item in args:
            self.append_parameter(item)
 

    def append_parameter(self, parameter_item):
        if isinstance(parameter_item, ParameterItem):
            parameter_item.priority_level = self._max_priority_level
            self._max_priority_level += 1
            self._all_params.append(parameter_item) 
    
    def clear(self):
        self._all_params.clear()
        self._max_priority_level = 0

    @property
    def parameter_items(self):
        return self._all_params

    def __iter__(self):
        pass
        # return iter(self._all_params)

    def __str__(self):
        sio = StringIO()
        sio.write("ParamGenerator:\n")
        for item in self.parameter_items:
            sio.write(str(item))
            sio.write("\n")
        return sio.getvalue()
    
    def __getitem__(self, i):
        if isinstance(i, int):
            return self._all_params[i]
        else:
            raise IndexError()



if __name__ == "__main__":
    m = ParamGenerator()
    m.append_parameter(ParameterItem("hgjhsdg"))
    m.append_parameter(ParameterItem("dgdag'ag"))
    print(m[0])

    # m = ParamGenerator({NAME_OPTION:"vlg", PRIORITY_OPTION:0, RANGE_OPTION: 1})
    print(m)