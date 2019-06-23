import os
import sys
import jsonpickle
jsonpickle.load_backend('json', 'dumps', 'loads', ValueError)
jsonpickle.set_preferred_backend('json')
jsonpickle.set_encoder_options('json', sort_keys=False, indent=4)

import pyfans.utils.ui_helper as uih
from pyfans.utils.ui_helper import DataContextWidget
from PyQt4 import QtCore, QtGui
from pyfans.hardware.forms.UI_CalibrationEdit import Ui_CalibrationEdit


class CalibrationInfoItem(object):
    def __init__(self, name="", amplification_factor=1, frequency_response_filename="", amplifier_noise_filename="", **kwargs):
        self._name = name
        self._amplification_factor = amplification_factor
        self._frequency_response_filename = frequency_response_filename
        self._amplifier_noise_filename = amplifier_noise_filename
        # print("constructor called")

    @property
    def name(self):
        return  self._name
    
    @name.setter
    def name(self, value):
        if value != self.name:
            self._name = value

    @property
    def amplification_factor(self):
        return self._amplification_factor

    @amplification_factor.setter
    def amplification_factor(self, value):
        if value != self._amplification_factor:
            self._amplification_factor = value

    @property
    def frequency_response_filename(self):
        return self._frequency_response_filename

    @frequency_response_filename.setter
    def frequency_response_filename(self, value):
        if value != self._frequency_response_filename:
            self._frequency_response_filename = value

    @property
    def amplifier_noise_filename(self):
        return self._amplifier_noise_filename

    @amplifier_noise_filename.setter
    def amplifier_noise_filename(self, value):
        if value != self._amplifier_noise_filename:
            self._amplifier_noise_filename = value

    
class NotifiableCalibrationInfoItemWrapper(uih.NotifyPropertyChanged):
    def __init__(self, parent):
        super().__init__()
        if not isinstance(parent, CalibrationInfoItem):
            raise TypeError("object should be of type CalibrationInfoItem")

        self._parent = parent

    @property
    def parent(self):
        return self._parent    

    @property
    def name(self):
        return  self.parent.name
    
    @name.setter
    def name(self, value):
        if value != self.parent.name:
            self.parent.name = value
            self.onPropertyChanged("name", self, value)

    @property
    def amplification_factor(self):
        return self.parent.amplification_factor

    @amplification_factor.setter
    def amplification_factor(self, value):
        if value != self.parent.amplification_factor:
            self.parent.amplification_factor = value
            self.onPropertyChanged("amplification_factor", self, value)

    @property
    def frequency_response_filename(self):
        return self._frequency_response_filename

    @frequency_response_filename.setter
    def frequency_response_filename(self, value):
        if value != self.parent.frequency_response_filename:
            self.parent.frequency_response_filename = value
            self.onPropertyChanged("frequency_response_filename", self, value)

    @property
    def amplifier_noise_filename(self):
        return self._amplifier_noise_filename

    @amplifier_noise_filename.setter
    def amplifier_noise_filename(self, value):
        if value != self.parent.amplifier_noise_filename:
            self.parent.amplifier_noise_filename = value
            self.onPropertyChanged("amplifier_noise_filename", self, value)


def generate_empty_calibration_info():
    obj = {}
    name = "default"
    ci = CalibrationInfoItem(
        name=name, 
        amplification_factor=1, 
        frequency_response_filename="",
        amplifier_noise_filename=""
        )

    obj["active"] = name
    obj["calibrations"] = {}
    obj["calibrations"][name] = ci
    return obj

class CalibrationView(QtGui.QDialog, Ui_CalibrationEdit, DataContextWidget):
    calibration_data_folder = "calibration_data"
    calibration_info_filename = "calibration_info.json"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.setupBinding()
        self._calibration_info_object = None
        self._selected_calibration = None
        self.loadCalibrationInfoFile()

    @property
    def calibration_info(self):
        return self._calibration_info_object

    @calibration_info.setter
    def calibration_info(self, value):
        if value != self._calibration_info_object:
            self._calibration_info_object = value

    @property
    def selected_calibration(self):
        return self._selected_calibration

    @selected_calibration.setter
    def selected_calibration(self, value):
        if value == self._selected_calibration:
            return 
        
        self._selected_calibration = value
       


    def setupUi(self):
        super().setupUi(self)

    def setupBinding(self):
        sourceObject = None
        self.name = uih.Binding(self.ui_calibration_name, "text", sourceObject, "name", validator=uih.NameValidator())
        self.amplification_factor = uih.Binding(self.ui_homemade_amplifier_gain, "text", sourceObject, "amplification_factor", converter=uih.StringToFloatConverter(), validator=QtGui.QDoubleValidator())

    def loadCalibrationInfoFile(self):
        directory = os.getcwd()
        dataFolder = os.path.join(directory, CalibrationView.calibration_data_folder)
        infoFname = os.path.join(dataFolder, CalibrationView.calibration_info_filename)
        if not os.path.isfile(infoFname):
            self.calibration_info = generate_empty_calibration_info()
        
        else:
            with open(infoFname, "r") as json_file:
                obj = jsonpickle.decode(json_file.read())
                self.calibration_info = obj
                self.refresh_data()

    def saveCalibrationInfoFile(self):
        if self.calibration_info is None:
            return 
        
        directory = os.getcwd()
        dataFolder = os.path.join(directory, CalibrationView.calibration_data_folder)
        infoFname = os.path.join(dataFolder, CalibrationView.calibration_info_filename)
        if os.path.isdir(dataFolder):
            with open(infoFname,"w") as json_file:
                json_str = jsonpickle.encode(self.calibration_info)
                json_file.write(json_str)


    def update_list_of_calibrations(self):
        keys = list(self.calibration_info["calibrations"].keys())
        print(keys)
        self.ui_selected_calibration.clear()
        self.ui_selected_calibration.addItems(keys)

    def refresh_data(self):
        active_name = self.calibration_info["active"]
        selected_calibration = self.calibration_info["calibrations"][active_name]
        self.selected_calibration = NotifiableCalibrationInfoItemWrapper(selected_calibration)
        self.dataContext = self.selected_calibration
        self.update_list_of_calibrations()

    def add_calibration(self):
        pass

    def remove_calibration(self):
        pass






    def closeEvent(self, event):
        self.saveCalibrationInfoFile()
        event.accept()
    

    


    

def main():
    app = QtGui.QApplication(sys.argv)
    #app.setStyle("cleanlooks")

    wnd = CalibrationView()
    wnd.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
