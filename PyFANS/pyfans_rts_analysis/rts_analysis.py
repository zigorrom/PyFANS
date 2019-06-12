import sys
import math
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from scipy import signal

def main():
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Basic plotting examples")
    win.resize(1000,600)
    win.setWindowTitle('pyqtgraph example: Plotting')

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)

    p1 = win.addPlot(title="Basic array plotting", colspan=3)
    timetrace_curve = p1.plot(pen="r")
    moving_normalization_curve = p1.plot(pen="y")
    filtered_timetrace = p1.plot(pen="g")


    p_psd = win.addPlot(title = "PSD", rowspan=3)
    p_psd.setLogMode(x=True, y=True)
    psd_curve = p_psd.plot(pen="r")
    psd_corrected_curve = p_psd.plot(pen="y")
    psd_smoothed_curve = p_psd.plot(pen="g")
    win.nextRow()
    p2 = win.addPlot(title="Basic array plotting", colspan=3)
    distance_curve = p2.plot(pen="r")
    cumulative_distance_curve = p2.plot(pen="g")
    diff_cumulative_distance_curve = p2.plot(pen="b")
    standard_deviation_curve = p2.plot(pen="y")
    p2.setXLink(p1)
    p2.setYLink(p1)
    win.nextRow()
    p_corr = win.addPlot(title="Correlation", colspan=3)
    p_corr.setXLink(p1)
    p_corr.setYLink(p1)
    correlation_curve_up = p_corr.plot(pen="g")
    correlation_curve_down = p_corr.plot(pen="b")
    initial_minus_diff_cumulative_curve = p_corr.plot(pen="y")
    win.nextRow()
    p3 = win.addPlot(title="Histogram ")
    histogram_curve = p3.plot(pen="r", symbol='o', brush='r', symbolBrush='r')
    
    p4 = win.addPlot(title="Histogram distance")
    histogram_distance = p4.plot(pen='g', symbol='o', brush='g', symbolBrush='g')

    p5 = win.addPlot(title="Histogram abs distance")
    histogram_abs_distance = p5.plot(pen='b', symbol='o', brush='b', symbolBrush='b')

    threshold_value = 0
    normalization_window = 10
    standard_deviation_window = 4
    transition_up = np.array([0,1,-1,0])
    transition_down = np.array([0,-1,1,0])

    fname =  "D:\\Testdata\\BG=1V\\T06_Noise_BG=1V_28_timetrace.npy"  
    # fname =  "H:\\WorkPC\\Testdata\\BG=1V\\T06_Noise_BG=1V_28_timetrace.npy"  
    #fname = "F:\\TestData\\BG=1V\\T06_Noise_BG=1V_28_timetrace.npy"
    with open(fname, 'rb') as f:
        header = f.readline()
        decoded_header = header.decode()
        frequency = None
        if decoded_header.startswith("Fs="):
            frequency = int(decoded_header[3:])
        
        print(frequency)
        timestep = 1/frequency
        maximal_transition_len = 4


        start_transition_idx = 0
        prev_sign = current_sign = 0
        cumulative_value = 0
        prev_cumulative_value = 0

        histogram_values = None
        histogram_edges = None
        histogram_bin_centers = None

        histogram_cumulative_values = None
        histogram_cumulative_edges = None
        histogram_cumulative_bin_centers = None

        histogram_diff_values = None
        histogram_diff_edges = None
        histogram_diff_bin_centers = None
        counter = 0
        prev_time = time.time()
        time_delay = 0.5

        try:
            # while True:
            while counter <1:
                print(counter)
                counter += 1 
                x = np.load(f)
                xlen = len(x)
                x_is_odd_len = ( xlen%2 == 0 )
                #print("x is odd ", x_is_odd_len)


                fft_spectrum = np.fft.fft(x)
                



                psd = np.array([x.real**2 + x.imag**2 for x in fft_spectrum])
                fft_freq = np.fft.fftfreq(psd.size, d=timestep)
                print(fft_freq)

                psd_len = x.size
                start_psd_idx = 1
                end_psd_idx = psd_len//2

                psd_positive = psd[start_psd_idx:end_psd_idx]
                fft_positive_freq = fft_freq[start_psd_idx:end_psd_idx]
                fpsd_positive = psd_positive*fft_positive_freq

                psd_positive_smoothed = signal.savgol_filter(fpsd_positive, 101, 3, delta=10)
                psd_positive_smoothed = psd_positive_smoothed / fft_positive_freq
                
                psd_change_factor = np.sqrt(psd_positive_smoothed / psd_positive)
                
                print("PSD change factor ", psd_change_factor)
                print(fft_positive_freq)

                
                coefficients = np.ones(fft_spectrum.shape)
                if x_is_odd_len:
                    coefficients[start_psd_idx:end_psd_idx] = psd_change_factor
                    coefficients[end_psd_idx] = psd_change_factor[-1]
                    coefficients[end_psd_idx+1:] = psd_change_factor[-1::-1]

                else:
                    coefficients[start_psd_idx:end_psd_idx] = psd_change_factor
                    coefficients[end_psd_idx:] =  psd_change_factor[-1::-1]
                
                # print("coefficients")
                # idx = 0
                # displen = 100
                # arrlen = coefficients.size
                # while idx < arrlen:
                #     print(coefficients[idx:idx+displen])
                #     idx+=displen
                print("coefficients", coefficients)


                fft_filtered = np.copy(fft_spectrum)
                for i, val in enumerate(fft_filtered):
                    fft_filtered[i] = val*coefficients[i]
                    if coefficients[i] == np.nan:
                        raise Exception("Nan at {0}".format(i))
                    
                
                # for idx, (x, c) in enumerate(zip(fft_spectrum, coefficients)):
                #     fft_filtered[idx]




                # fft_spectrum[start_psd_idx:end_psd_idx] = fft_spectrum[start_psd_idx:end_psd_idx]*psd_change_factor
                # fft_spectrum[end_psd_idx+1:] = fft_spectrum[end_psd_idx+1:]*psd_change_factor[-1::-1]

                # fft_spectrum /= 2

                print(fft_spectrum)
                     
                x_filtered = np.fft.ifft(fft_filtered)
                print(x_filtered )
                x_filtered = np.array([val.real for val in x_filtered])
                print(x_filtered )


                 

                filtered_timetrace.setData(x_filtered)








                





                



                # fft_freq_abs = np.abs(fft_freq)
                # f_psd = psd*fft_freq_abs
                # f_psd[0] = 1
                # min_val = np.amin(f_psd[1:])
                # psd_cor = np.zeros_like(psd)
                # psd_cor[0] = 1
                # psd_cor[1:] = (f_psd[1:] - min_val)
                # # psd_cor[1:] = (f_psd[1:] - min_val)/fft_freq_abs[1:]


                # print(psd)
                # print(fft_freq)

                psd_curve.setData(fft_positive_freq, psd_positive)
                psd_corrected_curve.setData(fft_positive_freq, fpsd_positive)
                psd_smoothed_curve.setData(fft_positive_freq, psd_positive_smoothed)
                # moving_normalization_x = np.zeros_like(x)
                # for i in range(len(x)-normalization_window):
                #     sub_array = x[i:i+normalization_window]
                #     min_val = np.amin(sub_array)
                #     max_val = np.amax(sub_array)
                #     max_min_val = max_val - min_val
                #     moving_normalization_x[i] = (x[i]-min_val)/max_min_val

                x_dist = x[1:] - x[:-1]
                timetrace_curve.setData(x)
                # distance_curve.setData(x_dist)
                # moving_normalization_curve.setData(moving_normalization_x)

                h_values_tmp = None
                if histogram_edges is None:
                    h_values_tmp, histogram_edges = np.histogram(x, bins="auto")
                    histogram_bin_centers = (histogram_edges[1:] + histogram_edges[:-1])/2
                else:
                    h_values_tmp, tmp_edges = np.histogram(x, bins=histogram_edges)
                
                if histogram_values is None:
                    histogram_values = h_values_tmp
                else:
                    histogram_values = histogram_values + h_values_tmp

                histogram_curve.setData(histogram_bin_centers, histogram_values)

                x_cumulation = np.zeros_like(x_dist)
                for idx, val in enumerate(x_dist):
                    current_sign =  math.copysign(1,x_dist[idx])
                    if current_sign != prev_sign:
                        for i in range(start_transition_idx, idx):
                            x_cumulation[i] = 0 #cumulative_value
                        
                        mid_point = int((start_transition_idx + idx)/2)
                        # x_cumulation[start_transition_idx] = cumulative_value
                        x_cumulation[mid_point] = cumulative_value

                        prev_cumulative_value = cumulative_value
                        start_transition_idx = idx
                        cumulative_value = val
                        prev_sign = current_sign
                    
                    elif idx - start_transition_idx > maximal_transition_len:
                        cumulative_value -= x_dist[start_transition_idx]
                        start_transition_idx += 1
                        cumulative_value += val

                    else:
                        cumulative_value += val
                        
                standard_deviation = np.zeros_like(x)
                for i in range(len(x)-standard_deviation_window):
                    standard_deviation[i] = np.std(x[i:i+standard_deviation_window])
                
                mean_std_deviation = np.mean(standard_deviation)
                threshold_deviation = 2 * mean_std_deviation

                for idx, val in enumerate(standard_deviation):
                    if val < threshold_deviation:
                        standard_deviation[idx] = 0
                        

                standard_deviation_curve.setData(standard_deviation)
                
                diff_x_cumulation = x_cumulation[1:] - x_cumulation[:-1]
                # initial_minus_diff_cumulative = x[:-1] - x_dist
                diff_cumulative_distance_curve.setData(diff_x_cumulation)

                
                # initial_minus_diff_cumulative = x[1:-1] - diff_x_cumulation
                # initial_minus_diff_cumulative_curve.setData(initial_minus_diff_cumulative)
                # diff_x_cumulation[np.abs(diff_x_cumulation) < threshold_value] = 0
                # min_val = np.amin(diff_x_cumulation)
                # max_val = np.amax(diff_x_cumulation)
                # mid_val = (max_val + min_val) / 2
                # # transition_up = np.array([mid_val,mid_val, max_val, min_val, mid_val,mid_val])
                # # transition_down = np.array([mid_val,mid_val, min_val, max_val, mid_val,mid_val])
                transition_up = np.array([-1,1])
                # transition_down = transition_up
                sign_diff_cumulative = np.sign(diff_x_cumulation)
                convolution_transition_up = np.convolve(sign_diff_cumulative, transition_up, mode='same')

                for i in range(len(convolution_transition_up)):
                    convolution_transition_up[i] = convolution_transition_up[i] if standard_deviation[i]>0 and abs(convolution_transition_up[i])>1 else 0
                    # convolution_transition_up[i] = convolution_transition_up[i] if abs(convolution_transition_up[i])>1 else 0


                # convolution_transition_down = np.convolve(diff_x_cumulation, transition_down, mode='same')
                correlation_curve_up.setData(convolution_transition_up)
                # correlation_curve_down.setData(convolution_transition_down)

                cumulative_distance_curve.setData(x_cumulation)
                # level_value = 0
                # initial_index = 0
                # peak_search = False
                # resulting_curve = np.zeros_like(standard_deviation)
                # for idx_diff,val in enumerate(diff_x_cumulation):
                #     diff_x_cumulation[idx_diff] = level_value 
                #     if standard_deviation[idx_diff]>0:
                #         if not peak_search:
                #             initial_index = idx_diff
                #         peak_search = True
                #     elif peak_search:
                #         # print(idx_diff)
                #         peak_search = False
                #         print("indexes")
                #         print(initial_index, idx_diff)
                #         print(diff_x_cumulation[initial_index])
                #         sub_arr = diff_x_cumulation[initial_index:idx_diff]
                #         print(sub_arr)
                #         local_max_idx = np.argmax(sub_arr) 
                #         local_min_idx = np.argmin(sub_arr)
                #         transition = (diff_x_cumulation[local_max_idx]-diff_x_cumulation[local_min_idx])/2
                #         print("min, max")
                #         print(local_min_idx, local_max_idx)
                #         index_difference = (local_max_idx - local_min_idx)
                #         # print(index_difference)
                #         if index_difference == 1:
                #             level_value = 1
                #             # level_value+=transition
                #         elif index_difference == -1:
                #             level_value = 0
                #             # level_value -=transition

                #         else:
                #             pass

                #         for i in range(initial_index, i):
                #             resulting_curve[i] = level_value
                            

                 
                      

                # correlation_curve_up.setData(resulting_curve)
                        


                    


                if histogram_cumulative_edges is None:
                    h_values_tmp, histogram_cumulative_edges = np.histogram(x_cumulation, bins="auto")
                    histogram_cumulative_bin_centers = (histogram_cumulative_edges[1:] + histogram_cumulative_edges[:-1])/2
                else:
                    h_values_tmp, tmp_edges = np.histogram(x_cumulation, bins=histogram_cumulative_edges)
                
                if histogram_cumulative_values is None:
                    histogram_cumulative_values = h_values_tmp

                else:
                    histogram_cumulative_values = histogram_cumulative_values + h_values_tmp

                histogram_distance.setData(histogram_cumulative_bin_centers, histogram_cumulative_values)

                # diff_amplitudes = diff_x_cumulation[standard_deviation>0]

                # if histogram_diff_edges is None:
                #     # h_values_tmp, histogram_diff_edges = np.histogram(diff_x_cumulation, bins=100, range=(-1.5,1.5))
                #     h_values_tmp, histogram_diff_edges = np.histogram(diff_amplitudes, bins=1000, range=(-1.5,1.5))
                #     histogram_diff_bin_centers = (histogram_diff_edges[1:] + histogram_diff_edges[:-1])/2
                # else:
                #     # h_values_tmp, tmp_edges = np.histogram(diff_x_cumulation, bins=histogram_diff_edges)
                #     h_values_tmp, tmp_edges = np.histogram(diff_amplitudes, bins=histogram_diff_edges)
                
                # if histogram_diff_values is None:
                #     histogram_diff_values = h_values_tmp
                # else:
                #     histogram_diff_values = histogram_diff_values + h_values_tmp
                
                # histogram_abs_distance.setData(histogram_diff_bin_centers, histogram_diff_values)
                # print(histogram_diff_bin_centers)
                
                QtGui.QApplication.processEvents()
                # while time.time() - prev_time < time_delay:
                #     pass


        
        

        except Exception as e:
            print("Exception reading file" )
            print(e)
        


    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()



if __name__ == "__main__":
    main()
