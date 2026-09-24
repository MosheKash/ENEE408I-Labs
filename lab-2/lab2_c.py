import matplotlib.pyplot as plt
import numpy as np
import wave

# Problem 1:

wav_data = wave.open('Cafe_with_noise.wav', 'r')
framerate = wav_data.getframerate()
signal = wav_data.readframes(-1)
signal = np.frombuffer(signal, dtype=np.int16)
time = np.arange(len(signal)) / framerate

plt.figure(1)
plt.title("Problem 1: Plotting Cafe_with_noise.wav")
plt.plot(time, signal)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.show()

# Problem 2:

spectrum = np.fft.rfft(signal)
freqs = np.fft.rfftfreq(len(signal), d=1 / framerate)
magnitude = np.abs(spectrum) / len(signal)

plt.figure(1)
plt.title("Problem 2: Plotting Cafe_with_noise.wav in Frequency Domain")
plt.plot(freqs, magnitude)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.show()

# Problem 3:

# Problem 4:

# Problem 5: