import os
import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, uic
from pyqtgraph.Point import Point
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pickle
from scipy import signal
from scipy import stats
from scipy.fftpack import fft, ifft, fftfreq
import math
import cmath

npphase = np.vectorize(cmath.polar)
nprect = np.vectorize(cmath.rect) 

#def mouseMoved(evt):
#    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
#    if p1.sceneBoundingRect().contains(pos):
#        mousePoint = vb.mapSceneToView(pos)
#        index = int(mousePoint.x())
#        if index > 0 and index < len(data1):
#            label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
#        vLine.setPos(mousePoint.x())
#        hLine.setPos(mousePoint.y())



#proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
##p1.scene().sigMouseMoved.connect(mouseMoved)
def lorenz_func(freq, freq0):
    return 1/(1+np.square(freq/freq0))

def P2R(radii, angles):
    return radii * np.exp(1j*angles)

def R2P(x):
    return np.abs(x), np.angle(x)

def fourier_filter(data,timestep):
    n = data.size
    freq = fftfreq(n,d = timestep)
    print(freq)
    ind = np.arange(n)
    times=  ind*timestep
    ft = fft(data)
    phase = np.angle(ft, deg = False)
    psd = np.abs(ft)**2

    res = np.real(ifft(ft))
    psd_freq = np.abs(psd*freq)

    #reconstruct = np.zeros_like(phase)
    window = None
    half_window = signal.hann(n/2)
    if n % 2==0:
        window = np.repeat(half_window,2)
    else:
        window = np.hstack((half_window,0,half_window))
       

    #window = signa
    reconstruct = ft*np.abs(freq)* window #*signal.hann(n)
    #for i in range(len(phase)):
    #    reconstruct[i] = P2R(np.sqrt(psd[i]),phase[i])

    psd_windowed = np.abs(reconstruct)**2

    reconstructed_res = np.real(ifft(reconstruct))
    
    #lorenz = lorenz_func(freq, 1000)

    #result_conv = np.zeros_like(freq)


    #for idx,f in enumerate(freq):
    #    lorenz_wnd = None
    #    wnd_sum = 1
    #    if f == 0:
    #        lorenz_wnd = np.zeros_like(freq)
    #    else:
    #        lorenz_wnd = lorenz_func(freq, f)*freq
    #        wnd_sum = np.sum(lorenz_wnd)

    #    conv = np.sum(np.multiply(lorenz_wnd,psd_freq))/wnd_sum #/np.sum(lorenz_wnd)
    #    #conv = np.sum(np.multiply(lorenz_wnd,psd))/np.sum(lorenz_wnd)
    #    #result_conv = signal.convolve(psd,wnd,mode = "same")/sum(wnd)
    #    result_conv[idx] = conv
        

    #pg.plot(res, title = "After Fourier")
    pg.plot(times,data, title = "Before Fourier")
    pg.plot(freq,psd, title = "PSD")
    pg.plot(freq,psd_windowed, title = "PSD_windowed")
    
    #pg.plot(freq,psd_freq, title = "PSD*f")
    #pg.plot(freq,phase, title = "phase")
    pg.plot(times,reconstructed_res,title = "Reconstructed")
    
    #win = pg.GraphicsWindow(title="Basic plotting examples")
    #win.resize(1000,600)
    #win.setWindowTitle('pyqtgraph example: Plotting')

    ## Enable antialiasing for prettier plots
    ##pg.setConfigOptions(antialias=True)

    #p2 = win.addPlot(title="Initial and reconstructed")
    #p2.plot(data, pen=(255,0,0), name="Red curve")
    #p2.plot(reconstructed_res, pen=(0,255,0), name="Blue curve")
    
    
    

    #pg.plot(freq,lorenz)
    #pg.plot(freq,result_conv,title = "convolution")



