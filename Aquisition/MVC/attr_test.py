class A(object):
    def __init__():
        self._name = "s"
    
    def name():
        def fget(self): return self._name
        def fset(self,value): self._name = value
        return locals()
    name = property(**name())


print( A.__mro__)
for cls in A.__mro__:
    for c,v in cls.__dict__.items():
        if isinstance(v,property):
            print(c)
        

