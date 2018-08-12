import numpy as np
from PyQt4.QtCore import QObject, pyqtSignal

class Transformation(QObject):
    sigTransformChanged = pyqtSignal()
    def __init__(self):
        super().__init__()

    def convert(self, x, y):
        return x,y

    def convert_back(self, x,y):
        return x,y

class MultipliedXYTransformation(Transformation):
    def __init__(self, **kwargs):
        super().__init__()
        self._isMultiplied = kwargs.get("is_multiplied", False)

    @property
    def is_multiplied(self):
        return self._isMultiplied

    @is_multiplied.setter
    def is_multiplied(self, value):
        if self._isMultiplied == value:
            return 
    
        self._isMultiplied = value
        self.sigTransformChanged.emit()
    

    def convert(self, x, y):
        if self.is_multiplied:
            return x, np.multiply(x,y)
        else:
            return x,y

    def convert_back(self, x,y):
        if self.is_multiplied:
            return x, np.divide(y,x)
        else:
            return x,y