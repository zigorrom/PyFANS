import numpy as np
from itertools import zip_longest

filename = "F:\\Noise\\T=300K\\t16-100x100nm_noise_4.dat"

time, current = np.loadtxt(filename).transpose()
current_len = len(current)
print(current_len)


ft = np.fft.rfft(current)
fft_len = len(ft)
freq= np.fft.rfftfreq(fft_len, time[0])
print(fft_len)

multiplied = np.multiply(ft,2)

new_current = np.fft.ifft(ft)
print(len(new_current))
##print(new_current)

rt  = "F:\\Noise\\T=300K\\t16-100x100nm_noise_4_res.dat"
np.savetxt(rt,np.vstack((freq,ft)).transpose())
