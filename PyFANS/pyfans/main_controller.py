import os
import sys
import time
import pickle
from collections import deque
from multiprocessing import JoinableQueue
from multiprocessing import Event

from PyQt4 import uic, QtGui, QtCore

import pyfans
import pyfans.plot as plt
from pyfans.ui.about import UI_About
from pyfans.ui.voltage_widget import UI_VoltageWidget
from pyfans.ui.console import UI_Console
from pyfans.ui.time_info import UI_TimeInfo
from pyfans.ui.lock_window import UI_LockWindow
from pyfans.ui.theme_switch_window import UI_ThemeSwitchWindow
from pyfans.utils.sound_player import SoundPlayer
from pyfans.ui.email_notification import EmailAuthForm, EmailSender

from pyfans.experiment.fans_experiment_settings import ExperimentSettings
from pyfans.experiment.measurement_data_structures import MeasurementInfo
import pyfans.experiment.process_communication_protocol as pcp

from pyfans.hardware.fans_hardware_settings import HardwareSettings, HardwareSettingsView
import pyfans.hardware.modern_fans_controller as mfans
import pyfans.hardware.modern_fans_smu as msmu
from pyfans.hardware.StandAloneVoltageControl import VoltageControlView
import pyfans.experiment.modern_fans_experiment as mfexp


import pyfans_analyzer.experiment_data_analysis as eds

