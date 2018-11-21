import sys

from PyQt4 import uic, QtGui, QtCore

import pyfans.hardware.modern_fans_controller as mfc
import pyfans.hardware.modern_fans_smu as mfs
import pyfans.hardware.fans_channel_switch as dut_switch
from pyfans.hardware.communication_layer import get_available_gpib_resources, get_available_com_resources

from pyfans.hardware.forms.UI_VoltageControl import Ui_VoltageControl
#from fans_smu import ManualSMU, voltage_setting_function
#from fans_controller import FANS_AO_channel, FANS_CONTROLLER
#from fans_constants import *
#from PyQt4 import uic, QtGui, QtCore
#from communication_layer import get_available_gpib_resources, get_available_com_resources
#from hp34401a_multimeter import HP34401A,HP34401A_FUNCTIONS
#from fans_smu import HybridSMU_System


# mainViewBase, mainViewForm = uic.loadUiType("UI/UI_VoltageControl.ui")
# class VoltageControlView(mainViewBase,mainViewForm):
class VoltageControlView(QtGui.QWidget, Ui_VoltageControl):
    def __init__(self,parent = None, parent_fans_smu = None ):
        # super(mainViewBase,self).__init__(parent)
        super().__init__(parent)
        self.setupUi()
        
        self.stand_alone_program = True
        self._fans_smu = None
        self._initialized = False
        self._repetitive_timer = QtCore.QTimer(self)
        self._repetitive_timer.setInterval(100)
        self._repetitive_timer.timeout.connect(self.read_values)

        if isinstance(parent_fans_smu, mfs.FANS_SMU):
            self._fans_smu = parent_fans_smu
            self.stand_alone_program = False
            self._initialized = True
            self.__set_initialization_ui_dizabled()

        else:
            self._gpib_resources = get_available_gpib_resources()
            self.ui_controller_resource.addItems(self._gpib_resources)
            
    def setupUi(self):
        super().setupUi(self)
        ds_validator = QtGui.QDoubleValidator()
        ds_validator.setNotation(ds_validator.StandardNotation)
        self.ui_ds_value.setValidator(ds_validator)

        gs_validator = QtGui.QDoubleValidator()
        gs_validator.setNotation(gs_validator.StandardNotation)
        self.ui_gs_value.setValidator(gs_validator)

        
    def __set_initialization_ui_dizabled(self):
        self.ui_controller_resource.setEnabled(False)
        self.ui_initialize.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_ui_initialize_clicked(self):
        assert self.stand_alone_program, "Allowed only for standalone application"

        selected_resource = self.ui_controller_resource.currentIndex()
        resource = self._gpib_resources[selected_resource]

        #sample_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_6
        #gate_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_8
        #main_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_7
        #self.acquistion_channel = mfans.FANS_AI_CHANNELS.AI_CH_1 ### here should be 1
        #drain_source_voltage_switch_channel = mfans.FANS_AO_CHANNELS.AO_CH_10

        fans_controller = mfc.FANS_CONTROLLER(resource)
        
        self._fans_smu = mfs.FANS_SMU_Specialized(fans_controller, 
                                                  mfc.FANS_AO_CHANNELS.AO_CH_1,
                                                  mfc.FANS_AO_CHANNELS.AO_CH_4,
                                                  mfc.FANS_AI_CHANNELS.AI_CH_6, 
                                                  mfc.FANS_AO_CHANNELS.AO_CH_9,
                                                  mfc.FANS_AO_CHANNELS.AO_CH_12, 
                                                  mfc.FANS_AI_CHANNELS.AI_CH_8, 
                                                  mfc.FANS_AI_CHANNELS.AI_CH_7, 
                                                  mfc.FANS_AO_CHANNELS.AO_CH_10)
        self._initialized = True

    @QtCore.pyqtSlot()
    def on_ui_set_load_resistance_clicked(self):
        assert isinstance(self._fans_smu, mfs.FANS_SMU), "Not properly initialized fans smu controller"
        value = float(self.ui_load_resistance.text())
        self._fans_smu.smu_load_resistance = value

    def set_values_on_ui(self, drain_source_voltage, gate_voltage, main_voltage, drain_current, sample_resistance):
        self.ui_drain_source_voltage.setText(str(drain_source_voltage))
        self.ui_gate_voltage.setText(str(gate_voltage))
        self.ui_main_voltage.setText(str(main_voltage))
        self.ui_drain_current.setText(str(drain_current))
        self.ui_sample_resistence.setText(str(sample_resistance))
        
    def set_ui_load_resistance(self):
        assert isinstance(self._fans_smu, mfs.FANS_SMU), "Not properly initialized fans smu controller"
        self.ui_load_resistance.setText(str(self._fans_smu.smu_load_resistance))

    def read_values(self):
        assert isinstance(self._fans_smu, mfs.FANS_SMU), "Not properly initialized fans smu controller"
        value_dictionary = self._fans_smu.read_all_parameters()
        drain_source_voltage = value_dictionary.get(mfs.FANS_SMU.DRAIN_SOURCE_VOLTAGE_VAR)
        gate_voltage = value_dictionary.get(mfs.FANS_SMU.GATE_SOURVCE_VOLTAGE_VAR)
        main_voltage = value_dictionary.get(mfs.FANS_SMU.MAIN_VOLTAGE_VAR)
        drain_current = value_dictionary.get(mfs.FANS_SMU.DRAIN_CURRENT_VAR)
        sample_resistance = value_dictionary.get(mfs.FANS_SMU.SAMPLE_RESISTANCE_VAR)
        self.set_values_on_ui(drain_source_voltage, gate_voltage, main_voltage, drain_current, sample_resistance)


    @QtCore.pyqtSlot()
    def on_ui_start_single_measurement_clicked(self):
        assert isinstance(self._fans_smu, mfs.FANS_SMU), "Not properly initialized fans smu controller"
        self.set_ui_load_resistance()
        self.read_values()

    @QtCore.pyqtSlot()
    def on_ui_start_repetitive_measurement_clicked(self):
        assert isinstance(self._fans_smu, mfs.FANS_SMU), "Not properly initialized fans smu controller"
        self.set_ui_load_resistance()
        self._repetitive_timer.start()


    @QtCore.pyqtSlot()
    def on_ui_stop_repetitive_measurement_clicked(self):
        self._repetitive_timer.stop()


    @QtCore.pyqtSlot()
    def on_ui_ds_positiv_clicked(self):
        if not self._initialized:
            return
        print("ui_ds_positiv")
        self._fans_smu.set_drain_source_polarity_positiv()


    @QtCore.pyqtSlot()
    def on_ui_ds_negativ_clicked(self):
        if not self._initialized:
            return
        print("ui_ds_negativ")
        self._fans_smu.set_drain_source_polarity_negativ()

    @QtCore.pyqtSlot()
    def on_ui_gs_positiv_clicked(self):
        if not self._initialized:
            return
        print("ui_gs_positiv")
        self._fans_smu.set_gate_polarity_positiv()


    @QtCore.pyqtSlot()
    def on_ui_gs_negativ_clicked(self):
        if not self._initialized:
            return
        print("ui_gs_negativ")
        self._fans_smu.set_gate_polarity_negativ()

    @QtCore.pyqtSlot()
    def on_ui_ds_move_left_fast_clicked(self):
        if not self._initialized:
            return
        print("ui_ds_move_left_fast")
        self._fans_smu.move_ds_motor_left_fast()

    @QtCore.pyqtSlot()
    def on_ui_ds_move_left_clicked(self):
        if not self._initialized:
            return
        print("ui_ds_move_left")
        self._fans_smu.move_ds_motor_left()

    @QtCore.pyqtSlot()
    def on_ui_move_right_clicked(self):
        if not self._initialized:
            return
        print("ui_move_right")
        self._fans_smu.move_ds_motor_right()

    @QtCore.pyqtSlot()
    def on_ui_move_right_fast_clicked(self):
        if not self._initialized:
            return
        print("ui_move_right_fast")
        self._fans_smu.move_ds_motor_right_fast()

    @QtCore.pyqtSlot()
    def on_ui_gs_move_left_fast_clicked(self):
        if not self._initialized:
            return
        print("ui_gs_move_left_fast")
        self._fans_smu.move_gate_motor_left_fast()

    @QtCore.pyqtSlot()
    def on_ui_gs_move_left_clicked(self):
        if not self._initialized:
            return
        print("ui_gs_move_left")
        self._fans_smu.move_gate_motor_left()

    @QtCore.pyqtSlot()
    def on_ui_gs_move_right_clicked(self):
        if not self._initialized:
            return
        print("ui_gs_move_right")
        self._fans_smu.move_gate_motor_right()

    @QtCore.pyqtSlot()
    def on_ui_gs_move_right_fast_clicked(self):
        if not self._initialized:
            return
        print("ui_gs_move_right_fast")
        self._fans_smu.move_gate_motor_right_fast()

    @QtCore.pyqtSlot()
    def on_ui_ds_set_value_clicked(self):
        if not self._initialized:
            return
        print("setting ds value clicked")
        value = float(self.ui_ds_value.text()) #value()
        self._fans_smu.smu_set_drain_source_voltage(value)
        print("done setting ds value")

    @QtCore.pyqtSlot()
    def on_ui_gs_set_value_clicked(self):
        if not self._initialized:
            return
        print("setting gs value clicked")
        value = float(self.ui_gs_value.text()) #.value()
        self._fans_smu.smu_set_gate_voltage(value)
        print("done setting gs value")

    @QtCore.pyqtSlot()
    def on_ui_switch_dut_clicked(self):
        if not self._initialized:
            return
        
        print("selectig dut")
        new_dut = self.ui_selected_dut.value()-1
        fans_controller = self._fans_smu.fans_controller
        dut_switcher = dut_switch.FANS_DUT_Switch(fans_controller)
        dut_switcher.switch_to_dut(new_dut)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Voltage Control")
    #app.setStyle("cleanlooks")

    #css = "QLineEdit#sample_voltage_start {background-color: yellow}"
    #app.setStyleSheet(css)
    #sample_voltage_start

    wnd = VoltageControlView()
    wnd.show()

    sys.exit(app.exec_())