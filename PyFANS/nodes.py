from binding import Observable,notifiable_property
from PyQt4 import QtCore
from range_handlers import RANGE_HANDLERS, normal_range_handler, back_forth_range_handler,zero_start_range_handler,zero_start_back_forth


class SettingsModel(QtCore.QAbstractItemModel):

    sortRole   = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    """INPUTS: Node, QObject"""
    def __init__(self, root, parent=None):
        super(SettingsModel, self).__init__(parent)
        self._rootNode = root
        #if self._rootNode:
            #self._rootNode.addObserver(

    def _on_model_changed(self, row, column, parent):
        if isinstance(row,int) and isinstance(column, int):
            index = self.index(row, column,parent)
            self.dataChanged.emit(index, index)

    #index

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()


    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def columnCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.columnCount()
        

    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role):
        
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())
        
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))
        
        if role == SettingsModel.sortRole:
            return node.typeInfo()

        if role == SettingsModel.filterRole:
            return node.typeInfo()


    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        
        if index.isValid():
            
            node = index.internalPointer()
            
            if role == QtCore.Qt.EditRole:
                d = node.data(index.column()) 
                if d == value:
                    return False

                
                node.setData(index.column(),value)

                self.dataChanged.emit(index, index)
                return True
            
        return False

    
    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:                            
                if section == 0:
                    return "Settings"
                elif section == 1:
                    return "Typeinfo"
                else:
                    return "Value"
            else:
                return ""

        
    
    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    

    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""
    def parent(self, index):
        
        node = self.getNode(index)
        
        parentNode = node.parent()
        
        
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    #def parent_from_node(self,node):
        
    #    parentNode = node.parent()
        
    #    if parentNode == self._rootNode:
    #        return QtCore.QModelIndex()
    #    return self.createIndex(parentNode.row(),0,parentNode)


    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    def index(self, row, column, parent):
        
        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()



    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    
    """INPUTS: int, int, QModelIndex"""
    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        
        parentNode = self.getNode(parent)
        
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for row in range(rows):
            
            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)
        
        self.endInsertRows()

        return success
    


    """INPUTS: int, int, QModelIndex"""
    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        for row in range(rows):
            success = parentNode.removeChild(position)
            
        self.endRemoveRows()
        
        return success


#class ExperimentSettingsViewModel(QtCore.QAbstractListModel):
#    def __init__(self, settings = None, parent = None):
#        super(ExperimentSettingsViewModel,self).__init__(parent)#,parent)
#        self.__settings = settings #ExperimentSettings() #settings

#    def rowCount(self,index):
#        #return 1
#        if self.__settings:# amount of properties in ExperimentSettings class
#            return self.__settings.get_column_count()

#    #def columnCount(self, index):
#    #    if self.__settings:# amount of properties in ExperimentSettings class
#    #        return self.__settings.get_column_count()

#    """INPUTS: QModelIndex"""
#    """OUTPUT: int (flag)"""
#    def flags(self, index):
#        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

#    """INPUTS: QModelIndex, int"""
#    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
#    def data(self, index, role):
#        if not index.isValid():
#            return None
#        if not self.__settings:
#            return None

#        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
#            return self.__settings.data(index.row()) #.column())

#    def setData(self, index, value,role = QtCore.Qt.EditRole):
#        if not index.isValid():
#            return False

#        if role == QtCore.Qt.EditRole:
#            self.__settings.setData(index.row(),value)#.column(),value)
#            self.dataChanged.emit(index,index)
#            return True




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


###
### OLD version
### 
#class HardwareSettings(Node):
#    def __init__(self, name = 'hardware_settings', parent = None):
#        super().__init__(name, parent)
#        self.__dynamic_signal_analyzer_resource = ""
#        self.__main_gate_voltage_multimeter_resource = ""
#        self.__sample_voltage_multimeter_resource = ""
#        #self.__front_gate_voltage_multimeter_resource = ""
#        self.__arduino_controller_resource = ""
#        self.__sample_potentiometer_channel = 0
#        self.__gate_potentiometer_channel = 0

#    def typeInfo(self):
#        return "HardwareSettings"

#    @classmethod
#    def typeInfo(cls):
#        return "HardwareSettings"

#    @property
#    def dsa_resource(self):
#        return self.__dynamic_signal_analyzer_resource

