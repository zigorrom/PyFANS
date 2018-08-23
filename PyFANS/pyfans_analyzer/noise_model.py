import numpy as np
from PyQt4 import QtCore
from lmfit import Model
from pyfans_analyzer.coordinate_transform import Transformation



class BaseNoiseComponent(QtCore.QObject):
    sigNoiseUpdateRequired = QtCore.pyqtSignal()
    PREFIX_SPLITTER = "_p_"
    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__()
        self._name = name
        self._enabled = enabled
        self._plotter = plotter
        self._coordinate_transform = kwargs.get("coordinate_transform", Transformation())
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def transform(self):
        return self._coordinate_transform

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled == value:
            return 
        self._enabled = value
        self.on_enabled_changed(value)
        self.sigNoiseUpdateRequired.emit()

    def notifyUpdateRequired(self):
        self.sigNoiseUpdateRequired.emit()

    @property
    def plotter(self):
        return self._plotter

    def component_type(self):
        return self.TYPE_NAME

    def on_enabled_changed(self,new_value):
        raise NotImplementedError()

    def on_setting_state_finished(self):
        pass

    def getModelPrefix(self):
        return "{0}{1}".format(self.name, self.PREFIX_SPLITTER)

    def getModelFunction(self,logMode):
        raise NotImplementedError

    def getFittingModelAndParams(self, logMode=True):
        raise NotImplementedError()

    def remove(self):
        pass

    @property
    def whereToAdd(self):
        viewRange =  self.plotter.getViewRange() #+[2,-1]
        print("viewRange: {0}".format(viewRange))
        whereToAddX = 0.9*viewRange[0][0]+0.1*viewRange[0][1]
        whereToAddY = 0.8*viewRange[1][1]+0.2*viewRange[1][0]
        whereToAdd = (whereToAddX,whereToAddY)
        return whereToAdd

    def params_to_serialize(self):
        return [
            "name",
            "enabled",
            "component_type"
        ]

    #def pretty_names(self):


    def get_state(self):
        d = dict()
        params = self.params_to_serialize()
        for attr in self.params_to_serialize():
            try:
                value = getattr(self, attr, None)
                if callable(value):
                    value = value()
                d[attr] = value
            except Exception as e:
                print(e)

        return d

    def set_state(self, state_dict):
        params = self.params_to_serialize()
        params.remove("component_type")
        for attr in params:
            try:
                setattr(self, attr, state_dict[attr])
            except Exception as e:
                print("Cannot set attribute {0}".format(attr))
        
        self.on_setting_state_finished()

    # #pickling area
    # def __getstate__(self):
    #     d = {""}
    #     pass
    # #\pickling area

