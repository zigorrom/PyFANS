import pint 
from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore
import ui_helper as uih
import range_handlers as rh


class RangeItemModel(QtCore.QAbstractTableModel): 
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    def __init__(self, parent=None, *args): 
        super(RangeItemModel, self).__init__()
        self.datatable = []
        #self.datatable.append(RangeItem("rng_1",None))
        #self.datatable.append(RangeItem("rng_4",None))

    def get_composite_range(self):
        return self.datatable

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable) 

    def columnCount(self, parent=QtCore.QModelIndex()):
        return RangeItem.COLUMN_COUNT

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        node = self.datatable[row]
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())
        
        #if role == QtCore.Qt.DecorationRole:
        #    if index.column() == RangeItem.NAME_OPTION:
        #        resource = node.resource()
        #        return QtGui.QIcon(QtGui.QPixmap(resource))
        
        if role == self.sortRole:
            return node.typeInfo()

        if role == self.filterRole:
            return node.typeInfo()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            row = index.row()
            column = index.column()
            node = self.datatable[row] #index.internalPointer()
            if role == QtCore.Qt.EditRole:
                node.setData(column,value)
                stop_index = self.createIndex(row,RangeItem.COLUMN_COUNT, index.parent())
                

                self.dataChanged.emit(index, stop_index)
                return True
        return False

        #if role == QtCore.Qt.DisplayRole:
        #    i = index.row()
        #    j = index.column()
        #    return '{0}'.format(self.datatable.iget_value(i, j))
        #else:
        #    return QtCore.QVariant()
    def addItem(self):
        item = RangeItem("Range {0}".format(self.rowCount()), None)
        self.datatable.append(item)
        index = QtCore.QModelIndex()
        self.dataChanged.emit(index,index)

    def removeItem(self, row):
        if not self.datatable:
            return
        if row >=0:
            if row < self.rowCount():
                del self.datatable[row]
        else:
            del self.datatable[-1]

        index = QtCore.QModelIndex()
        self.dataChanged.emit(index,index)
    
    def removeAllItems(self):
        self.datatable.clear()
        index = QtCore.QModelIndex()
        self.dataChanged.emit(index,index)

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable



class RangeItem(QtGui.QStandardItem):
    ureg = UnitRegistry()
    #string_to_volt_converter = uih.string_to_volt_converter(ureg)
    TYPE_NAME = "RANGE ITEM"
    NAME_OPTION = 0
    TYPE_OPTION = 1
    RANGE_START_OPTION = 2
    RANGE_END_OPTION = 3
    RANGE_COUNT_OPTION = 4
    RANGE_STEP_OPTION = 5
    COLUMN_COUNT = 6

    def __init__(self, range_name, rng, **kwargs):
        super().__init__(**kwargs)
        self._range_name = range_name
        if not isinstance(rng, rh.float_range):
            rng = rh.float_range(0,0)
        self._rng = rng

    def columnCount(self):
        return RangeItem.COLUMN_COUNT #(NUMBER OF OPTIONS)

    @property
    def range_item(self):
        return self._rng

    def typeInfo(self):
        return RangeItem.TYPE_NAME

    @classmethod
    def typeInfo(cls):
        return RangeItem.TYPE_NAME

    @property
    def range_name(self):
        return self._range_name

    @property
    def range_start(self):
        return self._rng.start

    @range_start.setter
    def range_start(self, value):
        self._rng.start = value 

    @property
    def range_stop(self):
        return self._rng.stop

    @range_stop.setter
    def range_stop(self, value):
        self._rng.stop = value

    @property
    def count(self):
        return self._rng.length

    @count.setter
    def count(self, value):
        self._rng.length = value

    @property
    def step(self):
        return self._rng.step

    @step.setter
    def step(self, value):
        self._rng.step = value

    def data(self,column):
        #print("getting data col:{0}".format(column))
        if column is RangeItem.NAME_OPTION: return self.range_name
        elif column is RangeItem.TYPE_OPTION: return self.typeInfo()
        elif column is RangeItem.RANGE_START_OPTION: return self.range_start
        elif column is RangeItem.RANGE_END_OPTION: return self.range_stop
        elif column is RangeItem.RANGE_COUNT_OPTION: return self.count
        elif column is RangeItem.RANGE_STEP_OPTION: return self.step
        else: return None
        
    def setData(self,column,value):
        #print("setting data")
        if column is RangeItem.NAME_OPTION: 
            self.range_name=value
            return True
        elif column is RangeItem.TYPE_OPTION: 
            return True
        elif column is RangeItem.RANGE_START_OPTION: 
            value = uih.convert_value_to_volts(self.ureg, value) #self.string_to_volt_converter(value) #float(value)
            self.range_start = value
            return True
        elif column is RangeItem.RANGE_END_OPTION: 
            value = uih.convert_value_to_volts(self.ureg, value) #float(value)
            self.range_stop = value
            return True
        elif column is RangeItem.RANGE_COUNT_OPTION: 
            value = int(value)
            self.count = value
            return True
        elif column is RangeItem.RANGE_STEP_OPTION: 
            #value = float(value)
            #self.step = value
            return True
        else:
            return False




