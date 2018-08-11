import numpy as np
from PyQt4 import QtCore


class BaseNoiseComponent(QtCore.QObject):
    def __init__(self, name, enabled, plotter):
        super().__init__()
        self._name = name
        self._enabled = enabled
        self._plotter = plotter
    
    @property
    def name(self):
        return self._name

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled == value:
            return 
        self._enabled = value
        self.on_enabled_changed(value)

    @property
    def plotter(self):
        return self._plotter

    def on_enabled_changed(self,new_value):
        raise NotImplementedError()

    def on_handle_position_changed(self, position):
        raise NotImplementedError()

    def __whereToAdd__(self):
        viewRange =  self.plotter.getViewRange() #+[2,-1]
        print("viewRange: {0}".format(viewRange))
        whereToAddX = 0.9*viewRange[0][0]+0.1*viewRange[0][1]
        whereToAddY = 0.8*viewRange[1][1]+0.2*viewRange[1][0]
        whereToAdd = (whereToAddX,whereToAddY)
        return whereToAdd

# class 

class FlickerNoiseComponent(BaseNoiseComponent): #Node):
    PREFIX = "FLICKER"
    TYPE_NAME = "FLICKER NOISE NODE"

    ALPHA_FLICKER_OPTION_NAME = "alpha"
    AMPLITUDE_OPTION_NAME = "amplitude"
    FREQUENCY_OPTION_NAME = "frequency"
    sigAmplitudeChanged = QtCore.pyqtSignal(float)

    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter)
        
        self._frequency = kwargs.get(self.FREQUENCY_OPTION_NAME, None)
        self._amplitude = kwargs.get(self.AMPLITUDE_OPTION_NAME, None)
        self._alpha_flicker = kwargs.get(self.ALPHA_FLICKER_OPTION_NAME, 1)
        self._handle = None
        self._curve = None
        self.opts = kwargs
        self.__create_handle__()
    
    def __create_handle__(self):
        whereToAdd = self.__whereToAdd__()
        pen = self.opts.get("pen", "r")
        self._handle = self.plotter.create_flicker_handle(
            self.name, 
            positionChangedCallback=self.on_handle_position_changed, 
            initPosition=whereToAdd 
            )
        self._curve = self.plotter.get_curve_by_name(self.name)
        # position = self._handle.currentPosition
        # print("initial")
        # print(position)
        # print("where to add")
        # # print(whereToAdd)
        # x,y = position.x(), position.y()
        # self._frequency = np.power(10, x)
        # self._amplitude = np.power(10, y)
        # self.update_curve(self.frequency, self.amplitude)

    @property
    def handle(self):
        return self._handle

    @property
    def curve(self):
        return self._curve
    
    def update_curve(self, currentFreq, currentAmplitude):
        func = self.getModelFunction()
        xPosHandle = np.log10(currentFreq)
        xStart = xPosHandle - 1
        xEnd = xPosHandle + 1
        
        rng = self.plotter.getViewRange()
        xmin, xmax = rng[0]
        xmin = max(xmin, xStart)
        xmax = min(xmax, xEnd)
        npoints = (xmax-xmin)/0.1 +1
        
        # freq = np.logspace(0,5, 51)
        freq = np.logspace(xmin,xmax, npoints)
        
        data = func(freq, alpha=self.alpha_flicker, amplitude = currentAmplitude, f0=currentFreq)
        self.curve.setData(freq,data)
        
    def on_enabled_changed(self,new_value):
        self._curve.setVisible(new_value)
        self._handle.setVisible(new_value)

    def on_handle_position_changed(self, handle, position):
        self._frequency= 10**position.x()
        self._amplitude = 10**position.y()
        self.update_curve(self.frequency, self.amplitude)
        # print("{0}:{1}".format(position, handle.currentPosition))
        self.sigAmplitudeChanged.emit(self.absolute_amplitude)

    def on_update_position(self, freq, amplitude):
        self.update_curve(freq, amplitude)
        freq = np.log10(freq)
        amplitude = np.log10(amplitude)
        self.handle.setCurrentPosition(freq,amplitude)
        
    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if self._frequency == value:
            return 

        self._frequency = value
        self.on_update_position(self.frequency, self.amplitude)

    @property
    def alpha_flicker(self):
        return self._alpha_flicker

    @alpha_flicker.setter
    def alpha_flicker(self, value):
        if self._alpha_flicker==value:
            return

        self._alpha_flicker = value
        self.on_update_position(self.frequency, self.amplitude)

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        if self._amplitude == value:
            return

        self._amplitude = value
        self.on_update_position(self.frequency, self.amplitude)

    @property
    def absolute_amplitude(self):
        return self.amplitude * self.frequency

    @absolute_amplitude.setter
    def absolute_amplitude(self, value):
        if self.frequency > 0:
            # account alpha
            self.amplitude = value / self.frequency
        else:
            self.frequency = 1.0
            self.amplitude = value

    # def set_position(self, position):
    #     x,y = position
    #     self.frequency = x
    #     self.amplitude = y
        
    # def get_position(self):
    #     return (self.frequency, self.amplitude)

    # def get_model_data(self, frequency):
    #     # result = np.apply_along_axis(FlickerShapeFunction, 0, frequency, alphaFlicker = self.alpha_flicker, Amplitude = self.absolute_amplitude)
    #     return FlickerShapeFunction(frequency, self.alpha_flicker, self.absolute_amplitude)
        # return result #FlickerShapeFunction(frequency, self.alpha_flicker, self.absolute_amplitude)

    # def get_param_dict(self):
    #     key_format = "{n}_{p}"
    #     return {
    #         key_format.format(n=self.name, p=self.ALPHA_FLICKER_OPTION_NAME) : self.alpha_flicker,
    #         key_format.format(n=self.name,p=self.FREQUENCY_OPTION_NAME): self.frequency, 
    #         key_format.format(n=self.name,p=self.AMPLITUDE_OPTION_NAME): self.amplitude
    #     }

    # def set_params(self, **kwargs):
    #     # flicker_keys = kwargs.keys()
    #     # list(filter(lambda x: x < 0, number_list)
    #     # )
    #     #flicker_keys = filter(lambda x: x.startswith(FlickerNoiseNode.PREFIX), kwargs.keys())
        
    #     self._alpha_flicker = kwargs.get(self.ALPHA_FLICKER_OPTION_NAME, 1)
    #     self._amplitude = kwargs.get(self.AMPLITUDE_OPTION_NAME, 1e-11)
    #     self._frequency = kwargs.get(self.FREQUENCY_OPTION_NAME, 1)

    # def calculateCurve(self, frequency):
    #    
    
    def getModelFunction(self):
        def modelFunction(frequency, alpha=self.alpha_flicker, amplitude=self.amplitude, f0=self.frequency):
            fdivf0 = np.divide(f0,frequency)
            data = amplitude*np.power(fdivf0,alpha)
            return data
        return modelFunction
    

