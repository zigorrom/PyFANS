class A:
    def __init__(self):
        self._val = 10
    def setVal(self,val):
        self._val = val

    def fetVal(self):
        return self._val

def main():
    a= A()
    b = a
    print(b.fetVal())
    a.setVal(1234)
    print(b.fetVal())
    
if __name__ == "__main__":
    main()
