import sys
import pint
from pint import UnitRegistry
from PyQt4 import QtGui, QtCore
# import modern_fans_controller as mfc


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
        value = None
        if prop_val:
            value =value_type(prop_val) 
        else:
            value = value_type()

        return value

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