class ModifiableNoiseComponent(BaseNoiseComponent):
    handleOffsetNormal = QtCore.QPointF(-20, 20)
    handleOffsetMultiplFreq = QtCore.QPointF(0, 20)

    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter, **kwargs)
        self._handle = None
        self._curve = None
        self.opts = kwargs
        self.transform.sigTransformChanged.connect(self.on_transform_changed)
        self.create_handle_and_curve()
        self.update_handle()



    @property
    def handle(self):
        return self._handle

    @property
    def curve(self):
        return self._curve
    
    def on_enabled_changed(self, new_value):
        self._curve.setVisible(new_value)
        self._handle.setVisible(new_value)

    def on_transform_changed(self):
        self.update_handle()
        self.update_position()
        # self.on_update_position(self.frequency, self.amplitude)

    def update_handle(self):
        if self.transform.is_multiplied:
            self.handle.handle_offset = self.handleOffsetMultiplFreq
        else:
            self.handle.handle_offset = self.handleOffsetNormal

    def create_handle(self, *args, **kwargs):
        raise NotImplementedError()

    def remove(self):
        self.remove_handle()

    def remove_handle(self):
        self.plotter.remove_handle(self.name)

    def create_handle_and_curve(self):
        whereToAdd = self.whereToAdd
        pen = self.opts.get("pen", "r")
        scene_position = self.opts.get("scenePosition", None)
        # self._handle = self.plotter.create_flicker_handle(
        #     self.name, 
        #     positionChangedCallback=self.on_handle_position_changed, 
        #     initPosition=whereToAdd 
        #     )
        self._handle = self.create_handle(
            self.name,
            positionChangedCallback=self.on_handle_position_changed, 
            initPosition=whereToAdd,
            pen=pen,
            scenePosition=scene_position
        )
        self._curve = self.plotter.get_curve_by_name(self.name)

    def on_handle_position_changed(self, handle, position):
        frequency= 10**position.x()
        amplitude = 10**position.y()
        self._frequency,self._amplitude = self.transform.convert_back(frequency, amplitude)
        self.update_curve(self.frequency, self.amplitude)
        # print("{0}:{1}".format(position, handle.currentPosition))
        # self.sigAmplitudeChanged.emit(self, self.absolute_amplitude)
        self.update_params_on_handle_position_changed()

    def update_params_on_handle_position_changed(self):
        raise NotImplementedError()

    def generate_position(self):
        raise NotImplementedError()

    def update_position(self):# , freq, amplitude):
        freq, amplitude = self.generate_position()
        self.update_curve(freq, amplitude)
        freq, amplitude = self.transform.convert(freq, amplitude)
        freq = np.log10(freq)
        amplitude = np.log10(amplitude)
        self.handle.setCurrentPosition(freq,amplitude)

    def calculate_curve(self, frequency):
        raise NotImplementedError()

    def on_setting_state_finished(self):
        self.update_position()
        self.update_params_on_handle_position_changed()
        self.notifyUpdateRequired()

    def update_curve(self, currentFreq, currentAmplitude):
        
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
        data = self.calculate_curve(freq)
        # data = func(freq, alpha=self.alpha_flicker, amplitude = currentAmplitude, f0=currentFreq)
         
        # freq, data = self.transform.convert(freq, data)
        self.curve.setData(freq,data)
        self.notifyUpdateRequired()
    
class FlickerNoiseComponent(ModifiableNoiseComponent): #Node):
    # PREFIX = "FLICKER"
    # TYPE_NAME = "FLICKER NOISE NODE"
    TYPE_NAME = "__flicker__"
    ALPHA_FLICKER_OPTION_NAME = "alpha"
    AMPLITUDE_OPTION_NAME = "amplitude"
    FREQUENCY_OPTION_NAME = "frequency"
    handleOffsetNormal = QtCore.QPointF(-20, 20)
    handleOffsetMultiplFreq = QtCore.QPointF(0, 20)
    sigAmplitudeChanged = QtCore.pyqtSignal(object, object)

    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter, **kwargs)
        self._frequency = kwargs.get(self.FREQUENCY_OPTION_NAME, None)
        self._amplitude = kwargs.get(self.AMPLITUDE_OPTION_NAME, None)
        self._alpha_flicker = kwargs.get(self.ALPHA_FLICKER_OPTION_NAME, 1)
    
    def create_handle(self, *args, **kwargs):
        handle = self.plotter.create_flicker_handle(*args, **kwargs)
        handle.sigAlphaChanged.connect(self.update_alpha_flicker)
        return handle

    def calculate_curve(self, frequency):
        func = self.getModelFunction()
        data = func(frequency, alpha=self.alpha_flicker, amplitude = self.amplitude, frequency=self.frequency)
        return data

    def update_params_on_handle_position_changed(self):
        self.sigAmplitudeChanged.emit(self, self.absolute_amplitude)

    def generate_position(self):
        return self.frequency, self.amplitude
        
    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if self._frequency == value:
            return 

        self._frequency = value
        self.update_position()

    def update_alpha_flicker(self, value):
        self.alpha_flicker = value

    @property
    def alpha_flicker(self):
        return self._alpha_flicker

    @alpha_flicker.setter
    def alpha_flicker(self, value):
        if self._alpha_flicker==value:
            return

        self._alpha_flicker = value
        self.update_position()

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        if self._amplitude == value:
            return

        self._amplitude = value
        self.update_position()

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

    def params_to_serialize(self):
        parent_params = super().params_to_serialize()
        # this_params = ["frequency", "amplitude", "alpha_flicker"]
        this_params = ["frequency", "amplitude", "absolute_amplitude", "alpha_flicker"]
        this_params.extend(parent_params)
        return this_params
        # return [
        #     "name",
        #     "enabled"
        # ]

    def getModelFunction(self, logMode=False):
        def modelFunction(f, alpha=self.alpha_flicker, amplitude=self.amplitude, frequency=self.frequency):
            fdivf0 = np.divide(frequency,f)
            data = amplitude*np.power(fdivf0,alpha)
            freq, data = self.transform.convert(f, data)
            return data
        
        def modelFunctionLog(f, alpha=self.alpha_flicker, amplitude=self.amplitude, frequency=self.frequency):
            fdivf0 = np.divide(frequency,f)
            data = amplitude*np.power(fdivf0,alpha)
            freq, data = self.transform.convert(f, data)
            data = np.log10(data)
            return data
        
        if logMode:
            return modelFunctionLog
        else:
            return modelFunction

    def getFittingModelAndParams(self,logMode=True):
        func = self.getModelFunction(logMode=logMode)
        name = self.getModelPrefix() #"{0}>".format(self.name)
        model = Model(func, prefix=name)
        params = model.make_params()
        amplitudeParamName = "{0}amplitude".format(name)
        alphaParamName = "{0}alpha".format(name)
        f0ParamName = "{0}frequency".format(name)
        params[alphaParamName].vary = False
        params[f0ParamName].vary = True
        params[amplitudeParamName].min = 0.0

        return model, params