compositeRangeSelectorBase, compositeRangeSelectorForm = uic.loadUiType("UI/UI_RangeSelector_v4.ui")
class CompositeRangeSelectorView(compositeRangeSelectorBase, compositeRangeSelectorForm ):
    def __init__(self, parent = None):
        super(compositeRangeSelectorBase, self).__init__(parent)
        self.setupUi()
        self.model = RangeItemModel() 
        self.data_mapper = QtGui.QDataWidgetMapper(self)
        self.setModel(self.model)
        self.selected_row = -1
        #self.ui_start_val.textChanged.connect(self.submit_changes_to_model)
        #self.ui_stop_val.textChanged.connect(self.submit_changes_to_model)
        #self.ui_count.valueChanged.connect(self.submit_changes_to_model)
    #def submit_changes_to_model(self):
    #    self.data_mapper.submit()

    def setModel(self, model):
        self.ui_range_list.setModel(model)
        self.data_mapper.setModel(model)
        #self.data_mapper.setSubmitPolicy(QtGui.QDataWidgetMapper.ManualSubmit)
        self.data_mapper.addMapping(self.ui_start_val, RangeItem.RANGE_START_OPTION)
        self.data_mapper.addMapping(self.ui_stop_val, RangeItem.RANGE_END_OPTION)
        self.data_mapper.addMapping(self.ui_count, RangeItem.RANGE_COUNT_OPTION)
        self.data_mapper.addMapping(self.ui_step, RangeItem.RANGE_STEP_OPTION)
        self.ui_range_list.clicked.connect(self.setSelection)
        self.data_mapper.toFirst()

    def setSelection(self, current):
        #parent = current.parent()
        self.data_mapper.setCurrentModelIndex(current)
        self.selected_row = current.row()

    def setupUi(self):
        super().setupUi(self)

    def get_range(self):
        pass

    @QtCore.pyqtSlot()
    def on_ui_add_range_clicked(self):
        print("adding")
        self.model.addItem()

    @QtCore.pyqtSlot()
    def on_ui_remove_range_clicked(self):
        print("removing")
        print(self.selected_row)
        self.model.removeItem(self.selected_row)
        self.selected_row = -1

    @QtCore.pyqtSlot()
    def on_ui_reset_ranges_clicked(self):
        print("resetting")
        self.model.removeAllItems()


rangeSelectorBase, rangeSelectorForm = uic.loadUiType("UI/UI_RangeSelector_v3.ui")
class RangeSelectorView(rangeSelectorBase,rangeSelectorForm):
    ureg = UnitRegistry()
    voltage_start = uih.bind("ui_start_val", "text", uih.string_to_volt_converter(ureg))
    voltage_stop = uih.bind("ui_stop_val", "text", uih.string_to_volt_converter(ureg))
    voltage_step = uih.bind("ui_step", "text", uih.string_to_volt_converter(ureg))
    counts = uih.bind("ui_count", "value", int)
    range_handler = uih.bind("ui_range_mode", "currentIndex", int)
    repeats = uih.bind("ui_repeats", "value", int)

    def __init__(self, parent = None):
        super(rangeSelectorBase,self).__init__(parent)
        self.setupUi()
        self._value_range = None
        #self._range_handler = None
        

    def setupUi(self):
        super().setupUi(self)
        self.ui_start_val.setValidator(uih.QVoltageValidator())
        self.ui_stop_val.setValidator(uih.QVoltageValidator())

    def set_range(self, value_range):
        assert isinstance(value_range, rh.RangeObject)
        self._value_range = value_range
        self.refresh_view()

    def get_range(self):
        return self._value_range

    def refresh_view(self):
        if isinstance(self._value_range, rh.RangeObject) and isinstance(self._value_range.floatRange, rh.float_range):
            uih.setAllChildObjectSignaling(self, True)
            self.voltage_start = self._value_range.floatRange.start
            self.voltage_stop = self._value_range.floatRange.stop
            self.voltage_step = self._value_range.floatRange.step
            self.counts = self._value_range.floatRange.length
            self.range_handler = self._value_range.rangeHandler.value
            self.repeats = self._value_range._repeats
            uih.setAllChildObjectSignaling(self, False)

    def refresh_step_count(self):
        if isinstance(self._value_range, rh.RangeObject) and isinstance(self._value_range.floatRange, rh.float_range):
            uih.setAllChildObjectSignaling(self, True)
            self.voltage_step = self._value_range.floatRange.step
            self.counts = self._value_range.floatRange.length
            uih.setAllChildObjectSignaling(self, False)

    @QtCore.pyqtSlot(str)
    def on_ui_start_val_textChanged(self, value):
        if self._value_range:
            val = self.voltage_start
            self._value_range.floatRange.start = val 
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(str)
    def on_ui_stop_val_textChanged(self, value):
        if self._value_range:
            self._value_range.floatRange.stop = self.voltage_stop
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(str)
    def on_ui_count_valueChanged(self, value):
        if self._value_range:
            self._value_range.floatRange.length = self.counts
            self.voltage_step = self._value_range.floatRange.step
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(int)
    def on_ui_range_mode_currentIndexChanged(self, value):
        if self._value_range:
            self._value_range.rangeHandler = rh.RANGE_HANDLERS(value)

    @QtCore.pyqtSlot(int)
    def on_ui_repeats_valueChanged(self, value):
        if self._value_range:
            self._value_range.rangeRepeats = value



def test_RangeSelectorView():
    app = QtGui.QApplication([])
    
    vr = rh.float_range(0,10,0.1)
    ro = rh.RangeObject(vr)
    

    wnd = RangeSelectorView()
    wnd.set_range(ro)
    wnd.exec_()
    return app.exec_()

def test_CompositeRangeSelectorView():
    app = QtGui.QApplication([])
    
    wnd = CompositeRangeSelectorView()
    
    wnd.exec_()
    return app.exec_()


if __name__ == "__main__":
    import sys
    sys.exit(test_RangeSelectorView())
    # sys.exit(test_CompositeRangeSelectorView())