import os
import sys
import time
import pint
import pickle

from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore


import pyfans
from pyfans.utils.ui_helper import DataContextWidget
import pyfans.utils.ui_helper as uih
import pyfans.utils.utils as util
import pyfans.plot as plt
import pyfans.experiment.process_communication_protocol as pcp
from pyfans.experiment.fans_experiment_settings import ExperimentSettings,CharacteristicType, TimetraceMode
from pyfans.experiment.measurement_data_structures import MeasurementInfo
import pyfans.ranges.modern_range_editor as mredit

class CharacteristicTypeToStrConverter(uih.ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, value):
        try:
            return CharacteristicType[value]
            
        except Exception as e:
            raise uih.ConversionException()

    def convert_back(self, value):
        try:
            if not isinstance(value, CharacteristicType):
                raise Exception()

            return  value.name

        except Exception as e:
            raise uih.ConversionException()

class TimetraceModeToIndexConverter(uih.ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, value):
        try:
            return TimetraceMode(value)
            
        except Exception as e:
            raise  uih.ConversionException()

    def convert_back(self, value):
        try:
            if not isinstance(value, TimetraceMode):
                raise Exception()

            return  value.value

        except Exception as e:
            raise uih.ConversionException()


mainViewBase, mainViewForm = uic.loadUiType("UI/UI_NoiseMeasurement_v5_3.ui")
class FANS_UI_MainView(mainViewBase,mainViewForm, DataContextWidget):
    ureg = UnitRegistry()
    voltage_format = "{:8.6f}"
    resistance_format = "{:.3f}"
    current_format = "{:.5e}"
    temperature_format = "{:.2f}"
   
    sample_voltage_start = uih.bind("ui_sample_voltage_start", "text", float, voltage_format)
    sample_voltage_end = uih.bind("ui_sample_voltage_end", "text", float, voltage_format)
    front_gate_voltage_start = uih.bind("ui_front_gate_voltage_start", "text", float, voltage_format)
    front_gate_voltage_end = uih.bind("ui_front_gate_voltage_end", "text", float, voltage_format)
    sample_current_start = uih.bind("ui_sample_current_start", "text", float, current_format)
    sample_current_end = uih.bind("ui_sample_current_end", "text", float, current_format)
    sample_resistance_start = uih.bind("ui_sample_resistance_start", "text", float,resistance_format)
    sample_resistance_end = uih.bind("ui_sample_resistance_end", "text", float, resistance_format)
    main_voltage_start = uih.bind("ui_main_voltage_start", "text", float, voltage_format)
    main_voltage_end = uih.bind("ui_main_voltage_end", "text", float, voltage_format)
    temperature_start = uih.bind("ui_temperature_start", "text", float, temperature_format)
    temperature_end = uih.bind("ui_temperature_end", "text", float, temperature_format)

    sigExperimentStart = QtCore.pyqtSignal()
    sigExperimentStop = QtCore.pyqtSignal()
    sigMainWindowClosing = QtCore.pyqtSignal()

    def __init__(self, parent = None):
       super(mainViewBase,self).__init__(parent)
       self.setupUi()
       self.setupBinding()
       self.init_values()
       self._controller = None
       self._experiment_settings = None
       
    def showMaximized(self):
        super().showMaximized()

    def setupUi(self):
        print("setting the ui up")
        super().setupUi(self)
        # self.ui_expandable_container.setContentLayout(self.ui_scroll_area.layout())
        # flags = QtCore.Qt.FramelessWindowHint
        # self.setWindowFlags(flags)
        self._temperature_checkbox_group = QtGui.QButtonGroup()
        self._temperature_checkbox_group.addButton(self.ui_set_temperature_single)
        self._temperature_checkbox_group.addButton(self.ui_use_set_temperature_range)

        self._drain_source_checkbox_group = QtGui.QButtonGroup()
        self._drain_source_checkbox_group.addButton(self.ui_set_drain_source_voltage)
        self._drain_source_checkbox_group.addButton(self.ui_use_set_vds_range)

        self._gate_source_checkbox_group = QtGui.QButtonGroup()
        self._gate_source_checkbox_group.addButton(self.ui_set_gate_source_voltage)
        self._gate_source_checkbox_group.addButton(self.ui_use_set_vfg_range)

        self.__setup_folder_browse_button()
        self._spectrumPlotWidget =  plt.SpectrumPlotWidget(self.ui_plot,{0:(0,1600,1),1:(0,102400,64)}, create_helper_handles=True, update_history=True)
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0,100)
        self.statusbar.addPermanentWidget(self.progressBar)
        self.set_ui_idle()

        showHelperCurvesAction = QtGui.QWidgetAction(self.menuSettings)
        checkBox = QtGui.QCheckBox("Helper Curves")
        checkBox.toggled.connect(self.on_showHelperCurvesAction_toggled)
        checkBox.setChecked(False)
        self.on_showHelperCurvesAction_toggled(False)
        showHelperCurvesAction.setDefaultWidget(checkBox)
        self.menuSettings.addAction(showHelperCurvesAction)

        showHistoryCurvesAction = QtGui.QWidgetAction(self.menuSettings)
        checkBox = QtGui.QCheckBox("History Curves")
        checkBox.toggled.connect(self.on_showHistoryCurvesAction_toggled)
        checkBox.setChecked(False)
        self.on_showHistoryCurvesAction_toggled(False)
        showHistoryCurvesAction.setDefaultWidget(checkBox)
        self.menuSettings.addAction(showHistoryCurvesAction)
        
    def setupBinding(self):
        sourceObject = None
        self.calibrate_before_measurement = uih.Binding(self.ui_calibrate, "checked", sourceObject, "calibrate_before_measurement", converter=uih.AssureBoolConverter()) # uih.bind("ui_calibrate", "checked", bool)
        self.overload_reject = uih.Binding(self.ui_overload_reject, "checked", sourceObject, "overload_rejecion", converter=uih.AssureBoolConverter()) 
        self.simulate_measurement = uih.Binding(self.ui_simulate, "checked", sourceObject, "simulate_experiment", converter=uih.AssureBoolConverter())
        self.number_of_averages =  uih.Binding(self.ui_averages, "value", sourceObject, "averages", converter=uih.StringToIntConverter()) 
        self.use_homemade_amplifier = uih.Binding(self.ui_use_homemade_amplifier, "checked", sourceObject, "use_homemade_amplifier", converter=uih.AssureBoolConverter())
        self.second_amplifier_gain = uih.Binding(self.ui_second_amp_coeff, "currentText", sourceObject, "second_amp_coeff", converter=uih.StringToIntConverter())
        self.perform_temperature_measurement = uih.Binding(self.ui_need_meas_temp, "checked", sourceObject, "need_measure_temperature", converter=uih.AssureBoolConverter())
        self.current_temperature =  uih.Binding(self.ui_temperature, "text", sourceObject, "current_temperature", converter=uih.StringToFloatConverter(), stringFormat=self.temperature_format, validator=QtGui.QDoubleValidator()) 
        self.use_temperature_range =  uih.Binding(self.ui_use_set_temperature_range, "checked", sourceObject, "use_temperature_range", converter=uih.AssureBoolConverter()) 
        self.use_automated_temperature_control =  uih.Binding(self.ui_automated_temperature, "checked", sourceObject, "use_automated_temperature_control", converter=uih.AssureBoolConverter()) 
        self.use_single_temperature =  uih.Binding(self.ui_set_temperature_single, "checked", sourceObject, "use_single_temperature", converter=uih.AssureBoolConverter()) 

        self.load_resistance =  uih.Binding(self.ui_load_resistance, "text", sourceObject, "load_resistance", converter=uih.StringToFloatConverter(), validator=QtGui.QIntValidator())
        self.perform_measurement_of_gated_structure = uih.Binding(self.ui_meas_gated_structure, "checked", sourceObject, "meas_gated_structure", converter=uih.AssureBoolConverter())
        self.use_dut_selector = uih.Binding(self.ui_use_dut_selector, "checked", sourceObject, "use_transistor_selector", converter=uih.AssureBoolConverter())
        self.use_automated_voltage_control = uih.Binding(self.ui_use_automated_voltage_control, "checked", sourceObject, "use_automated_voltage_control", converter=uih.AssureBoolConverter())
        self.measurement_characteristic_type = uih.Binding(self.ui_meas_characteristic_type, "currentText", sourceObject, "meas_characteristic_type", converter=CharacteristicTypeToStrConverter())
        self.drain_source_voltage = uih.Binding(self.ui_drain_source_voltage, "text", sourceObject, "drain_source_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.use_single_vds =  uih.Binding(self.ui_set_drain_source_voltage, "checked", sourceObject, "use_single_vds", converter=uih.AssureBoolConverter()) 

        self.front_gate_voltage = uih.Binding(self.ui_front_gate_voltage, "text", sourceObject, "front_gate_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.use_single_vfg = uih.Binding(self.ui_set_gate_source_voltage, "checked", sourceObject, "use_single_vfg", converter=uih.AssureBoolConverter()) 

        self.use_drain_source_range = uih.Binding(self.ui_use_set_vds_range, "checked", sourceObject, "use_set_vds_range", converter=uih.AssureBoolConverter())
        self.use_gate_source_range = uih.Binding(self.ui_use_set_vfg_range, "checked", sourceObject, "use_set_vfg_range", converter=uih.AssureBoolConverter())
        self.experimentName = uih.Binding(self.ui_experimentName, "text", sourceObject, "experiment_name", validator=uih.NameValidator())
        self.measurementName = uih.Binding(self.ui_measurementName, "text", sourceObject, "measurement_name", validator=uih.NameValidator())
        self.measurementCount = uih.Binding(self.ui_measurementCount, "value", sourceObject, "measurement_count")
        self.timetrace_mode = uih.Binding(self.ui_timetrace_mode, "currentIndex", sourceObject, "timetrace_mode", converter=TimetraceModeToIndexConverter())
        self.timetrace_mode.targetData = TimetraceMode.FULL.value
        self.timetrace_length =uih.Binding(self.ui_timetrace_length, "value", sourceObject, "timetrace_length")
        self.set_zero_after_measurement = uih.Binding(self.ui_set_zero_after_measurement, "checked", sourceObject, "set_zero_after_measurement", converter=uih.AssureBoolConverter())
        self.use_smart_spectrum_option = uih.Binding(self.ui_use_smart_spectrum, "checked", sourceObject, "use_smart_spectrum_option", converter=uih.AssureBoolConverter()) 


       
    def on_showHistoryCurvesAction_toggled(self, state):
        print("show history curves {0}".format(state))
        self._spectrumPlotWidget.setHistoryCurvesVisible(state)

    def on_showHelperCurvesAction_toggled(self, state):
        self._spectrumPlotWidget.setHelperCurvesVisible(state)

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

    def subscribe_to_open_settings_action(self, slot):
        self.connect(self.action_open_settings.triggered, slot)

    def subscribe_to_save_settings_action(self, slot):
        self.connect(self.action_save_settings.triggered, slot)

    def subscribe_to_time_info_action(self, slot):
        self.connect(self.actionTimeInfoWindow.triggered, slot)

    def subscribe_to_about_action(self, slot):
        self.connect(self.actionAbout.triggered, slot)

    def subscribe_to_what_to_do_action(self,slot):
        self.connect(self.action_what_to_do.triggered, slot)

    def subscribe_to_lock_screen_action(self, slot):
        self.connect(self.actionLockScreen.triggered, slot)

    def subscribe_to_switch_theme_action(self,slot):
        self.connect(self.actionThemeSwitch.triggered, slot)

    def subscribe_to_analysis_window_open_action(self,slot):
        self.connect(self.actionOpenAnalysisWindow.triggered, slot)

    def subscribe_to_experiment_start_action(self, slot):
        self.connect(self.sigExperimentStart, slot)

    def subscribe_to_experiment_stop_acion(self, slot):
        self.connect(self.sigExperimentStop, slot)

    def subscribe_to_window_closing_action(self, slot):
        self.connect(self.sigMainWindowClosing, slot)

    def subscribe_to_voltage_control_clicked(self, slot):
        self.connect(self.ui_voltage_control.clicked, slot)

    def subscribe_to_timetrace_converter_action(self, slot):
        self.connect(self.actionTimetraceConversion.triggered, slot)

    def subscribe_to_dut_selector_action(self, slot):
        self.connect(self.ui_transistorSelector.clicked, slot)

    @property
    def controller(self):
        return self._controller
    
    @controller.setter
    def controller(self,value):
        assert isinstance(value, pyfans.FANS_UI_Controller)
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
        util.open_folder_in_explorer(self.experiment_settings.working_directory)
        

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
        self.dataContext = settings
        if settings.working_directory:
            self.set_selected_folder_context_menu_item_text(settings.working_directory)
        
    UI_STATE_IDLE, UI_STATE_STARTED, UI_STATE_STOPPING = ui_states = range(3)
    def set_ui_state(self, state):
        if not state in self.ui_states:
            return

        if state is self.UI_STATE_IDLE:
            self.ui_startButton.setEnabled(True)
            self.ui_stopButton.setEnabled(True)
            self.progressBar.setVisible(False)
            self.progressBar.setValue(0)
            self.ui_settings_frame.setEnabled(True)
        elif state is self.UI_STATE_STARTED:
            self.ui_startButton.setEnabled(False)
            self.ui_stopButton.setEnabled(True)
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
            self.ui_settings_frame.setEnabled(False)
        elif state is self.UI_STATE_STOPPING:
            self.ui_startButton.setEnabled(False)
            self.ui_stopButton.setEnabled(False)
            self.progressBar.setVisible(True)
            self.ui_settings_frame.setEnabled(False)

    def set_ui_idle(self):
        self.set_ui_state(self.UI_STATE_IDLE)

    def set_ui_started(self):
        self.set_ui_state(self.UI_STATE_STARTED)

    def set_ui_stopping(self):
        self.set_ui_state(self.UI_STATE_STOPPING)

    #**************
    #event handlers
    #**************

    # TIMETRACE_NONE, TIMETRACE_PARTIAL, TIMETRACE_FULL = range(3)
    @QtCore.pyqtSlot(int)
    def on_ui_timetrace_mode_currentIndexChanged(self, index):
        print("timetrace mode changed to {0}".format(index))
        if index == TimetraceMode.NONE.value:
            self.ui_timetrace_length.hide()
        elif index == TimetraceMode.PARTIAL.value:
            self.ui_timetrace_length.show() 
        elif index == TimetraceMode.FULL.value:
            self.ui_timetrace_length.hide()

    @QtCore.pyqtSlot()
    def on_ui_open_hardware_settings_clicked(self):
        print("open hardware settings")
        #self.controller.show_hardware_settings_view()
        self.actionHardwareSettings.trigger()

    @QtCore.pyqtSlot()
    def on_ui_temp_range_button_clicked(self):
        print("settings vds range")
        rng = self.experiment_settings.temperature_range
        
        if not isinstance(rng, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo)):
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.temperature_range = dialog.generateRangeInfo()

    @QtCore.pyqtSlot()
    def on_VdsRange_clicked(self):
        print("settings vds range")
        rng = self.experiment_settings.vds_range
        
        if not isinstance(rng, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo)):
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vds_range = dialog.generateRangeInfo()

    @QtCore.pyqtSlot()
    def on_VfgRange_clicked(self):
        print("settings vfg range")
        rng = self.experiment_settings.vfg_range
        if not isinstance(rng, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo)):
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vfg_range = dialog.generateRangeInfo()

   
    @QtCore.pyqtSlot()
    def on_ui_startButton_clicked(self):
        self.set_ui_started()
        self.updateSourceData()
        self.sigExperimentStart.emit()
        # self.controller.start_experiment()
        

    @QtCore.pyqtSlot()
    def on_ui_stopButton_clicked(self):
        self.set_ui_stopping()
        self.sigExperimentStop.emit()
        # self.controller.stop_experiment()

    def closeEvent(self, event):
        self.updateSourceData()
        self.sigMainWindowClosing.emit()
        # if self.controller:
        #     self.controller.on_main_view_closing()

    #**************
    #end event handlers
    #**************

    def ui_show_message_in_status_bar(self, message = "",  timeout=0):
        self.statusbar.showMessage(message, timeout)

    def ui_show_message_in_popup_window(self, message):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText(message)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle("Message from PyFANS")
        msg.setDetailedText(message)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        retval = msg.exec_()


    def ui_set_measurement_info_start(self, measurement_info):
        if isinstance(measurement_info, MeasurementInfo):
            self.front_gate_voltage_start = measurement_info.start_gate_voltage
            self.sample_voltage_start = measurement_info.start_sample_voltage
            self.sample_current_start = measurement_info.sample_current_start
            self.sample_resistance_start = measurement_info.sample_resistance_start
            self.temperature_start = measurement_info.start_temperature
            self.main_voltage_start = measurement_info.start_main_voltage
            # pass
            
    def ui_set_measurement_info_end(self, measurement_info):
        if isinstance(measurement_info, MeasurementInfo):
            self.front_gate_voltage_end= measurement_info.end_gate_voltage
            self.sample_voltage_end = measurement_info.end_sample_voltage
            self.sample_current_end = measurement_info.sample_current_end
            self.sample_resistance_end = measurement_info.sample_resistance_end
            self.temperature_end = measurement_info.end_temperature
            self.main_voltage_end = measurement_info.end_main_voltage
            # pass


    def ui_set_measurement_count(self, measurement_count):
        self.experiment_settings.measurement_count = measurement_count
        # self.measurementCount = measurement_count

    def ui_increment_measurement_count(self):
        self.experiment_settings.measurement_count += 1
        # self.measurementCount += 1

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
