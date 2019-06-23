import os
import numpy as np
import json



class FANSCalibration:
    def __init__(self, calibration_data_directory = ""):
        self._calibration_data_directory = calibration_data_directory 
        self._frequency_responce = None
        self._amp_noise = None
        self._homemade_ampl_gain = 172 #178
        self._second_ampl_gain = 100
        self._frequency_responce_filename = "amplifier_frequency_responce.dat"
        self._amplifier_noise_filename = "amp_noise.dat"
        self.assert_calibration_directory(calibration_data_directory)

    def assert_calibration_directory(self, directory):
        assert os.path.isdir(directory), "Specified directory does not exist"
        assert os.path.isfile(os.path.join(directory, self._frequency_responce_filename)), "frequency responce file does not exist here"
        assert os.path.isfile(os.path.join(directory, self._amplifier_noise_filename)), "amplifier noise file does not exist here"

    @property
    def calibration_data_directory(self):
        return self._calibration_data_directory

    @calibration_data_directory.setter
    def calibration_data_directory(self, value):
        self.assert_calibration_directory(value)
        self._calibration_data_directory = value

    @property
    def homemade_amplifier_gain(self):
        return self._homemade_ampl_gain

    @homemade_amplifier_gain.setter
    def homemade_amplifier_gain(self, value):
        assert isinstance(value, (int, float)), "Amplification coefficient is not a numeric value"
        self._homemade_ampl_gain = value

    @property
    def second_amplifier_gain(self):
        return self._second_ampl_gain

    @second_amplifier_gain.setter
    def second_amplifier_gain(self, value):
        assert isinstance(value, (int, float)), "Amplification coefficient is not a numeric value"
        self._second_ampl_gain = value


    def initialize_calibration(self):
        frequency_responce_filepath = os.path.join(self._calibration_data_directory, self._frequency_responce_filename )
        amp_noise_filepath = os.path.join(self._calibration_data_directory, self._amplifier_noise_filename)
        self._frequency_responce = np.loadtxt(frequency_responce_filepath)
        self._amp_noise = np.loadtxt(amp_noise_filepath)

    def apply_calibration(self, spectrum_data):
        try:
            hma_gain = self.homemade_amplifier_gain
            sec_ampl_gain = self.second_amplifier_gain

            total_amplification = hma_gain * hma_gain * sec_ampl_gain * sec_ampl_gain
            total_amplification_with_freq_resp = total_amplification * self._frequency_responce
            resulting_spectrum = np.subtract(spectrum_data, self._amp_noise)
            resulting_spectrum = np.divide(resulting_spectrum, total_amplification_with_freq_resp)
            
            return resulting_spectrum
        except Exception as e:
            print(str(e))
            return spectrum_data
        
        

if __name__ == "__main__":
    pass
    
    
