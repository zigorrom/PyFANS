import math
import numpy as np
import pyqtgraph as pg


def LengthOfFile(f):
    """ Get the length of the file for a regular file (not a device file)"""
    currentPos=f.tell()
    f.seek(0, 2)          # move to end of file
    length = f.tell()     # get current position
    f.seek(currentPos, 0) # go back to where we started
    return length

def BytesRemaining(f,f_len):
    """ Get number of bytes left to read, where f_len is the length of the file (probably from f_len=LengthOfFile(f) )"""
    currentPos=f.tell()
    return f_len-currentPos

def BytesRemainingAndSize(f):
    """ Get number of bytes left to read for a regular file (not a device file), returns a tuple of the bytes remaining and the total length of the file
        If your code is going to be doing this alot then use LengthOfFile and  BytesRemaining instead of this function
    """
    currentPos=f.tell()
    l=LengthOfFile(f)
    return l-currentPos,l

def CurrentPosition(f):
    currentPos = f.tell()
    return currentPos

class TimetraceFileBuffer:
    def __init__(self, filename):
        self._filename = filename
        self._file = None
        
        self.reset()        
        
    def reset(self):
        self._timetrace_sample_rate = None
        self._timetrace_time_step = None
        self._timetrace_file_header = None
        self._timetrace_total_length = None
        self._timetrace_total_time = None
        self._max_display_time = 0.2 # sec

        self._data_start_position = 0
        self._current_position = 0
        self._previous_position = 0
        # self._file_length = 0
        self._block_size = 0
        self._block_sample = 0

        self._current_start_idx = 0
        self._current_end_idx = 0
        
        self._data = None
        self._time = None
    

    def open(self):
        f = open(self._filename, "rb")
        self._file = f
        header = f.readline()
        self._timetrace_file_header = header.decode()
        self.parse_header()
        self._data_start_position = CurrentPosition(self._file)
        self._timetrace_total_length = LengthOfFile(self._file) - self._data_start_position
        self._init_block()
        



    def close(self):
        self._file.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, t, value, traceback):
        self.close()
        print(t)
        print(value)
        return True
    
    @property
    def sample_rate(self):
        return self._timetrace_sample_rate

    @property
    def time_step(self):
        return self._timetrace_time_step

    @property
    def block_size(self):
        return self._block_size

    @property
    def block_samples(self):
        return self._block_sample

    @property
    def data(self):
        return self._data

    @property
    def time(self):
        return self._time

    def parse_header(self):
        head = self._timetrace_file_header
        sample_rate_str = head.split("=")[1]
        self._timetrace_sample_rate = float(sample_rate_str)
        self._timetrace_time_step = 1/self._timetrace_sample_rate

    def _init_block(self):
        pos = CurrentPosition(self._file)
        data = np.load(self._file)
        new_pos = CurrentPosition(self._file)
        self._block_size = new_pos - pos
        self._block_sample = len(data)
        self._file.seek(pos)

    def _read_current_block(self):
        try:
            data = np.load(self._file)
            return data
        except Exception as e:
            return None

    # def get_timetrace_data(self,start_idx=None, end_idx=None, start_time=None, end_time=None):
    #     pass

    def _read_timetrace_interval_from_file(self, start_idx, end_idx):
        
        start_block = math.floor(start_idx/self.block_samples)
        end_block = math.ceil(end_idx/self.block_samples)
        print("start idx", start_block, "end_idx", end_block)
        start_idx = start_block*self.block_samples
        end_idx = end_block*self.block_samples
        data_arrays = list()
        file_start_position = start_block*self.block_size + self._data_start_position
        self._file.seek(file_start_position)
        for i in range(start_block, end_block):
            try:
                data = np.load(self._file)
                data_arrays.append(data)
            except Exception as e:
                end_block = i
                end_idx = end_block * self.block_samples
                break
        
        self._current_start_idx = start_idx
        self._current_end_idx = end_idx
        self._data = np.hstack(data_arrays)
        self._time = np.arange(start_idx*self.time_step, end_idx*self.time_step, self.time_step)


    def get_timetrace_data(self, start_idx=None, end_idx=None, start_time=None, end_time=None):
        if start_time is not None:
            start_idx =  math.floor(start_time/self.time_step)
        if end_time is not None:
            end_idx =  math.floor(end_time/self.time_step)
        
        if not isinstance(start_idx, int):
            raise TypeError("start index should be integer")

        if not isinstance(end_idx, int):
            raise TypeError("end index should be integer")
        
        
        if start_idx == end_idx:
            raise IndexError("start index is equal to end index")
            
        start_idx = 0 if start_idx<0 else start_idx
        end_idx = 0 if end_idx<0 else end_idx

        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        print("start idx", start_idx, "end_idx", end_idx)

        if start_idx<self._current_start_idx | end_idx>self._current_end_idx:
            if self._current_start_idx == 0 & self._current_end_idx == self._timetrace_total_length:
                return
            self._read_timetrace_interval_from_file(start_idx, end_idx)
        
        l = end_idx - start_idx
        max_display_len = math.floor(self._max_display_time/self.time_step)
        if l>max_display_len:
            l = max_display_len
            
        start_idx -= self._current_start_idx
        end_idx = start_idx+l
     
        
        
        return self._time[start_idx:end_idx], self._data[start_idx:end_idx]

        
        

        
    
    

    


def main():
    fname = "D:\\Testdata\\BG=1V\\T06_Noise_BG=1V_1_timetrace.npy"
    with TimetraceFileBuffer(fname) as tb:
        print(tb.sample_rate)
        print(tb.time_step)
        print(tb.block_size)
        print(tb.block_samples)
        tb.get_timetrace_data(start_time=0,end_time=1) 
        # print(tb.data)
        # print(tb.time)
        # print(len(tb.data))
        # print(len(tb.time))
        plot = pg.plot()
        curve = plot.plot(tb.time, tb.data)
        plot.sigXRangeChanged.connect(lambda obj, rng: curve.setData(*tb.get_timetrace_data(start_time=rng[0],end_time=rng[1])))
        if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):    
            pg.QtGui.QApplication.exec_()

        


def test_save():
    from tempfile import TemporaryFile
    out_file = TemporaryFile()
    l = 100
    for i in range(10):
        x = np.arange(l)
        print(x)
        np.save(out_file, x, allow_pickle=False)

    out_file.seek(0)
    print("everything is written")
    print("loading")
    counter = 0
    try:
        while True:
            print("reading array: {0}".format(counter))
            res = np.load(out_file, allow_pickle=False)
            print(res)
            counter+=1

    except Exception as e:
        print("Exception occured:")
        print(str(e))
        print(10*"*")
           
    print(res)
    print("end")


if __name__=="__main__":
    import sys
   
    main()
    # test_save()