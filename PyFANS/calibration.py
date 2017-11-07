import os
import numpy as np
import json
from scipy.interpolate import interp1d
#import pyqtgraph as pg


class FANSCalibration:
    def __init__(self, calibration_data_directory = ""):
        self._calibration_data_directory = calibration_data_directory 
        self._frequency_responce = None
        self._amp_noise = None
        self._homemade_ampl_gain = 178
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
            scaled_spectrum = np.divide(spectrum_data, total_amplification_with_freq_resp)
            resulting_spectrum = np.subtract(scaled_spectrum, self._amp_noise)
            return resulting_spectrum
        except Exception as e:
            print(str(e))
            return spectrum_data
        
        



class CalibrationSimple:
    def __init__(self, calibration_directory = ""):
        super().__init__()

        self.calibration_directory = calibration_directory

        self.frequencies = None
        self.h0 = None
        self.h0n = None
        self.k2 = None
        self.k2n = None

    def generate_filepath(self,fname):
        return os.path.join(self.calibration_directory, fname)
    
    def init_values(self):
        self.frequencies = np.loadtxt(self.generate_filepath("frequencies.dat"))
        self.h0 = np.loadtxt(self.generate_filepath("h0.dat"))
        self.h0n = np.loadtxt(self.generate_filepath("h0n.dat"))
        self.k2 = np.loadtxt(self.generate_filepath("k2.dat"))
        self.k2n = np.loadtxt(self.generate_filepath("k2n.dat"))

    def apply_calibration(self,noise_spectrum, preamp_amplification, second_amplification):
        freq, data = noise_spectrum
        freq_default = self.frequencies
        h0 = self.h0
        h0n = self.h0n
        k2 = self.k2
        k2n = self.k2n

        hm_ampl = preamp_amplification * preamp_amplification
        second_ampl = second_amplification * second_amplification

        real_spectrum = np.asarray([(((sv_meas/second_ampl - h0_)/k2_ - h0n_)/k2n_/hm_ampl)   for (sv_meas, h0_, k2_, h0n_, k2n_) in zip(data, h0, k2, h0n, k2n)])
        return np.vstack((freq,real_spectrum))


        #real_spectrum = np.asarray([((sv_meas/k_ampl - sv_ampl)/k_preamp - sv_preamp) for (sv_meas, k_ampl, sv_ampl, sv_preamp, k_preamp) in zip(data, second_amp_freq_response_sqr,second_amp_calibration_curve, preamp_calibration_curve, preamp_freq_response_sqr)])




class Calibration:
    def __init__(self, calibration_directory = "", use_preamplifier = True, use_second_amplifier = True):
        super().__init__()

        self.calibration_directory = calibration_directory
        self.calibration_data_info = {}
        self.calibration_data = {}
        
        self._use_preamplifier = use_preamplifier
        self._use_second_amplifier = use_second_amplifier
        
        self._spectrum_ranges = {}
        
        self.load_calibration_data()
            
        #self.load_calibration_data()

    def init_spectrum_range_calibration(self, spectrum_ranges):
        pass

    def load_calibration_data(self):
        try:
            filename = os.path.join(self.calibration_directory, "calibration_data.dat")
            with open(filename,"r") as f:
                self.calibration_data_info = json.load(f)

            for k,v in self.calibration_data_info.items():
                freq_resp_filename =  os.path.join(self.calibration_directory, v["frequency_response_filename"])
                calibration_curve_filename =  os.path.join(self.calibration_directory,v["calibration_curve_filename"])
                freq_resp = np.loadtxt(freq_resp_filename)
                frequencies, freq_response = freq_resp
                freq_resp_interp = interp1d(frequencies, freq_response)

                calib_curve = np.loadtxt(calibration_curve_filename)
                frequencies, calibration_curve = calib_curve
                calibration_interp = interp1d(frequencies, calibration_curve)

                self.calibration_data[k] = {"frequency_response":freq_resp,"freq_response_interp": freq_resp_interp, "calibration_curve": calib_curve, "calib_interp": calibration_interp}
                

            return True
        except Exception as e:
            return False
        
      
    def save_calibration_data(self):
        with open(os.path.join(self.calibration_directory, "calibration_data.dat"),"w") as f:
            json.dump(self.calibration_data_info,f)

        for k,v in self.calibration_data_info.items():
            freq_resp_filename = v["frequency_response_filename"]
            calibration_curve_filename = v["calibration_curve_filename"]
            ampl_data = self.calibration_data[k]
            freq_resp = ampl_data["frequency_response"]
            calib_curve = ampl_data["calibration_curve"]
            np.savetxt(os.path.join(self.calibration_directory,freq_resp_filename), freq_resp)
            np.savetxt(os.path.join(self.calibration_directory,calibration_curve_filename), calib_curve)



    def add_amplifier(self, amplifier_name, amplifier_id, frequencies, frequency_response, calibration_curve, amplifier_gain = 1):
        min_freq = frequencies[0]
        max_freq = frequencies[-1]
        self.calibration_data_info[amplifier_name] = {"ID": amplifier_id,"gain": amplifier_gain,"min_freq":min_freq,"max_freq": max_freq, "frequency_response_filename": "{0}_{1}.dat".format(amplifier_name,"freq_resp"), "calibration_curve_filename": "{0}_{1}.dat".format(amplifier_name,"calibration_curve")}
        freq_resp_interp = interp1d(frequencies, frequency_response)
        calibr_interp = interp1d(frequencies, calibration_curve)
        frequency_response = np.vstack((frequencies, frequency_response))
        calibration_curve = np.vstack((frequencies, calibration_curve))
        self.calibration_data[amplifier_name] = {"frequency_response":frequency_response, "freq_response_interp": freq_resp_interp,  "calibration_curve": calibration_curve, "calib_interp": calibr_interp}

    #def _apply_calibration(self, amplifier, gain, spectrum_data):
    #    freq, data = spectrum_data
    #    calibration_curve = self.calibration_data[amplifier]["calib_interp"](freq)
    #    freq_response_sqr = self.calibration_data[amplifier]["freq_response_interp"](freq)
    #    gain_sqr = gain*gain
    #    result = data/(gain_sqr*freq_response_sqr) - calibration_curve
    #    return result

    def get_amplifier_gain(self,amplifier):
        return self.calibration_data_info[amplifier]["gain"]

    def set_amplifier_gain(self, amplifier, gain):
        self.calibration_data_info[amplifier]["gain"] = gain

    def apply_calibration(self, noise_spectrum):
       

        frequencies, data = noise_spectrum
        preamp_calibration_curve =  self.calibration_data["preamp"]["calib_interp"](frequencies)
        preamp_gain = self.get_amplifier_gain("preamp")**2
        preamp_freq_response_sqr = self.calibration_data["preamp"]["freq_response_interp"](frequencies)*preamp_gain
        #pg.plot(frequencies, preamp_calibration_curve)
        #pg.plot(frequencies, preamp_freq_response_sqr)
        
        second_amp_calibration_curve = self.calibration_data["second_amp"]["calib_interp"](frequencies)
        second_amp_gain = self.get_amplifier_gain("second_amp")**2
        second_amp_freq_response_sqr = self.calibration_data["second_amp"]["freq_response_interp"](frequencies)*second_amp_gain
        #pg.plot(frequencies, second_amp_calibration_curve)
        #pg.plot(frequencies, second_amp_freq_response_sqr)

        #real_spectrum = (data/second_amp_freq_response_sqr - second_amp_calibration_curve)/ preamp_freq_response_sqr - preamp_calibration_curve
        real_spectrum = np.asarray([((sv_meas/k_ampl - sv_ampl)/k_preamp - sv_preamp) for (sv_meas, k_ampl, sv_ampl, sv_preamp, k_preamp) in zip(data, second_amp_freq_response_sqr,second_amp_calibration_curve, preamp_calibration_curve, preamp_freq_response_sqr)])
        #real_spectrum = np.asarray([((sv_meas/k_preamp - sv_preamp)/k_ampl - sv_ampl) for (sv_meas, k_ampl, sv_ampl, sv_preamp, k_preamp) in zip(data, second_amp_freq_response_sqr,second_amp_calibration_curve, preamp_calibration_curve, preamp_freq_response_sqr)])
         
        return np.vstack((frequencies,real_spectrum))

    #def divide_by_amplification_coefficient(self,
    
