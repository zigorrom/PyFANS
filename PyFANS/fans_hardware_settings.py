import modern_fans_controller as mfc
import ui_helper as uih

from PyQt4 import uic, QtCore
from communication_layer import get_available_gpib_resources, get_available_com_resources


HardwareSettingsBase, HardwareSettingsForm = uic.loadUiType("UI_HardwareSettings_v3.ui")
class HardwareSettingsView(HardwareSettingsBase, HardwareSettingsForm):
    
    fans_controller_resource = uih.bind("ui_fans_controller", "currentText", str)
    fans_sample_motor_channel = uih.bind("ui_sample_channel", "currentText",  uih.string_index_to_ao_channel_converter)
    fans_sample_relay_channel = uih.bind("ui_sample_relay", "currentText", uih.string_index_to_ao_channel_converter)
    fans_gate_motor_channel = uih.bind("ui_gate_channel", "currentText", uih.string_index_to_ao_channel_converter)
    fans_gate_relay_channel = uih.bind("ui_gate_relay", "currentText", uih.string_index_to_ao_channel_converter)
    fans_acquisition_channel = uih.bind("ui_acquisition_channel", "currentText", uih.string_index_to_ai_channel_converter)
    fans_sample_feedback_channel = uih.bind("ui_sample_feedback_channel", "currentText", uih.string_index_to_ai_channel_converter)
    fans_gate_feedback_channel = uih.bind("ui_gate_feedback_channel", "currentText", uih.string_index_to_ai_channel_converter)
    fans_main_feedback_channel = uih.bind("ui_main_feedback_channel", "currentText", uih.string_index_to_ai_channel_converter)

    def __init__(self,parent = None):
        super(HardwareSettingsBase,self).__init__(parent)
        self.setupUi(self)
        self.hardware_settings = None
        gpib_resources = get_available_gpib_resources()
        #com_resources = get_available_com_resources()
        self.ui_fans_controller.addItems(gpib_resources)
        
    
    
    @QtCore.pyqtSlot(int)
    def on_ui_fans_controller_currentIndexChanged(self,value):
        if self.hardware_settings:
            self.hardware_settings.fans_controller_resource = self.fans_controller_resource

    @QtCore.pyqtSlot(int)
    def on_ui_sample_channel_currentIndexChanged(self,value):
        if self.hardware_settings:
            self.hardware_settings.sample_motor_channel = self.fans_sample_motor_channel
    
    @QtCore.pyqtSlot(int)
    def on_ui_sample_relay_currentIndexChanged(self,value):
        if self.hardware_settings:
            self.hardware_settings.sample_relay_channel = self.fans_sample_relay_channel

    @QtCore.pyqtSlot(int)
    def on_ui_gate_channel_currentIndexChanged(self,value):
        if self.hardware_settings:
            self.hardware_settings.gate_motor_channel = self.fans_gate_motor_channel

    @QtCore.pyqtSlot(int)
    def on_ui_gate_relay_currentIndexChanged(self,value):
        if self.hardware_settings:    
            self.hardware_settings.gate_relay_channel = self.fans_gate_relay_channel
    
    @QtCore.pyqtSlot(int)
    def on_ui_acquisition_channel_currentIndexChanged(self, value):
        if self.hardware_settings:    
            self.hardware_settings.acquisition_channel = self.fans_acquisition_channel


    @QtCore.pyqtSlot(int)
    def on_ui_sample_feedback_channel_currentIndexChanged(self, value):
        if self.hardware_settings:
            self.hardware_settings.sample_feedback_channel = self.fans_sample_feedback_channel
        
    @QtCore.pyqtSlot(int)
    def on_ui_gate_feedback_channel_currentIndexChanged(self, value):
        if self.hardware_settings:
            self.hardware_settings.gate_feedback_channel = self.fans_gate_feedback_channel

    @QtCore.pyqtSlot(int)
    def on_ui_main_feedback_channel_currentIndexChanged(self, value):
        if self.hardware_settings:
            self.hardware_settings.main_feedback_channel = self.fans_main_feedback_channel

    
    def set_hardware_settings(self, hardware_settings):
        assert isinstance(hardware_settings, HardwareSettings)
        self.hardware_settings = hardware_settings
        self.refresh_view()
    
    def copy_settings_to_object(self):
        assert isinstance(self.hardware_settings, HardwareSettings)
        self.hardware_settings.fans_controller_resource = self.fans_controller_resource
        self.hardware_settings.sample_motor_channel = self.fans_sample_motor_channel
        self.hardware_settings.sample_relay_channel = self.fans_sample_relay_channel
        self.hardware_settings.gate_motor_channel = self.fans_gate_motor_channel
        self.hardware_settings.gate_relay_channel = self.fans_gate_relay_channel

        self.hardware_settings.acquisition_channel = self.fans_acquisition_channel
        self.hardware_settings.sample_feedback_channel = self.fans_sample_feedback_channel
        self.hardware_settings.gate_feedback_channel = self.fans_gate_feedback_channel
        self.hardware_settings.main_feedback_channel = self.fans_main_feedback_channel



    def refresh_view(self):
        if self.hardware_settings:
            uih.setAllChildObjectSignaling(self,True)
            self.fans_controller_resource = self.hardware_settings.fans_controller_resource
            self.fans_sample_motor_channel = uih.fans_channel_to_string(self.hardware_settings.sample_motor_channel) #.value
            self.fans_sample_relay_channel = uih.fans_channel_to_string(self.hardware_settings.sample_relay_channel)#.value
            self.fans_gate_motor_channel = uih.fans_channel_to_string(self.hardware_settings.gate_motor_channel)#.value
            self.fans_gate_relay_channel = uih.fans_channel_to_string(self.hardware_settings.gate_relay_channel)#.value
            self.fans_acquisition_channel = uih.fans_channel_to_string(self.hardware_settings.acquisition_channel)
            self.fans_sample_feedback_channel = uih.fans_channel_to_string(self.hardware_settings.sample_feedback_channel)
            self.fans_gate_feedback_channel = uih.fans_channel_to_string(self.hardware_settings.gate_feedback_channel)
            self.fans_main_feedback_channel = uih.fans_channel_to_string(self.hardware_settings.main_feedback_channel)
            uih.setAllChildObjectSignaling(self,False)


