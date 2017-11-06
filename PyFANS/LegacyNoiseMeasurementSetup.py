import sys
import os
import time
import numpy as np
from multiprocessing import JoinableQueue
from collections import deque


from PyQt4 import uic, QtGui, QtCore
from nodes import ExperimentSettings, Node, SettingsModel, ValueRange, HardwareSettings
from configuration import Configuration
from communication_layer import get_available_gpib_resources, get_available_com_resources
from plot import SpectrumPlotWidget
from experiment_handler import ProcessingThread, ExperimentController   #, ExperimentProcess
from measurement_data_structures import MeasurementInfo

class StatusObject(QtCore.QObject):
    message_arrived = QtCore.pyqtSignal(str)
    value_changed = QtCore.pyqtSignal(str,object)
    multiple_param_changed = QtCore.pyqtSignal(dict)
    #measurement_info_changed = QtCore.pyqtSignal(MeasurementInfo)
    refresh_measurement_start_data = QtCore.pyqtSignal(MeasurementInfo)
    refresh_measurement_end_data = QtCore.pyqtSignal(MeasurementInfo)

    def __init__(self):
        super().__init__()

    def send_message(self, message):
        if message:
            self.message_arrived.emit(message)

    def send_value_changed(self, parameter, value):
        self.value_changed.emit(parameter,value)

    #def send_measurement_info_changed(self, measurement_info):
    #    self.measurement_info_changed.emit(measurement_info)

    def send_refresh_measurement_start_data(self, measurement_info):
        self.refresh_measurement_start_data.emit(measurement_info)

    def send_refresh_measurement_end_data(self, measurement_info):
        self.refresh_measurement_end_data.emit(measurement_info)

    def send_multiple_param_changed(self, params):
        self.multiple_param_changed.emit(params)


