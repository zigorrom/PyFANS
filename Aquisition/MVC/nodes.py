
from binding import Observable,notifiable_property
           
##class Node(object):
class Node(Observable):
    def __init__(self, name = "unknown", parent=None):
        
        super(Node, self).__init__()
        
        self._name = name
        self._children = []
        self._parent = parent
        
        if parent is not None:
            parent.addChild(self)
    
    def typeInfo(self):
        return "NODE"

    @classmethod
    def typeInfo(cls):
        return "NODE"
    
    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None

        return True

    def columnCount(self):
        return 2

    def name():
        def fget(self):return self._name
        def fset(self,value):self._name = value
        return locals()
    name = notifiable_property("name",**name())
##    name = property(**name())

    def child(self, row):
        return self._children[row]

    def getChildByName(self,name, case_sensitive= False):
        def equal_case_sensitive(a,b):
            return a == b
        def equal_case_insensitive(a,b):
            return a.lower() == b.lower()

        comparator = equal_case_sensitive if case_sensitive else equal_case_insensitive
                                   
        childs = [n for n in self._children if comparator(n.name,name)]#n.name == name]
        if len(childs)>0:
            return childs[0]
        else:
            return None
    
    def childCount(self):
        return len(self._children)
    
    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)


    def log(self, tabLevel=-1):

        output     = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
        
        output += "|------" + self._name + "\n"
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += "\n"
        
        return output

    def __repr__(self):
        return self.log()

    def data(self,column):
        if      column is 0: return self.name
        elif    column is 1: return self.typeInfo()
        

    def setData(self,column,value):
        if column is 0: self.name=value#.toPyObject())
        elif column is 1: pass

    def resource(self):
        return None



class AcquisitionSettingsNode(Node):
    def __init__(self,name,parent=None):
        super(AcquisitionSettingsNode,self).__init__(name,parent)
        self._sample_rate = 500000
        self._homemade_amplifier = True
        self._amplifier = 1
        self._pga_amplifier = 1
        self._filter_gain = 1
        self._filter_cutoff = 1

    def sample_rate():
        def fget(self): return self._sample_rate
        def fset(self,value): self._sample_rate = value
        return locals()

    sample_rate = notifiable_property("sample_rate",**sample_rate())

    def homemade_amplifier():
        def fget(self): return self._homemade_amplifier
        def fset(self,value): self._homemade_amplifier = value
        return locals()

    homemade_amplifier = notifiable_property("homemade_amplifier",**homemade_amplifier())

    def amplifier():
        def fget(self): return self._amplifier
        def fset(self,value): self._amplifier = value
        return locals()

    amplifier = notifiable_property("amplifier", **amplifier())

    def pga_amplifier():
        def fget(self): return self._pga_amplifier
        def fset(self,value): self._pga_amplifier = value
        return locals()

    pga_amplifier = notifiable_property("pga_amplifier",**pga_amplifier())

    def filter_gain():
        def fget(self): return self._filter_gain
        def fset(self,value): self._filter_gain = value
        return locals()

    filter_gain = notifiable_property("filter_gain", **filter_gain())

    def filter_cutoff():
        def fget(self): return self._filter_cutoff
        def fset(self,value): self._filter_cutoff = value
        return locals()

    filter_cutoff = notifiable_property("filter_cutoff",**filter_cutoff())

    def typeInfo(self):
        return "ACQUISITION_SETTINGS"

    @classmethod
    def typeInfo(cls):
        return "ACQUISITION_SETTINGS"

    def data(self,column):
        r = super(AcquisitionSettingsNode,self).data(column)
        if column is 2: r = self.sample_rate
        elif column is 3: r = self.homemade_amplifier
        elif column is 4: r = self.amplifier
        elif column is 5: r = self.pga_amplifier
        elif column is 6: r = self.filter_gain
        elif column is 7: r = self.filter_cutoff
        return r

    def setData(self,column,value):
        super(AcquisitionSettingsNode,self).setData(column,value)
        if column is 2: self.sample_rate = value
        elif column is 3: self.homemade_amplifier = value
        elif column is 4: self.amplifier = value
        elif column is 5: self.pga_amplifier = value
        elif column is 6: self.filter_gain = value
        elif column is 7: self.filter_cutoff = value


    

