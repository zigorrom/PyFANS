import os
import sys
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

mainViewBase, mainViewForm = uic.loadUiType("UI_NoiseMeasurement_v3.ui")
class FANS_UI_MainView(mainViewBase,mainViewForm):
    ureg = UnitRegistry()
    calibrate_before_measurement = uih.bind("ui_calibrate", "checked", bool)
    overload_reject = uih.bind("ui_overload_reject", "checked", bool)
    display_refresh = uih.bind("ui_display_refresh", "value", int)
    simulate_measurement = uih.bind("ui_simulate", "checked", bool)
    number_of_averages = uih.bind("ui_averages", "value", int)
    use_homemade_amplifier = uih.bind("ui_use_homemade_amplifier", "checked", bool)
    second_amplifier_gain = uih.bind("ui_second_amp_coeff", "currentText", int)
    perform_temperature_measurement = uih.bind("ui_need_meas_temp","checked", bool)
    current_temperature = uih.bind("ui_current_temp", "text", float)
    load_resistance = uih.bind("ui_load_resistance", "text", float)
    perform_measurement_of_gated_structure = uih.bind("ui_meas_gated_structure", "checked", bool)
    use_dut_selector = uih.bind("ui_use_dut_selector", "checked", bool)
    use_automated_voltage_control = uih.bind("ui_use_automated_voltage_control", "checked", bool)
    measurement_characteristic_type = uih.bind("ui_meas_characteristic_type", "currentIndex", int)
    drain_source_voltage = uih.bind("ui_drain_source_voltage", "text", uih.string_to_volt_converter(ureg)) # ureg) #
    front_gate_voltage = uih.bind("ui_front_gate_voltage", "text", uih.string_to_volt_converter(ureg)) # ureg) #
    use_drain_source_range = uih.bind("ui_use_set_vds_range","checked", bool)
    use_gate_source_range = uih.bind("ui_use_set_vfg_range","checked", bool)
    sample_voltage_start = uih.bind("ui_sample_voltage_start", "text", float)
    sample_voltage_end = uih.bind("ui_sample_voltage_end", "text", float)
    front_gate_voltage_start = uih.bind("ui_front_gate_voltage_start", "text", float)
    front_gate_voltage_end = uih.bind("ui_front_gate_voltage_end", "text", float)
    sample_current_start = uih.bind("ui_sample_current_start", "text", float)
    sample_current_end = uih.bind("ui_sample_current_end", "text", float)
    sample_resistance_start = uih.bind("ui_sample_resistance_start", "text", float)
    sample_resistance_end = uih.bind("ui_sample_resistance_end", "text", float)
    experimentName = uih.bind("ui_experimentName", "text", str)
    measurementName = uih.bind("ui_measurementName", "text", str)
    measurementCount = uih.bind("ui_measurementCount", "value", int)
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

        self.experimentName = settings.experiment_name
        self.measurementName = settings.measurement_name
        self.measurementCount = settings.measurement_count
        uih.setAllChildObjectSignaling(self,False)
    #**************
    #event handlers
    #**************

    @QtCore.pyqtSlot()
    def on_ui_open_hardware_settings_clicked(self):
        print("open hardware settings")
        self.controller.show_hardware_settings_view()
                
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
        self._print_test()
    
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
            rng = rng.copy_range() #
        else:
            rng = rh.float_range(0,1,1)

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
            rng = rng.copy_range() #
        else:
            rng = rh.float_range(0,1,1)

        dialog = redit.RangeSelectorView()
        dialog.set_range(rng)
        res = dialog.exec_()
        if res:
            self.experiment_settings.vfg_range = dialog.get_range()

    
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
        self.controller.start_experiment()

    @QtCore.pyqtSlot()
    def on_ui_stopButton_clicked(self):
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

    def ui_show_message_in_status_bar(self, message,  timeout=-1):
        pass

    def ui_show_message_in_popup_window(self, message):
        pass

    def ui_set_measurement_info_start(self, measurement_info):
        pass

    def ui_set_measurement_info_end(self, measurement_info):
        pass

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
        pass

    def ui_update_timetrace(self, data):
        pass

    def ui_update_progress(self, progress):
        pass

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

            except EOFError as e:
                print(str(e))
                break
            except:
                pass

        self.alive = False

class FANS_UI_Controller(QtCore.QObject):
    settings_filename = "settings.cfg"
    def __init__(self, view):
        super().__init__()
        assert isinstance(view, FANS_UI_MainView)
        self.main_view = view
        self.main_view.set_controller(self)
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

        self.initialize_experiment()

    def load_settings(self):
        self.load_settings_from_file()
        self.main_view.experiment_settings = self.experiment_settings
        
    def start_experiment(self):
        print("start experiment")
        self.ui_refresh_timer.start()
        self.experiment_thread.start()
        self.processing_thread.start()
        #self.input_data_queue.join()
        #self.load_settings()
        #self.main_view.ui_increment_measurement_count()


    def stop_experiment(self):
        print("stop experiment")
        self.experiment_stop_event.set()
        #self.experiment_thread.stop()
        self.processing_thread.stop()
        self.ui_refresh_timer.stop()
        self.experiment_thread.join()
        
        #self.save_settings_to_file()

    def show_main_view(self):
        assert isinstance(self.main_view, FANS_UI_MainView)
        self.main_view.show()

    def on_main_view_closing(self):
        print("closing main view")
        self.save_settings_to_file()

    def show_hardware_settings_view(self):
        dialog = HardwareSettingsView()
        dialog.set_hardware_settings(self.hardware_settings)
        result = dialog.exec_()
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

        self.experiment_thread = mfexp.FANSExperiment(self.input_data_queue, self.experiment_stop_event)



    def on_experiment_started(self, params):
        experiment_name = params.get("experiment name")
        msg = "Experiment \"{0}\" started".format(experiment_name)
        self.main_view.ui_show_message_in_status_bar(msg, 1000)

    def on_experiment_finished(self):
        msg = "Experiment finished"
        self.main_view.ui_show_message_in_status_bar(msg, 1000)
        self.stop_experiment()

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
            print("updating gui")
            data = self.visualization_deque.popleft()
            cmd_format = "{0} command received"
            cmd = data.get(pcp.COMMAND)
            
            if cmd is pcp.ExperimentCommands.DATA:
                index = data[pcp.INDEX]
                rang = data[pcp.SPECTRUM_RANGE]
                #print("visualized data index: {0}".format(index))
                self.main_view.ui_update_spectrum_data(rang ,data)
        except Exception as e:
            pass


def test_ui():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS")
    app.setStyle("cleanlooks")
    #icon_file = "pyfans.ico"
    icon_file = "pyfans.png"
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
    controller.show_main_view()
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
    sys.exit(test_xml_serializer())


 