#    @dsa_resource.setter
#    def dsa_resource(self,value):
#        self.__dynamic_signal_analyzer_resource = value

#    @property
#    def main_gate_multimeter_resource(self):
#        return self.__main_gate_voltage_multimeter_resource

#    @main_gate_multimeter_resource.setter
#    def main_gate_multimeter_resource(self,value):
#        self.__main_gate_voltage_multimeter_resource = value

#    @property
#    def sample_multimeter_resource(self):
#        return self.__sample_voltage_multimeter_resource
    
#    @sample_multimeter_resource.setter
#    def sample_multimeter_resource(self,value):
#        self.__sample_voltage_multimeter_resource = value

#    #@property
#    #def gate_multimeter_resource(self):
#    #    return self.__front_gate_voltage_multimeter_resource

#    #@gate_multimeter_resource.setter
#    #def gate_multimeter_resource(self,value):
#    #    self.__front_gate_voltage_multimeter_resource = value

#    @property
#    def arduino_controller_resource(self):
#        return self.__arduino_controller_resource

#    @arduino_controller_resource.setter
#    def arduino_controller_resource(self,value):
#        self.__arduino_controller_resource = value

#    @property
#    def sample_potentiometer_channel(self):
#        return self.__sample_potentiometer_channel

#    @sample_potentiometer_channel.setter
#    def sample_potentiometer_channel(self,value):
#        self.__sample_potentiometer_channel = value

#    @property
#    def gate_potentiometer_channel(self):
#        return self.__gate_potentiometer_channel

#    @gate_potentiometer_channel.setter
#    def gate_potentiometer_channel(self,value):
#        self.__gate_potentiometer_channel = value

#        #self.__dynamic_signal_analyzer_resource = 0
#        #self.__main_voltage_multimeter_resource = 0
#        #self.__sample_voltage_multimeter_resource = 0
#        #self.__front_gate_voltage_multimeter_resource = 0
#        #self.__arduino_controller_resource = 0
#        #self.__sample_potentiometer_channel = 0
#        #self.__gate_potentiometer_channel = 0

#    def data(self, column):
#        ret = super().data(column)
#        if column is 2: ret = self.dsa_resource
#        elif column is 3: ret = self.main_gate_multimeter_resource#.main_multimeter_resource
#        elif column is 4: ret = self.sample_multimeter_resource
#        #elif column is 5: ret = self.gate_multimeter_resource
#        elif column is 6: ret = self.arduino_controller_resource
#        elif column is 7: ret = self.sample_potentiometer_channel
#        elif column is 8: ret = self.gate_potentiometer_channel
#        return ret

#    def setData(self, column, value):
#        super().setData(column, value)
#        if column is 2: self.dsa_resource = value
#        elif column is 3: self.main_gate_multimeter_resource = value
#        elif column is 4: self.sample_multimeter_resource = value
#        #elif column is 5: self.gate_multimeter_resource = value
#        elif column is 6: self.arduino_controller_resource = value
#        elif column is 7: self.sample_potentiometer_channel = value
#        elif column is 8: self.gate_potentiometer_channel = value



