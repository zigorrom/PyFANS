import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline


class FANS_PID:
    def __init__(self, P = 0.2, I = 0.0, D= 0.0):
        self.Kp = P
        self.Ki = I
        self.Kd = D

        self._sampling_time = 0.0
        self.current_time = time.time()
        self.last_time = self.current_time

        self.set_point = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0

        self.last_error = 0.0

        self.int_error = 0.0
        self.guard = 0.0

        self.output = 0.0

        self.clear()

    def clear(self):
        self.set_point = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
        self.last_error = 0.0
        self.int_error = 0.0
        self.guard = 0.0
        self.output = 0.0

    def update(self, current_value):
        error = self.set_point - current_value
        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error
        
        if (delta_time >= self._sampling_time):
            self.p_term = self.Kp * error
            self.i_term += error * delta_time

            if self.i_term < -self.guard:
                self.i_term = -self.guard
            elif self.i_term > self.guard:
                self.i_term = self.guard

            self.d_term = 0.0
            if delta_time > 0:
                self.d_term = delta_error / delta_time

            self.last_time = self.current_time
            self.last_error = error

            self.output = self.p_term + (self.Ki * self.i_term) + (self.Kd * self.d_term)

        return self.output

    @property
    def SetPoint(self):
        return self.set_point

    @SetPoint.setter
    def SetPoint(self,value):
        assert isinstance(value, float)
        self.set_point = value

    @property
    def proportional_gain(self):
        return self.Kp

    @proportional_gain.setter
    def proportional_gain(self, value):
        assert isinstance(value, float)
        self.Kp = value

    @property
    def integral_gain(self):
        return self.Ki
    
    @integral_gain.setter
    def integral_gain(self, value):
        assert isinstance(value, float)
        self.Ki = value    

    @property
    def differencial_gain(self):
        return self.Kd
    
    @differencial_gain.setter
    def differencial_gain(self, value):
        assert isinstance(value, float)
        self.Kd = value    

    @property
    def guard_value(self):
        return self.guard
    
    @guard_value.setter
    def guard_value(self, value):
        assert isinstance(value, float)
        self.guard = value

    @property
    def sampling_time(self):
        return self._sampling_time

    @sampling_time.setter
    def sampling_time(self,value):
        assert isinstance(value, float)
        self._sampling_time = value


def test_pid(P = 0.2,  I = 0.0, D= 0.0, L=100, name = ""):
    """Self-test PID class
    .. note::
        ...
        for i in range(1, END):
            pid.update(feedback)
            output = pid.output
            if pid.SetPoint > 0:
                feedback += (output - (1/i))
            if i>9:
                pid.SetPoint = 1
            time.sleep(0.02)
        ---
    """
    pid = FANS_PID(P, I, D)

    pid.SetPoint = 0.0
    pid.sampling_time = 0.01
    pid.guard_value = 50.0

    END = L
    feedback = 0

    feedback_list = []
    time_list = []
    setpoint_list = []

    for i in range(1, END):
        output = pid.update(feedback)
        if pid.SetPoint > 0:
            feedback += (output - (1/i))
        if i>9:
            pid.SetPoint = 1.0
        time.sleep(0.02)

        feedback_list.append(feedback)
        setpoint_list.append(pid.SetPoint)
        time_list.append(i)

    time_sm = np.array(time_list)
    time_smooth = np.linspace(time_sm.min(), time_sm.max(), 300)
    feedback_smooth = spline(time_list, feedback_list, time_smooth)

    #plt.ion()
    plt.plot(time_smooth, feedback_smooth)
    plt.plot(time_list, setpoint_list)
    plt.xlim((0, L))
    plt.ylim((min(feedback_list)-0.5, max(feedback_list)+0.5))
    plt.xlabel('time (s)')
    plt.ylabel('PID (PV)')
    plt.title('TEST PID {0}'.format(name))
    plt.ylim((1-0.5, 1+0.5))
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    for i in np.arange(0,0.001, 0.0001):
        test_pid(0.6, 1.8, i, L=200, name = i)
#    test_pid(0.8, L=50)