class FANS_UI_Controller(QtCore.QObject):
    settings_filename = "settings.cfg"
    def __init__(self, view):
        super().__init__()
        assert isinstance(view, pyfans.FANS_UI_MainView)
        
        self.threadPool = QtCore.QThreadPool()
        
        self.main_view = view
        self.main_view.set_controller(self)
        self.show_main_view()

        self.experimentData = eds.ExperimentData()
        self.analysis_window = None

        self._voltage_control = None
        self.voltage_widget = UI_VoltageWidget()
        self.waterfall_noise_window = plt.WaterfallNoiseWindow()
        self._console_window = UI_Console()
        self._time_info_window = UI_TimeInfo()
        self._lock_screen_window = UI_LockWindow()
        

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
        
        # app = QtGui.QApplication.instance()
        # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())

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

    def play_sound(self, filename):
        r = SoundPlayer(filename)
        self.threadPool.start(r)

    def play_on_startup(self):
        self.play_sound("Media/startup.mp3")

    def play_what_to_do(self):
        self.play_sound("Media/help.mp3")

    def subscribe_to_ui_signals(self):
        self.main_view.subscribe_to_email_login_action(self.login_to_email_sender)
        self.main_view.subscribe_to_hardware_settings_action(self.show_hardware_settings_view)
        self.main_view.subscribe_to_waterfall_noise_action(self.show_waterfall_noise_window)
        self.main_view.subscribe_to_open_console_window_action(self.show_console_window)
        self.main_view.subscribe_to_open_settings_action(self.on_open_settings_action)
        self.main_view.subscribe_to_save_settings_action(self.on_save_settings_action)
        self.main_view.subscribe_to_time_info_action(self.show_time_info_window)
        self.main_view.subscribe_to_about_action(self.on_show_about_window)
        self.main_view.subscribe_to_what_to_do_action(self.on_what_to_do_action)
        self.main_view.subscribe_to_lock_screen_action(self.on_lock_screen_action)
        self.main_view.subscribe_to_switch_theme_action(self.on_theme_switch_action)
        self.main_view.subscribe_to_analysis_window_open_action(self.on_analysis_window_open_action)
        self.main_view.subscribe_to_voltage_control_clicked(self.on_voltage_control_view_clicked)
        self.main_view.subscribe_to_timetrace_converter_action(self.on_open_timetrace_conversion)

        self.main_view.subscribe_to_experiment_start_action(self.start_experiment)
        self.main_view.subscribe_to_experiment_stop_acion(self.stop_experiment)
        self.main_view.subscribe_to_window_closing_action(self.on_main_view_closing)  
      

    def on_open_settings_action(self):
        name = QtGui.QFileDialog.getOpenFileName(self.main_view, "Open Settings File", filter = "*.pfs")
        if os.path.isfile(name):
            with open(name,"rb") as f:
                exp_settings = pickle.load(f)
                self.experiment_settings = exp_settings
                self.main_view.experiment_settings = exp_settings

    def on_save_settings_action(self):
        name = QtGui.QFileDialog().getSaveFileName(self.main_view, "Save Settings File")
        basename = os.path.basename(name)
        filename, ext = os.path.splitext(basename)
        if not ext:
            name += ".pfs"

        # self.copy_main_view_settings_to_settings_object()
        with open(name,"wb") as f:
            pickle.dump(self.experiment_settings, f)

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
        # self.copy_main_view_settings_to_settings_object()
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
        #self.ui_refresh_timer.stop()
        self.experiment_thread.join()
        self.ui_refresh_timer.stop()
        self.main_view.set_ui_idle()
        #self.save_settings_to_file()

    # def copy_main_view_settings_to_settings_object(self):
    #     assert isinstance(self.main_view, pyfans.FANS_UI_MainView)
    #     mv = self.main_view
    #     self.experiment_settings.calibrate_before_measurement = mv.calibrate_before_measurement
    #     self.experiment_settings.overload_rejecion = mv.overload_reject
    #     self.experiment_settings.simulate_experiment = mv.simulate_measurement
    #     self.experiment_settings.averages = mv.number_of_averages
    #     self.experiment_settings.use_homemade_amplifier = mv.use_homemade_amplifier
    #     self.experiment_settings.second_amp_coeff = mv.second_amplifier_gain
    #     self.experiment_settings.need_measure_temperature = mv.perform_temperature_measurement
    #     self.experiment_settings.current_temperature = mv.current_temperature
    #     self.experiment_settings.load_resistance = mv.load_resistance
    #     self.experiment_settings.meas_gated_structure = mv.perform_measurement_of_gated_structure
    #     self.experiment_settings.use_transistor_selector = mv.use_dut_selector
    #     self.experiment_settings.use_automated_voltage_control = mv.use_automated_voltage_control
    #     self.experiment_settings.meas_characteristic_type = mv.measurement_characteristic_type
    #     self.experiment_settings.drain_source_voltage = mv.drain_source_voltage
    #     self.experiment_settings.front_gate_voltage = mv.front_gate_voltage
    #     self.experiment_settings.use_set_vds_range = mv.use_drain_source_range
    #     self.experiment_settings.use_set_vfg_range = mv.use_gate_source_range
    #     self.experiment_settings.experiment_name = mv.experimentName
    #     self.experiment_settings.measurement_name = mv.measurementName
    #     self.experiment_settings.measurement_count = mv.measurementCount
    #     mv.save_timetrace_settings(self.experiment_settings)
    #     self.experiment_settings.set_zero_after_measurement = mv.set_zero_after_measurement
    

    def show_main_view(self):
        assert isinstance(self.main_view, pyfans.FANS_UI_MainView)
        #self.main_view.show()
        self.main_view.showMaximized()

    def on_main_view_closing(self):
        print("closing main view")
        # self.copy_main_view_settings_to_settings_object()
        self.save_settings_to_file()

        self.close_child_windows()

    def close_child_windows(self):
        widgetList = (self.voltage_widget,self.waterfall_noise_window,self._console_window,self._time_info_window,self._voltage_control)
        for child in widgetList:
            try:
                child.close()
            except:
                print("Cannot child widget {0}".format(child))
                pass
        
        # self.waterfall_noise_window.close()
        # self._console_window.close()
        # self._time_info_window.close()
        # self._lock_screen_window.close()
        
        # self._voltage_control.close()

    def show_time_info_window(self):
        self._time_info_window.show()

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
        print("from voltage control dialog")
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
        self.processing_thread.experimentTimeUpdate.connect(self.on_experiment_time_update)
        self.experiment_thread = mfexp.FANSExperimentHandler(self.input_data_queue, self.experiment_settings, self.hardware_settings, self.script_executed_with_console) # FANSExperiment(self.input_data_queue, self.experiment_stop_event)



    def on_experiment_started(self, params):
        experiment_name = params.get("experiment_name") #experiment_name
        msg = "Experiment \"{0}\" started".format(experiment_name)
        self.main_view.ui_show_message_in_status_bar(msg, 1000)
        #self.wa.send_message(msg)
        self.experimentData.clear()
        self.send_message_via_email(msg)
        self._time_info_window.reset()
        self._time_info_window.start_timer()

    def on_experiment_finished(self):
        msg = "Experiment finished"
        self.main_view.ui_show_message_in_status_bar(msg, 1000)
        #self.wa.send_message(msg)
        self.send_message_via_email(msg)
        self.stop_experiment()
        self._time_info_window.stop_timer()
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Experiment completed!!!")
        msg.setInformativeText("Additional info about measurement")
        msg.setWindowTitle("Measurement completed")
        msg.setDetailedText("Data saved in folder: {0}".format(self.experiment_settings.working_directory))
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        
    def on_voltage_control_view_clicked(self):
        if not self._voltage_control:
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
        if self.waterfall_noise_window:
            equivalent_resistance = measurement_info.equivalent_resistance_start
            sample_resistance = measurement_info.sample_resistance_start
            load_resistance = measurement_info.load_resistance
            temperature = measurement_info.start_temperature
            self.waterfall_noise_window.update_thermal_noise(equivalent_resistance, sample_resistance, load_resistance, temperature)

        self.main_view.ui_set_measurement_info_start(measurement_info)

    def on_end_measurement_info_received(self,measurement_info):
        self.main_view.ui_set_measurement_info_end(measurement_info)
        self.experimentData.append(measurement_info)

    def on_resulting_spectrum_received(self,data):
        self.main_view.ui_update_resulting_spectrum_data(data)

    def on_thermal_noise_received(self, data):
        self.main_view.ui_update_calculated_thermal_noise(data)

    def on_setting_voltage_start(self):
        print("UI: voltage setting started")
        #self.voltage_control.setWindowModality(QtCore.Qt.ApplicationModal)
        self.voltage_widget.show()
        self.voltage_widget.set_in_progress_state()

    def on_setting_voltage_stop(self, error_code):
        print("UI: voltage setting stopped")
        if error_code == 0:
            self.voltage_widget.set_okay_state()
        else:
            self.voltage_widget.set_error_state()
        time.sleep(0.5)
        self.voltage_widget.hide()

    def on_drain_source_voltage_changed(self, voltage):
        print("UI: voltage {0}".format(voltage))
        self.voltage_widget.set_drain_source_voltage(voltage)

    def on_gate_source_voltage_changed(self, voltage):
        print("UI: voltage {0}".format(voltage))
        self.voltage_widget.set_gate_source_voltage(voltage)

    def on_progress_changed(self, progress):
        self.main_view.ui_update_progress(progress)

    def on_experiment_time_update(self, time_dict):
        self._time_info_window.set_time(**time_dict)

    def on_open_timetrace_conversion(self):
        print("opening timetrace conversion")
        # import subprocess
        # subprocess.Popen()

    def on_show_about_window(self):
        self.aboutWnd = UI_About()
        self.aboutWnd.show()

    def on_what_to_do_action(self):
        self.play_what_to_do()

    def on_lock_screen_action(self):
        print("screen is locked")
        self._lock_screen_window.exec_()

    def on_theme_switch_action(self):
        print("on theme switch")
        dialog = UI_ThemeSwitchWindow()
        dialog.exec_()

    def on_analysis_window_open_action(self):
        print("analysis window")
        # if not hasattr(self, "analysis_window"):
        if not self.analysis_window:
            self.analysis_window = eds.ExperimentDataAnalysis(layout="horizontal")
            self.analysis_window.setData(self.experimentData)
        self.analysis_window.show()
        # self.main_view.ui_dock_widget.setWidget(widget)

    def on_log_message_received(self, message):
        if message:
            print("received log message")
            print(message)
            self.main_view.ui_show_message_in_status_bar(message, 100)#._status_object.send_message(message)
            self.console_window.append_text(message)

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
    experimentTimeUpdate = QtCore.pyqtSignal(dict)

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

                elif cmd is pcp.ExperimentCommands.EXPERIMENT_TIME_UPDATE:
                    self.experimentTimeUpdate.emit(param)
                    

            except EOFError as e:
                print(str(e))
                break
            except:
                pass

        self.alive = False


