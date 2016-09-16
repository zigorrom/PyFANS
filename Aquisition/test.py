import numpy as np


nch = 4
package = []
for ch in range(nch):
    package.append((123,np.empty(100, dtype=float)))

for ch in range(nch):
    for i in range(100):
        package[ch][1][i] = i*3

print(package)
