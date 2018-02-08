import os
import sys
import time
import pint
import pickle

from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore

import plot as plt

from collections import deque
from multiprocessing import JoinableQueue
from multiprocessing import Event

from communication_layer import get_available_gpib_resources, get_available_com_resources
import ui_helper as uih
import range_handlers as rh
import range_editor as redit

from fans_experiment_settings import ExperimentSettings
from fans_hardware_settings import HardwareSettingsView, HardwareSettings

import modern_fans_experiment as mfexp
import process_communication_protocol as pcp
from measurement_data_structures import MeasurementInfo
from modern_fans_voltage_control import VoltageControl
from StandAloneVoltageControl import VoltageControlView
import modern_fans_controller as mfans
#import modern_agilent_u2542a as mdaq
import modern_fans_smu as msmu

mainViewBase, mainViewForm = uic.loadUiType("UI/UI_NoiseMeasurement_v5.ui")
class FANS_UI_MainView(mainViewBase,mainViewForm):
    ureg = UnitRegistry()
    voltage_format = "{:8.6f}"
    resistance_format = "{:.3f}"
    current_format = "{:.5e}"
    temperature_format = "{:.2f}"
    calibrate_before_measurement = uih.bind("ui_calibrate", "checked", bool)
    overload_reject = uih.bind("ui_overload_reject", "checked", bool)
    display_refresh = uih.bind("ui_display_refresh", "value", int)
    simulate_measurement = uih.bind("ui_simulate", "checked", bool)
    number_of_averages = uih.bind("ui_averages", "value", int)
    use_homemade_amplifier = uih.bind("ui_use_homemade_amplifier", "checked", bool)
    second_amplifier_gain = uih.bind("ui_second_amp_coeff", "currentText", int)
    perform_temperature_measurement = uih.bind("ui_need_meas_temp","checked", bool)
    current_temperature = uih.bind("ui_current_temp", "text", float, temperature_format)
    load_resistance = uih.bind("ui_load_resistance", "text", float)
    perform_measurement_of_gated_structure = uih.bind("ui_meas_gated_structure", "checked", bool)
    use_dut_selector = uih.bind("ui_use_dut_selector", "checked", bool)
    use_automated_voltage_control = uih.bind("ui_use_automated_voltage_control", "checked", bool)
    measurement_characteristic_type = uih.bind("ui_meas_characteristic_type", "currentIndex", int)
    drain_source_voltage = uih.bind("ui_drain_source_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
    front_gate_voltage = uih.bind("ui_front_gate_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
    use_drain_source_range = uih.bind("ui_use_set_vds_range","checked", bool)
    use_gate_source_range = uih.bind("ui_use_set_vfg_range","checked", bool)
    sample_voltage_start = uih.bind("ui_sample_voltage_start", "text", float, voltage_format)
    sample_voltage_end = uih.bind("ui_sample_voltage_end", "text", float, voltage_format)
    front_gate_voltage_start = uih.bind("ui_front_gate_voltage_start", "text", float, voltage_format)
    front_gate_voltage_end = uih.bind("ui_front_gate_voltage_end", "text", float, voltage_format)
    sample_current_start = uih.bind("ui_sample_current_start", "text", float, current_format)
    sample_current_end = uih.bind("ui_sample_current_end", "text", float, current_format)
    sample_resistance_start = uih.bind("ui_sample_resistance_start", "text", float,resistance_format)
    sample_resistance_end = uih.bind("ui_sample_resistance_end", "text", float, resistance_format)
    experimentName = uih.bind("ui_experimentName", "text", str)
    measurementName = uih.bind("ui_measurementName", "text", str)
    measurementCount = uih.bind("ui_measurementCount", "value", int)
    timetrace_mode = uih.bind("ui_timetrace_mode", "currentIndex", int)
    timetrace_length = uih.bind("ui_timetrace_length", "value", int)
    set_zero_after_measurement = uih.bind("ui_set_zero_after_measurement", "checked", bool)
    valueChanged = QtCore.pyqtSignal(str, object) #str - name of the object, object - new value

    def __init__(self, parent = None):
       super(mainViewBase,self).__init__(parent)
       self.setupUi()
       self.init_values()
       self._controller = None
       self._experiment_settings = None
       
    def setupUi(self):
        print("setting the ui up")
        super().setupUi(self)
        self.ui_current_temp.setValidator(QtGui.QDoubleValidator(notation = QtGui.QDoubleValidator.StandardNotation))
        self.ui_load_resistance.setValidator(QtGui.QIntValidator())
        self.ui_drain_source_voltage.setValidator(uih.QVoltageValidator())
        self.ui_front_gate_voltage.setValidator(uih.QVoltageValidator())
        self.__setup_folder_browse_button()
        self._spectrumPlotWidget =  plt.SpectrumPlotWidget(self.ui_plot,{0:(0,1600,1),1:(0,102400,64)})
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0,100)
        self.statusbar.addPermanentWidget(self.progressBar)
        self.set_ui_idle()


    def connect(self, signal, slot):
        #assert isinstance(signal, QtCore.pyqtSignal), "signal should be of pyqtSignal type"
        signal.connect(slot)

    def disconnect(self, signal, slot):
        #assert isinstance(signal, QtCore.pyqtSignal), "signal should be of pyqtSignal type"
        signal.disconnect(slot)

    def subscribe_to_email_login_action(self, slot):
        self.connect(self.actionLoginEmail.triggered, slot)

    def subscribe_to_hardware_settings_action(self, slot):
        self.connect(self.actionHardwareSettings.triggered, slot)

    def subscribe_to_waterfall_noise_action(self, slot):
        self.connect(self.actionOpenRealtimeNoiseWindow.triggered, slot)

    def subscribe_to_timetrace_action(self, slot):
        self.connect(self.actionOpenTimetraceWindow.triggered,slot)

    def subscribe_to_open_console_window_action(self, slot):
        self.connect(self.actionOpenConsoleWindow.triggered, slot)

    def subscribe_to_open_remote_action(self, slot):
        self.connect(self.actionOpenRemote.triggered, slot)

    @property
    def controller(self):
        return self._controller
    
    @controller.setter
    def controller(self,value):
        assert isinstance(value, FANS_UI_Controller)
        self._controller = value
          
    def set_controller(self, controller):
        self.controller = controller

    def init_values(self):
        print("initializing values")
        #self._calibrate_before_measurement = False
        #self.front_gate_voltage = "123 mV"

    #  *************************************
    #   BROWSER BUTTON
    #

    def __setup_folder_browse_button(self):
        self.popMenu = QtGui.QMenu(self)
        self.selected_folder_context_menu_item = QtGui.QAction(self)
        self.selected_folder_context_menu_item.triggered.connect(self.on_open_folder_in_explorer)
        self.popMenu.addAction(self.selected_folder_context_menu_item)
        self.popMenu.addSeparator()
        self.folderBrowseButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.folderBrowseButton.customContextMenuRequested.connect(self.on_folder_browse_button_context_menu)
    
    def set_selected_folder_context_menu_item_text(self,text):
        self.selected_folder_context_menu_item.setText(text)

    def on_folder_browse_button_context_menu(self,point):
        self.popMenu.exec_(self.folderBrowseButton.mapToGlobal(point))

    def on_open_folder_in_explorer(self):
        print("opening folder")
        request = 'explorer "{0}"'.format(self.experiment_settings.working_directory)#self._settings.working_directory)
        print(request)
        os.system(request)

    @QtCore.pyqtSlot()
    def on_folderBrowseButton_clicked(self):
        print("Select folder")
        folder_name = os.path.abspath(QtGui.QFileDialog.getExistingDirectory(self,caption="Select Folder", directory = self.experiment_settings.working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(folder_name)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        if retval and self.experiment_settings:
            self.experiment_settings.working_directory = folder_name
            self.set_selected_folder_context_menu_item_text(folder_name)

    #
    # END BROWSER BUTTON
    #*****************************************
    
    @property
    def experiment_settings(self):
        return self._experiment_settings
    
    @experiment_settings.setter
    def experiment_settings(self, value):
        self.set_experiment_settings_object(value)

    def set_experiment_settings_object(self, settings):
        assert isinstance(settings, ExperimentSettings), "Unsupported experiment settings type"
        self._experiment_settings = settings
        self.refresh_view()

    def refresh_view(self):
        assert isinstance(self._experiment_settings, ExperimentSettings), "Not initialized experiment settings"
        settings = self.experiment_settings
        uih.setAllChildObjectSignaling(self,True)
        self.calibrate_before_measurement = settings.calibrate_before_measurement
        self.overload_reject = settings.overload_rejecion
        self.simulate_measurement = settings.simulate_experiment
        self.number_of_averages = settings.averages
        self.use_homemade_amplifier = settings.use_homemade_amplifier
        self.second_amplifier_gain = settings.second_amp_coeff
        self.perform_temperature_measurement = settings.need_measure_temperature
        self.current_temperature = settings.current_temperature  #  "Not initialized" #settings.curre
        self.load_resistance = settings.load_resistance
        self.perform_measurement_of_gated_structure = settings.meas_gated_structure
        self.use_dut_selector = settings.use_transistor_selector #
        self.use_automated_voltage_control = settings.use_automated_voltage_control
        self.measurement_characteristic_type = settings.meas_characteristic_type
        self.drain_source_voltage = settings.drain_source_voltage
        self.use_drain_source_range = settings.use_set_vds_range
        self.front_gate_voltage = settings.front_gate_voltage
        self.use_gate_source_range = settings.use_set_vfg_range
        self.load_timetrace_settings(settings)
        self.set_zero_after_measurement = settings.set_zero_after_measurement

        self.experimentName = settings.experiment_name
        self.measurementName = settings.measurement_name
        self.measurementCount = settings.measurement_count
        uih.setAllChildObjectSignaling(self,False)

    UI_STATE_IDLE, UI_STATE_STARTED, UI_STATE_STOPPING = ui_states = range(3)
    def set_ui_state(self, state):
        if not state in self.ui_states:
            return

        if state is self.UI_STATE_IDLE:
            self.ui_startButton.setEnabled(True)
            self.ui_stopButton.setEnabled(True)
            self.progressBar.setVisible(False)
            self.progressBar.setValue(0)
        elif state is self.UI_STATE_STARTED:
            self.ui_startButton.setEnabled(False)
            self.ui_stopButton.setEnabled(True)
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
        elif state is self.UI_STATE_STOPPING:
            self.ui_startButton.setEnabled(False)
            self.ui_stopButton.setEnabled(False)
            self.progressBar.setVisible(True)

    def set_ui_idle(self):
        self.set_ui_state(self.UI_STATE_IDLE)

    def set_ui_started(self):
        self.set_ui_state(self.UI_STATE_STARTED)

    def set_ui_stopping(self):
        self.set_ui_state(self.UI_STATE_STOPPING)

    #**************
    #event handlers
    #**************

    TIMETRACE_NONE, TIMETRACE_PARTIAL, TIMETRACE_FULL = range(3)
    @QtCore.pyqtSlot(int)
    def on_ui_timetrace_mode_currentIndexChanged(self, index):
        print("timetrace mode changed to {0}".format(index))
        
        if index is self.TIMETRACE_NONE:
            self.ui_timetrace_length.hide()
        elif index is self.TIMETRACE_PARTIAL:
            self.ui_timetrace_length.show()
        elif index is self.TIMETRACE_FULL:
            self.ui_timetrace_length.hide()
        else:
            return
        self.save_timetrace_settings(self.experiment_settings)

    @QtCore.pyqtSlot(int)
    def on_ui_timetrace_length_valueChanged(self, value):
        print("timetrace length changed to {0}".format(value))
        self.save_timetrace_settings(self.experiment_settings)

    def save_timetrace_settings(self, experiment_settings):
        assert isinstance(experiment_settings, ExperimentSettings), "Cannot save timetrace data"
        mode = self.timetrace_mode
        length = self.timetrace_length
        write_timetrace_value = 0
        if mode is self.TIMETRACE_NONE:
            write_timetrace_value = 0    
        elif mode is self.TIMETRACE_PARTIAL:
            write_timetrace_value = length
        elif mode is self.TIMETRACE_FULL:
            write_timetrace_value = -1
        else:
            return
        experiment_settings.write_timetrace = write_timetrace_value


    def load_timetrace_settings(self, experiment_settings):
        assert isinstance(experiment_settings, ExperimentSettings), "Cannot load timetrace data"
        write_timetrace_value = experiment_settings.write_timetrace
        if write_timetrace_value is None:
            write_timetrace_value  = 0
        mode = self.TIMETRACE_NONE
        length = 1
        if write_timetrace_value < 0:
            mode = self.TIMETRACE_FULL
        elif write_timetrace_value == 0:
            mode = self.TIMETRACE_NONE
        elif write_timetrace_value > 0:
            mode = self.TIMETRACE_PARTIAL
            length = write_timetrace_value

        self.timetrace_mode = mode
        self.timetrace_length = length 
        self.on_ui_timetrace_mode_currentIndexChanged(mode)

    @QtCore.pyqtSlot()
    def on_ui_open_hardware_settings_clicked(self):
        print("open hardware settings")
        #self.controller.show_hardware_settings_view()
        self.actionHardwareSettings.trigger()
                
    @QtCore.pyqtSlot(int)
    def on_ui_calibrate_stateChanged(self, value):
        self.experiment_settings.calibrate_before_measurement = self.calibrate_before_measurement
        
    @QtCore.pyqtSlot(int)
    def on_ui_overload_reject_stateChanged(self, value):
        self.experiment_settings.overload_rejecion = self.overload_reject

    def _print_test(self):
        print("test")

    @QtCore.pyqtSlot(int)
    def on_ui_simulate_stateChanged(self,value):
        self.experiment_settings.simulate_experiment = self.simulate_measurement
       
    @QtCore.pyqtSlot(int)
    def on_ui_averages_valueChanged(self,value):
        self.experiment_settings.averages = self.number_of_averages

    @QtCore.pyqtSlot(int)
    def on_ui_use_homemade_amplifier_stateChanged(self, value):
        self.experiment_settings.use_homemade_amplifier = self.use_homemade_amplifier

    @QtCore.pyqtSlot(int)
    def on_ui_second_amp_coeff_currentIndexChanged(self,value):
        self.experiment_settings.second_amp_coeff = self.second_amplifier_gain
        #idx = self.experiment_settings.second_amp_coeff 
        #raise NotImplementedError()

    @QtCore.pyqtSlot(int)
    def on_ui_need_meas_temp_stateChanged(self, value):
        self.experiment_settings.need_measure_temperature = self.perform_temperature_measurement
    
    @QtCore.pyqtSlot(str)
    def on_ui_current_temp_textChanged(self, value):
        self.experiment_settings.current_temperature = self.current_temperature

    @QtCore.pyqtSlot(str)
    def on_ui_load_resistance_textChanged(self, value):
        self.experiment_settings.load_resistance = self.load_resistance
    
    @QtCore.pyqtSlot(int)
    def on_ui_meas_gated_structure_stateChanged(self, value):
        self.experiment_settings.meas_gated_structure = self.perform_measurement_of_gated_structure

    @QtCore.pyqtSlot(int)
    def on_ui_use_dut_selector_stateChanged(self, value):
        self.experiment_settings.use_transistor_selector = self.use_dut_selector

    @QtCore.pyqtSlot()
    def on_ui_transistorSelector_clicked(self):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_use_automated_voltage_control_stateChanged(self, value):
        self.experiment_settings.use_automated_voltage_control = self.use_automated_voltage_control
    
    @QtCore.pyqtSlot()
    def on_ui_voltage_control_clicked(self):
        self.controller.on_voltage_control_view_clicked()
        
    
    @QtCore.pyqtSlot(int)
    def on_ui_meas_characteristic_type_currentIndexChanged(self, value):
        self.experiment_settings.meas_characteristic_type = self.measurement_characteristic_type

    @QtCore.pyqtSlot(str)
    def on_ui_drain_source_voltage_textChanged(self, value):
        self.ui_drain_source_voltage.setToolTip("Vds = {0} V".format(self.drain_source_voltage))
        val = self.drain_source_voltage
        self.experiment_settings.drain_source_voltage = val
        #self.drain_source_voltage = val
        
    @QtCore.pyqtSlot(int)
    def on_ui_use_set_vds_range_stateChanged(self, value):
        self.experiment_settings.use_set_vds_range = self.use_drain_source_range

    @QtCore.pyqtSlot()
    def on_VdsRange_clicked(self):
        print("settings vds range")
        rng = self.experiment_settings.vds_range
        if rng:
            rng = rng.copy_object() #
        else:
            rng =  rh.RangeObject.empty_object()

        dialog = redit.RangeSelectorView()
        dialog.set_range(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vds_range = dialog.get_range()


    @QtCore.pyqtSlot(str)
    def on_ui_front_gate_voltage_textChanged(self, value):
        self.ui_front_gate_voltage.setToolTip("Vgs = {0} V".format(self.front_gate_voltage))
        val = self.front_gate_voltage
        self.experiment_settings.front_gate_voltage = val
        #self.front_gate_voltage = val
    
    @QtCore.pyqtSlot(int)
    def on_ui_use_set_vfg_range_stateChanged(self, value):
        self.experiment_settings.use_set_vfg_range = self.use_gate_source_range

    @QtCore.pyqtSlot()
    def on_VfgRange_clicked(self):
        print("settings vfg range")
        rng = self.experiment_settings.vfg_range
        if rng:
            rng = rng.copy_object() #
        else:
            rng = rh.RangeObject.empty_object()

        dialog = redit.RangeSelectorView()
        dialog.set_range(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vfg_range = dialog.get_range()

    @QtCore.pyqtSlot(int)
    def on_ui_set_zero_after_measurement_stateChanged(self, value):
        #print("set zero after measurement changed to {0}".format(value))
        self.experiment_settings.set_zero_after_measurement = self.set_zero_after_measurement


    @QtCore.pyqtSlot(str)
    def on_ui_experimentName_textChanged(self, value):
        self.experiment_settings.experiment_name = self.experimentName

    @QtCore.pyqtSlot(str)
    def on_ui_measurementName_textChanged(self,value):
        self.experiment_settings.measurement_name = self.measurementName

    @QtCore.pyqtSlot(int)
    def on_ui_measurementCount_valueChanged(self, value):
        self.experiment_settings.measurement_count = self.measurementCount

    @QtCore.pyqtSlot()
    def on_ui_startButton_clicked(self):
        self.set_ui_started()
        self.controller.start_experiment()
        

    @QtCore.pyqtSlot()
    def on_ui_stopButton_clicked(self):
        self.set_ui_stopping()
        self.controller.stop_experiment()

    


    def closeEvent(self, event):
        self.controller.on_main_view_closing()

    #**************
    #end event handlers
    #**************

    def ui_set_experiment_started(self):
        pass

    def ui_set_experiment_idle(self):
        pass

    def ui_set_experiment_stopped(self):
        pass

    def ui_show_message_in_status_bar(self, message = "",  timeout=0):
        self.statusbar.showMessage(message, timeout)

    def ui_show_message_in_popup_window(self, message):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText(message)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(message)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        retval = msg.exec_()


    def ui_set_measurement_info_start(self, measurement_info):
        if isinstance(measurement_info, MeasurementInfo):
            self.front_gate_voltage_start = measurement_info.start_gate_voltage
            self.sample_voltage_start = measurement_info.start_sample_voltage
            self.sample_current_start = measurement_info.sample_current_start
            self.sample_resistance_start = measurement_info.sample_resistance_start
            self.current_temperature = measurement_info.start_temperature
            
    def ui_set_measurement_info_end(self, measurement_info):
        if isinstance(measurement_info, MeasurementInfo):
            self.front_gate_voltage_end= measurement_info.end_gate_voltage
            self.sample_voltage_end = measurement_info.end_sample_voltage
            self.sample_current_end = measurement_info.sample_current_end
            self.sample_resistance_end = measurement_info.sample_resistance_end
            self.current_temperature = measurement_info.end_temperature

    def ui_set_measurement_count(self, measurement_count):
        self.measurementCount = measurement_count

    def ui_increment_measurement_count(self):
        self.measurementCount += 1

    def ui_update_spectrum_data(self, rang, data):
        self._spectrumPlotWidget.update_spectrum(rang, data)

    def ui_update_resulting_spectrum_data(self, data):
        frequency = data[pcp.FREQUENCIES]
        spectrum_data = data[pcp.DATA]
        self._spectrumPlotWidget.updata_resulting_spectrum(frequency,spectrum_data)

    def ui_update_calculated_thermal_noise(self, data):
        frequency = data[pcp.FREQUENCIES]
        spectrum_data = data[pcp.DATA]
        self._spectrumPlotWidget.update_thermal_noise(frequency,spectrum_data)

    def ui_update_timetrace(self, data):
        pass

    def ui_update_progress(self, progress):
        self.progressBar.setValue(progress)

class ProcessingThread(QtCore.QThread):
    
    threadStarted = QtCore.pyqtSignal()
    threadStopped = QtCore.pyqtSignal()
    commandReceived = QtCore.pyqtSignal(pcp.ExperimentCommands) #int)
    experimentStarted = QtCore.pyqtSignal(dict)
    experimentFinished = QtCore.pyqtSignal()
    measurementStarted = QtCore.pyqtSignal(dict)
    measurementFinished = QtCore.pyqtSignal()
    measurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    startMeasurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    endMeasurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    resulting_spectrum_update = QtCore.pyqtSignal(dict)
    log_message_received = QtCore.pyqtSignal(str)
    progressChanged = QtCore.pyqtSignal(int)
    thermal_noise_update = QtCore.pyqtSignal(dict)
    voltageSettingStarted = QtCore.pyqtSignal()
    voltageSettingStopped = QtCore.pyqtSignal(int)
    drainSourceVoltageChanged = QtCore.pyqtSignal(float)
    gateSourceVoltageChanged = QtCore.pyqtSignal(float)

    def __init__(self, input_data_queue = None,visualization_queue = None, parent = None):
        super().__init__(parent)
        self.alive = False
        assert isinstance(visualization_queue, deque)
        self._visualization_queue = visualization_queue
        #assert isinstance(input_data_queue, JoinableQueue)
        self._input_data_queue = input_data_queue

    def stop(self):
        self.alive = False
        self.wait()

    def run(self):
        self.alive = True
        #while self.alive
        while self.alive or (not self._input_data_queue.empty()):
            try:
                data = self._input_data_queue.get(timeout = 1)
                self._input_data_queue.task_done()
                cmd_format = "{0} command received"
                cmd = data.get(pcp.COMMAND)
                param = data.get(pcp.PARAMETER)
                
                #print(cmd_format.format(ExperimentCommands[cmd]))
                if cmd is None:
                    continue
                elif cmd is pcp.ExperimentCommands.EXPERIMENT_STARTED:
                    self.commandReceived.emit(pcp.ExperimentCommands.EXPERIMENT_STARTED)
                    self.experimentStarted.emit(param)
                    continue

                elif cmd is pcp.ExperimentCommands.EXPERIMENT_FINISHED:
                    self.alive = False
                    self.commandReceived.emit(pcp.ExperimentCommands.EXPERIMENT_FINISHED)
                    self.experimentFinished.emit()
                    break

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_STARTED:
                    self.commandReceived.emit(pcp.ExperimentCommands.MEASUREMENT_STARTED)
                    self.measurementStarted.emit(param)
                    continue

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_FINISHED:
                    self.commandReceived.emit(pcp.ExperimentCommands.MEASUREMENT_FINISHED)
                    self.measurementFinished.emit()
                    continue

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_INFO:
                    self.measurementDataArrived.emit(param)

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_INFO_START:
                    self.startMeasurementDataArrived.emit(param)

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_INFO_END:
                    self.endMeasurementDataArrived.emit(param)

                elif cmd is pcp.ExperimentCommands.DATA:
                    self._visualization_queue.append(data)   
                     
                elif cmd is pcp.ExperimentCommands.SPECTRUM_DATA:
                    self.resulting_spectrum_update.emit(data)
                
                elif cmd is pcp.ExperimentCommands.LOG_MESSAGE:
                    self.log_message_received.emit(param)

                elif cmd is pcp.ExperimentCommands.PROGRESS_CHANGED:
                    self.progressChanged.emit(param)

                elif cmd is pcp.ExperimentCommands.THERMAL_NOISE:
                    self.thermal_noise_update.emit(data)

                elif cmd is pcp.ExperimentCommands.VOLTAGE_SETTING_STARTED:
                    self.voltageSettingStarted.emit()

                elif cmd is pcp.ExperimentCommands.VOLTAGE_SETTING_STOPPED:
                    self.voltageSettingStopped.emit(param)

                elif cmd is pcp.ExperimentCommands.DRAIN_SOURCE_VOLTAGE_CHANGED:
                    self.drainSourceVoltageChanged.emit(param)

                elif cmd is pcp.ExperimentCommands.GATE_SOURCE_VOLTAGE_CHANGED:
                    self.gateSourceVoltageChanged.emit(param)

            except EOFError as e:
                print(str(e))
                break
            except:
                pass

        self.alive = False


emailAuthBase, emailAuthForm = uic.loadUiType("UI/UI_email_auth.ui")
class EmailAuthForm(emailAuthBase, emailAuthForm):
    #email_cfg = "em.cfg"

    username = uih.bind("ui_login", "text", str)
    password = uih.bind("ui_password", "text", str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    email_cfg = "em.cfg"
    #message_format = """
    #From: {f}
    #To: {t}
    #Subject: {s}
    #{msg}
    #"""
    def __init__(self):
        self._server = ""
        self._my_address = ""
        self._login = ""
        self._password = ""
        self._login_successful = False
        
        with open("em.cfg") as cfg:
            self._server = cfg.readline().rstrip()
            self._my_address = cfg.readline().rstrip()

    def initialize(self, login, password):
        assert isinstance(login, str)
        assert isinstance(password, str)
        try:
            server = smtplib.SMTP(self._server)
            res_code, res_message = server.starttls()
            assert res_code == 220, "SMTP is not ready"
            res_code, res_message = server.login(login, password)
            assert res_code == 235, "Authentication unseccessful"
            res_code, res_message = server.quit()
            assert res_code == 221, "Quit error"
            self._login_successful = True
            self._login = login
            self._password = password
            print("email login successful")

        except Exception as e:
            print(str(e))
            self._login_successful = False
            print("email login failed")
        finally:
            return self._login_successful 

    def logoff(self):
        self._login_successful = False
        self._login = ""
        self._password = ""
        print("logoff successful")

    def send_message(self, subject, message):
        try:
            assert self._login_successful, "Initialize first"
            server = smtplib.SMTP(self._server)
            res_code, res_message = server.starttls()
            assert res_code == 220, "SMTP is not ready"
            res_code, res_message = server.login(self._login, self._password)
            assert res_code == 235, "Authentication unseccessful"
            res_code, res_message = server.mail(self._my_address)
            assert res_code == 250, "Sender FAILURE"
            res_code, res_message = server.rcpt(self._my_address)
            assert res_code == 250, "Sender FAILURE"

            my_address = self._my_address.format(login = self._login)
            msg = MIMEMultipart()
            msg['From'] = my_address
            msg['To'] = my_address
            msg['Subject'] = subject
            msg.attach(MIMEText(message))

            #message = self.message_format.format(f = self._my_address, t = self._my_address.format(login = self._login), s = subject, msg = message)
            message = msg.as_string()

            res_code, res_message = server.data(message)
            assert res_code == 250, "Message sending error"
            res_code, res_message = server.quit()
            assert res_code == 221, "Quit error"
            print("message is queued")
            return True
            
        except Exception as e:
            print(str(e))
            return False

        

consoleViewBase, consoleViewForm = uic.loadUiType("UI/UI_Console.ui")
class UI_Console(consoleViewBase, consoleViewForm):
    def __init__(self, parent = None):
        super(consoleViewBase,self).__init__(parent)
        self.setupUi()
        #self.


    def setupUi(self):
        super().setupUi(self)

    @QtCore.pyqtSlot(str)
    def append_text(self, text):
        self.console_widget.appendPlainText(text)

    def clear(self):
        pass


class FANS_UI_Controller(QtCore.QObject):
    settings_filename = "settings.cfg"
    def __init__(self, view):
        super().__init__()
        assert isinstance(view, FANS_UI_MainView)
        self.main_view = view
        self.main_view.set_controller(self)
        self.show_main_view()

        self.voltage_control = VoltageControl()
        self.waterfall_noise_window = plt.WaterfallNoiseWindow()
        self._console_window = UI_Console()

        self._script_executed_with_console = True #self.check_if_script_executed_with_console()
        #print("Script is executed with console: {0}".format(self.script_executed_with_console))
        #if self.script_executed_with_console:
        #    self.console_window = UI_Console()


        self.subscribe_to_ui_signals()
        self.experiment_settings = None
        self.hardware_settings = None
        self.load_settings()

        self.experiment_stop_event = Event()
        self.visualization_deque = deque(maxlen = 100)
        self.input_data_queue = JoinableQueue() 
        self.processing_thread = None
        self.experiment_thread = None
        self.ui_refresh_timer = QtCore.QTimer(self)
        self.ui_refresh_timer.setInterval(50)
        self.ui_refresh_timer.timeout.connect(self.update_ui)
        self.email_sender = None
        self.play_on_startup()
        #self.login_to_email_sender()

        #self.wa = WhatsAppSender()
        #self.initialize_experiment()
    @property
    def script_executed_with_console(self):
        return self._script_executed_with_console

    @script_executed_with_console.setter
    def script_executed_with_console(self, value):
        self._script_executed_with_console = value

    @property
    def console_window(self):
        return self._console_window

    def play_on_startup(self):
        from playsound import playsound
        filename = "Media/startup.mp3"
        if os.path.isfile(filename):
            playsound(filename)


   

    def subscribe_to_ui_signals(self):
        self.main_view.subscribe_to_email_login_action(self.login_to_email_sender)
        self.main_view.subscribe_to_hardware_settings_action(self.show_hardware_settings_view)
        self.main_view.subscribe_to_waterfall_noise_action(self.show_waterfall_noise_window)
        self.main_view.subscribe_to_open_console_window_action(self.show_console_window)
        #pass
    #def login_test(self):
    #    print("test")

    def login_to_email_sender(self):
        dialog = EmailAuthForm()
        result = dialog.exec_()
        if result:
            self.email_sender = EmailSender()
            result = self.email_sender.initialize(dialog.username, dialog.password)
            if result:
                self.email_sender.send_message("FANS LOGIN", "You are logged in as a FANS user")
                self.main_view.ui_show_message_in_popup_window("Successfully logged in")
            else:
                self.email_sender.logoff()
                self.main_view.ui_show_message_in_popup_window("Log in failed!")
        else:
            if self.email_sender:
                self.email_sender.logoff()     
                self.main_view.ui_show_message_in_popup_window("Log in failed!")



    def send_message_via_email(self, message):
        if self.email_sender:
            self.email_sender.send_message("FANS Message", message)

    def load_settings(self):
        self.load_settings_from_file()
        self.main_view.experiment_settings = self.experiment_settings
        
    def start_experiment(self):
        print("start experiment")
        self.copy_main_view_settings_to_settings_object()
        #self.main_view.set_ui_started()
        self.initialize_experiment()
        self.ui_refresh_timer.start()
        self.experiment_thread.start()
        self.processing_thread.start()
        #self.input_data_queue.join()
        #self.load_settings()
        #self.main_view.ui_increment_measurement_count()


    def stop_experiment(self):
        print("stop experiment")
        self.experiment_stop_event.set()
        self.experiment_thread.stop()
        self.processing_thread.stop()
        self.ui_refresh_timer.stop()
        self.experiment_thread.join()
        self.main_view.set_ui_idle()
        #self.save_settings_to_file()

    def copy_main_view_settings_to_settings_object(self):
        assert isinstance(self.main_view, FANS_UI_MainView)
        mv = self.main_view
        self.experiment_settings.calibrate_before_measurement = mv.calibrate_before_measurement
        self.experiment_settings.overload_rejecion = mv.overload_reject
        self.experiment_settings.simulate_experiment = mv.simulate_measurement
        self.experiment_settings.averages = mv.number_of_averages
        self.experiment_settings.use_homemade_amplifier = mv.use_homemade_amplifier
        self.experiment_settings.second_amp_coeff = mv.second_amplifier_gain
        self.experiment_settings.need_measure_temperature = mv.perform_temperature_measurement
        self.experiment_settings.current_temperature = mv.current_temperature
        self.experiment_settings.load_resistance = mv.load_resistance
        self.experiment_settings.meas_gated_structure = mv.perform_measurement_of_gated_structure
        self.experiment_settings.use_transistor_selector = mv.use_dut_selector
        self.experiment_settings.use_automated_voltage_control = mv.use_automated_voltage_control
        self.experiment_settings.meas_characteristic_type = mv.measurement_characteristic_type
        self.experiment_settings.drain_source_voltage = mv.drain_source_voltage
        self.experiment_settings.front_gate_voltage = mv.front_gate_voltage
        self.experiment_settings.use_set_vds_range = mv.use_drain_source_range
        self.experiment_settings.use_set_vfg_range = mv.use_gate_source_range
        self.experiment_settings.experiment_name = mv.experimentName
        self.experiment_settings.measurement_name = mv.measurementName
        self.experiment_settings.measurement_count = mv.measurementCount
        mv.save_timetrace_settings(self.experiment_settings)
        self.experiment_settings.set_zero_after_measurement = mv.set_zero_after_measurement
    

    def show_main_view(self):
        assert isinstance(self.main_view, FANS_UI_MainView)
        #self.main_view.show()
        self.main_view.showMaximized()

    def on_main_view_closing(self):
        print("closing main view")
        self.copy_main_view_settings_to_settings_object()
        self.save_settings_to_file()

    def show_console_window(self):
        #
        if self.script_executed_with_console:
            msg = "program is started in console mode"
            print(msg)
            self.main_view.ui_show_message_in_status_bar(msg,3000)
        else:
            print("opening console window")
            self.console_window.show()

    def show_waterfall_noise_window(self):
        self.waterfall_noise_window.show()

    def show_hardware_settings_view(self):
        dialog = HardwareSettingsView()
        dialog.set_hardware_settings(self.hardware_settings)
        result = dialog.exec_()
        if result:
            dialog.copy_settings_to_object()
        print(result)
    
    def save_settings_to_file(self):
        with open(self.settings_filename,"wb") as f:
            save_object = (self.experiment_settings, self.hardware_settings) 
            pickle.dump(save_object, f)
       
    def load_settings_from_file(self):
        if not os.path.isfile(self.settings_filename):
            print("creating new settings")
            self.experiment_settings = ExperimentSettings()
            self.hardware_settings = HardwareSettings()
        else:
            print("loading settings from file")
            with open(self.settings_filename,"rb") as f:
                exp_settings, hardware_settings = pickle.load(f)
                self.experiment_settings = exp_settings
                self.hardware_settings = hardware_settings
   
    def initialize_experiment(self):
        self.processing_thread = ProcessingThread(self.input_data_queue, self.visualization_deque)
        self.processing_thread.experimentStarted.connect(self.on_experiment_started)
        self.processing_thread.experimentFinished.connect(self.on_experiment_finished)
        self.processing_thread.measurementStarted.connect(self.on_measurement_started)
        self.processing_thread.measurementFinished.connect(self.on_measurement_finished)
        self.processing_thread.startMeasurementDataArrived.connect(self.on_start_measurement_info_received)
        self.processing_thread.endMeasurementDataArrived.connect(self.on_end_measurement_info_received)
        self.processing_thread.resulting_spectrum_update.connect(self.on_resulting_spectrum_received)
        self.processing_thread.log_message_received.connect(self.on_log_message_received)
        self.processing_thread.commandReceived.connect(self.on_command_received)
        self.processing_thread.progressChanged.connect(self.on_progress_changed)
        self.processing_thread.thermal_noise_update.connect(self.on_thermal_noise_received)
        self.processing_thread.voltageSettingStarted.connect(self.on_setting_voltage_start)
        self.processing_thread.voltageSettingStopped.connect(self.on_setting_voltage_stop)
        self.processing_thread.drainSourceVoltageChanged.connect(self.on_drain_source_voltage_changed)
        self.processing_thread.gateSourceVoltageChanged.connect(self.on_gate_source_voltage_changed)

        self.experiment_thread = mfexp.FANSExperimentHandler(self.input_data_queue, self.experiment_settings, self.hardware_settings) # FANSExperiment(self.input_data_queue, self.experiment_stop_event)



    def on_experiment_started(self, params):
        experiment_name = params.get("experiment_name") #experiment_name
        msg = "Experiment \"{0}\" started".format(experiment_name)
        self.main_view.ui_show_message_in_status_bar(msg, 1000)
        #self.wa.send_message(msg)
        self.send_message_via_email(msg)

    def on_experiment_finished(self):
        msg = "Experiment finished"
        self.main_view.ui_show_message_in_status_bar(msg, 1000)
        #self.wa.send_message(msg)
        self.send_message_via_email(msg)
        self.stop_experiment()
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Experiment completed!!!")
        msg.setInformativeText("Additional info about measurement")
        msg.setWindowTitle("Measurement completed")
        msg.setDetailedText("Data saved in folder: {0}".format(self.experiment_settings.working_directory))
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        
    def on_voltage_control_view_clicked(self):
        resource = self.hardware_settings.fans_controller_resource
        fans_controller = mfans.FANS_CONTROLLER(resource)

        sample_motor_pin = self.hardware_settings.sample_motor_channel #get_fans_ao_channels_from_number(self.hardware_settings.sample_motor_channel)
        gate_motor_pin = self.hardware_settings.gate_motor_channel #get_fans_ao_channels_from_number(self.hardware_settings.gate_motor_channel)
        sample_relay = self.hardware_settings.sample_relay_channel #get_fans_ao_channels_from_number(self.hardware_settings.sample_relay_channel)
        gate_relay = self.hardware_settings.gate_relay_channel #get_fans_ao_channels_from_number(self.hardware_settings.gate_relay_channel)

        sample_feedback_pin = self.hardware_settings.sample_feedback_channel  #mfans.FANS_AI_CHANNELS.AI_CH_6
        gate_feedback_pin = self.hardware_settings.gate_feedback_channel #mfans.FANS_AI_CHANNELS.AI_CH_8
        main_feedback_pin = self.hardware_settings.main_feedback_channel #mfans.FANS_AI_CHANNELS.AI_CH_7
        
        drain_source_voltage_switch_channel = mfans.FANS_AO_CHANNELS.AO_CH_10

        load_resistance = self.experiment_settings.load_resistance
        fans_smu = msmu.FANS_SMU_Specialized(fans_controller, sample_motor_pin, sample_relay, sample_feedback_pin, gate_motor_pin, gate_relay, gate_feedback_pin, main_feedback_pin, drain_source_voltage_switch_channel)
        fans_smu.set_smu_parameters(100, load_resistance)

        self._voltage_control = VoltageControlView(parent_fans_smu = fans_smu)
        self._voltage_control.show()

    def on_measurement_started(self, params):
        measurement_name = params.get("measurement_name")
        measurement_count = params.get("measurement_count")
        msg = "Measurement \"{0}:{1}\" started".format(measurement_name, measurement_count)
        print(msg)
        self.main_view.ui_show_message_in_status_bar(msg, 1000)
        #self.main_view.ui_set_measurement_count(measurement_count+1)

    def on_measurement_finished(self):
        self.main_view.ui_increment_measurement_count()

    def on_start_measurement_info_received(self, measurement_info):
        self.main_view.ui_set_measurement_info_start(measurement_info)

    def on_end_measurement_info_received(self,measurement_info):
        self.main_view.ui_set_measurement_info_end(measurement_info)

    def on_resulting_spectrum_received(self,data):
        self.main_view.ui_update_resulting_spectrum_data(data)

    def on_thermal_noise_received(self, data):
        self.main_view.ui_update_calculated_thermal_noise(data)

    def on_setting_voltage_start(self):
        print("UI: voltage setting started")
        #self.voltage_control.setWindowModality(QtCore.Qt.ApplicationModal)
        self.voltage_control.show()
        self.voltage_control.set_in_progress_state()

    def on_setting_voltage_stop(self, error_code):
        print("UI: voltage setting stopped")
        if error_code == 0:
            self.voltage_control.set_okay_state()
        else:
            self.voltage_control.set_error_state()
        time.sleep(0.5)
        self.voltage_control.hide()

    def on_drain_source_voltage_changed(self, voltage):
        print("UI: voltage {0}".format(voltage))
        self.voltage_control.set_drain_source_voltage(voltage)

    def on_gate_source_voltage_changed(self, voltage):
        print("UI: voltage {0}".format(voltage))
        self.voltage_control.set_gate_source_voltage(voltage)

    def on_progress_changed(self, progress):
        self.main_view.ui_update_progress(progress)

    def on_log_message_received(self, message):
        if message:
            print("received log message")
            print(message)
            self.main_view.ui_show_message_in_status_bar(message, 100)#._status_object.send_message(message)

    def on_command_received(self, cmd):
        if isinstance(cmd, pcp.ExperimentCommands):
            self.main_view.ui_show_message_in_status_bar(cmd.name)

    def update_ui(self):
        try:
            #print("updating gui")
            data = self.visualization_deque.popleft()
            cmd_format = "{0} command received"
            cmd = data.get(pcp.COMMAND)
            
            if cmd is pcp.ExperimentCommands.DATA:
                index = data[pcp.INDEX]
                rang = data[pcp.SPECTRUM_RANGE]
                #print("visualized data index: {0}".format(index))
                self.main_view.ui_update_spectrum_data(rang ,data)
                self.waterfall_noise_window.update_data(rang,data)
        except Exception as e:
            pass


def check_if_script_executed_with_console():
    executable = sys.executable
    basename = os.path.basename(executable)
    filename, file_extention = os.path.splitext(basename)
    if filename == "pythonw":
        return False
    else:
        return True

from queue import Queue

# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!
class WriteStream(object):
    def __init__(self,queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass

# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal 
class MyReceiver(QtCore.QObject):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self,queue,*args,**kwargs):
        QtCore.QObject.__init__(self,*args,**kwargs)
        self.queue = queue

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)



def test_ui():
    import ctypes
    myappid = "fzj.pyfans.pyfans.21" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
   

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS")
    app.setStyle("cleanlooks")
    #icon_file = "pyfans.ico"
    icon_file = "UI/Icons/pyfans.png"
    app_icon = QtGui.QIcon()
    app_icon.addFile(icon_file, QtCore.QSize(16,16))
    app_icon.addFile(icon_file, QtCore.QSize(24,24))
    app_icon.addFile(icon_file, QtCore.QSize(32,32))
    app_icon.addFile(icon_file, QtCore.QSize(48,48))
    app_icon.addFile(icon_file, QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)
    #app.setWindowIcon(QtGui.QIcon('pyfans.ico'))
    
    wnd = FANS_UI_MainView()
    controller = FANS_UI_Controller(wnd)
    script_executed_with_console = check_if_script_executed_with_console()
    controller.script_executed_with_console = script_executed_with_console
    wnd.ui_show_message_in_status_bar("Execution in {0} mode".format("console" if script_executed_with_console else "window"), 5000)
    #filename, file_extention = os.path.splitext(sys.executable)
    #wnd.ui_show_message_in_status_bar("Execution with {0}".format(filename))
    if not script_executed_with_console:
        queue = Queue()
        sys.stdout = WriteStream(queue)
        console_thread = QtCore.QThread()
        receiver = MyReceiver(queue)
        receiver.mysignal.connect(controller.console_window.append_text)
        receiver.moveToThread(console_thread)
        console_thread.started.connect(receiver.run)
        console_thread.start()
    
    #controller.show_main_view()
    return app.exec_()
    
def test_cmd():
    s = ExperimentSettings()
    s.averages = 10
    t =uih.get_module_name_and_type(1)
    print(t)
    v = uih.get_value_of_module_type(6, t)
    print(v)
    return 0


if __name__== "__main__":
    sys.exit(test_ui())
    #sys.exit(test_cmd())
    #sys.exit(test_xml_serializer())


 
