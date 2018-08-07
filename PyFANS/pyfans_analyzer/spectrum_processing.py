import sys
import numpy as np
import pyqtgraph as pg

from scipy.interpolate import interp1d, UnivariateSpline, InterpolatedUnivariateSpline
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


def squareSpline(x1,y1,x2,y2,x3,y3):
    deriv1 = (y2-y1)/(x2-x1)
    deriv2 = (y3-y2)/(x3-x2)
    a = 0.5 * (deriv2-deriv1)/(x3-x1)
    b = deriv1-2*x1*a
    c = y1-a*x1*x1-b*x1
    result = a*x2*x2+b*x2+c
    return result

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
    
    freq_selected = freq[::2]
    data_selected = data[::2]
    # smoothed = UnivariateSpline( freq_selected, data_selected, k=3)
    # smoothed= smoothed(freq_selected)
    
    smoothed = np.convolve(kernel, data_selected, mode='valid')
    # smoothed = signal.savgol_filter(data_selected, 21, 1, 0, 1)

    plt = pg.plot(freq_selected[:len(smoothed)],smoothed)
    plt.plot(freq_selected,data_selected)
    plt.setLogMode(True,True)

    smoothed = data
    # plot = pg.plot(kernel)
    return smoothed


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



