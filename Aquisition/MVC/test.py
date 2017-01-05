class A:
    def __init__(self):
        self._val = 10
        print(type(self))
    def setVal(self,val):
        self._val = val

    def fetVal(self):
        return self._val

def parrot(voltage, state='a stiff', action='voom'):
    print("-- This parrot wouldn't", action, end=' ')
    print("if you put", voltage, "volts through it.", end=' ')
    print("E's", state, "!")

def main():     
    d = {"voltage": "four million", "state": "bleedin' demised", "action": "VOOM"}
    parrot(**d)

    
if __name__ == "__main__":
    main()
