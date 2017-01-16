from PyQt4 import QtCore, QtGui, QtXml,uic
from xml_highlighter import XMLHighlighter
from nodes import *
import sys
from node_configuration import Configuration 


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



base, form = uic.loadUiType("Views/main.ui")

class WndTutorial(base,form):
    def updateXml(self):
        print("Updating xml")
##        xml = self._rootNode.asXml()

        s = XmlNodeSerializer()
        xml = s.serialize(self._rootNode)
        self.ui_xml.setPlainText(xml)
        node = s.deserialize(xml)
        print("\n"*3)
        print("AFTER DESERIALIZATION")
        print(node)

        self.config.save_config()
            
        

    def __init__(self,parent = None):
        super(base,self).__init__(parent)
        self.setupUi(self)
        self.config = Configuration()
        self._rootNode = self.config.get_root_node()

        self._proxyModel = QtGui.QSortFilterProxyModel(self)
        self._model = SettingsModel(self._rootNode, self)

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
        QtCore.QObject.connect(self._model , QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.updateXml)

        highlighter = XMLHighlighter(self.ui_xml)
        self.updateXml()
        

        

propBase, propForm = uic.loadUiType("Views/PropertiesLayout.ui")
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
        


        

nodeBase, nodeForm = uic.loadUiType("Views/NodeProperties.ui") 
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

labelBase, labelForm = uic.loadUiType("Views/LabelWidget.ui")
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


numericBase, numericForm = uic.loadUiType("Views/NumericWidget.ui")
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
        

checkBase, checkForm = uic.loadUiType("Views/CheckWidget.ui")
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
    

comboBase, comboForm = uic.loadUiType("Views/ComboWidget.ui")
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
        

inChannelBase, inChannelForm = uic.loadUiType("Views/InChannelWidget - Copy.ui")
class InChannelEditor(inChannelBase, inChannelForm):
    def __init__(self,parent = None):
        super(inChannelBase,self).__init__(parent)
        self.setupUi(self)

##        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self.ui_tableView.setModel(proxyModel.sourceModel())
##        self.ui_tableView.setItemDelegate
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

    t = Node
    
    
##    l2 = [[for cls in v.__mro__] for v in lst]
##    print(l2)
##    
##    classes = a.__class__.__mro__
##    for cls in classes:
##        for k,v in cls.__dict__.items():            
##            if isinstance(v,property):
##                print("PROPERTY NAME: {0}".format(k))
    
    sys.exit(app.exec_())
