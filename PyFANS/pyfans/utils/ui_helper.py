import sys
import pint
import traceback

from pint import UnitRegistry
from PyQt4 import QtGui, QtCore
from enum import Enum
# import modern_fans_controller as mfc
#from  pyfans.experiment.modern_fans_experiment import CharacteristicType

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

class NameValidator(QtGui.QRegExpValidator):
    def __init__(self, parent=None):
        regex = QtCore.QRegExp("^[a-zA-Z][^.,;:?/\\`~|!@$%^&* ]*$")
        super().__init__(regex, parent)
        
    def fixup(self, string):
        if not isinstance(string, str):
            return 

        string = string.replace(' ', '_').replace('.','_')
        return string



class ValueConverter:
    def __init__(self, defaultTargetValue=None, defaultSourceValue=None):
        self.defaultTargetValue = defaultTargetValue
        self.defaultSourceValue = defaultSourceValue

    def convert(self, value, source_type, **kwargs):
        try:
            if value is None:
                raise ConversionException()

            return source_type(value) 
        
        except ConversionException:
            raise

        except Exception as e:
            print_exception(e)
            raise ConversionException()
            #return default_value

    def convert_back(self, value, target_type, **kwargs):
        try:
            if value is None:
                raise ConversionException()

            return target_type(value) 
            
        except ConversionException:
            raise

        except Exception as e:
            print_exception(e)
            raise ConversionException()
            # return default_value

class StringToTypeConverter(ValueConverter):
    def __init__(self, type_to_convert):
        if not isinstance(type_to_convert, type):
            raise TypeError("Incorrect type")
        
        super().__init__()
        self._type = type_to_convert

    def convert(self, value, **kwargs):
        return super().convert(value, self._type, **kwargs)

    def convert_back(self, value, **kwargs):
        try:
            stringFormat = kwargs.get("stringFormat", None)
            if not stringFormat:
                return super().convert_back(value, str, **kwargs)
            
            elif value is None:
                return ""
            
            else:
                return stringFormat.format(value)

        except Exception as e:
            raise ConversionException()
   
class StringToIntConverter(StringToTypeConverter):
    def __init__(self):
        super().__init__(int)

class StringToFloatConverter(StringToTypeConverter):
    def __init__(self):
        super().__init__(float)

class StringToVoltageConverter(StringToTypeConverter):
    def __init__(self):
        self.ureg = UnitRegistry()
        super().__init__(type(self.ureg))

    def convert(self, value, **kwargs):
        try:
            v = self.ureg(value)
            if not isinstance(v,pint.quantity._Quantity):
                v = float(v) * self.ureg.volt
            print("{0} {1}".format(v.magnitude, v.units))
            v.ito(self.ureg.volt)
            return v.magnitude
        except Exception as e:
            raise ConversionException()

class AssureConverter(ValueConverter):
    def __init__(self, type_to_assure):
        if not isinstance(type_to_assure, type):
            raise TypeError("Incorrect type")
        self._assureType = type_to_assure

    def convert(self, value):
        return super().convert(value, self._assureType)

    def convert_back(self, value):
        return super().convert_back(value, self._assureType)


class AssureBoolConverter(AssureConverter):
    def __init__(self):
        super().__init__(bool)

class AssureIntConverter(AssureConverter):
    def __init__(self):
        super().__init__(int)


