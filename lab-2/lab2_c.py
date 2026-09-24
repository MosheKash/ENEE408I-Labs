import matplotlib.pyplot as plt
import numpy as np
import wave
import os

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

print(f"Problem 2: There is a very large spike located around {np.round(freqs[np.argmax(magnitude)])} hz. This is the noise in question that is removed. The next problem will apply a lowpass filter to remove the noise spike. Will assign the cutoff frequency a little bit lower, at 90% of the frequency, so at {np.round(freqs[np.argmax(magnitude)] * 0.9)}")

plt.figure(1)
plt.title("Problem 2: Plotting Cafe_with_noise.wav in Frequency Domain")
plt.plot(freqs, magnitude)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.show()

# Problem 3:

cutoff = freqs[np.argmax(magnitude)] * 0.9
spectrum[freqs > cutoff] = 0
filtered = np.fft.irfft(spectrum, n=len(signal))

print(f"Problem 3: The filtered audio clip has been saved to filtered.wav")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "filtered.wav")

with wave.open(out_path, 'wb') as out:
    out.setnchannels(wav_data.getnchannels())
    out.setsampwidth(wav_data.getsampwidth())
    out.setframerate(framerate)
    out.writeframes(np.clip(filtered, -32768, 32767).astype(np.int16).tobytes())

plt.figure(2, figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.title("Filtered Signal: Time Domain")
plt.plot(time, filtered)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.subplot(2, 1, 2)
plt.title("Filtered Signal: Frequency Domain")
plt.plot(freqs, np.abs(np.fft.rfft(filtered)) / len(filtered))
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

plt.tight_layout()
plt.show()