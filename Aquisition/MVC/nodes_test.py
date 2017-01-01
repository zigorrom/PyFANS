from PyQt4 import QtCore, QtGui, uic
import sys

class Node(object):
    
    def __init__(self, name, parent=None):
        
        super(Node, self).__init__()
        
        self._name = name
        self._children = []
        self._parent = parent
        
        if parent is not None:
            parent.addChild(self)


    def typeInfo(self):
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

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]
    
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
        if      column is 0: return self.name()
        elif    column is 1: return self.typeInfo()
        

    def setData(self,column,value):
        if column is 0: self.setName(value)#.toPyObject())
        elif column is 1: pass

    def resource(self):
        return None

    

class LabelNode(Node):
    def __init__(self,name, label = "",parent=None):
        super(LabelNode,self).__init__(name,parent)

        self._label = label

    def typeInfo(self):
        return "LABEL"

    def label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def data(self,column):
        r = super(LabelNode,self).data(column)
        if column is 2: r = self.label()
        return r

    def setData(self,column,value):
        super(LabelNode,self).setData(column,value)
        if column is 2: self.set_label(value)#.toPyObject())
        

    
    

class NumericNode(Node):
    def __init__(self,name,  value = 10,parent = None):
        super(NumericNode,self).__init__(name,parent)
        self._value = value
        

    def typeInfo(self):
        return "NUMERIC"

    def value(self):
        return self._value

    def set_value(self,value):
        self._value = value

    def data(self,column):
        r = super(NumericNode,self).data(column)
        if column is 2: r = self.value()
        return r

    def setData(self,column,value):
        super(NumericNode,self).setData(column,value)
        if column is 2: self.set_value(value)#.toPyObject())
    

class CheckNode(Node):
    def __init__(self,name,checked = False, parent=None):
        super(CheckNode,self).__init__(name,parent)
        self._checked = checked

    def typeInfo(self):
        return "CHECK"

    def is_checked(self):
        return self._checked

    def set_value(self,value):
        self._checked = value


    def data(self,column):
        r = super(CheckNode,self).data(column)
        if column is 2: r = self.is_checked()
        return r

    def setData(self,column,value):
        super(CheckNode,self).setData(column,value)
        if column is 2: self.set_value(value)#.toPyObject())

    
class ComboNode(Node):
    def __init__(self,name,case_list = [], parent=None):
        super(ComboNode,self).__init__(name,parent)
        self._case_list = case_list
        self._selectedIndex = 0


    def typeInfo(self):
        return "COMBO"

    def selectedIndex(self):
        return self._selectedIndex

    def set_selectedIndex(self,index):
        self._selectedIndex = index

    def case_list(self):
        return self._case_list

    def set_case_list(self,case_list):
        self._case_list = case_list


    def data(self,column):
        r = super(ComboNode,self).data(column)
        if column is 2: r = self.selectedIndex()
        return r

    def setData(self,column,value):
        super(ComboNode,self).setData(column,value)
        if column is 2: self.set_selectedIndex(value)#.toPyObject())


class InChannelNode(Node):
    def __init__(self,name,parent=None):
        super(InChannelNode,self).__init__(name,parent)
        self._enabled = CheckNode(name+"_enabled", parent = self)
        self._range = ComboNode(name+"_range", case_list=['One','Two','Three'], parent = self)
        self._polarity = ComboNode(name+"_polarity",case_list=['Unipolar','Bipolar'],parent = self)
        self._function = ComboNode(name+"_function",case_list=['Vds','Vlg','Vbg'],parent=  self)

    def enabled(self):
        return self._enabled.is_checked()

    def set_enabled(self,value):
        self._enabled.set_value(value)

    def enabled_label(self):
        return self._enabled.name()

    def selected_range(self):
        return self._range.selectedIndex()

    def set_selected_range(self,value):
        self._range.set_selectedIndex(value)

    def range_label(self):
        return self._range.name()

    def selected_polarity(self):
        return self._polarity.selectedIndex()

    def set_selected_polarity(self,value):
        self._polarity.set_selectedIndex(value)

    def polarity_label(self):
        return self._polarity.name()

    def selected_function(self):
        return self._function.selectedIndex()

    def set_selected_function(self,value):
        self._function.set_selectedIndex(value)

    def function_label(self):
        return self._function.name()

    def typeInfo(self):
        return "IN_CHANNEL"

    def columnCount(self):
        return 3

    def data(self, column):
        r = super(InChannelNode,self).data(column)
        if column is 2:     r = self.enabled()
        elif column is 3:   r = self.selected_range()
        elif column is 4:   r = self.selected_polarity()
        elif column is 5:   r = self.selected_function()
        elif column is 6:   r = self.enabled_label()
        elif column is 7:   r = self.range_label()
        elif column is 8:   r = self.polarity_label()
        elif column is 9:   r = self.function_label()
        return r

    def setData(self, column, value):
        super(InChannelNode,self).setData(column,value)
        if column is 2:     self.set_enabled(value)
        elif column is 3:   self.set_selected_range(value)
        elif column is 4:   self.set_selected_polarity(value)
        elif column is 5:   self.set_selected_function(value)
        