class Binding:
    def __init__(self, widget, widgetPropertyName, sourceObject, sourcePropertyName, **kwargs):
          
        # if not isinstance(sourceObject, NotifyPropertyChanged):
        #     raise TypeError("sourceObject must be inherited from NotifyPropertyChanged class!!")

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

        self._stringFormat = kwargs.get("stringFormat", None)

        #only source to target/ only target to source/ both
        self._binding_direction = kwargs.get("binding_direction", BindingDirection.Both)
        
        self._validator = kwargs.get("validator", None)
        # try:
        #     self._targetObject
        # except:
        #     pass
        setValidator = getattr(self._targetObject, "setValidator", None)
        if callable(setValidator):
            setValidator(self._validator)

        self._converter = kwargs.get("converter", None)

        self._updatingSourceData = False
        self._updatingTargetData = False
        self._hasError = False

        # if not isinstance(self._converter, ValueConverter):
        #     return TypeError("converter has a wrong type")

        self.originalStylesheet = self._targetObject.styleSheet()
        self.errorStylesheet = "border: 2px solid red;"

        self._sigTargetDataChanged = None
        self._sigSourceDataChanged = None
        # self.__create_bindings()
        # self.__updateUi()
        self.reset()

    def __del__(self):
        try:
            self._sigSourceDataChanged.disconnect(self.__updateTargetData__)
        except:
            print("source data changed is not connected")
            
        try:
            self._sigTargetDataChanged.disconnect(self.__updateSourceData__)
        except:
            print("target data changed is not connected")


    def reset(self):
        try:
            self._sigSourceDataChanged.disconnect(self.__updateTargetData__)
        except:
            print("source data changed is not connected")
            
        try:
            self._sigTargetDataChanged.disconnect(self.__updateSourceData__)
        except:
            print("target data changed is not connected")

        if not isinstance(self._sourceObject, NotifyPropertyChanged):
            print("Source object is not suitable to create a binding")
            return

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
   
        elif widgetPropertyName == "currentRow":
            return widget.currentRowChanged
 
        else:
            return None
        
    def __updateUi(self):
        self.__updateTargetData__(self._sourcePropertyName, self, self.sourceData)
        self.__check_target_data_valid__()
        # self.__updateSourceData__(self.targetData)

    def setSourceObject(self, sourceObject):
        if not isinstance(sourceObject, NotifyPropertyChanged):
            raise TypeError("sourceObject must be inherited from NotifyPropertyChanged class!!")

        self._sourceObject = sourceObject
        self.reset()

    def __updateTargetData__(self, name, sender, value):
        if name != self._sourcePropertyName:
            return 

        if self._updatingSourceData:
            return 

        
        print("updating target")
        self._updatingTargetData = True
        self._targetObject.blockSignals(True)

        if self._converter is None:
            self.targetData = value
        
        else:    
            try:
                if self._stringFormat:
                    self.targetData = self._converter.convert_back(value, stringFormat=self._stringFormat)
                else:
                    self.targetData = self._converter.convert_back(value)
                self.__check_target_data_valid__()
            except ConversionException as e:
                print_exception(e)
            
        self._targetObject.blockSignals(False)
        self._updatingTargetData = False
        # self.targetData = self.sourceData
    
    def __check_target_data_valid__(self):
        if self._converter is None:
            print("No converter registered. Data considered valid")
            return
        try:
            self._converter.convert(self.targetData)
            # if self._validator:
            #     validation = self._validator.validate()
            self.setNormalStyle()

        except ConversionException as e:
            self.setErrorStyle()
            
        
    def invalidateSourceData(self):
        self.__updateSourceData__(self.targetData)
    
    def invalidateTargetData(self):
        self.__updateTargetData__(self._sourcePropertyName, self, self.sourceData)

    # @QtCore.pyqtSlot(int)
    def __updateSourceData__(self, value):
        if self._updatingTargetData:
            return
        
        print("updating source property {0}".format(self._sourcePropertyName))
        self._updatingSourceData = True
        if self._converter is None:
            self.sourceData = value #self.targetData
        
        else: 
            try:
                convertedValue = self._converter.convert(self.targetData)
                self.sourceData = convertedValue
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
        # self.__updateUi()
        

    @property
    def sourceData(self):
        try:
            return getattr(self._sourceObject, self._sourcePropertyName)
        except Exception:
            return None

    @sourceData.setter
    def sourceData(self, value):
        try:
            setattr(self._sourceObject, self._sourcePropertyName, value)
            # self.__updateUi()
        except Exception:
            pass
 

    
