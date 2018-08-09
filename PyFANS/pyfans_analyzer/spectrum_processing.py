import sys
import numpy as np
import pyqtgraph as pg

from scipy import interpolate
from scipy.interpolate import interp1d, UnivariateSpline, InterpolatedUnivariateSpline, CubicSpline
from scipy import optimize
from scipy import signal
from scipy.signal import cubic

fname = "D:\\Testdata\\BG=1V\\T06_Noise_BG=1V_1.dat"

def read_file(filename):
    a = np.loadtxt(filename, skiprows=1)
    return a

def cutoffCorrection(freq, data, resistance, capacity):
    result = np.zero_like(data)
    twoPi = 2 * np.pi
    RC = resistance*capacity
    twoPiRCsqr = np.power(twoPi * RC, 2)
    for idx, data in enumerate(data):
        result[idx] = data*(1 + twoPiRCsqr*freq[idx]*freq[idx])
    
    return result

def smoothSpline(freq,data, NStartPoints = 10):
    VF = freq*data
    N = len(data)
    count = N - NStartPoints
    result = np.zeros(N)

    for i in range(0, N):
        for j in range(NStartPoints, count):
            VF[j] = squareSpline(freq[j-1],VF[j-1],freq[j],VF[j],freq[j+1],VF[j+1]) 

    V=VF/freq
    return V

def remove50Hz(freq, data):
    data = np.copy(data)
    data_length = len(data)
    prev_idx = 0
    for idx, f in enumerate(freq):
        if f%50 == 0:
            if idx < data_length-1:
                data[idx] = (data[idx+1]+data[idx-1])/2
            else:
                data[idx] = data[idx-1]

    return data
        


def remove_pickups_savgol(data, deltaX = 1, window_length=5):
    result = signal.savgol_filter(data,window_length, 1)
    return result

def subtract_thermal_noise(data, thermal_noise_level):
    data = np.copy(data)
    floor_value = thermal_noise_level
    data_len_minus_one = len(data)-1
    for i, val in enumerate(data):
        new_val = val-thermal_noise_level
        if new_val < 0:
            if i<1:
                new_val = data[i+1]-thermal_noise_level
                if new_val < 0:
                    new_val = floor_value

            elif i==data_len_minus_one:
                new_val = data[i-1]-thermal_noise_level
                if new_val < 0:
                    new_val = floor_value
            else:
                new_val = (data[i+1]+data[i-1])/2-thermal_noise_level
                if new_val < 0:
                    new_val = floor_value

        data[i] = new_val

    return data




def squareSpline(x1,y1,x2,y2,x3,y3):
    deriv1 = (y2-y1)/(x2-x1)
    deriv2 = (y3-y2)/(x3-x2)
    a = 0.5 * (deriv2-deriv1)/(x3-x1)
    b = deriv1-2*x1*a
    c = y1-a*x1*x1-b*x1
    result = a*x2*x2+b*x2+c
    return result


def runningMeanFast(freq, data, N):
    print("convolution")
    kernel = np.hanning(N)
    kernel = kernel / kernel.sum()
    res_data =  np.convolve(data, kernel, mode ="same") #[(N-1):]
    # res_data =  np.convolve(data, kernel)[(N-1):]
    res_freq = freq #[(N-1):]
    # print(len(data))
    # print(len(res_data))
    # print(len(res_freq))
    # print("end convolution")
    return res_freq, res_data


def test_skipping_values(self, freq, data):
    plt = pg.plot()
    plt.addLegend()
    plt.plot(freq,data, name="initial")
    for i in range(2,10):
        plt.plot(freq[::i], data[::i], pen=pg.intColor(i), name="skip {0}".format(i))

def data_length_log_space(freq_start, freq_stop, points_per_decade = 10):
    log_f_start = np.log10(freq_start)
    log_f_end = np.log10(freq_stop)
    log_step = 1/points_per_decade
    return int(np.floor((log_f_end-log_f_start)/log_step))


def interpolate_data_log_space(freq, data, points_per_decade = 10, convolution_winsize = 11):
    
    freq_in_log_space = np.log10(freq)
    log_f_start = freq_in_log_space[0]
    log_f_end = freq_in_log_space[-1]
    log_step = 1/points_per_decade
    
    # log_spaced_frequencies = np.fromiter((10**x for x in np.arange(log_f_start, log_f_end, log_step)),float)
    
    desired_log_spaced_frequencies = np.arange(log_f_start, log_f_end, log_step)
    

    interpolation_function = interp1d(freq_in_log_space,data, kind="linear")
    result = interpolation_function(desired_log_spaced_frequencies)

    #test
    if convolution_winsize is not None:
        if convolution_winsize > 0:
            desired_log_spaced_frequencies, result = runningMeanFast(desired_log_spaced_frequencies,result, convolution_winsize)
    
    desired_lin_spaced_frequencies = np.power(10,desired_log_spaced_frequencies)

    return desired_lin_spaced_frequencies, result



def smooth(freq, data):
    
    kernel_len = 102
    #convolution 
    kernel = np.hanning(kernel_len)
    kernel = kernel / kernel.sum()
    

    
    freq_selected = freq #[::2]
    data_selected = data #[::2]

    
    smoothed = remove50Hz(freq, data) # remove_pickups(data_selected)

    plt = pg.plot(freq_selected,data)

    plt.plot(freq_selected, smoothed, pen=pg.mkPen(color="r", width=4))
    
    log_spaced_freq, log_spaced_data = interpolate_data_log_space(freq, smoothed, points_per_decade=20) 

    plt.plot(log_spaced_freq, log_spaced_data, pen="g", symbol="o", symbolPen="g", symbolBrush="g")
    
    plt.setLogMode(True,True)

   
    return data


def main():
    app = pg.QtGui.QApplication(sys.argv)
    frequency = 100000 #1600 #100
    data = read_file(fname)[:frequency]
    # print(data)

    freq, data = np.transpose(data)
    # data=freq*data
    # plt = pg.plot(freq, data)
    # plt.setLogMode(True,True)
    
    # test_skipping_values(freq, data)
    res = smooth(freq, data)
    # plt.plot(freq[:len(res)], res, pen="r")

    print(data)
    return app.exec_()

if __name__ == "__main__":
    main()



