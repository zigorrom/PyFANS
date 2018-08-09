   
import numpy as np
import pyfans_analyzer.spectrum_processing as sp
from pyqtgraph import mkPen


class ProxyDataPlotHandler:
    def __init__(self, plotter):
        self._plotter = plotter
        
        self._originalDataCurve = None
        self._displayDataCurve = None
        self.setupCurvesOnPlotter()

        self._remove_pickups = None
        self._smoothing = None
        self._smoothing_winsize = None
        self._cutoff_correction = None
        self._use_crop = None
        self._crop_start = None 
        self._crop_end = None
        self._multiply_by_freq = None

        self._originalFreq = None
        self._originalData = None
        self._displayFreq = None
        self._displayData = None
        self._updatingParams = False

        
    def setupCurvesOnPlotter(self):
        original_curve_name = "original"
        display_curve_name = "display"
        curve = self._plotter.get_curve_by_name(original_curve_name)
        if curve is None:
            curve = self._plotter.create_curve(original_curve_name, pen=mkPen("r", width=3),zValue=900)
            self._originalDataCurve=curve

        curve = self._plotter.get_curve_by_name(display_curve_name)
        if curve is None:
            curve = self._plotter.create_curve(display_curve_name, pen="g",zValue=1000)
            self._displayDataCurve=curve

        
    def setOriginalData(self, freq, data):
        self._originalFreq = freq
        self._originalData = data
        self.updateDisplayData()
        self.updateOriginalDataPlot()
        # self.updateDisplatDataPlot()

    def getDisplayData(self):
        return self._displayFreq, self._displayData

    def updateDisplatDataPlot(self):
        if self._displayDataCurve is None:
            return 

        print("updating display data curve")
        self._displayDataCurve.setData(self._displayFreq,self._displayData)

    def updateOriginalDataPlot(self):
        if self._originalDataCurve is None:
            return 

        print("updating original data curve")
        self._originalDataCurve.setData(self._originalFreq,self._originalData)

    def beginUpdate(self):
        self._updatingParams = True

    def endUpdate(self):
        self._updatingParams = False
        self.updateDisplayData()


    def updateDisplayData(self):
        if self._updatingParams:
            return
        print("updating display data")

        self._displayFreq = self._originalFreq
        self._displayData = self._originalData

        if self.use_crop == True:
            print("start cropping")
            print("start {0}".format(self.crop_start))
            if isinstance(self.crop_start, (int,float)):
                try:
                    idxs = np.where((self._originalFreq>=self.crop_start)) #&(self._originalFreq<=self.end_crop_frequency))
                    print(idxs)
                    self._displayFreq = self._originalFreq[idxs]
                    self._displayData = self._originalData[idxs]
                except Exception as e:
                    print("Exception in crop start")
                    print(e)
                    self._displayFreq = self._originalFreq
                    self._displayData = self._originalData

            print("end {0}".format(self.crop_end))
            if isinstance(self.crop_end, (int,float)):
                try:
                    idxs = np.where((self._originalFreq<=self.crop_end)) #&(self._originalFreq<=self.end_crop_frequency))
                    self._displayFreq = self._originalFreq[idxs]
                    self._displayData = self._originalData[idxs]
                except Exception as e:
                    print("Exception in crop end")
                    print(e)
                    self._displayFreq = self._originalFreq
                    self._displayData = self._originalData
            
            print("finish cropping")
        
        if self.remove_pickups == True:
            try:
                 self._displayData = sp.remove50Hz(self._displayFreq, self._displayData)
                #  self._displayFreq = self._originalFreq
            except Exception as e:
                print("Exception in remove_pickups")
                print(e)
                
        
        if self.smoothing == True:
            try:
                self._displayFreq, self._displayData = sp.interpolate_data_log_space( self._displayFreq, self._displayData, points_per_decade=21, convolution_winsize=self.smoothing_winsize) 
                
            except Exception as e:
                print("Exception in remove_pickups")
                print(e)
                
        self.updateDisplatDataPlot()


    def update_multiply_by_frequency(self):

        if self.multiply_by_frequency:
            self._displayData = np.multiply(self._displayFreq, self._displayData)
            self._originalData = np.multiply(self._originalFreq, self._originalData)
        else:
            self._displayData = np.multiply(self._displayFreq, self._displayData)
            self._originalData = np.multiply(self._originalFreq, self._originalData)
        self.updateDisplatDataPlot()
        self.updateOriginalDataPlot()

    @property
    def multiply_by_frequency(self):
        return self._multiply_by_frequency

    @multiply_by_frequency.setter
    def multiply_by_frequency(self, value):
        if self._multiply_by_frequency == value:
            return
        self._multiply_by_frequency = value
        # self.update_multiply_by_frequency()
        # self.updateDisplayData()

    @property
    def use_crop(self):
        return self._use_crop

    @use_crop.setter
    def use_crop(self, value):
        if self._use_crop == value:
            return
        self._use_crop = value
        self.updateDisplayData()
    
    @property
    def remove_pickups(self):
        return self._remove_pickups

    @remove_pickups.setter
    def remove_pickups(self, value):
        if self._remove_pickups == value:
            return
        self._remove_pickups = value
        self.updateDisplayData()

    @property
    def smoothing(self):
        return self._smoothing

    @smoothing.setter
    def smoothing(self, value):
        if self._smoothing == value:
            return
        self._smoothing = value
        self.updateDisplayData()

    @property
    def smoothing_winsize(self):
        return self._smoothing_winsize

    @smoothing_winsize.setter
    def smoothing_winsize(self, value):
        if self._smoothing_winsize == value:
            return 

        self._smoothing_winsize = value
        self.updateDisplayData()
        


    @property
    def cutoff_correction(self):
        return self._cutoff_correction

    @cutoff_correction.setter
    def cutoff_correction(self, value):
        if self._cutoff_correction == value:
            return
        self._cutoff_correction = value
        self.updateDisplayData()
    
    @property
    def crop_start(self):
        return self._crop_start

    @crop_start.setter
    def crop_start(self, value):
        if self._crop_start == value:
            return 

        self._crop_start = value
        self.updateDisplayData()

    @property
    def crop_end(self):
        return self._crop_end

    @crop_end.setter
    def crop_end(self, value):
        if self._crop_end == value:
            return 
        self._crop_end = value
        self.updateDisplayData()

    
    