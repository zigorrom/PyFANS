from pyfans.tests import test_binding
from pyfans.ui.voltage_widget import test_voltage_control
import pyfans.experiment.modern_fans_experiment as mfe

mfe.main()
# test_binding.main()
# test_binding.test_main_window()
# test_voltage_control()

# class test_class:
#     def __init__(self):
#         self._test = 1


#     @property
#     def test(self):
#         return self._test

#     @test.setter
#     def test(self, value):
#         self._test = value

# def test_pickle():
#     import pickle
    
    
#     t = test_class()
#     t.test = 2

#     print(pickle.dumps(t, protocol=0))


# test_pickle()