class HardwareSettings(Node):
    def __init__(self, name = 'hardware_settings', parent = None):
        super().__init__(name, parent)
        self.__dynamic_signal_analyzer_resource = ""
        self.__main_sample_multimeter_resource = ""
        self.__gate_multimeter_resource = ""
        self.__fans_controller_resource = ""
        self.__sample_motor_channel = 0
        self.__sample_relay_channel = 0
        self.__gate_motor_channel = 0
        self.__gate_relay_channel = 0


    def typeInfo(self):
        return "HardwareSettings"

    @classmethod
    def typeInfo(cls):
        return "HardwareSettings"


    #self.__dynamic_signal_analyzer_resource = ""
    @property
    def dsa_resource(self):
        return self.__dynamic_signal_analyzer_resource

    @dsa_resource.setter
    def dsa_resource(self,value):
        self.__dynamic_signal_analyzer_resource = value

    
    #self.__gate_multimeter_resource = ""
    @property
    def gate_multimeter_resource(self):
        return self.__gate_multimeter_resource

    @gate_multimeter_resource.setter
    def gate_multimeter_resource(self,value):
        self.__gate_multimeter_resource = value

    #self.__main_sample_multimeter_resource = ""
    @property
    def main_sample_multimeter_resource(self):
        return self.__main_sample_multimeter_resource
    
    @main_sample_multimeter_resource.setter
    def main_sample_multimeter_resource(self,value):
        self.__main_sample_multimeter_resource = value

    #self.__fans_controller_resource = ""
    @property
    def fans_controller_resource(self):
        return self.__fans_controller_resource

    @fans_controller_resource.setter
    def fans_controller_resource(self,value):
        self.__fans_controller_resource = value

    
   #self.__sample_motor_channel = 0
    @property
    def sample_motor_channel(self):
        return self.__sample_motor_channel

    @sample_motor_channel.setter
    def sample_motor_channel(self,value):
        value = int(value)
        self.__sample_motor_channel = value


    #self.__sample_relay_channel = 0
    @property
    def sample_relay_channel(self):
        return self.__sample_relay_channel

    @sample_relay_channel.setter
    def sample_relay_channel(self,value):
        value = int(value)
        self.__sample_relay_channel = value


    #self.__gate_motor_channel = 0
    @property
    def gate_motor_channel(self):
        return self.__gate_motor_channel

    @gate_motor_channel.setter
    def gate_motor_channel(self,value):
        value = int(value)
        self.__gate_motor_channel = value

    #self.__gate_relay_channel = 0
    @property
    def gate_relay_channel(self):
        return self.__gate_relay_channel

    @gate_relay_channel.setter
    def gate_relay_channel(self,value):
        value = int(value)
        self.__gate_relay_channel = value
  
    def data(self, column):
        ret = super().data(column)
        if column is 2: ret = self.dsa_resource
        elif column is 3: ret = self.main_sample_multimeter_resource
        elif column is 4: ret = self.gate_multimeter_resource
        elif column is 5: ret = self.fans_controller_resource
        elif column is 6: ret = self.sample_motor_channel
        elif column is 7: ret = self.sample_relay_channel
        elif column is 8: ret = self.gate_motor_channel
        elif column is 9: ret = self.gate_relay_channel
        
        return ret

    def setData(self, column, value):
        super().setData(column, value)
        if column is 2: self.dsa_resource = value
        elif column is 3: self.main_sample_multimeter_resource = value
        elif column is 4: self.gate_multimeter_resource = value
        elif column is 5: self.fans_controller_resource = value
        elif column is 6: self.sample_motor_channel = value
        elif column is 7: self.sample_relay_channel = value
        elif column is 8: self.gate_motor_channel = value
        elif column is 9: self.gate_relay_channel = value
        

       
class ValueRange(Node):
    def __init__(self,name = "range", parent = None):
        super(ValueRange,self).__init__(name, parent)
        self.__start_val = 0
        self.__start_units = 0
        
        self.__end_val = 1
        self.__end_units = 0

        self.__points = 10

        self.__range_mode = 0

        self.__unit_values = [1, 0.001] # order in user interface must be V->mV
    
    @property
    def start_value(self):
        return self.__start_val

    @start_value.setter
    def start_value(self,value):
        self.__start_val = value

    @property
    def start_units(self):
        return self.__start_units
         
    @start_units.setter
    def start_units(self,value):
        self.__start_units = value

    @property
    def end_value(self):
        return self.__end_val

    @end_value.setter
    def end_value(self,value):
        self.__end_val = value

    @property
    def end_units(self):
        return self.__end_units
         
    @end_units.setter
    def end_units(self,value):
        self.__end_units = value

    @property
    def points(self):
        return self.__points

    
    @points.setter
    def points(self,value):
        self.__points = value

    @property
    def range_mode(self):
        return self.__range_mode    
        
    @range_mode.setter
    def range_mode(self,value):
        self.__range_mode = value

    

    def typeInfo(self):
        return "ValueRange"

    @classmethod
    def typeInfo(cls):
        return "ValueRange"

    def data(self, column):
        ret = super().data(column)
        if column is 2: ret = self.start_value
        elif column is 3: ret = self.start_units
        elif column is 4: ret = self.end_value
        elif column is 5: ret = self.end_units
        elif column is 6: ret = self.points
        elif column is 7: ret = self.range_mode
        return ret

    def setData(self, column, value):
        super().setData(column, value)
        if column is 2: self.start_value = value
        elif column is 3: self.start_units = value
        elif column is 4: self.end_value = value
        elif column is 5: self.end_units = value
        elif column is 6: self.points = value
        elif column is 7: self.range_mode = value

    def get_start_value(self):
        return self.start_value*self.__unit_values[self.start_units]

    def get_end_value(self):
        return self.end_value*self.__unit_values[self.end_units]

    def get_range_handler(self):
        if self.range_mode is 0: return normal_range_handler(self.get_start_value(), self.get_end_value(), len = self.points)
        elif self.range_mode is 1: return back_forth_range_handler(self.get_start_value(), self.get_end_value(), len = self.points)
        elif self.range_mode is 2: return zero_start_range_handler(self.get_start_value(), self.get_end_value(), len = self.points)
        elif self.range_mode is 3: return zero_start_back_forth(self.get_start_value(), self.get_end_value(), len = self.points)
        else:
            raise ValueError("Incorrect value of selected range handler")


