

           

class Node(object):
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
    name = property(**name())

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
    label= property(**label())
    

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
    value = property(**value())
    

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
    checked = property(**checked())

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
    selectedIndex = property(**selectedIndex())

##    def selectedValue():
##        def fget(self):return self._selectedValue
##        def fset(self,value): self._selectedValue = value
##        return locals()
##    selectedIndex = property(**selectedValue())
    
##    def case_list(self):
##        return self._case_list
    def case_list():
        def fget(self): return self._case_list
        def fset(self,value): self._case_list = value
        return locals()
    case_list = property(**case_list())
    
    
    def data(self,column):
        r = super(ComboNode,self).data(column)
        if column is 2: r = self.selectedIndex
##        elif column is 2: r = self.enumeration.names.index(self._selectedValue)
        return r

    def setData(self,column,value):
        super(ComboNode,self).setData(column,value)
        if column is 2: self.selectedIndex = value#.toPyObject())
##        if column is 2: self.selectedValue = self.enumeration.names[value]


class InChannelNode(Node):
    def __init__(self,name,parent=None):
        super(InChannelNode,self).__init__(name,parent)
##        self._enabled = CheckNode("enabled", parent = self)
##        self._range = ComboNode("range", case_list=['One','Two','Three'], parent = self)
##        self._polarity = ComboNode("polarity",case_list=['Unipolar','Bipolar'],parent = self)
##        self._function = ComboNode("function",case_list=['Vds','Vlg','Vbg'],parent=  self)

##    def _recurseXml(self, doc, parent):
##        node = doc.createElement(self.typeInfo())
##        parent.appendChild(node)
##
##        for i in self._children:
##            i._recurseXml(doc, node)


##    def enabled():
##        def fget(self):return self._enabled.checked
##        def fset(self,value): self._enabled.checked = value
##            
##        return locals()
##    enabled = property(**enabled())
##
##    def enabled_label():
##        def fget(self): return self._enabled.name
##        return locals()
##    enabled_label = property(**enabled_label())
##
##    def selected_range():
##        def fget(self): return self._range.selectedIndex
##        def fset(self,value): self._range.selectedIndex = value
##        return locals()
##    selected_range = property(**selected_range())
##
##    def range_label():
##        def fget(self):return self._range.name
##        return locals()
##
##    range_label = property(**range_label())
##        
##        
##    def selected_polarity():
##        def fget(self): return self._polarity.selectedIndex
##        def fset(self,value): self._polarity.selectedIndex = value
##        return locals()
##    selected_polarity = property(**selected_polarity())
##
##    def polarity_label():
##        def fget(self): return self._polarity.name
##        return locals()
##    polarity_label = property(**polarity_label())
##
##    def selected_function():
##        def fget(self): return self._function.selectedIndex
##        def fset(self,value): self._function.selectedIndex = value
##        return locals()
##    selected_function = property(**selected_function())
##    
##    
##    def function_label():
##        def fget(self):return self._function.name
##        return locals()
##    function_label = property(**function_label())
##
    
    def typeInfo(self):
        return "IN_CHANNEL"

    @classmethod
    def typeInfo(cls):
        return "IN_CHANNEL"

    def columnCount(self):
        return 3

    def data(self, column):
        r = super(InChannelNode,self).data(column)
##        if column is 2:     r = self.enabled
##        elif column is 3:   r = self.selected_range
##        elif column is 4:   r = self.selected_polarity
##        elif column is 5:   r = self.selected_function
##        elif column is 6:   r = self.enabled_label()
##        elif column is 7:   r = self.range_label()
##        elif column is 8:   r = self.polarity_label()
##        elif column is 9:   r = self.function_label()
        return r

    def setData(self, column, value):
        super(InChannelNode,self).setData(column,value)
##        if column is 2:     self.enabled = value
##        elif column is 3:   self.selected_range = value
##        elif column is 4:   self.selected_polarity = value
##        elif column is 5:   self.selected_function =value
        

class OutChannelNode(Node):
    def __init__(self,name,parent=None):
        super(OutChannelNode,self).__init__(name,parent)
##        self._enabled = CheckNode(name+"_enabled", parent = self)
##        self._range = ComboNode(name+"_range", parent = self)
##        self._polarity = ComboNode(name+"_polarity",parent = self)
##        self._output_pin = ComboNode(name+"_out_pin",parent = self)
##        self._function = ComboNode(name+"_function",parent=  self)

    def typeInfo(self):
        return "OUT_CHANNEL"

    @classmethod
    def typeInfo(cls):
        return "OUT_CHANNEL"


class AcquisitionSettingsNode(Node):
    def __init__(self,name,parent=None):
        super(AcquisitionSettingsNode,self).__init__(name,parent)
##        self._sample_rate = NumericNode("sample_rate", parent = self)
##        self._points_per_shot = NumericNode("points_per_shot", parent = self)
##        self._homemade_amplifier = CheckNode("homemade_amplifier", parent = self)
##        self._pga_gain = ComboNode("pga_gain",parent = self)
##        self._filter_gain = ComboNode("filter_gain", parent = self)
##        self._filter_cutoff = ComboNode("filter_cutoff",parent = self)

    def typeInfo(self):
        return "ACQUISITION_SETTINGS"

    @classmethod
    def typeInfo(cls):
        return "ACQUISITION_SETTINGS"