mainViewBase, mainViewForm = uic.loadUiType("UI_NoiseMeasurement_v2.ui")
class MainView(mainViewBase,mainViewForm):
    def __init__(self, parent = None):
       super(mainViewBase,self).__init__(parent)
       self.setupUi(self)
       self.setupFolderBrowseButton()
       
       self._config  = Configuration()
       rootNode = self._config.get_node_from_path("Settings")#Node("settings")
       self.setSettings(rootNode)
       self.setupPlots()


       self._status_object = StatusObject()
       self._status_object.message_arrived.connect(self._on_message_arrived)
       self._status_object.value_changed.connect(self._on_parameter_changed)
       
       self._status_object.refresh_measurement_start_data.connect(self._on_refresh_measurement_start_data)
       self._status_object.refresh_measurement_end_data.connect(self._on_refresh_measurement_end_data)

       #self._status_object.measurement_info_changed.connect(self._on_measurement_info_changed)
       self._status_object.multiple_param_changed.connect(self._on_multiple_param_changed)

       self._experiment_controller = ExperimentController(self._spectrumPlotWidget, status_object = self._status_object)
       

    def setupFolderBrowseButton(self):
        self.popMenu = QtGui.QMenu(self)
        self.selected_folder_context_menu_item = QtGui.QAction(self)
        self.selected_folder_context_menu_item.triggered.connect(self.on_open_folder_in_explorer)
        self.popMenu.addAction(self.selected_folder_context_menu_item)
        self.popMenu.addSeparator()

        #open_folder_action = QtGui.QAction("Open in explorer...",self)
        #open_folder_action.triggered.connect(self.on_open_folder_in_explorer)
        #self.popMenu.addAction(open_folder_action)
        
        self.folderBrowseButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.folderBrowseButton.customContextMenuRequested.connect(self.on_folder_browse_button_context_menu)
        
    def set_selected_folder_context_menu_item_text(self,text):
        self.selected_folder_context_menu_item.setText(text)

    def on_open_folder_in_explorer(self):
        print("opening folder")
        print(self._settings.working_directory)
        request = 'explorer "{0}"'.format(self._settings.working_directory)
        print(request)
        os.system(request)

    def on_folder_browse_button_context_menu(self,point):
        self.popMenu.exec_(self.folderBrowseButton.mapToGlobal(point))
    
    def __update_view(self):
        self._viewModel.layoutChanged.emit()

    def __ui_set_measurement_name(self, measurement_name):
        self.ui_measurementName.setText(measurement_name)
        
        #self._settings.measurement_name = measurement_name
        #self.__update_view()
        #index = self._viewModel.createIndex(
        #self._viewModel.index(

    def __ui_set_experiment_name(self, experiment_name):
        #self._settings.experiment_name = experiment_name
        #self.__update_view()
        self.ui_experimentName.setText(experiment_name)

    def __ui_set_measurement_couter(self,measurement_counter):
        #self._settings.measurement_count = measurement_counter
        #self.__update_view()
        #print("setting measurement counter {0}".format(measurement_counter))
        self.ui_measurementCount.setValue(int(measurement_counter))
    
    def  _on_refresh_measurement_start_data(self, measurement_info):
        if isinstance(measurement_info, MeasurementInfo):
            self.sample_voltage_start.setText(str(measurement_info.start_sample_voltage))
            self.front_gate_voltage_start.setText(str(measurement_info.start_gate_voltage))
            self.sample_current_start.setText(str(measurement_info.sample_current_start))
            self.sample_resistance_start.setText(str(measurement_info.sample_resistance_start))
            self.ui_current_temp.setText(str(measurement_info.start_temperature))
      
    def  _on_refresh_measurement_end_data(self, measurement_info):
        if isinstance(measurement_info, MeasurementInfo):
            self.sample_voltage_end.setText(str(measurement_info.end_sample_voltage))
            self.front_gate_voltage_end.setText(str(measurement_info.end_gate_voltage))
            self.sample_current_end.setText(str(measurement_info.sample_current_end))
            self.sample_resistance_end.setText(str(measurement_info.sample_resistance_end))
            self.ui_current_temp.setText(str(measurement_info.end_temperature))

    #def __ui_set_measurement_info(self, measurement_info):
    #    print("updating ui")
    #    print(measurement_info.start_sample_voltage)
    #    print(measurement_info.end_sample_voltage)

    #    self.sample_voltage_start.setText(str(measurement_info.start_sample_voltage))
    #    self.sample_voltage_end.setText(str(measurement_info.end_sample_voltage))
        
    #    self.front_gate_voltage_start.setText(str(measurement_info.start_gate_voltage))
    #    self.front_gate_voltage_end.setText(str(measurement_info.end_gate_voltage))
    #def _on_measurement_info_changed(self, measurement_info):
    #    print("measurement info changed")
    #    if isinstance(measurement_info, MeasurementInfo):
    #        print("measurement_info :{0}".format(measurement_info))
    #        self.__ui_set_measurement_info(measurement_info)

    def _on_multiple_param_changed(self, params):
        if isinstance(params,dict):
            for k,v in params.items():
                self._on_parameter_changed(k,v)

        
    def _on_parameter_changed(self,parameter, value):
        print("parameter_changed")
        print(parameter)
        print(value)
        
        if not parameter:
            return
        elif parameter == "measurement_name":
            #print(parameter)
            self.__ui_set_measurement_name(value)
        elif parameter == "experiment_name":
            #print(parameter)
            self.__ui_set_experiment_name(value)
        elif parameter == "measurement_count":
            #print(parameter)
            self.__ui_set_measurement_couter(value)
            
        #idx = QtCore.QModelIndex()
        #self._viewModel.dataChanged.emit(idx,idx)
        
    def _on_message_arrived(self,message, timeout = 0):
        #assert isinstance(self.statusbar, QtGui.QStatusBar)
        #print("in message handler\n ******************************************")
        if message:
            self.statusbar.showMessage(message, timeout)

        #print("message_arrived")


    def setupPlots(self):
        self._spectrumPlotWidget =  SpectrumPlotWidget(self.ui_plot,{0:(0,1600,1),1:(0,102400,64)})


    def setSettings(self, rootNode):
       
       settings = rootNode.getChildByName("ExperimentSettings")
       assert isinstance(settings,ExperimentSettings)
       self._settings = settings
       self._viewModel = SettingsModel(rootNode)
       self._dataMapper = QtGui.QDataWidgetMapper()
       self._dataMapper.setModel(self._viewModel)
       self._dataMapper.addMapping(self.ui_experimentName ,1)
       self._dataMapper.addMapping(self.ui_measurementName ,2)
       self._dataMapper.addMapping(self.ui_measurementCount ,3)
       self._dataMapper.addMapping(self.ui_calibrate ,4)
       self._dataMapper.addMapping(self.ui_overload_reject ,5)
       self._dataMapper.addMapping(self.ui_display_refresh ,6)
       self._dataMapper.addMapping(self.ui_averages ,7)
       self._dataMapper.addMapping(self.ui_use_homemade_amplifier ,8)
       #self._dataMapper.addMapping(self. ,9)
       #self._dataMapper.addMapping(self. ,10)
       self._dataMapper.addMapping(self.ui_second_amp_coeff ,11)
       self._dataMapper.addMapping(self.ui_load_resistance ,12)
       self._dataMapper.addMapping(self.ui_need_meas_temp ,13)
       self._dataMapper.addMapping(self.ui_meas_gated_structure ,14)
       self._dataMapper.addMapping(self.ui_meas_characteristic_type ,15,"currentIndex")
       self._dataMapper.addMapping(self.ui_use_dut_selector ,16)
       #self._dataMapper.addMapping(self. ,17)
       self._dataMapper.addMapping(self.ui_use_set_vds_range ,18)
       #self._dataMapper.addMapping(self. ,19)
       self._dataMapper.addMapping(self.ui_use_set_vfg_range ,20)
       #self._dataMapper.addMapping(self. ,21)
       self._dataMapper.addMapping(self.ui_front_gate_voltage ,22)
       self._dataMapper.addMapping(self.ui_drain_source_voltage ,23)
       self._dataMapper.addMapping(self.ui_use_automated_voltage_control, 24)
       self._dataMapper.addMapping(self.ui_simulate, 25)
       #QtCore.QObject.connect(self._viewModel, QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.on_data_changed)
       self._dataMapper.toFirst()
       
       self.set_selected_folder_context_menu_item_text(self._settings.working_directory)


    def on_data_changed(self):
        print("view model changed")
        #s = XmlNodeSerializer()
        #xml = s.serialize(self._config.get_root_node())
        self._on_message_arrived("saving config file")
        self._config.save_config()
        self._on_message_arrived("config saved!")


    @QtCore.pyqtSlot()
    def on_ui_open_hardware_settings_clicked(self):
        print("open hardware settings")
        dialog = HardwareSettingsView()
        rootNode = self._config.get_root_node()
        viewModel = SettingsModel(rootNode)
        hardware_settings = self._config.get_node_from_path("HardwareSettings")
        assert isinstance(hardware_settings,HardwareSettings)
        idx = QtCore.QModelIndex()
        if hardware_settings!= rootNode:
            idx = viewModel.createIndex(hardware_settings.row(),0,hardware_settings)
        dialog.setModel(viewModel)
        dialog.setSelection(idx)
        result = dialog.exec_()
        print(result)

    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        self.on_data_changed()
        print("start")
        self._experiment_controller.start()

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        print("stop")
        self._experiment_controller.stop()

    def show_range_selector(self,model, currentIndex):
        dialog = RangeSelectorView()
        dialog.setModel(model)
        dialog.setSelection(currentIndex)
        result = dialog.exec_()
        print(result)

    @QtCore.pyqtSlot()
    def on_VdsRange_clicked(self):
        print("Vds range")
        
        rootNode = self._config.get_root_node()
        rang = self._config.get_node_from_path("drain_source_range")
        viewModel = SettingsModel(rootNode)
        
        assert isinstance(rang,ValueRange)
        
        idx = QtCore.QModelIndex()
        if rang!= rootNode:
            idx = viewModel.createIndex(rang.row(),0,rang)

        self.show_range_selector(viewModel, idx)
       



    @QtCore.pyqtSlot()
    def on_VfgRange_clicked(self):
        print("Vfg range")

        rootNode = self._config.get_root_node()
        rang = self._config.get_node_from_path("front_gate_range")
        viewModel = SettingsModel(rootNode)
        
        assert isinstance(rang,ValueRange)
        
        idx = QtCore.QModelIndex()
        if rang!= rootNode:
            idx = viewModel.createIndex(rang.row(),0,rang)

        self.show_range_selector(viewModel, idx)


    @QtCore.pyqtSlot()
    def on_transistorSelector_clicked(self):
        dialog = DUTselectorView()
        result = dialog.exec_()
        print("Select transistors")

    @QtCore.pyqtSlot()
    def on_folderBrowseButton_clicked(self):
        print("Select folder")
        
        folder_name = os.path.abspath(QtGui.QFileDialog.getExistingDirectory(self,caption="Select Folder", directory = self._settings.working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(folder_name)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        if retval and self._settings:
            self._settings.working_directory = folder_name
            self.set_selected_folder_context_menu_item_text(folder_name)
            
    
    @QtCore.pyqtSlot()
    def on_selectVoltageChangeOrder_clicked(self):
        print("selectVoltageChangeOrder")
        
    def closeEvent(self,event):
        self._config.save_config()


HardwareSettingsBase, HardwareSettingsForm = uic.loadUiType("UI_HardwareSettings_new.ui")
class HardwareSettingsView(HardwareSettingsBase, HardwareSettingsForm):
    def __init__(self,parent = None):
        super(HardwareSettingsBase,self).__init__(parent)
        self.setupUi(self)
        gpib_resources = get_available_gpib_resources()
        #com_resources = get_available_com_resources()
        self.ui_analyzer.addItems(gpib_resources)
        self.ui_sample_main.addItems(gpib_resources)
        self.ui_gate.addItems(gpib_resources)
        self.ui_fans_controller.addItems(gpib_resources)
        self._dataMapper = QtGui.QDataWidgetMapper()

    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)

    def setModel(self, model):
        self._viewModel = model
        self._dataMapper.setModel(self._viewModel)
        self._dataMapper.addMapping(self.ui_analyzer ,2)
        self._dataMapper.addMapping(self.ui_sample_main ,3)
        self._dataMapper.addMapping(self.ui_gate ,4)
        self._dataMapper.addMapping(self.ui_fans_controller, 5)
        self._dataMapper.addMapping(self.ui_sample_channel, 6)
        self._dataMapper.addMapping(self.ui_sample_relay, 7)
        self._dataMapper.addMapping(self.ui_gate_channel, 8)    
        self._dataMapper.addMapping(self.ui_gate_relay, 9)

#HardwareSettingsBase, HardwareSettingsForm = uic.loadUiType("UI_HardwareSettings.ui")
#class HardwareSettingsView(HardwareSettingsBase, HardwareSettingsForm):
#    def __init__(self,parent = None):
#        super(HardwareSettingsBase,self).__init__(parent)
#        self.setupUi(self)
#        gpib_resources = get_available_gpib_resources()
#        com_resources = get_available_com_resources()
#        self.ui_analyzer.addItems(gpib_resources)
#        self.ui_main_gate.addItems(gpib_resources)
#        self.ui_sample.addItems(gpib_resources)
#        self.ui_arduino.addItems(com_resources)
#        self._dataMapper = QtGui.QDataWidgetMapper()

#    def setSelection(self, current):
#        parent = current.parent()
#        self._dataMapper.setRootIndex(parent)
#        self._dataMapper.setCurrentModelIndex(current)

#    def setModel(self, model):
#        self._viewModel = model
#        self._dataMapper.setModel(self._viewModel)
#        self._dataMapper.addMapping(self.ui_analyzer ,2)
#        self._dataMapper.addMapping(self.ui_main_gate ,3)
#        self._dataMapper.addMapping(self.ui_sample ,4)
#        #5 skipped in Hardware Settings node
#        self._dataMapper.addMapping(self.ui_arduino ,6)
#        self._dataMapper.addMapping(self.ui_sample_channel ,7,"currentIndex")
#        self._dataMapper.addMapping(self.ui_gate_channel ,8,"currentIndex")



DUTselectorViewBase, DUTselectorViewForm = uic.loadUiType("UI_TransistorSelector.ui")
class DUTselectorView(DUTselectorViewBase,DUTselectorViewForm):
    def __init__(self,parent = None):
        super(DUTselectorViewBase,self).__init__(parent)
        self.setupUi(self)


rangeSelectorBase, rangeSelectorForm = uic.loadUiType("UI_RangeSelector.ui")
class RangeSelectorView(rangeSelectorBase,rangeSelectorForm):
    def __init__(self,parent = None):
        super(rangeSelectorBase,self).__init__(parent)
        self.setupUi(self)
        self._dataMapper = QtGui.QDataWidgetMapper()

    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)

    def setModel(self, model):
        self._viewModel = model
        self._dataMapper.setModel(self._viewModel)

        #rootNode = configuration.get_root_node()
        #self._viewModel = SettingsModel(rootNode)
        #self._range = configuration.get_node_from_path("drain_source_range")
        #assert isinstance(self._range,ValueRange)
        #parent = self._range.parent()
        #idx = QtCore.QModelIndex()
        #if parent != rootNode:
        #    idx = self._viewModel.createIndex(parent.row(),0,parent)
        #self._viewModel = SettingsModel(self._settings)

        #self._dataMapper.setModel(self._viewModel)
        self._dataMapper.addMapping(self.ui_start_val ,2)
        self._dataMapper.addMapping(self.ui_start_units ,3,"currentIndex")
        self._dataMapper.addMapping(self.ui_stop_val ,4)
        self._dataMapper.addMapping(self.ui_stop_units ,5,"currentIndex")
        self._dataMapper.addMapping(self.ui_count ,6)
        self._dataMapper.addMapping(self.ui_range_mode ,7,"currentIndex")
        
        #QtCore.QObject.connect(self._viewModel, QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.on_data_changed)
        #self._dataMapper.setRootIndex(idx)
        #self._dataMapper.toFirst()


    def on_data_changed(self):
        print("range changed")


def update():
    print("update") 

if __name__== "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("LegacyNoiseMeasurementSetup")
    #app.setStyle("cleanlooks")

    #css = "QLineEdit#sample_voltage_start {background-color: yellow}"
    #app.setStyleSheet(css)
    #sample_voltage_start

    wnd = MainView()
    wnd.show()

    sys.exit(app.exec_())



    


   

    