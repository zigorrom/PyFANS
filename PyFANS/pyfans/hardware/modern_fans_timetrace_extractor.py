import sys
import os
import argparse
import numpy as np
import pandas as pd
import fnmatch
from tqdm import tqdm
from scipy.signal import decimate



def search_for_new_style_measurement_data_file(folder):
    print("SEARCHING FOT MEASUREMENT DATA FILE IN:\n\r{0}".format(folder))
    print("*"*10)
    pattern = "MeasurmentData_*.dat"
    files = os.listdir(folder)
    matches = fnmatch.filter(files, pattern)
    if matches:
        print("FOUND MATCHES:\n\r{0}".format(matches))
        print("*"*10)
    #print(matches)
    return matches

def print_error(error):
    print("Exception occured")
    print(10*"*")
    print(str(error))
    print(10*"*")

def generate_output_filename(initial_filename, postfix, output_extension, output_folder=None):
    base_name = os.path.basename(initial_filename)
    dirname = os.path.dirname(initial_filename)
    if os.path.isdir(output_folder):
        dirname = output_folder

    filename, file_extension = os.path.splitext(base_name)
    # filename, file_extension = os.path.splitext(initial_filename)
    #out_file = ".".join([filename+postfix, output_extension])
    out_file = os.path.join(dirname, filename+postfix+"."+output_extension)
    return out_file

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

def CheckDecimationConditions(signal_sampling_rate, decimated_sample_rate):
    condition_is_good = False
    try:
        if not isinstance(signal_sampling_rate, int) or not isinstance(decimated_sample_rate, int):
            raise TypeError("signal_sampling_rate or decimated sampling rate is of wrong format")

        sr_div,sr_mod = divmod(signal_sampling_rate, decimated_sample_rate)
        if sr_mod == 0:
            condition_is_good = True
    
    except Exception as e:
        condition_is_good = False
    finally:
        return condition_is_good

def DecimateSignal(signal_array, signal_sampling_rate, decimated_sample_rate):
    decimation_factor = int(signal_sampling_rate / decimated_sample_rate)
    decimated = decimate(signal_array,decimation_factor,n=8,ftype="iir",axis = 0 ,zero_phase=True)
    return decimated

