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
    N = 10#len(data)
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


def smooth(freq, data):
    kernel = np.hanning(40)
    kernel = kernel / kernel.sum()
    
    # x = linspace(-3, 3, 100)
    # y = exp(-x**2) + randn(100)/10
    # weights = np.arange(1, 2, 0.2)
    # weights = [1,1,1,1,1,1]
    N=len(data)
    rmserror = 10
    s_val = N * (rmserror * np.fabs(data).max())**2
    # UnivariateSpline( x, y, s=s )

    smoothed = smoothSpline(freq, data)
    # smoothed = UnivariateSpline(freq, data) #s_val)
    # smoothed.set_smoothing_factor(0.1)
    # smoothed = InterpolatedUnivariateSpline(freq, data)
    # smoothed = signal.spline_filter(data)
    # smoothed = smoothed(freq)

    # smoothed = np.convolve(kernel, data, mode='VALID')
    # smoothed = signal.savgol_filter(data, 21, 1, 0, 1)
    
    # plot = pg.plot(kernel)
    return smoothed


def main():
    app = pg.QtGui.QApplication(sys.argv)
    frequency = 1600 #100
    data = read_file(fname)[:frequency]
    # print(data)

    freq, data = np.transpose(data)
    # data=freq*data
    plt = pg.plot(freq, data)
    plt.setLogMode(True,True)

    res = smooth(freq, data)
    plt.plot(freq[:len(res)], res, pen="r")

    print(data)
    return app.exec_()

if __name__ == "__main__":
    main()