class HardwareSettings():
    def __init__(self):
        self._fans_controller_resource = None
        self._sample_motor_channel = None
        self._sample_relay_channel = None
        self._gate_motor_channel = None
        self._gate_relay_channel = None
        self._acquisition_channel = None
        self._sample_feedback = None
        self._gate_feedback = None
        self._main_feedback = None

    @property
    def fans_controller_resource(self):
        return self._fans_controller_resource

    @fans_controller_resource.setter
    def fans_controller_resource(self, value):
        assert isinstance(value, str), "unexpected data type"
        self._fans_controller_resource = value

    @property
    def sample_motor_channel(self):
        return self._sample_motor_channel
    
    @sample_motor_channel.setter
    def sample_motor_channel(self, value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._sample_motor_channel = value

    @property
    def sample_relay_channel(self):
        return self._sample_relay_channel

    @sample_relay_channel.setter
    def sample_relay_channel(self,value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._sample_relay_channel = value

    @property
    def gate_motor_channel(self):
        return self._gate_motor_channel
    
    @gate_motor_channel.setter
    def gate_motor_channel(self, value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._gate_motor_channel = value

    @property
    def gate_relay_channel(self):
        return self._gate_relay_channel

    @gate_relay_channel.setter
    def gate_relay_channel(self, value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._gate_relay_channel = value

    @property
    def acquisition_channel(self):
        return self._acquisition_channel

    @acquisition_channel.setter
    def acquisition_channel(self,value):
        assert isinstance(value, mfc.FANS_AI_CHANNELS)
        self._acquisition_channel = value

    @property
    def sample_feedback_channel(self):
        return self._sample_feedback

    @sample_feedback_channel.setter
    def sample_feedback_channel(self,value):
        assert isinstance(value, mfc.FANS_AI_CHANNELS)
        self._sample_feedback = value

    @property
    def gate_feedback_channel(self):
        return self._gate_feedback

    @gate_feedback_channel.setter
    def gate_feedback_channel(self,value):
        assert isinstance(value, mfc.FANS_AI_CHANNELS)
        self._gate_feedback = value
       
    @property
    def main_feedback_channel(self):
        return self._main_feedback

    @main_feedback_channel.setter
    def main_feedback_channel(self,value):
        assert isinstance(value, mfc.FANS_AI_CHANNELS)
        self._main_feedback = value

if __name__ == "__main__":
    print("test")