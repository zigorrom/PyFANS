import numpy as np

package = []
length = 100
for i in range(4):
    package.append(((1,2,3,),np.empty(length,dtype = float)))

for i in range(4):
    for j in range(length):
        package[i][1][j] = 2
        
print(package)
    
