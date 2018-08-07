import sys
import numpy as np
import pyqtgraph as pg

from scipy import interpolate
from scipy.interpolate import interp1d, UnivariateSpline, InterpolatedUnivariateSpline, CubicSpline
from scipy import optimize
from scipy import signal
from scipy.signal import cubic

fname = 

def read_file(filename):
    a = np.loadtxt(filename, skiprows=1)
    return a



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

def remove_pickups(data, deltaX = 1):
    res = np.copy(data)
    sigma = 2*deltaX
    for i in range(1,len(data)-1):
        difference = sigma * np.abs(data[i+1]-data[i-1])
        average = (data[i+1]+data[i-1])/2
        if np.abs(data[i] - average) > difference:
            res[i] = average
    
    return res




def squareSpline(x1,y1,x2,y2,x3,y3):
    deriv1 = (y2-y1)/(x2-x1)
    deriv2 = (y3-y2)/(x3-x2)
    a = 0.5 * (deriv2-deriv1)/(x3-x1)
    b = deriv1-2*x1*a
    c = y1-a*x1*x1-b*x1
    result = a*x2*x2+b*x2+c
    return result


def runningMeanFast(x, N):
    kernel = np.hanning(N)
    kernel = kernel / kernel.sum()
    

    # kernel = np.ones((N,))/N
    return np.convolve(x, kernel)[(N-1):]

# def pretreatSpectrum(self, data):
#     for i in range(1,len(data)-1):
def test_skipping_values(self, freq, data):
    plt = pg.plot()
    plt.addLegend()
    plt.plot(freq,data, name="initial")
    for i in range(2,10):
        plt.plot(freq[::i], data[::i], pen=pg.intColor(i), name="skip {0}".format(i))


def smooth(freq, data):
    
    kernel_len = 102
    #convolution 
    kernel = np.hanning(kernel_len)
    kernel = kernel / kernel.sum()
    


    #UnivariateSpline



    # x = linspace(-3, 3, 100)
    # y = exp(-x**2) + randn(100)/10
    # weights = np.arange(1, 2, 0.2)
    # weights = [1,1,1,1,1,1]
    # N=len(data)
    # rmserror = 10
    # s_val = N * (rmserror * np.fabs(data).max())**2
    # UnivariateSpline( x, y, s=s )
    
    # smoothed = smoothSpline(freq, data, 100)
    # smoothed = smoothSpline(freq, data)
   
    #savgolFilter
    
    # smoothed = signal.spline_filter(data)
    
    freq_selected = freq #[::2]
    data_selected = data #[::2]
    # smoothed = UnivariateSpline( freq_selected, data_selected, k=3)
    # smoothed= smoothed(freq_selected)

    
    smoothed = remove_pickups(data_selected)
    
    # smoothed = np.convolve(kernel, data_selected, mode='valid')
    # smoothed = signal.savgol_filter(data_selected, 21, 1, 0, 1)

    # plt = pg.plot(freq_selected[:len(smoothed)],smoothed)
    # spline = UnivariateSpline ( freq_selected, smoothed)
    # spline.set_smoothing_factor(0.5)
    # smoothed = spline(freq_selected)

    # smoothed = CubicSpline(freq_selected, smoothed)
    # smoothed=smoothed(freq_selected)
    start_freq = np.log10(freq[0])
    end_freq = np.log10(freq[-1])
    n = 30*np.floor(end_freq - start_freq)+1


    log_spaced_freq = np.logspace(start_freq,end_freq, num=n)

    smoothed = interp1d(freq_selected, smoothed, kind="cubic")
    smoothed = smoothed(log_spaced_freq)

    # tck = interpolate.splrep(freq_selected, smoothed)
    # smoothed = interpolate.splev(log_spaced_freq, tck)
    
    # smoothed = smoothed(freq_selected)
    # smoothed = signal.savgol_filter(smoothed, 3, 0, 0, 1)
    plt = pg.plot(freq_selected,freq_selected*data)
    # plt.plot(freq_selected,smoothed, pen=pg.mkPen(color="r", width=4))
    res = log_spaced_freq*smoothed
    # res = runningMeanFast(res, 10)

    plt.plot(log_spaced_freq, res, pen=pg.mkPen(color="r", width=4))
   
    plt.setLogMode(True,True)

    # smoothed = data
    # plot = pg.plot(kernel)
    return data


def main():
    app = pg.QtGui.QApplication(sys.argv)
    frequency = 1600 #100
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