class OutChannelNode(Node):
    def __init__(self,name,parent=None):
        super(OutChannelNode,self).__init__(name,parent)
        self._enabled = CheckNode(name+"_enabled", parent = self)
        self._range = ComboNode(name+"_range", parent = self)
        self._polarity = ComboNode(name+"_polarity",parent = self)
        self._output_pin = ComboNode(name+"_out_pin",parent = self)
        self._function = ComboNode(name+"_function",parent=  self)

    def typeInfo(self):
        return "OUT_CHANNEL"


class AcquisitionSettingsNode(Node):
    def __init__(self,name,parent=None):
        super(AcquisitionSettingsNode,self).__init__(name,parent)
        self._sample_rate = NumericNode("sample_rate", parent = self)
        self._points_per_shot = NumericNode("points_per_shot", parent = self)
        self._homemade_amplifier = CheckNode("homemade_amplifier", parent = self)
        self._pga_gain = ComboNode("pga_gain",parent = self)
        self._filter_gain = ComboNode("filter_gain", parent = self)
        self._filter_cutoff = ComboNode("filter_cutoff",parent = self)

    def typeInfo(self):
        return "ACQUISITION_SETTINGS"


class SettingsModel(QtCore.QAbstractItemModel):

    sortRole   = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    """INPUTS: Node, QObject"""
    def __init__(self, root, parent=None):
        super(SettingsModel, self).__init__(parent)
        self._rootNode = root

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



base, form = uic.loadUiType("main.ui")

class WndTutorial(base,form):
    def __init__(self,parent = None):
        super(base,self).__init__(parent)
        self.setupUi(self)

        rootNode = Node("Settings")

        acq_settings = AcquisitionSettingsNode("acquisition_settings",parent = rootNode)

        inp_settings = Node("input_settings", parent = rootNode)

        ch1 = InChannelNode("ch1",inp_settings)
        ch2 = InChannelNode("ch2",inp_settings)
        ch3 = InChannelNode("ch3",inp_settings)
        ch4 = InChannelNode("ch4",inp_settings)



        out_settings = Node("out_settings", parent = rootNode)

        och1 = OutChannelNode("och1",out_settings)
        och2 = OutChannelNode("och2",out_settings)

