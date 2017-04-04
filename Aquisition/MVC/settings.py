from PyQt4 import QtCore, QtGui, QtXml,uic
from xml_highlighter import XMLHighlighter
from nodes import *
from fans_constants import *
from agilent_u2542a_constants import *
import sys
from node_configuration import Configuration 
from xml_serializer import XmlNodeSerializer

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
##        print("\n"*3)
##        print("AFTER DESERIALIZATION")
##        print(node)

        self.config.save_config()
            
        

    def __init__(self,configuration = None,parent = None):
        super(base,self).__init__(parent)
        self.setupUi(self)
        if configuration is None:
            self.config = Configuration()
        else:
            self.config = configuration
            
        self._rootNode = self.config.get_root_node()
        #print(self.config.get_node_from_path("input_settings.ch1"))

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
    
    def __addControl(self, typeInfo, control):
        self._controls[typeInfo] = control
        self.layoutSpecs.addWidget(control)

    def _setAllControlsVisibility(self, visible):
        for k,v in self._controls.items():
            v.setVisible(visible)
    
    def _setControlVisibility(self, typeInfo, visible):
        self._controls[typeInfo].setVisible(visible)

    def _setSelectionForType(self, typeInfo, current):
        self._controls[typeInfo].setSelection(current)

    def _setModelForControls(self,proxyModel):
        for k,v in self._controls.items():
            v.setModel(proxyModel)

    def __init__(self, parent = None):
        super(propBase, self).__init__(parent)
        self.setupUi(self)
        self._proxyModel = None
        self._controls = dict()

        #self.__addControl("NODE", NodeEditor(self))
        self.__addControl("LABEL", LabelEditor(parent=self))
        self.__addControl("COMBO", ComboEditor(parent=self))
        self.__addControl("CHECK", CheckEditor(parent=self))
        self.__addControl("NUMERIC", NumericEditor(parent=self))
        self.__addControl("IN_CHANNEL", InChannelEditor(parent=self))
        self.__addControl("OUT_CHANNEL", OutChannelEditor(parent=self))
        self.__addControl("ACQUISITION_SETTINGS", AcquisitionSettingsEditor(parent=self))
        self.__addControl("VOLTAGE_SETTINGS",VoltageSettingsEditor(parent=self))
        
        self._nodeEditor = NodeEditor(self)
        self.layoutNode.addWidget(self._nodeEditor)

        self._setAllControlsVisibility(False)

        
               
    """INPUTS: QModelIndex, QModelIndex"""
    def setSelection(self, current, old):

        current = self._proxyModel.mapToSource(current)

        node = current.internalPointer()
        
        if node is not None:
            typeInfo = node.typeInfo()
        
        self._setAllControlsVisibility(False)
        if typeInfo is not "NODE":
            self._setControlVisibility(typeInfo, True)
            self._setSelectionForType(typeInfo, current)

        self._nodeEditor.setSelection(current)
        
           
        #else:
        #    self._labelEditor.setVisible(False)
        #    self._comboEditor.setVisible(False)
        #    self._checkEditor.setVisible(False)
        #    self._numericEditor.setVisible(False)
        #    self._inChannelEditor.setVisible(False)
        #    self._acquisitionEditor.setVisible(False)
        #    self._outChannelEditot.setVisible(False)

            
        
    
    def setModel(self, proxyModel):
        
        self._proxyModel = proxyModel
        
        self._nodeEditor.setModel(proxyModel)

        self._setModelForControls(proxyModel)




        

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
        self.ui_combo.addItems(node.case_list)
        parent = current.parent()
        
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        


outChannelBase, outChannelForm = uic.loadUiType("Views/OutChannelWidget.ui")
class OutChannelEditor(outChannelBase, outChannelForm):
     def __init__(self,parent = None):
         super(outChannelBase, self).__init__(parent)
         self.setupUi(self)
         self._dataMapper = QtGui.QDataWidgetMapper(self)
         

     def setModel(self,proxyModel):
         self._proxyModel = proxyModel
         self._dataMapper.setModel(proxyModel.sourceModel())
         self._dataMapper.addMapping(self.ui_enabled,2,"currentIndex")
         self._dataMapper.addMapping(self.ui_range,3,"currentIndex")
         self._dataMapper.addMapping(self.ui_polarity,4,"currentIndex")
         self._dataMapper.addMapping(self.ui_function,5,"currentIndex")
         self._dataMapper.addMapping(self.ui_out_pin,6,"currentIndex")

     def setSelection(self, current):
         parent = current.parent()
         self._dataMapper.setRootIndex(parent)
         self._dataMapper.setCurrentModelIndex(current)
       