class WeightParamGroup(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'weight_group'
        opts['addText'] = "Add"
        opts['addList'] = ['float']
        pTypes.GroupParameter.__init__(self, **opts)
    
    def addNew(self, typ):
        val = {
            'float': 0.0,
        }[typ]
        self.addChild(dict(name="w%d" % (len(self.childs)+1), type=typ, value=val, removable=True, renamable=True))


registerParameterType('weight_group', WeightParamGroup, override = True)


def generate_arr(array):
    sign, nelem = array
    a = np.empty(nelem)
    a.fill(sign)
    return a



mainViewBase, mainViewForm = uic.loadUiType("RTS_main_view.ui")
class RTSmainView(mainViewBase,mainViewForm):
    def __init__(self, parent = None):
        super().__init__()
        self.params_filename = "params.dat"
        self.loaded_data = None
        self.parameters = None
        self.setupUi()
        self.setupParameterTree()
        #self.timetrace_filename = ""
        settings = QtCore.QSettings("foo","foo")
        self.timetrace_filename = settings.value('filename', type=str)#.toString()
        if self.timetrace_filename:
            self.load_data(self.timetrace_filename)

    def setupUi(self):
        super().setupUi(self)
        self.plot1 = self.ui_plot_area.addPlot(row=1, col=0)
        self.plot2 = self.ui_plot_area.addPlot(row=2, col=0, colspan =2)
        self.histogram_plot = self.ui_plot_area.addPlot(row = 1, col = 1)
        self.label = pg.LabelItem(justify='right')

        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.region.sigRegionChanged.connect(self.update)
        ## Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
        ## item when doing auto-range calculations.
        self.plot2.addItem(self.region, ignoreBounds=True)
        self.plot1.setAutoVisible(y=True)
        
        self.general_curve = self.plot2.plot(pen = pg.mkColor("g"))
        self.general_curve.setVisible(True)
        self.analysis_curve = self.plot1.plot(pen = pg.mkColor("y"))
        self.analysis_curve.setVisible(True)
        self.histogram_curve = self.histogram_plot.plot(pen = pg.mkColor("b"), fillLevel=0, fillBrush=(255,255,255,30))
        self.histogram_curve.setVisible(True)

        self.rts_curve = self.plot1.plot(pen = pg.mkPen("r", width = 3)) #pg.mkColor("r"),width = 3)
        self.rts_curve.setVisible(True)
        self.rts_curve.setZValue(100)

        #self.plot1.addItem(pg.MultiRectROI([[0, 0], [20,0 ], [40, 0]], width = 1e-06))

        #roi = pg.MultiRectROI(, width=5, pen=(2,9))
        #self.plot1.addItem(roi)

        print("init")

    def getDefaultParams(self):
        return [ {'name': 'Automated RTS recognition', 'type': 'group', 'children': [
                        {'name': 'Error', 'type': 'float', 'value': 1e-06},
                        {'name': 'Weights', 'type': 'str', 'value': '2'}
                        #WeightParamGroup(name="Weights", children=[
                                                       
                        #])
                    ]},
                    {'name':'Window', 'type': 'int', 'value':10},
                    {'name': 'Filtering', 'type': 'group', 'children':[
                        {'name':'Filter design', 'type':'list', 'values': {"Butterworth":0,
                                                                           "Chebyshev I":1,
                                                                           "Chebyshev II":2,
                                                                           "Elliptic":3,
                                                                           "Bessel":4
                                                                           }},    
                        {'name':'Order', 'type': 'int', 'value': 1},
                        {'name':'Type', 'type':'list', 'values': {"lowpass":0,
                                                                 "highpass":1 }},
                        {'name':'Frequency','type': 'float', 'value':100.0},
                        {'name':'Apply', 'type':'action'}
                        
                        ]}         
                 ]

    def save_state(self, filename,state):
        """Save a tree as a pickle file
        """
        with open(filename, 'wb') as fid:
            pickle.dump(state,fid)

    def load_state(self, filename):
        """Load a tree state to a pickle file
        """
        try:
            with open(filename, 'rb') as fid:
               data = pickle.load(fid)
               return data
        except FileNotFoundError as e:
            print("File Not Found")
            return None
        
    def setupParameterTree(self):
        self.param_tree = ParameterTree()
        self.param_tree.setWindowTitle('pyqtgraph example: Parameter Tree')
        #self.param_tree.setFixedWidth(300)
        self.parameterTreeLayout.addWidget(self.param_tree)
        self.parameterTreeLayout.setSizes([500,150])

        #self.parameterTreeLayour.
        
        self.parameters = Parameter.create(name='params', type='group')
        params = self.getDefaultParams()
        self.parameters.addChildren(params)

        state = self.load_state(self.params_filename)
        if state:
            self.parameters.restoreState(state)
        #else: 
            #params = self.getDefaultParams()
            #self.parameters.addChildren(params)

        self.parameters.sigTreeStateChanged.connect(self.action_signaled)

        self.param_tree.setParameters(self.parameters, showTop=False)
        

    def action_signaled(self, *args, **kwargs):
        print(args)
        print(kwargs)



    def closeEvent(self,event):
        print("closing")
        settings = QtCore.QSettings("foo","foo")
        if self.timetrace_filename:
            settings.setValue("filename", self.timetrace_filename)

        if self.parameters:
            self.save_state(self.params_filename, self.parameters.saveState())
        

    def update(self):
        minX, maxX = self.region.getRegion()
        
        self.plot1.setXRange(minX, maxX, padding=0)
        
        region_data = self.loaded_data.loc[lambda df: (df.time > minX) & (df.time < maxX),:]

        time = region_data.time
        data = region_data.data
        hist, bin_edges = np.histogram(data, bins = 'rice') #bins = 'auto')
        bin_centers = 0.5*(bin_edges[1:]+bin_edges[:-1])  #0.5*(x[1:] + x[:-1])
        self.histogram_curve.setData(bin_centers, hist)

        print("data points selected: {0}".format(len(time)))

        #rts_values = self.calc_levels(data)
        #self.rts_curve.setData(time, rts_values)
    @QtCore.pyqtSlot()
    def on_actionConvolve_triggered(self):
        print("convolution")
        minX, maxX = self.region.getRegion()
        region_data = self.loaded_data.loc[lambda df: (df.time > minX) & (df.time < maxX),:]
          
        time = region_data.time.values
        data = region_data.data.values

        win_size = self.parameters['Window']
        
        win = self.generate_window(win_size) #signal.hann(win_size)
        pg.plot(win, title = "Window size: {0}".format(win_size))

        #filtered = self.fit_using_pearson(data,win)
        #fit_using_pearson

        mean_value = np.mean(data)
        std = np.std(data)
        
        signal_to_noise = mean_value / std
        print("MEAN = {0}".format(mean_value))
        print("STD = {0}".format(std))
        print("SNR = {0}".format(signal_to_noise))
        
        filtered = signal.convolve(data,win, mode='same')/sum(win)
        
        fourier_filter(data, time[1]-time[0])
        #pearsonr, p_val = stats.pearsonr(data, filtered)
        #print("PearsonR = {0}".format(pearsonr))




        #optimal_wnd_size, pearsonr = self.fit_data_with_pulses(data, [3,5,10,15,20,25,30,50,100,200])
        #print("STD = {0}".format(std))
        #print("wnd_size = {0}".format(optimal_wnd_size))
        #win = signal.hann(optimal_wnd_size)
        #filtered = signal.convolve(data,win, mode='same')/sum(win)

        #filtered = data - filtered

        self.rts_curve.setData(time,filtered)

    

    def generate_window(self, wnd_size, front_size = 3):
        #wnd = np.hstack((np.zeros(wnd_size),np.ones(wnd_size)))
        
        wnd = signal.hann(2*front_size)
        wnd = np.insert(wnd,front_size,signal.boxcar(wnd_size))
        wnd = np.insert(np.zeros(2*front_size),front_size, wnd)
        return wnd


    def fit_using_pearson(self, data, wnd):
        wnd_size = len(wnd)
        half_wnd_size = wnd_size/2
        data_size = len(data)
        result_size = data_size - wnd_size
        result = np.zeros(data_size, dtype = np.float)
        for i in range(result_size):
            pearsonr,p_val =stats.pearsonr(data[i:i+wnd_size], wnd)
            result[i+half_wnd_size] = pearsonr * 1e-04
        return result


    def fit_data_with_pulses(self, data, wnd_length_arr:list):
        #current_std = 0
        current_pearsonr_to_one_dist = 1
        current_wnd_len = None

        for i, wnd_size in enumerate(wnd_length_arr):
            wnd = self.generate_window(wnd_size)  #signal.hann(wnd_size)
            print(wnd)
            #filtered = data - signal.convolve(data,wnd, mode='same')/sum(wnd)
            #std = np.std(filtered)
            pg.plot(wnd, title = "Window size: {0}".format(wnd_size))
            filtered = signal.convolve(data,wnd, mode='same')/sum(wnd)
            pearsonr, p_val = stats.pearsonr(data, filtered)
            dist = 1 - pearsonr
            print("PearsonR = {0}".format(pearsonr))
            print("wnd_size = {0}".format(wnd_size))
            if i == 0:
                #current_std = std
                current_pearsonr_to_one_dist = dist
                current_wnd_len = wnd_size

            elif dist < current_pearsonr_to_one_dist:
                current_pearsonr_to_one_dist = dist
                current_wnd_len = wnd_size

        return (current_wnd_len, current_pearsonr_to_one_dist)

    @QtCore.pyqtSlot()
    def on_actionSelectedArea_triggered(self):
        minX, maxX = self.region.getRegion()
        region_data = self.loaded_data.loc[lambda df: (df.time > minX) & (df.time < maxX),:]

        time = region_data.time.values
        data = region_data.data.values
        
        #weights = self.parameters.va
        weights = list(map(float, self.parameters["Automated RTS recognition","Weights"].split(';')))#.items()
        error = self.parameters["Automated RTS recognition","Error"]


        rts_values = self.calc_levels(data, weights, error)
        self.rts_curve.setData(time,rts_values)

    @QtCore.pyqtSlot()
    def on_actionFull_Set_triggered(self):
        time = self.loaded_data.time.values
        data = self.loaded_data.data.values
        rts_values = self.calc_levels(data)
        self.rts_curve.setData(time,rts_values)


    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        print("opening")
        print("Select folder")
        
        self.timetrace_filename = os.path.abspath(QtGui.QFileDialog.getOpenFileName(self,caption="Select File"))#, directory = self._settings.working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(self.timetrace_filename)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        if retval:
           self.load_data(self.timetrace_filename)

    def load_data(self, filename):
        print("loading file: {0}".format(filename))
        try:
            self.loaded_data = pd.read_csv(filename, delimiter = "\t", names=["time", "data"])
        
            time = self.loaded_data.time #["time"]

            rts = self.generate_rts(len(self.loaded_data.index), 1000, time[1], 5e-06)
            rts2 = self.generate_rts(len(self.loaded_data.index), 10, time[1], 5e-06)
            self.loaded_data.data = self.loaded_data.data + rts# + rts2
        
            data = self.loaded_data.data #["data"]
            #time,data = np.loadtxt(filename).T
            self.general_curve.setData(time,data)
            self.analysis_curve.setData(time,data)
        
            self.update()

        except Exception as e:
            print("failed to load data")
            

    def generate_rts(self, nelem, k,dt, amplitude = 1):
        k = float(k)
        ra = np.random.rand(nelem)
        # exponentially distributed jumps:
        t = np.log(1./ra)/k
        tr = np.floor(t/dt)
        x = []
        s = amplitude
        ones = np.ones(len(tr))
        ones[::2] = -1
        ones = ones * s

        arr =np.vstack((ones, tr)).T

        #np.apply_along_axis(generate_arr, 1, arr)
        result = np.zeros(nelem)

        current_idx = 0

        for val, n in arr:
            next_idx = current_idx+int(n)
            result[current_idx: next_idx] = val
            current_idx = next_idx

        return result
        
    def calc_levels(self,current_arr, weights= [1,0.7,0.4], error = 1e-06):
        L = len(current_arr)
        result = np.zeros(L)
        r_weights = weights #[1,0.7,0.4]#,0.8,0.7]
        l_weights = r_weights.reverse()
        N_half_wnd = len(r_weights)
        sigma = error
        left_avg = np.average(current_arr[0:N_half_wnd])
        right_arv = 0
        prev_val = 0
        
        result[:N_half_wnd] = left_avg
    ##    prev_time = 0
    ##    time_counter = 0
        for i in range(N_half_wnd,L-N_half_wnd):
            left_avg = np.average(current_arr[i-N_half_wnd:i],weights=l_weights)
            right_avg= np.average(current_arr[i:i+N_half_wnd],weights=r_weights)
            diff = right_avg - left_avg
            abs_diff = abs(diff)
            if abs_diff > sigma or abs(right_avg - prev_val) > sigma:
    ##            if time_counter >1:
    ##                amplitude_time_list.append([prev_val,prev_time])
                prev_val = right_avg
    ##            prev_time =0
    ##            time_counter =0 

            result[i] = prev_val
    ##        prev_time += dt
    ##        time_counter += 1
    ##        print(i)
        result[-N_half_wnd:] = prev_val

        return result
    

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #    QtGui.QApplication.instance().exec_()

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("RTS analysis")

    wnd = RTSmainView()
    wnd.show()

    sys.exit(app.exec_())
 