class FANS_TimetraceExtractor:
    def __init__(self, **kwargs):
        self._working_directory = kwargs.get("working_directory", "")
        self._output_folder = kwargs.get("output_folder", "")
        self._sample_rate = kwargs.get("sample_rate", 500000)
        self._points_per_sample = kwargs.get("points_per_sample", 50000)
        self._total_time_to_convert = kwargs.get("length", -1)
        self._filename_to_convert = kwargs.get("filename", None)
        self._measurement_filename = kwargs.get("measurement_data_file", None)
        self._output_extension = "dat"
        self._amplification_factor = kwargs.get("amplification", None)
        self._decimated_sample_rate = kwargs.get("decimated_sample_rate", 0)

    def perform_convertion(self):
        if self._filename_to_convert and os.path.isfile(self._filename_to_convert):
            try:
                self.process_single_timetrace_file(self._filename_to_convert, output_folder = self._output_folder)
            except Exception as e:
                print_error(e)
            return 

        working_directory = self._working_directory if os.path.isdir(self._working_directory) else os.getcwd()
        if not self._measurement_filename:
            print("Measurement filename is not specified - looking for measurement data file in folder: {0}".format(working_directory))
            self._measurement_filename = search_for_new_style_measurement_data_file(working_directory)
            if not self._measurement_filename:
                raise FileNotFoundError("Measurement data file is not found")

        if isinstance(self._measurement_filename, str):
            try:
                self.process_measurment_data_file(self._measurement_filename)
            except Exception as e:
                print("Exception while processing measurement file: {0}".format(self._measurement_filename))
                print_error(e)

        elif isinstance(self._measurement_filename, list):
            for meas_file in self._measurement_filename:
                try:
                    self.process_measurment_data_file(meas_file)
                except Exception as e:
                    print("Exception while processing measurement file: {0}".format(meas_file))
                    print_error(e)

    def process_measurment_data_file(self, measurement_data_filename):
        print("START PROCESSING MEASUREMENT DATA FILE: {0}".format(measurement_data_filename))

        measure_data = pd.read_csv(measurement_data_filename, index_col = False, delimiter = "\t")
        vds_end_col, drain_current_col, req_col, filename_col, rload_col, vmain_end_col, vds_start_col, vmain_start_col, rsample_start, rsample_end, temperature_start, temperature_end, kampl, naver, gate_volt_end, gate_volt_start = list(measure_data)
        print(measure_data)
        working_directory = os.path.dirname(measurement_data_filename)
        for index, row_data in measure_data.iterrows():
            filename, extention = os.path.splitext(row_data[filename_col])
            filename = os.path.join(working_directory, filename + "_timetrace.npy")

            amplification = row_data[kampl]
            if isinstance(self._amplification_factor, (int,float)):
                amplification = self._amplification_factor
            elif amplification:
                amplification = 172 * amplification
            else:
                amplification = 1

            if not os.path.isfile(filename):
                print("No such file...")
            try:
                self.process_single_timetrace_file(filename, amplification = amplification, output_folder = self._output_folder)
            except Exception as e:
                print("Exception while processing file: {0}".format(filename))
                print_error(e)
                print("continue with next file available")

        print("FINISHED PROCESSING OF MEASUREMENT DATA FILE")

    def process_single_timetrace_file(self, filename, output_folder = None, amplification = None):
        # if os.path.isdir(output_folder): #not output_filename:
        output_filename = generate_output_filename(filename, "_extracted" , self._output_extension, output_folder=output_folder)

        with open(filename, "rb") as timetrace_file, open(output_filename,"wb") as output_file:
            print("Start processing ...")
            print("Input filename: {0}".format(filename))
            print("Output filename: {0}".format(output_filename))
            
            header = timetrace_file.readline()
            header_str = header.decode()
            sample_rate = float(header_str.split("=")[1])
            print("File header: {0}".format(header_str))
            if CheckDecimationConditions(self._sample_rate, self._decimated_sample_rate):
                header = "Fs={0}\n".format(self._decimated_sample_rate).encode()
            output_file.write(header)
            prev_position = CurrentPosition(timetrace_file)
            file_len = LengthOfFile(timetrace_file) - prev_position

            if not isinstance(amplification,(int, float)):
                amplification = 1
                

            time_period = 1 / sample_rate
            total_time_to_convert = self._total_time_to_convert
            current_time = 0
            total_length = file_len

            stop_condition = None
            if total_time_to_convert<0:
                stop_condition = lambda t: True 
                total_length = file_len
            else: 
                stop_condition = lambda t: total_time_to_convert - t >= 0
                total_length = total_time_to_convert

            try:
                with tqdm(total = total_length) as pbar:
                    while stop_condition(current_time):
                        arr = np.load(timetrace_file)
                        arr = arr / amplification

                        if CheckDecimationConditions(self._sample_rate, self._decimated_sample_rate):
                            arr = DecimateSignal(arr, self._sample_rate, self._decimated_sample_rate)

                        np.savetxt(output_file, arr)
                        time_span = time_period * len(arr) 
                        current_time += time_span 
                        current_position = CurrentPosition(timetrace_file)
                        if total_time_to_convert < 0:
                            pbar.update(current_position - prev_position)
                        else: 
                            pbar.update(time_span)

                        prev_position = current_position

            except Exception as e:
                pass

            print("File processing finished")





def test_numpy_load():
    from tempfile import TemporaryFile
    out_file = TemporaryFile()
    l = 100
    for i in range(10):
        x = np.ones(l)
        print(x)
        np.save(out_file, x)

    out_file.seek(0)
    print("everything is written")
    print("loading")
    counter = 0
    try:
        while True:
            print("reading array: {0}".format(counter))
            res = np.load(out_file)
            print(res)
            counter+=1

    except Exception as e:
        print("Exception occured:")
        print(str(e))
        print(10*"*")
           
    print(res)
    print("end")


