import numpy as np
import py_expression_eval as py_eval

class PatchedParser(py_eval.Parser):
    
    def __init__(self):
        super().__init__()
        self.ops1.update({
            "Sv": self.voltageSpectralDensity
        })

    def importFunc(self, fname):
        data = np.loadtxt(fname,delimiter='\t', skiprows=1)
        print("importing data")

        return data
        
    def voltageSpectralDensity(self, args):# fname, atFrequency=None):
        print("calculating Sv")
        freqCol = 0
        fn = None
        freq = 1

        if isinstance(args ,(list, tuple)):
            if len(args)==2:
                fn = args[0]
                freq = args[1]
            else:
                raise ValueError("Unknown arguments")
        
        elif isinstance(args, str):
            fn = args
            freq = 1

        else:
            raise ValueError("Unknown arguments")
            
        data = self.importFunc(fn)
        idx = np.where(data[:,freqCol]==freq)
        return data[idx,1][0][0]
        # return 0
        
        

    


def testParser():
    fname = ""
    p = PatchedParser()
    expr = p.parse("Sv(x)")
    print(expr.simplify({}).toString())
    print(expr.variables())
    print(expr.evaluate({"x":fname}))

    expr = p.parse("Sv(x,y)")
    print(expr.simplify({}).toString())
    print(expr.variables())
    print(expr.evaluate({"x":fname, "y":4}))
    # print(p.importFunc(fname))

if __name__ == "__main__":
    print("Lets start")
    testParser()
    