def add_amplifiers():
    dir = os.path.dirname(__file__)
    c = Calibration(os.path.join(dir,"calibration_data"))
    dir  = os.path.join(os.path.dirname(__file__), "calibration_data")

    freq_file = os.path.join(dir,"frequencies.dat")
    h0_file = os.path.join(dir,"h0.dat")
    h0n_file = os.path.join(dir,"h0n.dat")

    k2_file = os.path.join(dir,"k2.dat")
    k2n_file = os.path.join(dir,"k2n.dat")

    frequencies = np.loadtxt(freq_file)
    preamp_calib_curve = np.loadtxt(h0_file)
    preamp_freq_resp = np.loadtxt(k2_file)

    second_amp_calib_curve = np.loadtxt(h0n_file)
    second_amp_freq_resp = np.loadtxt(k2n_file)

    c.add_amplifier("preamp", 0, frequencies, preamp_freq_resp, preamp_calib_curve, 178)
    c.add_amplifier("second_amp",1,frequencies, second_amp_freq_resp,second_amp_calib_curve, 100)
    c.save_calibration_data()

def load_amplifiers():
    dir = os.path.dirname(__file__)
    c = Calibration(os.path.join(dir,"calibration_data"))

def test_calibration():
    dir = os.path.dirname(__file__)
    c = Calibration(os.path.join(dir,"calibration_data"))

    #n = 10000
    #frequency = np.linspace(1,102400, n)
    #data = np.random.rand(n)
    #print(data)
    #res = c.apply_calibration((frequency,data))
    #print(res)

    filename = "meas__1.dat"
    loaded = np.loadtxt(filename,skiprows=2)
    data = np.transpose(loaded)

    print(data)
    result = c.apply_calibration(data)
    print(result)
    
def test_calibration_on_real_file():
    dir = os.path.dirname(__file__)
    c = Calibration(os.path.join(dir,"calibration_data"))
    folder_name  = "C:\\Users\\i.zadorozhnyi\\Desktop\\test_data"
    filename = "t04_func.dat"
    loaded = np.loadtxt(os.path.join(folder_name,filename))
    data = np.transpose(loaded)
    print(data)

    result = c.apply_calibration(data)
    np.savetxt(os.path.join(folder_name, "exported_{0}".format(filename)), result.T)




if __name__ == "__main__":
    #import sys
    #test_calibration_on_real_file()
    #if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
    #    pg.QtGui.QApplication.exec_()
    #add_amplifiers()

    #load_amplifiers()

    #test_calibration()
    pass
    
    