def perform_timetrace_extraction(**kwargs):
    #meas_data_filename = "O:\\Temp-ICS8\\Zadorozhnyi, Ihor\\10.04.2018\\Noise\\BG = 3V\\SOI#5R_Chip14_ALD_Coupling_BG=3V.dat" 
    #fn = "" 
    #e = FANS_TimetraceExtractor(filename = fn, amplification = 17200, length = -1)
    #e = FANS_TimetraceExtractor(measurement_data_file = meas_data_filename, length = -1, decimated_sample_rate = 10000)
    #e.perform_convertion()
    
    try: 
        e = FANS_TimetraceExtractor(**kwargs)
        e.perform_convertion()
    except Exception as e:
        print_error(e)

    return 0

#self._working_directory = kwargs.get("working_directory", "")
#self._sample_rate = kwargs.get("sample_rate", 500000)
#self._points_per_sample = kwargs.get("points_per_sample", 50000)
#self._total_time_to_convert = kwargs.get("length", -1)
#self._filename_to_convert = kwargs.get("filename", None)
#self._measurement_filename = kwargs.get("measurement_data_file", None)
#self._output_extension = "dat"
#self._amplification_factor = kwargs.get("amplification", None)
#self._decimated_sample_rate = kwargs.get("decimated_sample_rate", 0)

class Parameters:
    MeasurementDataFileOption = "-mf"
    SampleRateOption = "-sr"
    PointsPerShotOption = "-pps"
    LengthOption = "-l"
    FilenameOption  = "-f"
    OutputFolderOption = "-o"
    AmplificationOption = "-a"
    DecimatedSampleRateOption = "-dr"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert timetrace from binary format to readable .dat format')
    
    parser.add_argument(Parameters.MeasurementDataFileOption, metavar='measurement_data_file', type=str, nargs='?', default = "",
                    help='The name of main file where all measured data is stored')

    parser.add_argument(Parameters.SampleRateOption, metavar='sample_rate', type = int, nargs='?' , default = 500000,
                        help = 'The sample rate of data in binary file')
    
    parser.add_argument(Parameters.PointsPerShotOption, metavar='points_per_sample', type = int, nargs='?' , default = 50000,
                        help = 'Number of points in single block of data')

    parser.add_argument(Parameters.LengthOption, metavar='length', type = int, nargs='?' , default = -1,
                        help = 'The time in seconds to convert from binary file')

    parser.add_argument(Parameters.FilenameOption, metavar='filename', type = str, nargs='?' , default = "",
                        help = 'The name of file to convert. You would need to specify params for convertion')

    parser.add_argument(Parameters.AmplificationOption, metavar='amplification', type = int, nargs='?' , default = None,
                        help = 'The total amplification (Preamplified + main amplifier + PyFANS amplifier) used for the signal recording')

    parser.add_argument(Parameters.DecimatedSampleRateOption, metavar='decimated_sample_rate', type = int, nargs='?' , default = 0,
                        help = 'The sample rate to decimate to...')

    parser.add_argument(Parameters.OutputFolderOption, metavar='output_folder', type = str, nargs='?' , default = None,
                        help = 'The folder for output')

    parser.add_argument('--open', dest = 'open_folder', action= 'store_true')
    parser.set_defaults(open_folder = False)

    args = parser.parse_args()
    args = vars(args)
    type_of_program = args.get("t","console")
    m = {'mf': 'measurement_data_file','o': 'output_folder', 'sr' : 'sample_rate', 'pps' :  'points_per_sample', 'l': 'length', 'f': 'filename', 'a': 'amplification', 'dr' : 'decimated_sample_rate', 'open_folder': 'open_folder' }
    args = dict((m.get(k, k), v) for (k, v) in args.items())
    #if type_of_program == "console":
    sys.exit(perform_timetrace_extraction(**args))
    

    #perform_timetrace_extraction(**args)

    #test_numpy_load()
    #perform_timetrace_extraction()
    #sys.exit(gui())