class GenerationRecombinationNoiseComponent(ModifiableNoiseComponent): # Node):
    # PREFIX = "GR"
    # TYPE_NAME = "GR NOISE NODE"
    TYPE_NAME = "__gr__"
    FREQUENCY_OPTION_NAME = "frequency"
    AMPLITUDE_OPTION_NAME = "amplitude"
    handleOffsetNormal = QtCore.QPointF(-40, 40)
    handleOffsetMultiplFreq = QtCore.QPointF(0, 40)
    sigPositionChanged = QtCore.pyqtSignal(object, float,float)

    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter, **kwargs)

        self._frequency = kwargs.get(self.FREQUENCY_OPTION_NAME, None)
        self._amplitude = kwargs.get(self.AMPLITUDE_OPTION_NAME, None)
        
        
    def create_handle(self, *args, **kwargs):
        return self.plotter.create_gr_handle(*args, **kwargs)

    def calculate_curve(self, frequency):
        func = self.getModelFunction()
        data = func(frequency, amplitude = self.amplitude, frequency=self.frequency)
        return data

    def update_params_on_handle_position_changed(self):
        self.sigPositionChanged.emit(self, self.frequency, self.amplitude)

    def generate_position(self):
        return self.frequency, self.amplitude
    
    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        if self._amplitude == value:
            return
        self._amplitude = value
        self.update_position()

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if self._frequency == value:
            return
        self._frequency = value
        self.update_position()

    def params_to_serialize(self):
        parent_params = super().params_to_serialize()
        this_params = ["frequency", "amplitude"]
        this_params.extend(parent_params)
        return this_params

    def getModelFunction(self, logMode=False):
        def modelFunction(f, amplitude=self.amplitude, frequency=self.frequency):
            fdivf0 = np.divide(f,frequency)
            sqrfdivd0 = np.multiply(fdivf0,fdivf0)
            data = np.divide(amplitude,(1+sqrfdivd0))
            freq, data = self.transform.convert(f, data)
            return data
        # return modelFunction

        def modelFunctionLog(f, amplitude=self.amplitude, frequency=self.frequency):
            fdivf0 = np.divide(f,frequency)
            sqrfdivd0 = np.multiply(fdivf0,fdivf0)
            data = np.divide(amplitude,(1+sqrfdivd0))
            freq, data = self.transform.convert(f, data)
            data = np.log10(data)
            return data

        if logMode:
            return modelFunctionLog
        else:
            return modelFunction
        

    
    def getFittingModelAndParams(self, logMode=True):
        func = self.getModelFunction(logMode=logMode)
        name = self.getModelPrefix() #"{0}>".format(self.name)
        model = Model(func, prefix=name)
        params = model.make_params()
        amplitudeParamName = "{0}amplitude".format(name)
        f0ParamName = "{0}frequency".format(name)
        params[f0ParamName].min = 0.0
        params[amplitudeParamName].min = 0.0
        return model, params


