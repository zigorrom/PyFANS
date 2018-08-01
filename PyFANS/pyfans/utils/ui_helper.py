import sys
import pint
from pint import UnitRegistry
from PyQt4 import QtGui, QtCore
from enum import Enum
# import modern_fans_controller as mfc

class BindingDirection(Enum):
    SourceToTarget = 0
    TargetToSource = 1
    Both = 2

class NotifyPropertyChanged(QtCore.QObject):
    #str: name of changed property, 
    #object: the object which raised property changed event
    #object: the value of the changed property
    propertyChanged = QtCore.pyqtSignal(str, object, object)

    def __init__(self):
        pass
    
    def onPropertyChanged(self, name, sender, value):
        self.propertyChanged.emit(name, sender, value)

class ValueConverter:
    def __init__(self):
        pass

    def convert(self, value, target_type):
        pass

    def convert_back(self, value, target_type):
        pass



class Binding:
    def __init__(self, widget, widgetPropertyName, sourceObject, sourcePropertyName, **kwargs):
          
        if not isinstance(sourceObject, NotifyPropertyChanged):
            raise TypeError("sourceObject must be inherited from NotifyPropertyChanged class!!")

        if not isinstance(widget, QtCore.QObject):
            raise TypeError("widget should be inherited from QObject")

        if not widgetPropertyName:
            raise ValueError("widgetPropertyName should be a valid string")

        if not sourcePropertyName:
            raise ValueError("widgetPropertyName should be a valid string")

        #the object representing ui widget
        self._targetObject = widget
        #the object which contains data
        self._sourceObject = sourceObject
        
        #the property of widget to be updated
        self._targetPropertyName = widgetPropertyName
        #the property of source object to bind to
        self._sourcePropertyName = sourcePropertyName

        #when to update: OnLoseFocus, OnTextChanged/OnValueChanged/OnCurrentIndexChanged/OnToggled
        #self._when_to_update = None

        #only source to target/ only target to source/ both
        self._binding_direction = kwargs.get("binding_direction", BindingDirection.Both)
        
        self._validator = kwargs.get("validator", None)

        self._converter = kwargs.get("converter", ValueConverter())


        self._sigTargetDataChanged = self.__get_target_data_changed_signal(self._targetObject, self._targetPropertyName)
        self._sigSourceDataChanged = self._sourceObject.propertyChanged
        self.__create_bindings()
    

    
    def __del__(self):
        pass

    
 
    def __create_bindings(self):
        if self._binding_direction == BindingDirection.SourceToTarget:
            self._sigSourceDataChanged.connect(self.__updateTargetData__)

        elif self._binding_direction == BindingDirection.TargetToSource:
            self._sigTargetDataChanged.connect(self.__updateSourceData__)

        elif self._binding_direction == BindingDirection.Both:
            self._sigSourceDataChanged.connect(self.__updateTargetData__)
            self._sigTargetDataChanged.connect(self.__updateSourceData__)

        else:
            raise ValueError("unexpected value of binding direction")

    def __get_target_data_changed_signal(self, widget, widgetPropertyName):
        if widgetPropertyName == "text":
            return widget.textChanged

        elif widgetPropertyName == "value":
            return widget.valueChanged

        elif widgetPropertyName == "currentIndex":
            return widget.currentIndexChanged

        elif widgetPropertyName == "checked":
            return widget.toggled

        else:
            return None
        

    def __updateTargetData__(self, newValue):
        pass


    @QtCore.pyqtSlot(int)
    def __updateSourceData__(self, value):
        pass

    @QtCore.pyqtSlot(float)
    def __updateSourceData__(self, value):
        pass

    @QtCore.pyqtSlot(str)
    def __updateSourceData__(self, value):
        pass

    @property
    def targetData(self):
        pass    

    @targetData.setter
    def targetData(self, value):
        pass    

    @property
    def sourceData(self):
        pass

    @sourceData.setter
    def sourceData(self, value):
        pass

    
    def getSourceData(self):
        pass




def __assert_isinstance_wrapper(function, t):
    def wrapper(self,value):
        assert isinstance(value, t), "expected {0} - received {1}".format(t,type(value))
        return function(self, value)
    return wrapper

def assert_boolean_argument(function):
    return __assert_isinstance_wrapper(function, bool)

def assert_int_or_float_argument(function):
    return __assert_isinstance_wrapper(function,(int,float))

def assert_float_argument(function):
    return __assert_isinstance_wrapper(function, float)

def assert_string_argument(function):
    return __assert_isinstance_wrapper(function, str)

def assert_integer_argument(function):
    return __assert_isinstance_wrapper(function, int)

def assert_list_argument(function):
    return __assert_isinstance_wrapper(function, list)

def assert_tuple_argument(function):
    return __assert_isinstance_wrapper(function, tuple)

def assert_list_or_tuple_argument(function):
    return __assert_isinstance_wrapper(function, (list, tuple))

def get_module_name_and_type(t):
    module = t.__module__
    cls_name = type(t).__name__
    return "{0}.{1}".format(module,cls_name)

def get_value_of_module_type(value, module_type):
    module, t = module_type.split(".")
    mod = sys.modules[module]
    cls = getattr(mod, t)
    return cls(value)

def setAllChildObjectSignaling(parentObj, Signaling):
    assert isinstance(parentObj, QtCore.QObject)
    assert isinstance(Signaling, bool)
    for child in parentObj.children():
        #print(child.objectName())
        res = child.blockSignals(Signaling)
        #print(res)

def bind(objectName, propertyName, value_type, string_format = None):#, set_value_type):
    def getter(self):
        prop_val = self.findChild(QtCore.QObject, objectName).property(propertyName)
        # value = None
        try:
            if isinstance(prop_val, bool):
                return value_type(prop_val)

            elif not prop_val:
                if value_type == int or value_type == float:
                    return value_type(0)
                    
                elif value_type == bool:
                    return False

                elif value_type == str:
                    return ""
            
            else:
                value = value_type(prop_val)

        except Exception as e:
            prop_type = type(prop_val)
            print("Error handling convertion from type {0} to type {1}".format(prop_type, value_type))
            return None
        
        
        # # if prop_val:
        # #     value =value_type(prop_val) 
        
        
        
        # # else:
        # #     value = value_type()

        # return value

    def setter(self,value):
        if isinstance(string_format, str):
            if value is None:
                return
            value = string_format.format(value)
        #assert isinstance(value, set_value_type), "expected type {0}, reveiver {1}".format(set_value_type, type(value))
        self.findChild(QtCore.QObject, objectName).setProperty(propertyName, value)

    return property(getter, setter)

class QVoltageValidator(QtGui.QRegExpValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        regex = QtCore.QRegExp("^-?(?:0|[1-9]\d*).?(\d*)\s*(?:[yzafpnumcdhkMGTPEZY])?[V]")   #"(\d+).?(\d*)\s*(m|cm|km)")
        self.setRegExp(regex)

def convert_value_to_volts(ureg, value):
    assert isinstance(ureg, UnitRegistry)
    try:
          v = ureg(value)
          if not isinstance(v,pint.quantity._Quantity):
              v = float(v) * ureg.volt
          print("{0} {1}".format(v.magnitude, v.units))
          v.ito(ureg.volt)
          return v.magnitude
    except Exception as e:
          print("error while handling value")
          print(str(e))
          return 0.0

def string_to_volt_converter(ureg):
    def wrapper(value):
       return convert_value_to_volts(ureg, value)
    return wrapper