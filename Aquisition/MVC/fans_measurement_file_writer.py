from datetime import timedelta
import pandas as pd
import numpy as np
from numpy.random import randn

class ExperimentWriter:
    def __init__(self):
        self._workingFolder = ""
        self._measurement_data_file = None
        self._data_file = None

    #def create_experiment(self, ):
        












def main():
    store = pd.HDFStore("store.h5")
    print(store)
    
    #del store['df']
    #del store['s']
    #del store['wp']
    np.random.seed(1234)
    times = 100000
    index = pd.date_range('1/1/2000', periods=times)
    #df = pd.DataFrame(index=index,columns=['amplitude'])
    
    nsamples = 50000
    period = 1 #sec
    current_time = 0
    df = pd.DataFrame(index=times, data=arr)
        
    for i in range(times):
        arr = np.random.random(nsamples)
        times = np.linspace(current_time, current_time+period, nsamples, False)

        print(df)
        
        
        current_time+=period
        store.put('tables/t{0}'.format(i), df)

    
    #store['df'] = df
    
    
    
    

    
    #dftd = pd.DataFrame(dict(A = pd.Timestamp('20130101'), B = [ pd.Timestamp('20130101') + timedelta(days=i,seconds=10) for i in range(10) ]))

    #dftd['C'] = dftd['A']-dftd['B']

    #print(dftd)

    #store.append('dftd',dftd,data_columns=True)

    #print(store.select('dftd',"C<'-3.5D'"))
    print(store)
    store.close()

if __name__ == "__main__":
    main()