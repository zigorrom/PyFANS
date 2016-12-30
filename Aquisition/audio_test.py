import math
import pyaudio
from scipy import signal
import numpy as np

#sudo apt-get install python-pyaudio

PyAudio = pyaudio.PyAudio

#See http://en.wikipedia.org/wiki/Bit_rate#Audio
BITRATE = 320000 #number of frames per second/frameset.      

FREQUENCY = 2 #Hz, waves per second, 261.63=C4-note.
LENGTH = 1 #seconds to play sound

if FREQUENCY > BITRATE:
    BITRATE = FREQUENCY+100

NUMBEROFFRAMES = int(BITRATE * LENGTH)
RESTFRAMES = NUMBEROFFRAMES % BITRATE

t = np.linspace(0,LENGTH,NUMBEROFFRAMES)
WAVEDATA = signal.square(2*np.pi*FREQUENCY*t)
#WAVEDATA = ''    
#
#for x in range(NUMBEROFFRAMES):
# WAVEDATA = WAVEDATA+chr(int(math.sin(x/((BITRATE/FREQUENCY)/math.pi))*127+128))    
#
#for x in range(RESTFRAMES): 
# WAVEDATA = WAVEDATA+chr(128)

p = PyAudio()
stream = p.open(format = p.get_format_from_width(1), 
                channels = 1, 
                rate = BITRATE, 
                output = True)

stream.write(WAVEDATA)
stream.stop_stream()
stream.close()
p.terminate()
