import os
import sys
import time
import pint
import pickle

from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore


import pyfans
# from pyfans.main_controller import FANS_UI_Controller
import pyfans.utils.ui_helper as uih
#from pyfans.utils.ui_helper import Binding, BindingDirection, StringToIntConverter, StringToFloatConverter, StringToVoltageConverter, AssureBoolConverter, AssureIntConverter
import pyfans.plot as plt
import pyfans.experiment.process_communication_protocol as pcp
from pyfans.experiment.fans_experiment_settings import ExperimentSettings
from pyfans.experiment.modern_fans_experiment import CharacteristicType
import pyfans.ranges.modern_range_editor as mredit

class CharacteristicTypeToStrConverter(uih.ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, value):
        try:
            return CharacteristicType[value]
            
        except Exception as e:
            raise ConversionException()

    def convert_back(self, value):
        try:
            if not isinstance(value, CharacteristicType):
                raise Exception()

            return  value.name

        except Exception as e:
            raise ConversionException()


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
        self.ui_drain_source_voltage.setValidator(uih.VoltageValidator())
        self.ui_front_gate_voltage.setValidator(uih.VoltageValidator())
        self.__setup_folder_browse_button()
        self._spectrumPlotWidget =  plt.SpectrumPlotWidget(self.ui_plot,{0:(0,1600,1),1:(0,102400,64)})
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
        # self.menuSettings
    def setupBinding(self):
        sourceObject = None
        self.calibrate_before_measurement = uih.Binding(self.ui_calibrate, "checked", sourceObject, "calibrate_before_measurement", converter=uih.AssureBoolConverter()) # uih.bind("ui_calibrate", "checked", bool)

        self.overload_reject = uih.Binding(self.ui_overload_reject, "checked", sourceObject, "overload_rejecion", converter=uih.AssureBoolConverter()) 

        # self.display_refresh = uih.Binding(self.ui_display_refresh, "value", sourceObject, "display_refresh", converter=uih.StringToIntConverter())

        self.simulate_measurement = uih.Binding(self.ui_simulate, "checked", sourceObject, "simulate_experiment", converter=uih.AssureBoolConverter())

        self.number_of_averages =  uih.Binding(self.ui_averages, "value", sourceObject, "averages", converter=uih.StringToIntConverter()) 

        self.use_homemade_amplifier = uih.Binding(self.ui_use_homemade_amplifier, "checked", sourceObject, "use_homemade_amplifier", converter=uih.AssureBoolConverter())

        self.second_amplifier_gain = uih.Binding(self.ui_second_amp_coeff, "currentText", sourceObject, "second_amp_coeff", converter=uih.StringToIntConverter())

        self.perform_temperature_measurement = uih.Binding(self.ui_need_meas_temp, "checked", sourceObject, "need_measure_temperature", converter=uih.AssureBoolConverter())

        self.current_temperature =  uih.Binding(self.ui_current_temp, "text", sourceObject, "current_temperature", converter=uih.StringToFloatConverter(), stringFormat=temperature_format) 

        self.load_resistance =  uih.Binding(self.ui_load_resistance, "text", sourceObject, "load_resistance", converter=uih.StringToFloatConverter())

        self.perform_measurement_of_gated_structure = uih.Binding(self.ui_meas_gated_structure, "checked", sourceObject, "meas_gated_structure", converter=uih.AssureBoolConverter())

        # self.use_dut_selector = uih.Binding(self.ui_use_dut_selector, "checked", sourceObject, "use_dut_selector", converter=uih.AssureBoolConverter())

        self.use_automated_voltage_control = uih.Binding(self.ui_use_automated_voltage_control, "checked", sourceObject, "use_automated_voltage_control", converter=uih.AssureBoolConverter())

        self.measurement_characteristic_type = uih.Binding(self.ui_meas_characteristic_type, "currentIndex", sourceObject, "meas_characteristic_type", converter=CharacteristicTypeToStrConverter())
        # self.drain_source_voltage = uih.bind("ui_drain_source_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
        self.drain_source_voltage = uih.Binding(self.ui_drain_source_voltage, "text", sourceObject, "drain_source_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        # self.front_gate_voltage = uih.bind("ui_front_gate_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
        self.front_gate_voltage = uih.Binding(self.ui_front_gate_voltage, "text", sourceObject, "front_gate_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        # self.use_drain_source_range = uih.bind("ui_use_set_vds_range","checked", bool)
        self.use_drain_source_range = uih.Binding(self.ui_use_set_vds_range, "checked", sourceObject, "use_set_vds_range", converter=uih.AssureBoolConverter())
        # self.use_gate_source_range = uih.bind("ui_use_set_vfg_range","checked", bool)
        self.use_gate_source_range = uih.Binding(self.ui_use_set_vfg_range, "checked", sourceObject, "use_set_vfg_range", converter=uih.AssureBoolConverter())
        # self.experimentName = uih.bind("ui_experimentName", "text", str)
        self.experimentName = uih.Binding(self.ui_experimentName, "text", sourceObject, "experiment_name")
        # self.measurementName = uih.bind("ui_measurementName", "text", str)
        self.measurementName = uih.Binding(self.ui_measurementName, "text", sourceObject, "measurement_name")
        # self.measurementCount = uih.bind("ui_measurementCount", "value", int)
        self.measurementCount = uih.Binding(self.ui_measurementCount, "value", sourceObject, "measurement_count")
        self.timetrace_mode = uih.bind("ui_timetrace_mode", "currentIndex", int)
        self.timetrace_length = uih.bind("ui_timetrace_length", "value", int)
        self.set_zero_after_measurement = uih.bind("ui_set_zero_after_measurement", "checked", bool)

        ### binding to the other object
        # self.sample_voltage_start = uih.bind("ui_sample_voltage_start", "text", float, voltage_format)
        self.sample_voltage_start = uih.Binding(self.ui_sample_voltage_start, "text", sourceObject, "front_gate_voltage", converter=uih.StringToVoltageConverter())
        self.sample_voltage_end = uih.bind("ui_sample_voltage_end", "text", float, voltage_format)
        self.front_gate_voltage_start = uih.bind("ui_front_gate_voltage_start", "text", float, voltage_format)
        self.front_gate_voltage_end = uih.bind("ui_front_gate_voltage_end", "text", float, voltage_format)
        self.sample_current_start = uih.bind("ui_sample_current_start", "text", float, current_format)
        self.sample_current_end = uih.bind("ui_sample_current_end", "text", float, current_format)
        self.sample_resistance_start = uih.bind("ui_sample_resistance_start", "text", float,resistance_format)
        self.sample_resistance_end = uih.bind("ui_sample_resistance_end", "text", float, resistance_format)

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
        self.set_selected_folder_context_menu_item_text(settings.working_directory)
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
        # if rng:
        #     rng = rng.copy_object() #
        # else:
        #     rng =  rh.RangeObject.empty_object()

        if not isinstance(rng, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo)):
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        # dialog = redit.RangeSelectorView()
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vds_range = dialog.generateRangeInfo()


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
        # if rng:
        #     rng = rng.copy_object() #
        # else:
        #     rng = rh.RangeObject.empty_object()
        if not isinstance(rng, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo)):
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        # dialog = redit.RangeSelectorView()
        dialog = mredit.RangeEditorView()
        # dialog.set_range(rng)
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vfg_range = dialog.generateRangeInfo()

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