inChannelBase, inChannelForm = uic.loadUiType("Views/InChannelWidget.ui")
class InChannelEditor(inChannelBase, inChannelForm):
    def __init__(self,parent = None):
        super(inChannelBase,self).__init__(parent)
        self.setupUi(self)
        self._dataMapper = QtGui.QDataWidgetMapper(self)
        self.ui_range.clear()
        self.ui_range.addItems(DAQ_RANGES.names)
        self.ui_polarity.clear()
        self.ui_polarity.addItems(POLARITIES.names)
        self.ui_function.clear()
        self.ui_function.addItems(FANS_AI_FUNCTIONS.names)
        self.ui_mode.clear()
        self.ui_mode.addItems(AI_MODES.names)
        self.ui_filter_cutoff.clear()
        self.ui_filter_cutoff.addItems(FILTER_CUTOFF_FREQUENCIES.names)
        self.ui_filter_gain.clear()
        self.ui_filter_gain.addItems(FILTER_GAINS.names)
        self.ui_pga_gain.clear()
        self.ui_pga_gain.addItems(PGA_GAINS.names)

        

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        self._dataMapper.addMapping(self.ui_enabled,2)
        self._dataMapper.addMapping(self.ui_range,3,"currentIndex")
        self._dataMapper.addMapping(self.ui_polarity,4,"currentIndex")
        self._dataMapper.addMapping(self.ui_function,5,"currentIndex")
        self._dataMapper.addMapping(self.ui_mode,6,"currentIndex")
        self._dataMapper.addMapping(self.ui_filter_cutoff,7,"currentIndex")
        self._dataMapper.addMapping(self.ui_filter_gain,8,"currentIndex")
        self._dataMapper.addMapping(self.ui_pga_gain,9,"currentIndex")
        
    
    def setSelection(self,current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
    
acquisitionSettingsBase, acquisitionSettingsForm = uic.loadUiType("Views/AcquisitionSettings.ui")
class AcquisitionSettingsEditor(acquisitionSettingsBase, acquisitionSettingsForm):
    def __init__(self, parent = None):
        super(acquisitionSettingsBase,self).__init__(parent)
        self.setupUi(self)
       
        self.amplifier.addItems(["1","2","5"])
        self.pgaGain.addItems(PGA_GAINS.names)
        self.filterGain.addItems(FILTER_GAINS.names)
        self.filterCutoff.addItems(FILTER_CUTOFF_FREQUENCIES.names)



        self._dataMapper = QtGui.QDataWidgetMapper(self)

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.sampleRate,2)
        self._dataMapper.addMapping(self.homemadeAmplifier,3)
        self._dataMapper.addMapping(self.amplifier,4)
        self._dataMapper.addMapping(self.pgaGain,5)
        self._dataMapper.addMapping(self.filterGain,6)
        self._dataMapper.addMapping(self.filterCutoff,7)



    def setSelection(self,current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


channel_settings_base, channel_settings_form = uic.loadUiType("Views/ChannelSettings.ui")
class ChannelSettingsEditor(channel_settings_base,channel_settings_form):
    def __init__(self,root_node, parent = None):
        super(channel_settings_base,self).__init__(parent)
        self.setupUi(self)
        
        self.ui_ai_channels = InChannelEditor(self)
        self.ui_ao_channels = OutChannelEditor(self)
        self.ui_editor_layout.addWidget(self.ui_ai_channels)
        self.ui_editor_layout.addWidget(self.ui_ao_channels)


        self._proxyModel = QtGui.QSortFilterProxyModel(self)
        self._model = SettingsModel(root_node, self)

        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        self._proxyModel.setSortRole(SettingsModel.sortRole)
        self._proxyModel.setFilterRole(SettingsModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)
        
        #self.ui_channels_view.setModel(self._proxyModel)
        self.setModel(self._proxyModel)
        QtCore.QObject.connect(self.ui_channels_view.selectionModel(), QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"), self.setSelection)

        self.ui_ai_channels.setVisible(False)
        self.ui_ao_channels.setVisible(False)


    def setModel(self,proxyModel):
        self.ui_channels_view.setModel(self._proxyModel)
        self.ui_ai_channels.setModel(self._proxyModel)
        self.ui_ao_channels.setModel(self._proxyModel)
        
    def setSelection(self,current,old):
        current = self._proxyModel.mapToSource(current)
        node = current.internalPointer()
        if node is not None:
            typeInfo = node.typeInfo()

        if typeInfo is "IN_CHANNEL":
            self.ui_ai_channels.setVisible(True)
            self.ui_ao_channels.setVisible(False)
            self.ui_ai_channels.setSelection(current)
        elif typeInfo is "OUT_CHANNEL":
            self.ui_ai_channels.setVisible(False)
            self.ui_ao_channels.setVisible(True)
            self.ui_ao_channels.setSelection(current)
        else:
            self.ui_ai_channels.setVisible(False)
            self.ui_ao_channels.setVisible(False)



voltage_settings_base, voltage_settings_form = uic.loadUiType("Views/VoltageSettings.ui")
class VoltageSettingsEditor(voltage_settings_base, voltage_settings_form ):
    def __init__(self, configuration = None,parent= None):
        super(voltage_settings_base, self).__init__(parent)
        self.setupUi(self)
        self._dataMapper = QtGui.QDataWidgetMapper(self)
        if configuration:
            node = configuration.get_node_from_path("voltage_settings")
            self._proxyModel = QtGui.QSortFilterProxyModel(self)
            self._model = SettingsModel(node, self)

            self._proxyModel.setSourceModel(self._model)
            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
            self._proxyModel.setSortRole(SettingsModel.sortRole)
            self._proxyModel.setFilterRole(SettingsModel.filterRole)
            self._proxyModel.setFilterKeyColumn(0)
        
            self.setModel(self._proxyModel)


    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        self._dataMapper.addMapping(self.ui_drain_source_start,2)
        self._dataMapper.addMapping(self.ui_drain_source_stop,3)
        self._dataMapper.addMapping(self.ui_drain_source_step,4)
        self._dataMapper.addMapping(self.ui_gate_start,5)
        self._dataMapper.addMapping(self.ui_gate_stop,6)
        self._dataMapper.addMapping(self.ui_gate_step,7)

    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)


if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")
    
    wnd = WndTutorial()
    wnd.show()

    #t = Node
    
    
    #cfg = Configuration()
    #node = cfg.get_node_from_path("input_settings")
    #wnd = ChannelSettingsEditor(node)
    #wnd.show()
    
    #node = cfg.get_node_from_path("out_settings")
    #wnd = ChannelSettingsEditor(node)
    #wnd.show()
    
    sys.exit(app.exec_())