class DataContextWidget:
    def __init__(self, **kwargs):
        self._dataContext = None 
        self.dataContext = kwargs.get("dataContext")
        

    def __setContextForBindings__(self, dataContext):
        # print(dir(self))
        for attribute in dir(self):
            try:
                child = getattr(self, attribute)
                if not isinstance(child, Binding):
                    raise TypeError
                    
                child.setSourceObject(dataContext)
            except TypeError:
                continue
    
    def updateSourceData(self):
        for attribute in dir(self):
            try:
                child = getattr(self, attribute)
                if not isinstance(child, Binding):
                    raise TypeError
                    
                child.invalidateSourceData()

            except TypeError:
                continue
    
    def updateTargetData(self):
        for attribute in dir(self):
            try:
                child = getattr(self, attribute)
                if not isinstance(child, Binding):
                    raise TypeError
                    
                child.invalidateTargetData()
                
            except TypeError:
                continue

    @property
    def dataContext(self):
        return self._dataContext

    @dataContext.setter
    def dataContext(self, context):
        self._dataContext = context
        self.__setContextForBindings__(context)

    # def setDataContext(self, dataContext):
    #     self.dataContext

        




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

            elif prop_val:
                return value_type(prop_val)
                # if value_type == int or value_type == float:
                #     return value_type(0)
                    
                # elif value_type == bool:
                #     return False

                # elif value_type == str:
                #     return ""
            
            else:
                return value_type()

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

class VoltageValidator(QtGui.QRegExpValidator):
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