class LabelNode(Node):
    def __init__(self,name, label = "",parent=None):
        super(LabelNode,self).__init__(name,parent)

        self._label = label

    def typeInfo(self):
        return "LABEL"

    @classmethod
    def typeInfo(cls):
        return "LABEL"
    
    def label():
        def fget(self): return self._label
        def fset(self,value): self._label = value
        return locals()
    label= notifiable_property("label",**label())
##    label= property(**label())
    
    def data(self,column):
        r = super(LabelNode,self).data(column)
        if column is 2: r = self.label
        return r

    def setData(self,column,value):
        super(LabelNode,self).setData(column,value)
        if column is 2: self._label = value#.toPyObject())
        

    
    

class NumericNode(Node):
    def __init__(self,name,  value = 10,parent = None):
        super(NumericNode,self).__init__(name,parent)
        self._value = value
        

    def typeInfo(self):
        return "NUMERIC"

    @classmethod
    def typeInfo(cls):
        return "NUMERIC"
    

    def value():
        def fget(self): return self._value
        def fset(self,val): self._value = val 
        return locals()
    value = notifiable_property("value",**value())
##    value = property(**value()

    def data(self,column):
        r = super(NumericNode,self).data(column)
        if column is 2: r = self.value
        return r

    def setData(self,column,value):
        super(NumericNode,self).setData(column,value)
        if column is 2: self.value = value#.toPyObject())
    

class CheckNode(Node):
    def __init__(self,name,checked = False, parent=None):
        super(CheckNode,self).__init__(name,parent)
        self._checked = checked

    def typeInfo(self):
        return "CHECK"

    @classmethod
    def typeInfo(cls):
        return "CHECK"

    def checked():
        def fget(self): return self._checked
        def fset(self,value): self._checked = value
        return locals()
    checked = notifiable_property("checked",**checked())
##    checked = property(**checked())

    def data(self,column):
        r = super(CheckNode,self).data(column)
        if column is 2: r = self.checked
        return r

    def setData(self,column,value):
        super(CheckNode,self).setData(column,value)
        if column is 2: self.checked = value#.toPyObject())

    
class ComboNode(Node):
    def __init__(self,name,case_list = [] , parent=None):
        super(ComboNode,self).__init__(name,parent)
        self._case_list = case_list
        self._selectedIndex = 0
##        self.enumeration = enumeration
##        self.selectedValue = enumeration.names[0]


    def typeInfo(self):
        return "COMBO"

    @classmethod
    def typeInfo(cls):
        return "COMBO"
    
    def selectedIndex():
        def fget(self):return self._selectedIndex
        def fset(self,value): self._selectedIndex = value
        return locals()
    selectedIndex = notifiable_property("selected_index",**selectedIndex())


    def case_list():
        def fget(self): return self._case_list
        def fset(self,value): self._case_list = value
        return locals()
    case_list = notifiable_property("case_list", **case_list())
##    case_list = property(**case_list())
    
    
    def data(self,column):
        r = super(ComboNode,self).data(column)
        if column is 2: r = self.selectedIndex
##        elif column is 2: r = self.enumeration.names.index(self._selectedValue)
        return r

    def setData(self,column,value):
        super(ComboNode,self).setData(column,value)
        if column is 2: self.selectedIndex = value#.toPyObject())
##        if column is 2: self.selectedValue = self.enumeration.names[value]


