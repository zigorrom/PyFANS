
##To check
##https://github.com/DanielSank/observed
##https://pypi.python.org/pypi/obsub/0.2
##http://stackoverflow.com/questions/21992849/binding-a-pyqt-pyside-widget-to-a-local-variable-in-python

class Observable(object):
    def __init__(self):
        self.__observers = {}

    def addObserver(self, methodName, observer):
        s = self.__observers.setdefault(methodName, set())
        s.add(observer)

    def __fireCallbacks(self, methodName, *arg, **kw):
        if methodName in self.__observers:
            for o in self.__observers[methodName]:
                o(*arg, **kw)


def property_changed_event(prop):
    def _modified_property(obj,*arg,**kw):
        prop(obj,*arg,**kw)
        obj._Observable.__fireCallbacks(prop.__name__,*arg,**kw)

    return _modified_property


p = 

    
    