class GenerationRecombinationNoiseComponent(BaseNoiseComponent): # Node):
    PREFIX = "GR"
    TYPE_NAME = "GR NOISE NODE"

    FREQUENCY_OPTION_NAME = "frequency"
    AMPLITUDE_OPTION_NAME = "amplitude"
    
    sigPositionChanged = QtCore.pyqtSignal(float,float)

    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter)

        self._frequency = kwargs.get(self.FREQUENCY_OPTION_NAME, None)
        self._amplitude = kwargs.get(self.AMPLITUDE_OPTION_NAME, None)
        self._handle = None
        self._curve = None
        self.opts = kwargs
        self.__create_handle__()
        # self.set_params(**kwargs)
        
    def __create_handle__(self):
        whereToAdd = self.__whereToAdd__()
        pen = self.opts.get("pen", "r")
        self._handle = self.plotter.create_gr_handle(
            self.name, 
            positionChangedCallback=self.on_handle_position_changed, 
            initPosition=whereToAdd,
            pen=pen
            )
        self._curve = self.plotter.get_curve_by_name(self.name)

    def update_curve(self, currentFreq, currentAmplitude):
        func = self.getModelFunction()
        xPosHandle = np.log10(currentFreq)
        xStart = xPosHandle - 1
        xEnd = xPosHandle + 1
        
        rng = self.plotter.getViewRange()
        xmin, xmax = rng[0]
        xmin = max(xmin, xStart)
        xmax = min(xmax, xEnd)
        npoints = (xmax-xmin)/0.1 +1
        
        # freq = np.logspace(0,5, 51)
        freq = np.logspace(xmin,xmax, npoints)
        
        data = func(freq, amplitude = currentAmplitude, f0=currentFreq)
        self.curve.setData(freq,data)
        
    def on_enabled_changed(self,new_value):
        self._curve.setVisible(new_value)
        self._handle.setVisible(new_value)

    def on_handle_position_changed(self, handle, position):
        print(position)
        self._frequency= 10**position.x()
        self._amplitude = 10**position.y()
        self.update_curve(self.frequency, self.amplitude)
        # print("{0}:{1}".format(position, handle.currentPosition))
        self.sigPositionChanged.emit(self.frequency, self.amplitude)

    def on_update_position(self, freq, amplitude):
        self.update_curve(freq, amplitude)
        freq = np.log10(freq)
        amplitude = np.log10(amplitude)
        self.handle.setCurrentPosition(freq,amplitude)

    @property
    def curve(self):
        return self._curve

    @property
    def handle(self):
        return self._handle


    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        if self._amplitude == value:
            return
        self._amplitude = value
        self.on_update_position(self.frequency, self.amplitude)

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if self._frequency == value:
            return
        self._frequency = value
        self.on_update_position(self.frequency, self.amplitude)

    # def set_position(self, position):
    #     x,y = position
    #     self.frequency = x #position.x()
    #     self.amplitude = y #position.y()

    # def get_position(self):
    #     return (self.frequency, self.amplitude)

    def getModelFunction(self):
        def modelFunction(frequency, amplitude=self.amplitude, f0=self.frequency):
            fdivf0 = np.divide(frequency,f0)
            sqrfdivd0 = fdivf0*fdivf0
            data = amplitude/(1+sqrfdivd0)
            return data
        return modelFunction

    # def get_model_data(self, frequency):
    #     return LorentzianShapeFunction(frequency, self.frequency,self.amplitude)

    # def get_param_dict(self):
    #      return {self.FREQUENCY_OPTION_NAME: self.frequency, self.AMPLITUDE_OPTION_NAME: self.amplitude}

    # def set_params(self,**kwargs):
    #     self._frequency = kwargs.get(self.FREQUENCY_OPTION_NAME, 1)
    #     self._amplitude = kwargs.get(self.AMPLITUDE_OPTION_NAME, 0)



class ThermalNoiseComponent: #Node):
    PREFIX = "THERMAL"
    TYPE_NAME = "THERMAL NOISE NODE"
    
    RESISTANCE_OPTION_NAME = "resistance"
    TEMPERATURE_OPTION_NAME = "temperature"
    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter)

        self._resistance = kwargs.get("resistance", None)
        self._temperature = kwargs.get("temperature", None)
        # self.set_params(**kwargs)

    
    @property
    def resistance(self):
        return self._resistance
    
    @resistance.setter
    def resistance(self, value):
        self._resistance = value

    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self,value):
        self._temperature = value

    # def get_model_data(self, frequency):
    #     return ThermalNoiseFunction(frequency, self.temperature,self.resistance)

    def get_param_dict(self):
         return {self.RESISTANCE_OPTION_NAME: self.resistance, self.TEMPERATURE_OPTION_NAME: self.temperature}

    def set_params(self,**kwargs):
        self._resistance = kwargs.get(self.RESISTANCE_OPTION_NAME, 0)
        self._temperature = kwargs.get(self.TEMPERATURE_OPTION_NAME, 0)





    

    
    