class ThermalNoiseComponent(BaseNoiseComponent):  #Node):
    # PREFIX = "THERMAL"
    # TYPE_NAME = "THERMAL NOISE NODE"
    TYPE_NAME = "__thermal__"
    BOLTZMAN_CONSTANT = 1.38064852E-23
    RESISTANCE_OPTION_NAME = "resistance"
    TEMPERATURE_OPTION_NAME = "temperature"
    def __init__(self, name, enabled, plotter, **kwargs):
        super().__init__(name, enabled, plotter, **kwargs)

        # self._resistance = kwargs.get("resistance", None)
        # self._temperature = kwargs.get("temperature", None)
        self._thermal_noise = kwargs.get("thermal_noise", None)
        self._curve = None
        self.opts = kwargs
        rng = self.plotter.getViewRange()
        self.xMin = 10**rng[0][0]
        self.xMax = 10**rng[0][1]
        self.__create_curve__()
        self.transform.sigTransformChanged.connect(self.on_transform_changed)

    def __create_curve__(self):
        pen = self.opts.get("pen", "k")
        self._curve = self.plotter.create_curve(
            self.name,
            pen=pen,
            zValue=800,
            visible=True
        )
        self.plotter.subscribe_to_viewbox_x_range_changed(self.on_viewbox_x_range_changed)
        
    def on_viewbox_x_range_changed(self, vb, xrange):
        xmin,xmax = xrange
        self.xMin = 10**xmin
        self.xMax = 10**xmax
        self.update_thermal_noise()
    
    def update_thermal_noise(self):
        thermal_noise = self.thermal_noise_level
        xData = [self.xMin, self.xMax]
        yData = [thermal_noise,thermal_noise]
        xData, yData = self.transform.convert(xData, yData)
        self._curve.setData(xData,yData)

    def on_setting_state_finished(self):
        self.update_thermal_noise()

    def on_transform_changed(self):
        self.update_thermal_noise()
    # @property
    # def resistance(self):
    #     return self._resistance
    
    # @resistance.setter
    # def resistance(self, value):
    #     self._resistance = value
    #     self.update_thermal_noise()

    # @property
    # def temperature(self):
    #     return self._temperature
    
    # @temperature.setter
    # def temperature(self,value):
    #     self._temperature = value
    #     self.update_thermal_noise()
    # def get_model_data(self, frequency):
    #     return ThermalNoiseFunction(frequency, self.temperature,self.resistance)
    def remove(self):
        self.plotter.remove_curve(self.name)

    @property
    def thermal_noise_level(self):
        return self._thermal_noise

    @thermal_noise_level.setter
    def thermal_noise_level(self, value):
        if self._thermal_noise == value:
            return
        self._thermal_noise = value
        self.update_thermal_noise()

    def params_to_serialize(self):
        parent_params = super().params_to_serialize()
        this_params = ["thermal_noise_level"]
        this_params.extend(parent_params)
        return this_params

    def getModelFunction(self, logMode=False):
        def modelFunction(f):
            data = np.full_like(f, self.thermal_noise_level)
            freq, data = self.transform.convert(f, data)
            return data
        # return modelFunction

        def modelFunctionLog(f):
            data = np.full_like(f, self.thermal_noise_level)
            freq, data = self.transform.convert(f, data)
            data = np.log10(data)
            return data
        # return modelFunction

        if logMode:
            return modelFunctionLog
        else:
            return modelFunction
        # return 4*self.BOLTZMAN_CONSTANT*self.temperature*self.resistance

    def getFittingModelAndParams(self, logMode=True):
        func = self.getModelFunction(logMode=logMode)
        name = self.getModelPrefix() #"{0}>".format(self.name)
        model = Model(func, prefix=name)
        params = model.make_params()
        return model, params


    # def get_param_dict(self):
    #      return {self.RESISTANCE_OPTION_NAME: self.resistance, self.TEMPERATURE_OPTION_NAME: self.temperature}

    # def set_params(self,**kwargs):
    #     self._resistance = kwargs.get(self.RESISTANCE_OPTION_NAME, 0)
    #     self._temperature = kwargs.get(self.TEMPERATURE_OPTION_NAME, 0)
    



class NoiseModelToDictionaryConverter:
    def __init__(self):
        pass

    def convert(self, model):
        if not isinstance(model, dict):
            print("cannot convert non dictionary type")
            return None
        result = dict()
        
        for name, item in model.items():
            state = item.get_state()
            result[name] = state

        return result

    def convert_back(self):
        pass

    

    
    