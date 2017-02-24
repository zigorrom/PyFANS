from datetime import timedelta
import pandas as pd
import numpy as np

class ExperimentWriter:
    def __init__(self):
        self._workingFolder = ""
        self._measurement_data_file = None
        self._data_file = None

    #def create_experiment(self, ):
        












def main():
    store = pd.HDFStore("store.h5")
    np.random.seed(1234)
    index = pd.date_range('1/1/2000', periods=8)
    s = pd.Series(randn(5), index=['a', 'b', 'c', 'd', 'e'])
    df = pd.DataFrame(randn(8, 3), index=index,columns=['A', 'B', 'C'])
    wp = pd.Panel(randn(2, 5, 4), items=['Item1', 'Item2'],
                  major_axis=pd.date_range('1/1/2000', periods=5),
                  minor_axis=['A', 'B', 'C', 'D'])
    store['s'] = s
    store['df'] = df
    store['wp'] = wp
    print(store.root.wp._v_attrs.pandas_type)
    print(store)
    print(store['df'])

    
    #dftd = pd.DataFrame(dict(A = pd.Timestamp('20130101'), B = [ pd.Timestamp('20130101') + timedelta(days=i,seconds=10) for i in range(10) ]))

    #dftd['C'] = dftd['A']-dftd['B']

    #print(dftd)

    #store.append('dftd',dftd,data_columns=True)

    #print(store.select('dftd',"C<'-3.5D'"))
    store.close()

if __name__ == "__main__":
    main()