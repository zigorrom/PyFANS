import os
import sys
import numpy as np
from scipy import stats
import pyqtgraph as pg
from tqdm import tqdm
from measurement_file_handler import MeasurementInfoFile



def import_timetrace_data(filename):
    data = np.loadtxt(filename, skiprows=1)
    return data


def generate_name(folder, basename):
    basename, ext = os.path.splitext(basename)
    path = os.path.join(folder, "{0}_timetrace_extracted{1}".format(basename,ext))
    return path


    

    




def main():
    test_data_main_file = "D:\\PhD\\Measurements\\2018\\SOI#7R_Chip15_T24\\SOI#7R_Chip15_T24_RTS_Characterization_LG.dat"
    folder = os.path.dirname(test_data_main_file)
    print(folder)

    

    meas_info = MeasurementInfoFile(test_data_main_file)
    gate_voltages = np.zeros(meas_info.row_count)
    coeffs = np.zeros_like(gate_voltages)
    normal_test_results = list()
    histograms = 
    for i in tqdm(range(meas_info.row_count)):
        current_info = meas_info.current_measurement_info
        gate_voltages[i] = current_info.gate_voltage_end
        fname = generate_name(folder, current_info.measurement_filename)
        # print("{0}, exists{1}".format(fname, os.path.isfile(fname)))
        # data = import_timetrace_data(os.path.join())
        data = import_timetrace_data(fname)
        # print(data)
        res = stats.normaltest(data)
        normal_test_results.append(res)
        k,p = res
        coeffs[i] = p
        meas_info.next_row()
    
    plt = pg.plot(gate_voltages, coeffs, title="normality test")
    

if __name__== "__main__":
    app = pg.QtGui.QApplication(sys.argv)
    main()

    # pg.plot(1,2,3,4,5)
    sys.exit(app.exec_())