import serial
import visa

def instrument_await_function(func):
        def wrapper(self,*args,**kwargs):
            #print (isinstance(self,VisaInstrument))
            prev_timeout = self._VisaInstrument__instrument.timeout
            self._VisaInstrument__instrument.timeout = None
            #self.timeout = None
            #self.__instrument.timeout = None
            result = func(self,*args,**kwargs)
            self._VisaInstrument__instrument.timeout = prev_timeout
            #self.__instrument.timeout = prev_timeout 
            return result
        return wrapper

def get_available_gpib_resources():
    rm = visa.ResourceManager()
    return rm.list_resources()

def get_available_com_resources():
    import serial.tools.list_ports
    devs = serial.tools.list_ports.comports()
    names = list(map(lambda x: x.device ,devs))
    return names

class SerialInstrument:
    def __init__(self, resource, baud_rate = 9600):
        self.__port = serial.Serial(
            port = resource, 
            baudrate = baud_rate
            )
        self.__termination_char = "\n"
        self.__port.flushInput()
        self.__port.flushOutput()

    @property
    def termination_char(self):
        return self.__termination_char
    
    @termination_char.setter
    def termination_char(self,value):
        self.__termination_char = value

    def open(self):
        if not self.isOpen():
            self.__port.open()

    def close(self):
        self.__port.close()

    def isOpen(self):
        return self.__port.isOpen()

    def write(self, string):
        #assert self.isOpen()
        print("sending to device: {0}".format(string))
        self.__port.write(string.encode('ascii'))   #base64.b64encode(bytes(string, 'utf-8')))   #string.encode('')
                          

    def read(self, num_of_bytes = 1):
        #assert self.isOpen()
        return self.__port.read(num_of_bytes).decode()

    def read_until_termination(self):
        #assert self.isOpen()
        read_chars = []
        current_char = None
        while current_char != self.termination_char:
            current_char = self.read()
            read_chars.append(current_char)

        return "".join(read_chars)

    def query(self,string):
        #assert self.isOpen()
        self.write(string)
        return self.read_until_termination()

class VisaInstrument:
    def __init__(self, resource, debug=True):
        rm = visa.ResourceManager()
        self.__instrument = rm.open_resource(resource, write_termination = '\n',read_termination='\n')
        self.__debug_mode = debug

    @property
    def debug_mode(self):
        return self.__debug_mode

    @debug_mode.setter
    def debug_mode(self, value):
        if isinstance(value, bool):
            self.__debug_mode = value


    def write(self,string):
        assert isinstance(string, str)
        if self.__debug_mode:
            print("writing to device: {0}".format(string))
        self.__instrument.write(string)

    def query(self,string):
        assert isinstance(string, str)
        if self.__debug_mode:
            print("querying from device: {0}".format(string))
        return self.__instrument.ask(string)

    def read(self):
        return self.__instrument.read()

    def read_raw(self):
        return self.__instrument.read_raw()


if __name__ == "__main__":
    pass