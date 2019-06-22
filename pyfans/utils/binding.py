
##To check
##https://github.com/DanielSank/observed
##https://pypi.python.org/pypi/obsub/0.2
##http://stackoverflow.com/questions/21992849/binding-a-pyqt-pyside-widget-to-a-local-variable-in-python

class Observable(object):
    def __init__(self):
##        print("init observable")
        self.__observers = {}
    
    def clearAllObservers(self):
        self.__observers.clear()

    #def refreshObservers(self):
    #    for methodName, observers in self.__observers.items():
    #        #find correcponding method and fire callbacks
    #        pass

    def addObserver(self, methodName, observer):
        s = self.__observers.setdefault(methodName, set())
        s.add(observer)

    def __fireCallbacks(self, methodName, *arg, **kw):
        if methodName in self.__observers:
            for o in self.__observers[methodName]:
                o(*arg, **kw)




def notifiable_property(name = None ,fget = None, fset = None,fdel = None, doc = None):
    def _mfset(self, value):
        _name = name
        if fget(self) != value:
            fset(self,value)
            self._Observable__fireCallbacks(_name,value, sender = self)
            
    return property(fget,_mfset,fdel,doc)


class a(Observable):
    def __init__(self):
        Observable.__init__(self)
        print("init a")
        self.__name = "dkgfashgf"

    def name():
        def fget(self): return self.__name
        def fset(self,value): self.__name = value
        return locals()
    
    name = notifiable_property("new name",**name())

    

def cb(value,sender):
    print(sender)
    print("from callback: {0}".format(value))

def main():
    val = a()
    val.addObserver("new name",cb)
    print(val.name)
    val.name = "123123"
    print("check")
    val.name = "123123"




if __name__ == "__main__":
    main()

    
