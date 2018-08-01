import sys
import pint
import traceback

from pint import UnitRegistry
from PyQt4 import QtGui, QtCore
from enum import Enum
# import modern_fans_controller as mfc

def print_exception(exception):
    print("Exception occured:")
    print(20*'-')
    traceback.print_exc()
    print("The latest exception:")
    print(exception)
    print(20*'=')



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
        super().__init__()
    
    def onPropertyChanged(self, name, sender, value):
        self.propertyChanged.emit(name, sender, value)

class ConversionException(Exception):
    pass

class ValueConverter:
    def __init__(self, defaultTargetValue=None, defaultSourceValue=None):
        self.defaultTargetValue = defaultTargetValue
        self.defaultSourceValue = defaultSourceValue

    def convert(self, value, source_type, default_value = None):
        try:
            return source_type(value) 

        except Exception as e:
            print_exception(e)
            raise ConversionException()
            #return default_value

    def convert_back(self, value, target_type, default_value = None):
        try:
            return target_type(value) 

        except Exception as e:
            print_exception(e)
            raise ConversionException()
            # return default_value

class StringToIntConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, value):
        super().convert(value, int, 0)

    def convert_back(self, value):
        super().convert_back(value, str, "")

class StringToFloatConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, value):
        super().convert(value, float, 0.0)

    def convert_back(self, value):
        super().convert_back(value, str, "")

class StringToVoltageConverter(ValueConverter):
    def __init__(self):
        super().__init__()
        self.ureg = UnitRegistry()

    def convert(self, value):
        try:
            v = self.ureg(value)
            if not isinstance(v,pint.quantity._Quantity):
                v = float(v) * self.ureg.volt
            print("{0} {1}".format(v.magnitude, v.units))
            v.ito(self.ureg.volt)
            return v.magnitude
        except Exception as e:
            raise ConversionException()

    def convert_back(self, value):
        try:
            return str(value)
        except Exception as e:
            raise ConversionException()

class AssureConverter(ValueConverter):
    def __init__(self, type_to_assure):
        if not isinstance(type_to_assure, type):
            raise TypeError("Incorrect type")
        self._assureType = type_to_assure

    def convert(self, value):
        super().convert(value, self._assureType, None)

    def convert_back(self, value):
        super().convert_back(value, self._assureType, None)


class AssureBoolConverter(AssureConverter):
    def __init__(self):
        super().__init__(bool)

class AssureIntConverter(AssureConverter):
    def __init__(self):
        super().__init__(int)

        




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

        self._converter = kwargs.get("converter", None)

        self._updatingSourceData = False
        self._updatingTargetData = False
        self._hasError = False

        # if not isinstance(self._converter, ValueConverter):
        #     return TypeError("converter has a wrong type")

        self.originalStylesheet = self._targetObject.styleSheet()
        self.errorStylesheet = "border: 2px solid red;"

        self._sigTargetDataChanged = self.__get_target_data_changed_signal(self._targetObject, self._targetPropertyName)
        self._sigSourceDataChanged = self._sourceObject.propertyChanged
        self.__create_bindings()
        self.__updateUi()
     
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

        elif widgetPropertyName == "currentText":
            return widget.currentTextChanged

        else:
            return None
        
    def __updateUi(self):
        self.__updateTargetData__(self._sourcePropertyName, self, self.sourceData)
        self.__updateSourceData__(self.targetData)

    def __updateTargetData__(self, name, sender, value):
        if self._updatingSourceData:
            return 

        if name != self._sourcePropertyName:
            return 

        print("updating target")
        self._updatingTargetData = True
        self._targetObject.blockSignals(True)

        if self._converter is None:
            self.targetData = value
        
        else:    
            try:
                self.targetData = self._converter.convert_back(value)
            except ConversionException as e:
                print_exception(e)
            
        self._targetObject.blockSignals(False)
        self._updatingTargetData = False
        # self.targetData = self.sourceData

    # @QtCore.pyqtSlot(int)
    def __updateSourceData__(self, value):
        if self._updatingTargetData:
            return
        
        print("updating source")
        self._updatingSourceData = True
        if self._converter is None:
            self.sourceData = value #self.targetData
        
        else: 
            try:
                self.sourceData = self._converter.convert(self.targetData)
                self.setNormalStyle()
            except ConversionException as e:
                print_exception(e)
                self.setErrorStyle()

        self._updatingSourceData = False
    
    def setErrorStyle(self):
        self._hasError = True
        self._targetObject.setStyleSheet(self.errorStylesheet)

    def setNormalStyle(self):
        self._hasError = False
        self._targetObject.setStyleSheet(self.originalStylesheet)

    def hasError(self):
        return self._hasError

    @property
    def targetData(self):
        return self._targetObject.property(self._targetPropertyName)
        # if self._converter is None:
        #     return bareValue

        # return self._converter.convert(bareValue)
        

    @targetData.setter
    def targetData(self, value):
        self._targetObject.setProperty(self._targetPropertyName, value)
        

    @property
    def sourceData(self):
        return getattr(self._sourceObject, self._sourcePropertyName)

    @sourceData.setter
    def sourceData(self, value):
        setattr(self._sourceObject, self._sourcePropertyName, value)

    




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