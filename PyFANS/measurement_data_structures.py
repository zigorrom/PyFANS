class measurement_parameter_property(property):
    def __init__(self,name,units,description, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._units = units
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def units(self):
        return self._units

    @property
    def description(self):
        return self._description

def create_measurement_parameter_property(name, units, description):
    def real_decorator(func):
        return measurement_parameter_property(name,units, description, fget = func)
    return real_decorator


class test_class:
    def __init__(self, value):
        self._value = value

    @create_measurement_parameter_property("blah", "V",":asdfbashfg")
    def value(self):
        return self._value
    

def generate_measurement_info_filename(measurement_name, measurement_count, file_extension = "dat"):
    return "{0}_{1}.{2}".format(measurement_name,measurement_count, file_extension)

class MeasurementInfo:
    SAMPLE_VOLTAGE_END_OPTION = "Vds (end)" #self.start_sample_voltage, 
    SAMPLE_CURRENT_END_OPTION = "Id (end)" #            self.sample_current_start,
    EQUIVALENT_RESISTANCE_END_OPTION = "Req (end)"                #self._equivalent_resistance_start,
    FILENAME_OPTION = "Filename" #generate_measurement_info_filename(self.measurement_filename, self.measurement_count,self._measurement_file_extension),
    LOAD_RESISTANCE_OPTION = "Rload" #                self._load_resistance,
    MAIN_VOLTAGE_END_OPTION = "Vmain (end)" #                self.end_main_voltage,
    SAMPLE_VOLTAGE_START_OPTION = "Vds (start)"  #               self.start_sample_voltage,
    MAIN_VOLTAGE_START_OPTION = "Vmain (start)"  #               self.start_main_voltage,
    SAMPLE_RESISTANCE_START_OPTION = "Rs (start)" #                self._sample_resistance_start,
    SAMPLE_RESISTANCE_END_OPTION = "Rs (end)"     #           self._sample_resistance_end,
    TEMPERATURE_START_OPTION = "T (start)"  #                self.start_temperature,
    TEMPERATURE_END_OPTION = "T (end)" #                self.end_temperature,
    AMPLIFICATION_OPTION = "Kampl"#    amplification                None,
    AVERAGES_OPTION = "Naver"#    averages                None,
    GATE_VOLTAGE_END_OPTION = "Vgate (end)" #            self.end_gate_voltage
    GATE_VOLTAGE_START_OPTION = "Vgate (start)"
                



    def __init__(self, measurement_filename = "", measurement_count = 0,file_extension = "dat", load_resistance = 5000, second_amplifier_gain=100):
        self._measurement_filename = measurement_filename
        self._measurement_count = measurement_count
        self._measurement_file_extension = file_extension

        self._measured_temp_start = 0
        self._measured_temp_end = 0

        self._measured_main_voltage_start = 0
        self._measured_main_voltage_end = 0

        self._measured_sample_voltage_start = 0
        self._measured_sample_voltage_end = 0
        
        self._measured_gate_voltage_start = 0
        self._measured_gate_voltage_end = 0

        self._sample_current_start = 0
        self._sample_current_end = 0

        self._sample_resistance_start = 0
        self._sample_resistance_end = 0

        self._equivalent_resistance_start = 0
        self._equivalent_resistance_end = 0

        self._load_resistance = load_resistance

        self._second_amplifier_gain = second_amplifier_gain



    def update_start_values(self, main_voltage, sample_voltage, gate_voltage, temperature):
        self.start_main_voltage = main_voltage
        self.start_gate_voltage = gate_voltage
        self.start_sample_voltage = sample_voltage
        current, sample_resistance, equivalent_resistance = self._calculate_current_resistance(main_voltage, sample_voltage, self._load_resistance)
        self.sample_current_start = current
        self.sample_resistance_start = sample_resistance
        self.equivalent_resistance_start = equivalent_resistance
        self.start_temperature = temperature


    def update_end_values(self, main_voltage, sample_voltage, gate_voltage, temperature):
        self.end_main_voltage = main_voltage
        self.end_gate_voltage = gate_voltage
        self.end_sample_voltage = sample_voltage
        current, sample_resistance, equivalent_resistance = self._calculate_current_resistance(main_voltage, sample_voltage, self._load_resistance)
        self.sample_current_end = current
        self.sample_resistance_end = sample_resistance
        self.equivalent_resistance_end = equivalent_resistance
        self.end_temperature = temperature

    def _calculate_current_resistance(self, main_voltage, sample_voltage, load_resistance):
        current, sample_resistance, equivalent_resistance = (0, float("inf"), load_resistance)
        try:
            current = (main_voltage-sample_voltage)/load_resistance
            sample_resistance = sample_voltage/current
            equivalent_resistance = sample_resistance*load_resistance/(sample_resistance+load_resistance)
        except ZeroDivisionError:
            print("zero division error while calculating resistance...")
            
        return current, sample_resistance, equivalent_resistance


    @property
    def second_amplifier_gain(self):
        return self._second_amplifier_gain

    @second_amplifier_gain.setter
    def second_amplifier_gain(self,value):
        self._second_amplifier_gain = value

    @property
    def sample_current_start(self):
        return self._sample_current_start

    @sample_current_start.setter
    def sample_current_start(self,value):
        self._sample_current_start = value

    @property
    def sample_current_end(self):
        return self._sample_current_end

    @sample_current_end.setter
    def sample_current_end(self,value):
        self._sample_current_end = value


    @property
    def equivalent_resistance_start(self):
        return self._equivalent_resistance_start

    @equivalent_resistance_start.setter
    def equivalent_resistance_start(self,value):
        self._equivalent_resistance_start = value

    @property
    def equivalent_resistance_end(self):
        return self._equivalent_resistance_end

    @equivalent_resistance_end.setter
    def equivalent_resistance_end(self,value):
        self._equivalent_resistance_end = value


    @property
    def sample_resistance_start(self):
        return self._sample_resistance_start

    @sample_resistance_start.setter
    def sample_resistance_start(self,value):
        self._sample_resistance_start = value

    @property
    def sample_resistance_end(self):
        return self._sample_resistance_end

    @sample_resistance_end.setter
    def sample_resistance_end(self,value):
        self._sample_resistance_end = value

    @property
    def measurement_count(self):
        return self._measurement_count

    @measurement_count.setter
    def measurement_count(self,value):
        self._measurement_count = value

    @property
    def measurement_filename(self):
        return self._measurement_filename

    @measurement_filename.setter
    def measurement_filename(self,filename):
        self._measurement_filename = filename

    @property
    def start_temperature(self):
        return self._measured_temp_start
    
    @start_temperature.setter
    def start_temperature(self, value):
        self._measured_temp_start = value

    @property
    def end_temperature(self):
        return self._measured_temp_end
    
    @end_temperature.setter
    def end_temperature(self, value):
        self._measured_temp_end = value

    @property
    def start_main_voltage(self):
        return self._measured_main_voltage_start
    
    @start_main_voltage.setter
    def start_main_voltage(self, value):
        self._measured_main_voltage_start = value

    @property
    def end_main_voltage(self):
        return self._measured_main_voltage_end
    
    @end_main_voltage.setter
    def end_main_voltage(self, value):
        self._measured_main_voltage_end = value

    @property
    def start_sample_voltage(self):
        return self._measured_sample_voltage_start
    
    @start_sample_voltage.setter
    def start_sample_voltage(self, value):
        self._measured_sample_voltage_start = value

    @property
    def end_sample_voltage(self):
        return self._measured_sample_voltage_end
    
    @end_sample_voltage.setter
    def end_sample_voltage(self, value):
        self._measured_sample_voltage_end = value
        
    @property
    def start_gate_voltage(self):
        return self._measured_gate_voltage_start
    
    @start_gate_voltage.setter
    def start_gate_voltage(self,value):
        self._measured_gate_voltage_start = value

    @property
    def end_gate_voltage(self):
        return self._measured_gate_voltage_end
    
    @end_gate_voltage.setter
    def end_gate_voltage(self,value):
        self._measured_gate_voltage_end = value

        #    ["U\_sample","V"],
        #    ["Current", "A"],
        #    ["R\_equivalent", "Ohm"],
        #    ["Filename","str"],
        #    ["R\_load","Ohm"],
        #    ["U\_whole","V"],
        #    ["U\_0sample", "V"],
        #    ["U\_0whole","V"],
        #    ["R\-(0sample)","Ohm"],
        #    ["R\-(Esample)","Ohm"],
        #    ["Temperature\-(0)","K"],
        #    ["Temperature\-(E)","K"],
        #    ["k\-(ampl)","int"],
        #    ["N\-(aver)","int"],
        #    ["V\-(Gate)","V"]
    @property
    def header_list(self):
        return [
            self.SAMPLE_VOLTAGE_END_OPTION,
            self.SAMPLE_CURRENT_END_OPTION,
            self.EQUIVALENT_RESISTANCE_END_OPTION,
            self.FILENAME_OPTION,
            self.LOAD_RESISTANCE_OPTION,
            self.MAIN_VOLTAGE_END_OPTION,
            self.SAMPLE_VOLTAGE_START_OPTION,
            self.MAIN_VOLTAGE_START_OPTION,
            self.SAMPLE_RESISTANCE_START_OPTION,
            self.SAMPLE_RESISTANCE_END_OPTION,
            self.TEMPERATURE_START_OPTION,
            self.TEMPERATURE_END_OPTION,
            self.AMPLIFICATION_OPTION,
            self.AVERAGES_OPTION,
            self.GATE_VOLTAGE_END_OPTION,
            self.GATE_VOLTAGE_START_OPTION
            ]

    def to_dict(self):
        return {
            self.SAMPLE_VOLTAGE_END_OPTION: self.end_sample_voltage,
            self.SAMPLE_CURRENT_END_OPTION: self.sample_current_end,
            self.EQUIVALENT_RESISTANCE_END_OPTION: self.equivalent_resistance_end,
            self.FILENAME_OPTION: generate_measurement_info_filename(self.measurement_filename, self.measurement_count,self._measurement_file_extension),
            self.LOAD_RESISTANCE_OPTION: self._load_resistance,
            self.MAIN_VOLTAGE_END_OPTION: self.end_main_voltage,
            self.SAMPLE_VOLTAGE_START_OPTION: self.start_sample_voltage,
            self.MAIN_VOLTAGE_START_OPTION:self.start_main_voltage,
            self.SAMPLE_RESISTANCE_START_OPTION: self.sample_resistance_start,
            self.SAMPLE_RESISTANCE_END_OPTION: self.sample_resistance_end,
            self.TEMPERATURE_START_OPTION: self.start_temperature,
            self.TEMPERATURE_END_OPTION: self.end_temperature,
            self.AMPLIFICATION_OPTION: self.second_amplifier_gain,
            self.AVERAGES_OPTION: None,
            self.GATE_VOLTAGE_END_OPTION: self.end_gate_voltage,
            self.GATE_VOLTAGE_START_OPTION: self.start_gate_voltage
            }

    def __str__(self):
        list = [self.start_sample_voltage, 
                self.sample_current_start,
                self._equivalent_resistance_start,
                generate_measurement_info_filename(self.measurement_filename, self.measurement_count,self._measurement_file_extension),
                self._load_resistance,
                self.end_main_voltage,
                self.start_sample_voltage,
                self.start_main_voltage,
                self._sample_resistance_start,
                self._sample_resistance_end,
                self.start_temperature,
                self.end_temperature,
                None,
                None,
                self.end_gate_voltage
                ]
        representation = "\t".join(map(str,list)) + '\n'
        return representation
        

if __name__=="__main__":
    tc = test_class("asfgasgag")
    print(tc.value)
    print(tc.value.name)

