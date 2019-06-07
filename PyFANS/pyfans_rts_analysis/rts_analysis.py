import sys
import math
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

def main():
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Basic plotting examples")
    win.resize(1000,600)
    win.setWindowTitle('pyqtgraph example: Plotting')

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)

    p1 = win.addPlot(title="Basic array plotting", colspan=2)
    timetrace_curve = p1.plot(pen="r")
    win.nextRow()
    p2 = win.addPlot(title="Basic array plotting", colspan=2)
    distance_curve = p2.plot(pen="r")
    cumulative_distance_curve = p2.plot(pen="g")
    p2.setXLink(p1)
    win.nextRow()
    p3 = win.addPlot(title="Histogram ")
    histogram_curve = p3.plot(pen="r", symbol='o', brush='r')
    
    p4 = win.addPlot(title="Histogram distance")
    histogram_distance = p4.plot(pen='r', symbol='o', brush='r')
    threshold_value = 10
    fname =  "D:\\Testdata\\BG=1V\\T06_Noise_BG=1V_28_timetrace.npy"  
    with open(fname, 'rb') as f:
        header = f.readline()
        decoded_header = header.decode()
        frequency = None
        if decoded_header.startswith("Fs="):
            frequency = int(decoded_header[3:])
        
        print(frequency)
        timestep = 1/frequency

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
        counter = 0
        prev_time = time.time()
        time_delay = 0.5

        try:
            while True:
                print(counter)
                counter += 1 
                x = np.load(f)
                x_dist = x[1:] - x[:-1]
                timetrace_curve.setData(x)
                distance_curve.setData(x_dist)
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
                            x_cumulation[i] = cumulative_value
                        
                        prev_cumulative_value = cumulative_value
                        start_transition_idx = idx
                        cumulative_value = val
                        prev_sign = current_sign
                    
                    else:
                        cumulative_value += val
                        # if math.fabs(cumulative_value) > threshold_value:
                        #     x_cumulation[idx] = cumulative_value
                        # else:
                        #     x_cumulation[idx] = 0
                
                cumulative_distance_curve.setData(x_cumulation)

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
                
                QtGui.QApplication.processEvents()
                while time.time() - prev_time < time_delay:
                    pass


        
        # for idx, val in enumerate(x_dist):
        #     current_sign =  math.copysign(1,x_dist[idx])
        #     if current_sign != prev_sign:
        #         for i in range(start_transition_idx, idx):
        #             x_cumulation2[i] = cumulative_value

        #         start_transition_idx = idx
        #         cumulative_value = val
        #         prev_sign = current_sign
            
        #     else:
        #         cumulative_value += val
        #         x_cumulation2[idx] = cumulative_value


                #     histogram_edges = np.histogram_bin_edges(x, bins="auto")
                # if not histogram_cumulative_edges:
                #     histogram_cumulative_edges = np.histogram_bin_edges(x_dist)
                
                # time.sleep(0.1)
        #         x = np.load(f)
        #         print(x[0:10])


        except Exception as e:
            print("Exception reading file" )
            print(e)
        
        
        # x = np.load(f)
        # x_dist = x[1:] - x[:-1]
        # # print(x[:10])
        # # print(x_dist[:10])
        # p1.plot(x, pen='r', name="Initial data")
        # p2.plot(x_dist, pen='r', name="Distances")
        # h, h_edges = np.histogram(x,bins='fd')
        # h_centers = (h_edges[1:] + h_edges[:-1])/2
        # p3.plot(h_centers, h)

        # h_dist, h_dist_edges = np.histogram(x_dist,bins='fd')
        # h_dist_centers = (h_dist_edges[1:] + h_dist_edges[:-1])/2
        # p4.plot(h_dist_centers, h_dist)
        
        # # x_cumulation = np.zeros_like(x_dist)
        # x_cumulation = np.cumsum(x_dist)
        # p2.plot(x_cumulation, pen='b', name="Cumulation")
        # l = len(x_dist)

        # h_cumulation, h_cumulation_edges = np.histogram(x_cumulation,bins='fd')
        # h_cumulation_centers = (h_cumulation_edges[1:] + h_cumulation_edges[:-1])/2
        # p4.plot(h_cumulation_centers, h_cumulation)
        # x_cumulation2 = np.zeros_like(x_dist)


        
        # for idx, val in enumerate(x_dist):
        #     current_sign =  math.copysign(1,x_dist[idx])
        #     if current_sign != prev_sign:
        #         for i in range(start_transition_idx, idx):
        #             x_cumulation2[i] = cumulative_value

        #         start_transition_idx = idx
        #         cumulative_value = val
        #         prev_sign = current_sign
            
        #     else:
        #         cumulative_value += val
        #         x_cumulation2[idx] = cumulative_value

        # p2.plot(x_cumulation2, pen='g', name="Cumulation 2")

        # h_cumulation2, h_cumulation2_edges = np.histogram(x_cumulation2,bins='fd')
        # h_cumulation2_centers = (h_cumulation2_edges[1:] + h_cumulation2_edges[:-1])/2
        # p4.plot(h_cumulation2_centers, h_cumulation2, pen='g')




            

        # for k in f:
        # x = np.load(f)
        # try:
        #     while True:
        #         x = np.load(f)
        #         print(x[0:10])
        
        # except EOFError as e:
        #     print("Exception while reading data")
        #     print(e)

        # except Exception as e:
        #     print("Exception while reading data")
        #     print(e)


    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()



if __name__ == "__main__":
    main()
