class Aobj(object):
    def __init__(self):
        self._name = "s"
    
    def name():
        def fget(self): return self._name
        def fset(self,value): self._name = value
        return locals()
    name = property(**name())


def main():
    a = Aobj()
##    print( Aobj.__mro__)
    for cls in Aobj.__mro__:
        for c,v in cls.__dict__.items():
            if isinstance(v,property):
                print(v.fset(a,"kldfakjs"))

    
if __name__ == "__main__":
    main()
