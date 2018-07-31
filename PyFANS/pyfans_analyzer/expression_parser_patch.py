import numpy as np
import py_expression_eval as py_eval

class PatchedParser(py_eval.Parser):
    
    def __init__(self):
        super().__init__()
        self.ops1.update({
            "Sv": self.voltageSpectralDensity,
            "Si": self.currentSpectralDensity,
            "Sinorm": self.normalizedCurrentSpectralDensity

        })

    def importFunc(self, fname):
        data = np.loadtxt(fname,delimiter='\t', skiprows=1)
        # print("importing data")

        return data

    # def sv_func_optimized(self, filename, frequency):    
    def sv_func(self, filename, frequency):
        delimiter = "\t"
        freq_type = type(frequency)

        with open(filename) as f:
            f.readline()

            for i, line in enumerate(f):
                
                freq, sv = line.split(delimiter, 1)
                if freq_type(freq) == frequency:
                    return float(sv)
        return None


    def sv_func_old(self, filename, frequency):
        # print(filename)
        # print(frequency)
        freqCol = 0
        data = self.importFunc(filename)
        idx = np.where(data[:,freqCol]==frequency)
        return data[idx,1][0,0]

    def normalizedCurrentSpectralDensity(self, args):
        if isinstance(args, list):
            if len(args)>3:
                Current = args.pop()
                if not isinstance(Current, (int, float)):
                    TypeError("Unexpected resistance data type")

                Resistance = args.pop() 
                if not isinstance(Resistance, (int, float)):
                    TypeError("Unexpected resistance data type")
                
                csqr = Current*Current
                rsqr = Resistance*Resistance
                rc = rsqr*csqr
                sv = self.voltageSpectralDensity(args)
                return sv/rc
            else:
                ValueError("Not enough arguments") 
        else:
            ValueError("Not enough arguments") 

    def currentSpectralDensity(self, args):
        if isinstance(args, list):
            if len(args)>2:
                Resistance = args.pop() 
                if not isinstance(Resistance, (int, float)):
                    TypeError("Unexpected resistance data type")

                rsqr = Resistance*Resistance
                sv = self.voltageSpectralDensity(args)
                return sv/rsqr
            else:
                ValueError("Not enough arguments") 
        else:
            ValueError("Not enough arguments") 

    def voltageSpectralDensity(self, args):# fname, atFrequency=None):
        # print("calculating Sv")
        # print(args)
        # fn = None
        # freq = 1
        if not isinstance(args, list):
            raise ValueError("Unknown arguments")

        if len(args)==2:
            # fn = args[0]
            freq = args[1]
            if not isinstance(freq, (int, float)):
                raise ValueError("Unknown arguments")
                
            if isinstance(args[0], (list, np.ndarray)):
                result = np.array([self.sv_func(fn, freq) for fn in args[0]])
                return result
            
        elif len(args)>2:
            freq = args.pop()
            if not isinstance(freq, (int, float)):
                raise ValueError("Unknown arguments")

            result = np.array([self.sv_func(fn, freq) for fn in args])
            return result

        else:
            raise ValueError("Unknown arguments")
            
           



        # if isinstance(args ,(list, tuple, np.ndarray)):

        #     if len(args)==2:
        #         if isinstance(args[0], str) and isinstance(args[1], (int,float)):
        #             fn = args[0]
        #             freq = args[1]
        #             return self.sv_func(fn, freq)
        #         elif isinstance(args[0], (list, tuple, np.ndarray)) and isinstance(args[1], (int,float)):
        #             result = np.array([self.sv_func(fn, args[1]) for fn in args[0]])
        #             # result = np.apply_along_axis(self.sv_func, 0, args[0], args[1])
        #             return result
        #         else:
        #             return [self.sv_func(args[0],freq),self.sv_func(args[1], freq)]
            
        #     elif len(args) > 2:
        #         result = np.array([self.sv_func(fn, freq) for fn in args])
        #         # result = np.apply_along_axis(self.sv_func, 0, args, freq)
        #         return result
            
        #     elif isinstance(args, np.ndarray):
        #         result = np.array([self.sv_func(fn, freq) for fn in args])
        #         # result = np.apply_along_axis(self.sv_func, 0, args, freq)
        #         return result

        #     elif isinstance(args, str):
        #         return self.sv_func(args, freq)
                
        #     else:
        #         raise ValueError("Unknown arguments")
        

        # elif isinstance(args, str):
        #     freq = 1
        #     return self.sv_func(args, freq)

        # else:
        #     raise ValueError("Unknown arguments")

        
        # data = self.importFunc(fn)
        # idx = np.where(data[:,freqCol]==freq)
        # return data[idx,1][0][0]
        # return 0

     
        

    


def testParser():
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ExperimentDataAnalysis")
    app.setStyle("cleanlooks")

    fname = QtGui.QFileDialog.getOpenFileName()
    # fileDialog.show()
    arr = np.arange(5)
    fnames = [fname,fname,fname,fname] #np.repeat(fname,4)
    npfnames = np.repeat(fname,4)
    # print(fnames)
    # fname = ""
    # p = PatchedParser()
    # expr = p.parse("Sv(x,y)")
    # print(expr.simplify({}).toString())
    # print(expr.variables())
    # print(expr.evaluate({"x":npfnames,"y":1}))

    p = PatchedParser()
    expr = p.parse("Sv(x,1)/16")
    print(expr.simplify({}).toString())
    print(expr.variables())
    print(expr.evaluate({"x":npfnames}))#, "y": 1}))

    p = PatchedParser()
    expr = p.parse("Si(x,y,z)")
    print(expr.simplify({}).toString())
    print(expr.variables())
    print(expr.evaluate({"x":fnames, "y":1, "z":2}))

    p = PatchedParser()
    expr = p.parse("Sinorm(x,y,z,c)")
    print(expr.simplify({}).toString())
    print(expr.variables())
    print(expr.evaluate({"x":fnames, "y":1, "z":2, "c":2}))


    # p = PatchedParser()
    # expr = p.parse("abs(x)")
    # print(expr.simplify({}).toString())
    # print(expr.variables())
    # print(expr.evaluate({"x":arr}))

    # expr = p.parse("Sv(x,y)")
    # print(expr.simplify({}).toString())
    # print(expr.variables())
    # print(expr.evaluate({"x":fname, "y":4}))
    # # print(p.importFunc(fname))
    # app.quit()
    return app.quit()
    # return app.exec_()

if __name__ == "__main__":
    import sys
    print("Lets start")
    sys.exit(testParser())
    