class ExpandableWidget(QtGui.QWidget):
    """
    port and modification of the initial code from
    https://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
    """
    class ExpandableToolButtonStyle(QtGui.QCommonStyle):
        def __init__(self):
            super().__init__()

        def drawPrimitive(self, element, option, painter, widget):
            print("drawing primitives {0}".format(element))
            print("widget {0}".format(widget))
            # if element == 19: #QtGui.QStyle.PE_PanelButtonTool:
            painter.save()
            angle = 0 if widget.orientation == QtCore.Qt.Horizontal else 90

            rect = option.rect
            center = rect.center()
            transform = painter.transform() 
            transform.translate( center.x(), center.y() ).rotate( angle ).translate( -center.x(), -center.y() )
            painter.setTransform(transform)
            
            super().drawPrimitive(element, option, painter, widget)
            painter.restore()


        def drawItemText(self, painter,rectangle, alignment, palette, enabled, text, textRole):
            print("drawing text")
            super().drawItemText(painter,rectangle, alignment, palette, enabled, text, textRole)

        def drawItemPixmap(self, painter, rect, alignment, pixmap):
            print("drawing pixmap")
            super().drawItemPixmap(self, painter, rect, alignment, pixmap)
            
        def drawControl(self, controlElement, option, painter, widget):
            print("drawing control{0}".format(controlElement))
            super().drawControl(controlElement, option, painter, widget)


        def subControlRect(self, complexControl, opt, subControl, widget):
            print("requesting subcontrol rect {0}".format(subcontrol))
            return super().subControlRect(complexControl, opt, subControl,widget)

        def subElementRect(self, subElement, option, widget):
            print("requesting element rect {0}".format(subElement))
            return super().subElementRect(subElement, option, widget).translated(0,-100)
    

    class OrientationalToolButton(QtGui.QToolButton):
        """
        https://stackoverflow.com/questions/7339685/how-to-rotate-a-qpushbutton
        """
        def __init__(self, parent = None, **kwargs):
            super().__init__(parent)
            self._anchor = kwargs.get("position", QtCore.Qt.AnchorTop)
            self._orientation = QtCore.Qt.Horizontal if self._anchor == QtCore.Qt.AnchorTop or self._anchor == QtCore.Qt.AnchorBottom else QtCore.Qt.Vertical
            self.setStyle(ExpandableWidget.ExpandableToolButtonStyle())
            # self.resize(self.minimumSizeHint())
            self.adjustSize()


        @property
        def anchor(self):
            return self._anchor
  
        @property
        def orientation(self):
            return self._orientation
        
        def paintEvent(self, event):
            painter = QtGui.QStylePainter(self)
            if self._anchor == QtCore.Qt.AnchorLeft or self._anchor == QtCore.Qt.AnchorRight:
                painter.rotate(270)
                painter.translate(-1 * self.height(), 0)

            # elif self._anchor == QtCore.Qt.AnchorRight:
                # painter.rotate(90)
                # painter.translate(0, -1 * self.width())
            painter.drawComplexControl(QtGui.QStyle.CC_ToolButton, self.getSyleOptions())
        
        


        def minimumSizeHint(self):
            # size = QtCore.QSize(200,100)
            # self.adjustSize()
            print("min size hint")
            size = super(ExpandableWidget.OrientationalToolButton, self).minimumSizeHint()
            # size = QtCore.QSize(size.width(), self.iconSize().height() )
            print(size)
            if self._orientation == QtCore.Qt.Vertical:
                size.transpose()
            return size

        def sizeHint(self):
            print("size hint")
            # self.adjustSize()
            size = super(ExpandableWidget.OrientationalToolButton, self).sizeHint()
            # size = QtCore.QSize(size.width(), 100)
            # size = self.iconSize() # QtCore.QSize(self.width(), 20)
            # size = QtCore.QSize(self.width(), self.height())#self.iconSize().height())
            print(size)
            # size= QtCore.QSize(size.width(), size.height()-100 )

            if self._orientation == QtCore.Qt.Vertical:
                size.transpose()
            return size

        

        def getSyleOptions(self):
            options = QtGui.QStyleOptionToolButton()
            self.initStyleOption(options)
            
            # options.initFrom(self)
            # size = options.rect.size()
            # # size.transpose()
            # options.rect.setSize(size)
            # options.features = QtGui.QStyleOptionButton()#.None
            # if self.isFlat():
            #     options.features |= QtGui.QStyleOptionButton.Flat
            # if self.menu():
            #     options.features |= QtGui.QStyleOptionButton.HasMenu
            # if self.autoDefault() or self.isDefault():
            #     options.features |= QtGui.QStyleOptionButton.AutoDefaultButton
            # if self.isDefault():
            #     options.features |= QtGui.QStyleOptionButton.DefaultButton
            # if self.isDown() or (self.menu() and self.menu().isVisible()):
            #     options.state |= QtGui.QStyle.State_Sunken
            # if self.isChecked():
            #     options.state |= QtGui.QStyle.State_On
            # if not self.isFlat() and not self.isDown():
            #     options.state |= QtGui.QStyle.State_Raised

            # options.text = self.text()
            # options.icon = self.icon()
            # # print(self.text())
            # # print(self.icon())
            # options.iconSize = self.iconSize()
            # print(self.iconSize())
            return options






    def __init__(self, parent = None, **kwargs):
        super().__init__(parent)
        self._mainLayout = QtGui.QGridLayout()
        # self._toggleButton = OrientationalToolButton() # QtGui.QToolButton() ##
        self._headerLine = QtGui.QFrame()
        self._toggleAnimation = QtCore.QParallelAnimationGroup()
        self._contentArea = QtGui.QScrollArea()
        self._animationDuration = 300

        self._title = kwargs.get("title", "Expandable")
        self._animationDuration = kwargs.get("animation_duration", 300)
        
        self._initiallyExpanded = kwargs.get("expanded", True)

        self._position = kwargs.get("anchor", QtCore.Qt.AnchorTop)
        
        self._toggleButton = ExpandableWidget.OrientationalToolButton(position=self._position) 
        
        self._orientation = QtCore.Qt.Horizontal
        if self._position ==  QtCore.Qt.AnchorTop or self._position ==  QtCore.Qt.AnchorBottom:
            self._orientation = QtCore.Qt.Horizontal
        elif self._position ==  QtCore.Qt.AnchorLeft or self._position ==  QtCore.Qt.AnchorRight:
            self._orientation = QtCore.Qt.Vertical
        else:
            self._position = QtCore.Qt.AnchorTop
            self._orientation = QtCore.Qt.Horizontal

        self._expanded_arrow = None
        self._collapsed_arrow = None

        if self._position == QtCore.Qt.AnchorTop:
            self._expanded_arrow = QtCore.Qt.DownArrow
            self._collapsed_arrow = QtCore.Qt.RightArrow
            

        elif self._position == QtCore.Qt.AnchorBottom:
            self._expanded_arrow = QtCore.Qt.UpArrow
            self._collapsed_arrow = QtCore.Qt.RightArrow

        elif self._position ==  QtCore.Qt.AnchorLeft:
            self._expanded_arrow = QtCore.Qt.RightArrow
            self._collapsed_arrow = QtCore.Qt.DownArrow
        
        elif self._position ==  QtCore.Qt.AnchorRight:
            self._expanded_arrow = QtCore.Qt.LeftArrow
            self._collapsed_arrow = QtCore.Qt.DownArrow


        
        # self._expanded_arrow = QtCore.Qt.DownArrow if self._orientation == QtCore.Qt.Horizontal else QtCore.Qt.RightArrow
        # self._collapsed_arrow = QtCore.Qt.RightArrow if self._orientation == QtCore.Qt.Horizontal else QtCore.Qt.DownArrow

        self.setupUi()


    def setupUi(self):
        # transform: rotate(-90deg) translate(100%, 0);
        # transform-origin: right bottom;
        self._toggleButton.setStyleSheet("QToolButton { border: none; }")
        self._toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        if self._initiallyExpanded:
            self._toggleButton.setArrowType(self._expanded_arrow)
        else:
            self._toggleButton.setArrowType(self._collapsed_arrow)
        

        self._toggleButton.setText(self._title)
        self._toggleButton.setCheckable(True)
        self._toggleButton.setChecked(self._initiallyExpanded)

        
        self._headerLine.setFrameShadow(QtGui.QFrame.Sunken)
        
        self._contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")

        # self._toggleButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)

        if self._orientation == QtCore.Qt.Horizontal:
            self._toggleButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
            self._headerLine.setFrameShape(QtGui.QFrame.HLine)
            self._headerLine.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
            self._contentArea.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
            self._contentArea.setMaximumHeight(0)
            self._contentArea.setMinimumHeight(0)
            self._toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, "minimumHeight"))
            self._toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, "maximumHeight"))
            self._toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self._contentArea, "maximumHeight"))
            self._mainLayout.setVerticalSpacing(0)
           

        else:
            self._toggleButton.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
            self._headerLine.setFrameShape(QtGui.QFrame.VLine)
            self._headerLine.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
            self._contentArea.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
            self._contentArea.setMaximumWidth(0)
            self._contentArea.setMinimumWidth(0)
            self._toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, "minimumWidth"))
            self._toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, "maximumWidth"))
            self._toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self._contentArea, "maximumWidth"))
            self._mainLayout.setHorizontalSpacing(0)

           

        if self._position == QtCore.Qt.AnchorTop:
            self._mainLayout.addWidget(self._toggleButton, 0, 0,1,1,QtCore.Qt.AlignLeft)
            self._mainLayout.addWidget(self._headerLine, 0, 2,1,1)
            self._mainLayout.addWidget(self._contentArea, 1, 0,1,3)
            self._mainLayout.setAlignment(QtCore.Qt.AlignTop)
            self.setLayout(self._mainLayout)

        elif self._position == QtCore.Qt.AnchorBottom:
            self._mainLayout.addWidget(self._toggleButton, 1, 0,1,1,QtCore.Qt.AlignLeft)
            self._mainLayout.addWidget(self._headerLine, 1, 2,1,1)
            self._mainLayout.addWidget(self._contentArea, 0, 0,1,3)
            self._mainLayout.setAlignment(QtCore.Qt.AlignBottom)
            self.setLayout(self._mainLayout)

        elif self._position == QtCore.Qt.AnchorLeft:
            self._mainLayout.addWidget(self._toggleButton, 0, 0,1,1,QtCore.Qt.AlignLeft)
            self._mainLayout.addWidget(self._headerLine, 1, 0,1,1)
            self._mainLayout.addWidget(self._contentArea, 0, 1,3,1)
            self._mainLayout.setAlignment(QtCore.Qt.AlignLeft)
            self.setLayout(self._mainLayout)

        elif self._position == QtCore.Qt.AnchorRight:
            self._mainLayout.addWidget(self._toggleButton, 0, 1,1,1,QtCore.Qt.AlignLeft)
            self._mainLayout.addWidget(self._headerLine, 1, 1,1,1)
            self._mainLayout.addWidget(self._contentArea, 0, 0,3,1)
            self._mainLayout.setAlignment(QtCore.Qt.AlignRight)
            self.setLayout(self._mainLayout)

        
        self._mainLayout.setContentsMargins(0,0,0,0)
        self._toggleButton.clicked.connect(self.toggleState)


    @QtCore.pyqtSlot(bool)
    def toggleState(self, state):
        self._toggleButton.setArrowType(self._expanded_arrow if state else self._collapsed_arrow)
        self._toggleAnimation.setDirection(QtCore.QAbstractAnimation.Forward if state else QtCore.QAbstractAnimation.Backward)
        self._toggleAnimation.start()


    

    def setContentLayout(self, contentLayout):
        #trick to remove parent from layout manager
        l = self._contentArea.layout()
        if l:
            QtGui.QWidget().setLayout(l)

        self._contentArea.setLayout(contentLayout)
        
        if self._orientation == QtCore.Qt.Horizontal:
            collapsedParam = self.sizeHint().height() - self._contentArea.maximumHeight()
            contentParam = contentLayout.sizeHint().height()
            if self._initiallyExpanded:
                self._contentArea.setMaximumHeight(contentParam)
                self._contentArea.setMinimumHeight(0)
         
        else:
            collapsedParam = self.sizeHint().width() - self._contentArea.maximumWidth()
            contentParam = contentLayout.sizeHint().width()
            if self._initiallyExpanded:
                self._contentArea.setMaximumWidth(contentParam)
                self._contentArea.setMinimumWidth(0)

        # collapsedHeight = self.sizeHint().height() - self._contentArea.maximumHeight()
        # contentHeight = contentLayout.sizeHint().height()

        for i in range(self._toggleAnimation.animationCount() - 1):
            spoilerAnimation = self._toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self._animationDuration)
            spoilerAnimation.setStartValue(collapsedParam)
            spoilerAnimation.setEndValue(collapsedParam+contentParam)

        contentAnimation = self._toggleAnimation.animationAt(self._toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self._animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentParam)
        
        
        # self.toggleState(self._toggleButton.isChecked())



def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    mainWidget = QtGui.QWidget()
    globalLayout = QtGui.QHBoxLayout()

    wnd = ExpandableWidget(anchor=QtCore.Qt.AnchorRight, title="Settings")
    layout = QtGui.QVBoxLayout()
    widget = QtGui.QLabel()
    widget.setText("asfhakjhahsalkghaskgh")
    layout.addWidget(widget)
    wnd.setContentLayout(layout)

    testEdit = QtGui.QLineEdit()
    testEdit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    
    globalLayout.addWidget(testEdit)
    globalLayout.addWidget(wnd)
    mainWidget.setLayout(globalLayout)
    mainWidget.show()
    # wnd.show()

    sys.exit(app.exec_())

if __name__=="__main__":
    main()
    