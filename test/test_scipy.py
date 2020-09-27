import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import scipy.fftpack


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    print low , high , "test"
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


# Filter requirements.
order = 4
fs = 100.0       # sample rate, Hz
lowcut = 0.8
highcut = 3.8

# Get the filter coefficients so we can check its frequency response.
b, a = butter_bandpass(lowcut, highcut, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(lowcut, 0.5*np.sqrt(2), 'ko')
plt.plot(highcut, 0.5*np.sqrt(2), 'ko')
plt.axvline(lowcut, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()


# Demonstrate the use of the filter.
# First make some data to be filtered.
T = 30.0         # seconds
n = int(T * fs) # total number of samples
t = np.linspace(0, T, n, endpoint=False)
# "Noisy" data.  We want to recover the 1.2 Hz signal from this.
data = np.sin(1.2*2*np.pi*t) + 1.5*np.cos(9*2*np.pi*t) + 0.5*np.sin(12.0*2*np.pi*t)
datafile = open('dat_ired.txt', 'r')
datafile2 = open('dat_red.txt', 'r')
raw_dat_ired =  map(float, datafile.readline().split(","))
raw_dat_red = map(float, datafile2.readline().split(","))
print len(raw_dat_ired)
# Filter the data, and plot both the original and filtered signals.
y = butter_bandpass_filter(raw_dat_ired, lowcut, highcut, fs, order)
y2 = butter_bandpass_filter(raw_dat_red, lowcut, highcut, fs, order)



print len(y)
plt.subplot(2, 1, 2)
#plt.plot(t, raw_dat_ired, 'b-', label='raw_dat_ired')
#plt.plot(t, raw_dat_red, 'r-', label='raw_dat_red')
#plt.plot(t, y, 'g-', linewidth=2, label='ired filtered data')
plt.plot(t, y2/4096.0, 'y-', linewidth=2, label='red filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
plt.show()