from PyQt4 import QtCore, QtGui, uic
import sys

class Node(QtCore.QObject):
    
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
        child.parent = self

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
        pass

    def setData(self,column,value):
        pass

    def resource(self):
        pass

    

class LabelNode(Node):
    def __init__(self,name, label = "",parent=None):
        super().__init__(name,parent)

        self._label = label

    def typeInfo(self):
        return "LABEL"

    def label(self):
        return self._label

    def set_label(self, label):
        self._label = label

class NumericNode(Node):
    def __init__(self,name,  value = 10,parent = None):
        super().__init__(name,parent)
        self._value = value
        

    def typeInfo(self):
        return "NUMERIC"

    def value(self):
        return self._value

    def set_value(self,value):
        self._value = value

class CheckNode(Node):
    def __init__(self,name,checked = False, parent=None):
        super().__init__(name,parent)
        self._checked = checked

    def typeInfo(self):
        return "CHECK"

    def is_checked(self):
        return self._checked

    def set_value(self,value):
        self._checked = value
    
class ComboNode(Node):
    def __init__(self,name,case_list = [], parent=None):
        super().__init__(name,parent)
        self._case_list = case_list
        self._selectedIndex = 0


    def typeInfo(self):
        return "COMBO"

    def selectedIndex(self):
        return self._selectedIndex

    def set_selectionIndex(self,index):
        self._selectedIndex = index

    def case_list(self):
        return self._case_list

    def set_case_list(self,case_list):
        self._case_list = case_list


class InChannelNode(Node):
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self._enabled = CheckNode(name+"_enabled", parent = self)
        self._range = ComboNode(name+"_range", parent = self)
        self._polarity = ComboNode(name+"_polarity",parent = self)
        self._function = ComboNode(name+"_function",parent=  self)


    def typeInfo(self):
        return "IN_CHANNEL"

##    def enabled(self):
##        return self._enabled.is_checked()
##
##    def set_enabled(self, value):
##        self._enabled.setValue(value)


class OutChannelNode(Node):
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self._enabled = CheckNode(name+"_enabled", parent = self)
        self._range = ComboNode(name+"_range", parent = self)
        self._polarity = ComboNode(name+"_polarity",parent = self)
        self._output_pin = ComboNode(name+"_out_pin",parent = self)
        self._function = ComboNode(name+"_function",parent=  self)

    def typeInfo(self):
        return "OUT_CHANNEL"

class AcquisitionSettingsNode(Node):
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
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
        return 1

    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role):
        
        if not index.isValid():
            return None

        node = index.internalPointer()
        typeInfo = node.typeInfo()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()
            
            if index.column() == 1:
                return typeInfo

            if typeInfo == "LABEL":
                if index.column() == 2:
                    return node.label()
                
       
            if typeInfo == "NUMERIC":
                if index.column() == 2:
                    return node.value()
                
                
            if typeInfo == "CHECK":
                if index.column() == 2:
                    return node.is_checked()
                

            if typeInfo == "COMBO":
                if index.column() == 2:
                    return node.selectedIndex()
                


        
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo = node.typeInfo()
                
##                if typeInfo == "LIGHT":
##                    return QtGui.QIcon(QtGui.QPixmap(":/Light.png"))
##                
##                if typeInfo == "TRANSFORM":
##                    return QtGui.QIcon(QtGui.QPixmap(":/Transform.png"))
##                
##                if typeInfo == "CAMERA":
##                

        
        if role == SettingsModel.sortRole:
            return node.typeInfo()

        if role == SettingsModel.filterRole:
            return node.typeInfo()


    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            
            node = index.internalPointer()
            typeInfo = node.typeInfo()
            
            if role == QtCore.Qt.EditRole:
                          
                if index.column() == 0:
                    node.setName(value)

                if typeInfo == "LABEL":
                    if index.column() == 2:
                        return node.set_label()
                
       
                if typeInfo == "NUMERIC":
                    if index.column() == 2:
                        return node.set_value()
                    
                    
                if typeInfo == "CHECK":
                    if index.column() == 2:
                        return node.set_value()
                    

                if typeInfo == "COMBO":
                    if index.column() == 2:
                        return node.set_selectedIndex()    
                        


                self.dataChanged.emit(index, index)
                return True
            
        return False

    
    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Settings"
            else:
                return "Typeinfo"

        
    
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
        
        print(node.typeInfo())
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

##        print(type(rootNode))
        acq_settings = AcquisitionSettingsNode("acquisition_settings", rootNode)
        selected_channel = LabelNode("selected_channel",acq_settings)
        sample_rate = NumericNode("sample_rate",acq_settings)
        pps = NumericNode("points per shot", acq_settings)
        hma = CheckNode("homemade amp",acq_settings)
        pga = ComboNode("pga",acq_settings)
        fg = ComboNode("fg",acq_settings)
        fc = ComboNode("fc",acq_settings)

        inp_settings = Node("input_settings", rootNode)
        ch1 = InChannelNode("ch1",inp_settings)
        ch2 = InChannelNode("ch2",inp_settings)
        ch3 = InChannelNode("ch3",inp_settings)
        ch4 = InChannelNode("ch4",inp_settings)



        out_settings = Node("out_settings", rootNode)
        och1 = OutChannelNode("och1",out_settings)
        och2 = OutChannelNode("och2",out_settings)


        self._proxyModel = QtGui.QSortFilterProxyModel(self)
        self._model = SettingsModel(rootNode, self)

        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        self._proxyModel.setSortRole(SettingsModel.sortRole)
        self._proxyModel.setFilterRole(SettingsModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)
        
        self.treeView.setModel(self._proxyModel)
        
##        QtCore.QObject.connect(self.uiFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        
        self.treeView.setSortingEnabled(True)

##        QtCore.QObject.connect(self.treeView.selectionModel(), QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"), self._propEditor.setSelection)


if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")
    
    wnd = WndTutorial()
    wnd.show()

    sys.exit(app.exec_())