##        print(rootNode)

        self._proxyModel = QtGui.QSortFilterProxyModel(self)
        self._model = SettingsModel(rootNode, self)

        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        self._proxyModel.setSortRole(SettingsModel.sortRole)
        self._proxyModel.setFilterRole(SettingsModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)
        
        self.treeView.setModel(self._proxyModel)
        
        QtCore.QObject.connect(self.uiFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        
        self.treeView.setSortingEnabled(True)

        self._propEditor = PropertiesEditor(self)
        self.layoutMain.addWidget(self._propEditor)
        self._propEditor.setModel(self._proxyModel)

        QtCore.QObject.connect(self.treeView.selectionModel(), QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"), self._propEditor.setSelection)

propBase, propForm = uic.loadUiType("PropertiesLayout.ui")
"""PROPERTIESEDITOR"""
class PropertiesEditor(propBase, propForm):
    
    def __init__(self, parent = None):
        super(propBase, self).__init__(parent)
        self.setupUi(self)

        self._proxyModel = None
        
        self._nodeEditor = NodeEditor(self)
        self._labelEditor = LabelEditor(self)
        self._comboEditor = ComboEditor(self)
        self._checkEditor = CheckEditor(self)
        self._numericEditor = NumericEditor(self)
        self._inChannelEditor = InChannelEditor(self)

        
        self.layoutNode.addWidget(self._nodeEditor)
        self.layoutSpecs.addWidget(self._labelEditor)
        self.layoutSpecs.addWidget(self._comboEditor)
        self.layoutSpecs.addWidget(self._checkEditor)
        self.layoutSpecs.addWidget(self._numericEditor)
        self.layoutSpecs.addWidget(self._inChannelEditor)
        

        self._labelEditor.setVisible(False)
        self._comboEditor.setVisible(False)
        self._checkEditor.setVisible(False)
        self._numericEditor.setVisible(False)
        self._inChannelEditor.setVisible(False)
               
    """INPUTS: QModelIndex, QModelIndex"""
    def setSelection(self, current, old):

        current = self._proxyModel.mapToSource(current)

        node = current.internalPointer()
        
        if node is not None:
            typeInfo = node.typeInfo()
            
        if typeInfo == "LABEL":
            self._labelEditor.setVisible(True)
            self._comboEditor.setVisible(False)
            self._checkEditor.setVisible(False)
            self._numericEditor.setVisible(False)
            self._inChannelEditor.setVisible(False)
            self._labelEditor.setSelection(current)
        elif typeInfo == "COMBO":
            self._comboEditor.setVisible(True)
            self._labelEditor.setVisible(False)
            self._checkEditor.setVisible(False)
            self._numericEditor.setVisible(False)
            self._inChannelEditor.setVisible(False)
            self._comboEditor.setSelection(current)
        elif typeInfo == "CHECK":
            self._comboEditor.setVisible(False)
            self._labelEditor.setVisible(False)
            self._checkEditor.setVisible(True)
            self._numericEditor.setVisible(False)
            self._inChannelEditor.setVisible(False)
            self._checkEditor.setSelection(current)
        elif typeInfo == "NUMERIC":
            self._comboEditor.setVisible(False)
            self._labelEditor.setVisible(False)
            self._checkEditor.setVisible(False)
            self._numericEditor.setVisible(True)
            self._inChannelEditor.setVisible(False)
            self._numericEditor.setSelection(current)
        elif typeInfo == "IN_CHANNEL":
            self._comboEditor.setVisible(False)
            self._labelEditor.setVisible(False)
            self._checkEditor.setVisible(False)
            self._numericEditor.setVisible(False)
            self._inChannelEditor.setVisible(True)
            self._inChannelEditor.setSelection(current)
            pass
            
        else:
            self._labelEditor.setVisible(False)
            self._comboEditor.setVisible(False)
            self._checkEditor.setVisible(False)
            self._numericEditor.setVisible(False)
            self._inChannelEditor.setVisible(False)
            
        self._nodeEditor.setSelection(current)
    
    def setModel(self, proxyModel):
        
        self._proxyModel = proxyModel
        
        self._nodeEditor.setModel(proxyModel)
        self._labelEditor.setModel(proxyModel)
        self._comboEditor.setModel(proxyModel)
        self._checkEditor.setModel(proxyModel)
        self._numericEditor.setModel(proxyModel)
        self._inChannelEditor.setModel(proxyModel)



        

nodeBase, nodeForm = uic.loadUiType("NodeProperties.ui") 
class NodeEditor(nodeBase, nodeForm):
    
    def __init__(self, parent=None):
        super(nodeBase, self).__init__(parent)
        
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper()
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiType, 1)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        
        self._dataMapper.setCurrentModelIndex(current)

labelBase, labelForm = uic.loadUiType("LabelWidget.ui")
class LabelEditor(labelBase, labelForm):
    def __init__(self,parent = None):
        super(labelBase,self).__init__(parent)
        self.setupUi(self)

        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())

        self._dataMapper.addMapping(self.ui_name,0,"text")
        self._dataMapper.addMapping(self.ui_label,2)

    def setSelection(self,current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


numericBase, numericForm = uic.loadUiType("NumericWidget.ui")
class NumericEditor(numericBase, numericForm):
    def __init__(self,parent = None):
        super(numericBase,self).__init__(parent)
        self.setupUi(self)

        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())

        self._dataMapper.addMapping(self.ui_name,0,"text")
        self._dataMapper.addMapping(self.ui_number,2)

    def setSelection(self,current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        

checkBase, checkForm = uic.loadUiType("CheckWidget.ui")
class CheckEditor(checkBase, checkForm):
    def __init__(self,parent = None):
        super(checkBase,self).__init__(parent)
        self.setupUi(self)
        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())

        self._dataMapper.addMapping(self.ui_name,0,"text")
        self._dataMapper.addMapping(self.ui_check,2)
        
    def setSelection(self,current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
    

comboBase, comboForm = uic.loadUiType("ComboWidget.ui")
class ComboEditor(comboBase, comboForm):
    def __init__(self,parent = None):
        super(comboBase,self).__init__(parent)
        self.setupUi(self)

        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        
        self._dataMapper.addMapping(self.ui_name,0,"text")
        self._dataMapper.addMapping(self.ui_combo,2,"currentIndex")

    def setSelection(self,current):
        node = self._proxyModel.sourceModel().getNode(current)
        self.ui_combo.clear()
        self.ui_combo.addItems(node.case_list())
        parent = current.parent()
        
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        

inChannelBase, inChannelForm = uic.loadUiType("InChannelWidget - Copy.ui")
class InChannelEditor(inChannelBase, inChannelForm):
    def __init__(self,parent = None):
        super(inChannelBase,self).__init__(parent)
        self.setupUi(self)

##        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self.ui_tableView.setModel(proxyModel.sourceModel())
##        self._dataMapper.setModel(proxyModel.sourceModel())
##        self._dataMapper.addMapping(self.ui_tableView,2)
##
##        self._dataMapper.addMapping(self.ui_enabled,2)
##        self._dataMapper.addMapping(self.ui_range,3)
##        self._dataMapper.addMapping(self.ui_polarity,4)
##        self._dataMapper.addMapping(self.ui_function,5)
##
##        self._dataMapper.addMapping(self.ui_en_label,6,"text")
##        self._dataMapper.addMapping(self.ui_rang_label,7,"text")
##        self._dataMapper.addMapping(self.ui_pol_label,8,"text")
##        self._dataMapper.addMapping(self.ui_func_label,9,"text")
        
    
    def setSelection(self,current):
        parent = current.parent()
        self.ui_tableView.setRootIndex(current)#parent)
##        self.ui_tableView.setCurrentModelIndex(current)
##        self._dataMapper.setRootIndex(parent)
##        self._dataMapper.setCurrentModelIndex(current)
    




if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")
    
    wnd = WndTutorial()
    wnd.show()

    sys.exit(app.exec_())