#mode: ac/dc
#cs_hold
#filter_cutoff
#filter_gain
#pga_gain
class InChannelNode(Node):
    def __init__(self,name,parent=None):
        super(InChannelNode,self).__init__(name,parent)
        self._enabled = True#CheckNode("enabled", parent = self)
        self._range = None #ComboNode("range", case_list=['One','Two','Three'], parent = self)
        self._polarity = None#ComboNode("polarity",case_list=['Unipolar','Bipolar'],parent = self)
        self._function = None#ComboNode("function",case_list=['Vds','Vlg','Vbg'],parent=  self)
        self._mode = None
        self._filter_cutoff =None
        self._filter_gain = None
        self._pga_gain = None

    def mode():
        def fget(self): return self._mode
        def fset(self,value): self._mode = value
        return locals()
    mode = notifiable_property("mode",**mode())

    def filter_cutoff():
        def fget(self): return self._filter_cutoff
        def fset(self,value): self._filter_cutoff = value
        return locals()
    filter_cutoff = notifiable_property("mode",**filter_cutoff())

    def filter_gain():
        def fget(self): return self._filter_gain
        def fset(self,value): self._filter_gain = value
        return locals()
    filter_gain = notifiable_property("mode",**filter_gain())

    def pga_gain():
        def fget(self): return self._pga_gain
        def fset(self,value): self._pga_gain = value
        return locals()
    pga_gain = notifiable_property("mode",**pga_gain())


    def enabled():
        def fget(self):return self._enabled
        def fset(self,value): self._enabled = value
        return locals()
    enabled = notifiable_property("enabled",**enabled())

    
    def selected_range():
        def fget(self): return self._range
        def fset(self,value): self._range = value
        return locals()
    selected_range = notifiable_property("range",**selected_range())

        
    def selected_polarity():
        def fget(self): return self._polarity
        def fset(self,value): self._polarity= value
        return locals()
    selected_polarity = notifiable_property("polarity",**selected_polarity())

    
    def selected_function():
        def fget(self): return self._function
        def fset(self,value): self._function = value
        return locals()
    selected_function = notifiable_property("function",**selected_function())
    
    
    
    def typeInfo(self):
        return "IN_CHANNEL"

    @classmethod
    def typeInfo(cls):
        return "IN_CHANNEL"

    
    def data(self, column):
        r = super(InChannelNode,self).data(column)
        if column is 2:     r = self.enabled
        elif column is 3:   r = self.selected_range
        elif column is 4:   r = self.selected_polarity
        elif column is 5:   r = self.selected_function
        elif column is 6:   r = self.mode
        elif column is 7:   r = self.filter_cutoff
        elif column is 8:   r = self.filter_gain
        elif column is 9:   r = self.pga_gain
        return r

    def setData(self, column, value):
        super(InChannelNode,self).setData(column,value)
        if column is 2:     self.enabled = value
        elif column is 3:   self.selected_range = value
        elif column is 4:   self.selected_polarity = value
        elif column is 5:   self.selected_function = value
        elif column is 6:   self.mode = value
        elif column is 7:   self.filter_cutoff = value
        elif column is 8:   self.filter_gain = value
        elif column is 9:   self.pga_gain = value
        

class OutChannelNode(Node):
    def __init__(self,name,parent=None):
        super(OutChannelNode,self).__init__(name,parent)
        self._enabled = True#CheckNode(name+"_enabled", parent = self)
        self._range =  None#ComboNode(name+"_range", parent = self)
        self._polarity = None#ComboNode(name+"_polarity",parent = self)
        self._output_pin = None#ComboNode(name+"_out_pin",parent = self)
        self._function = None#ComboNode(name+"_function",parent=  self)

    def enabled():
        def fget(self):return self._enabled
        def fset(self,value): self._enabled = value
        return locals()
    enabled = notifiable_property("enabled",**enabled())

    def selected_range():
        def fget(self): return self._range
        def fset(self,value): self._range = value
        return locals()
    selected_range = notifiable_property("range",**selected_range())

    def selected_polarity():
        def fget(self): return self._polarity
        def fset(self,value): self._polarity= value
        return locals()
    selected_polarity = notifiable_property("polarity",**selected_polarity())

    def selected_function():
        def fget(self): return self._function
        def fset(self,value): self._function = value
        return locals()
    selected_function = notifiable_property("function",**selected_function())

    def selected_output():
        def fget(self): return self._output_pin
        def fset(self,value): self._output_pin = value
        return locals()
    selected_output = notifiable_property("selected_output",**selected_output())


    def data(self, column):
        r = super(OutChannelNode,self).data(column)
        if column is 2:     r = self.enabled
        elif column is 3:   r = self.selected_range
        elif column is 4:   r = self.selected_polarity
        elif column is 5:   r = self.selected_function
        elif column is 6:   r = self.selected_output
        return r

    def setData(self, column, value):
        super(OutChannelNode,self).setData(column,value)
        if column is 2:     self.enabled = value
        elif column is 3:   self.selected_range = value
        elif column is 4:   self.selected_polarity = value
        elif column is 5:   self.selected_function =value
        elif column is 6:   self.selected_output = value

    def typeInfo(self):
        return "OUT_CHANNEL"

    @classmethod
    def typeInfo(cls):
        return "OUT_CHANNEL"