class ExperimentSettings(Node):
    def __init__(self, name = "ExperimentSettings", parent = None):
        super(ExperimentSettings,self).__init__(name,parent)
        #this settings - separate class. shoy\uld be saved to file

        self.__simulate_experiment = False

        self.__working_directory = None
        self.__experiment_name = None
        self.__measurement_name = None
        self.__measurement_count  = 0
        
        self.__calibrate_before_measurement = False
        self.__overload_rejecion = False

        self.__display_refresh = 10
        self.__averages = 100

        self.__use_homemade_amplifier = True
        self.__homemade_amp_coeff = 178
        self.__use_second_amplifier = True
        self.__second_amp_coeff = 100

        self.__load_resistance = 5000
        
        self.__need_measure_temperature = False
        self.__meas_gated_structure = True
        self.__meas_characteristic_type = 0; # 0 is output 1 is transfer

        self.__use_automated_voltage_control = False

        self.__use_transistor_selector = False
        self.__transistor_list = None

        self.__use_set_vds_range = False
        #self.__vds_range = None
        #ValueRange("drain_source_range",self)

        self.__use_set_vfg_range = False
        #self.__vfg_range = None
        #ValueRange("front_gate_range",self)

        self.__front_gate_voltage = 0
        self.__drain_source_voltage = 0

    def get_column_count(self):
       return 24  # amount of properties in ExperimentSettings class

    def data(self,column):
        #super(ExperimentSettings,self).data

        #self.__working_directory = None
        if column is 0: return self.working_directory
        #self.__expeiment_name = None
        elif column is 1: return self.experiment_name
        #self.__measurement_name = None
        elif column is 2: return self.measurement_name
        #self.__measurement_count  = 0
        elif column is 3: return self.measurement_count

        
        #self.__calibrate_before_measurement = False
        elif column is 4: return self.calibrate_before_measurement
        #self.__overload_rejecion = False
        elif column is 5: return self.overload_rejecion

        #self.__display_refresh = 10
        elif column is 6: return self.display_refresh
        #self.__averages = 100
        elif column is 7: return self.averages

        #self.__use_homemade_amplifier = True
        elif column is 8: return self.use_homemade_amplifier
        #self.__homemade_amp_coeff = 178
        elif column is 9: return self.homemade_amp_coeff


        #self.__use_second_amplifier = True
        elif column is 10: return self.use_second_amplifier
        #self.__second_amp_coeff = 100
        elif column is 11: return self.second_amp_coeff

        #self.__load_resistance = 5000
        elif column is 12: return self.load_resistance

        #self.__need_measure_temperature = False
        elif column is 13: return self.need_measure_temperature

        #self.__meas_gated_structure = True
        elif column is 14: return self.meas_gated_structure
        #self.__meas_characteristic_type = 0; # 0 is output 1 is transfer
        elif column is 15: return self.meas_characteristic_type

        #self.__use_transistor_selector = False
        elif column is 16: return self.use_transistor_selector
        #self.__transistor_list = None
        elif column is 17: return self.transistor_list

        #self.__use_set_vds_range = False
        elif column is 18: return self.use_set_vds_range
        #self.__vds_range = None
        #elif column is 19: return self.vds_range

        #self.__use_set_vfg_range = False
        elif column is 20: return self.use_set_vfg_range
        #self.__vfg_range = None
        #elif column is 21: return self.vfg_range

        #self.__front_gate_voltage = 0
        elif column is 22: return self.front_gate_voltage
        #self.__drain_source_voltage = 0
        elif column is 23: return self.drain_source_voltage
        
        elif column is 24: return self.use_automated_voltage_control
        elif column is 25: return self.simulate_experiment
        else:
            return None

    def setData(self,column, value):
         #self.__working_directory = None
        if column is 0: self.working_directory = value
        #self.__expeiment_name = None
        elif column is 1:  self.experiment_name= value
        #self.__measurement_name = None
        elif column is 2:  self.measurement_name= value
        #self.__measurement_count  = 0
        elif column is 3:  self.measurement_count= value

        
        #self.__calibrate_before_measurement = False
        elif column is 4:  self.calibrate_before_measurement= value
        #self.__overload_rejecion = False
        elif column is 5:  self.overload_rejecion= value

        #self.__display_refresh = 10
        elif column is 6:  self.display_refresh= value
        #self.__averages = 100
        elif column is 7:  self.averages= value

        #self.__use_homemade_amplifier = True
        elif column is 8:  self.use_homemade_amplifier= value
        #self.__homemade_amp_coeff = 178
        elif column is 9:  self.homemade_amp_coeff= value


        #self.__use_second_amplifier = True
        elif column is 10:  self.use_second_amplifier= value
        #self.__second_amp_coeff = 100
        elif column is 11:  self.second_amp_coeff= value

        #self.__load_resistance = 5000
        elif column is 12:  self.load_resistance= value

        #self.__need_measure_temperature = False
        elif column is 13:  self.need_measure_temperature= value

        #self.__meas_gated_structure = True
        elif column is 14:  self.meas_gated_structure= value
        #self.__meas_characteristic_type = 0; # 0 is output 1 is transfer
        elif column is 15:  self.meas_characteristic_type= value

        #self.__use_transistor_selector = False
        elif column is 16:  self.use_transistor_selector= value
        #self.__transistor_list = None
        elif column is 17:  self.transistor_list= value

        #self.__use_set_vds_range = False
        elif column is 18:  self.use_set_vds_range= value
        #self.__vds_range = None
        #elif column is 19:  self.vds_range= value

        #self.__use_set_vfg_range = False
        elif column is 20:  self.use_set_vfg_range= value
        #self.__vfg_range = None
        #elif column is 21:  self.vfg_range= value

        #self.__front_gate_voltage = 0
        elif column is 22:  self.front_gate_voltage= value
        #self.__drain_source_voltage = 0
        elif column is 23:  self.drain_source_voltage= value
        elif column is 24: self.use_automated_voltage_control = value
        elif column is 25: self.simulate_experiment = value

    def typeInfo(self):
        return "ExperimentSettings"

    @classmethod
    def typeInfo(cls):
        return "ExperimentSettings"

    #@property
    #def vds_range(self):
    #    return self.__vds_range

    #@vds_range.setter
    #def vds_range(self,value):
    #    self.__vds_range = value

    #@property
    #def vfg_range(self):
    #    return self.__vfg_range

    #@vfg_range.setter
    #def vfg_range(self,value):
    #    self.__vfg_range = value

    @property
    def simulate_experiment(self):
        return self.__simulate_experiment

    @simulate_experiment.setter
    def simulate_experiment(self,value):
        self.__simulate_experiment = value

    @property 
    def use_automated_voltage_control(self):
        return self.__use_automated_voltage_control

    @use_automated_voltage_control.setter
    def use_automated_voltage_control(self, value):
        self.__use_automated_voltage_control = value


    @property
    def front_gate_voltage(self):
        return self.__front_gate_voltage

    @front_gate_voltage.setter
    def front_gate_voltage(self,value):
        self.__front_gate_voltage = value

    @property
    def drain_source_voltage(self):
        return self.__drain_source_voltage

    @drain_source_voltage.setter
    def drain_source_voltage(self,value):
        self.__drain_source_voltage = value

    @property
    def working_directory(self):
        return self.__working_directory

    @working_directory.setter
    def working_directory(self,value):
        self.__working_directory = value

    #self.__expeiment_name = None
    @property
    def experiment_name(self):
        return self.__experiment_name

    @experiment_name.setter
    def experiment_name(self,value):
        self.__experiment_name = value

    #self.__measurement_name = None
    @property
    def measurement_name(self):
        return self.__measurement_name

    @measurement_name.setter
    def measurement_name(self,value):
        self.__measurement_name = value

    #self.__measurement_count  = 0
    @property
    def measurement_count(self):
        return self.__measurement_count

    @measurement_count.setter
    def measurement_count(self,value):
        self.__measurement_count = value    


    #self.__calibrate_before_measurement = False
    @property
    def calibrate_before_measurement(self):
        return self.__calibrate_before_measurement

    @calibrate_before_measurement.setter
    def calibrate_before_measurement(self,value):
        self.__calibrate_before_measurement= value    

    #self.__overload_rejecion = False
    @property
    def overload_rejecion(self):
        return self.__overload_rejecion

    @overload_rejecion.setter
    def overload_rejecion(self,value):
        self.__overload_rejecion= value    

    #self.__display_refresh = 10
    @property
    def display_refresh(self):
        return self.__display_refresh

    @display_refresh.setter
    def display_refresh(self,value):
        self.__display_refresh= value    
    #self.__averages = 100
    @property
    def averages(self):
        return self.__averages

    @averages.setter
    def averages(self,value):
        self.__averages= value  

    #self.__use_homemade_amplifier = True
    @property
    def use_homemade_amplifier(self):
        return self.__use_homemade_amplifier

    @use_homemade_amplifier.setter
    def use_homemade_amplifier(self,value):
        self.__use_homemade_amplifier= value  


    #self.__homemade_amp_coeff = 178
    @property
    def homemade_amp_coeff(self):
        return self.__homemade_amp_coeff

    @homemade_amp_coeff.setter
    def homemade_amp_coeff(self,value):
        self.__homemade_amp_coeff= value  

    #self.__use_second_amplifier = True
    @property
    def use_second_amplifier(self):
        return self.__use_second_amplifier

    @use_second_amplifier.setter
    def use_second_amplifier(self,value):
        self.__use_second_amplifier= value 


    #self.__second_amp_coeff = 100
    @property
    def second_amp_coeff(self):
        return self.__second_amp_coeff

    @second_amp_coeff.setter
    def second_amp_coeff(self,value):
        self.__second_amp_coeff= value 

    #self.__load_resistance = 5000
    @property
    def load_resistance(self):
        return self.__load_resistance

    @load_resistance.setter
    def load_resistance(self,value):
        self.__load_resistance= value 
        
    #self.__need_measure_temperature = False
    @property
    def need_measure_temperature(self):
        return self.__need_measure_temperature

    @need_measure_temperature.setter
    def need_measure_temperature(self,value):
        self.__need_measure_temperature= value 

    #self.__meas_gated_structure = True
    @property
    def meas_gated_structure(self):
        return self.__meas_gated_structure

    @meas_gated_structure.setter
    def meas_gated_structure(self,value):
        self.__meas_gated_structure= value 
   
    #self.__meas_characteristic_type = 0; # 0 is output 1 is transfer
    @property
    def meas_characteristic_type(self):
        return self.__meas_characteristic_type

    @meas_characteristic_type.setter
    def meas_characteristic_type(self,value):
        self.__meas_characteristic_type= value

    #self.__use_transistor_selector = False
    @property
    def use_transistor_selector(self):
        return self.__use_transistor_selector

    @use_transistor_selector.setter
    def use_transistor_selector(self,value):
        self.__use_transistor_selector= value

    #self.__transistor_list = None
    @property
    def transistor_list(self):
        return self.__transistor_list

    @transistor_list.setter
    def transistor_list(self,value):
        self.__transistor_list= value

    #self.__use_set_vds_range = False
    @property
    def use_set_vds_range(self):
        return self.__use_set_vds_range

    @use_set_vds_range.setter
    def use_set_vds_range(self,value):
        self.__use_set_vds_range= value
    #self.__use_set_vfg_range = False
    @property
    def use_set_vfg_range(self):
        return self.__use_set_vfg_range

    @use_set_vfg_range.setter
    def use_set_vfg_range(self,value):
        self.__use_set_vfg_range= value
