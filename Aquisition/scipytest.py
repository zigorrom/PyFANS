from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

fs = 500e3
N = 10e6
nchan = 4
amp = 2*np.sqrt(2)
freq = 123400
noise_power = 0.001 * fs / 2
time = np.arange(nchan*N) / fs
x = amp*np.sin(2*np.pi*freq*time)
x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
x = np.reshape(x,(nchan,N))
print(x)
f, Pxx_den = signal.periodogram(x, fs)
print(f)
print(Pxx_den)
plt.semilogy(f, Pxx_den[0])
plt.semilogy(f, Pxx_den[1])
plt.semilogy(f, Pxx_den[2])
plt.semilogy(f, Pxx_den[3])
plt.ylim([1e-7, 1e2])
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()
