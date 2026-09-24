import numpy as np
from scipy.linalg import solve
from scipy.fft import fft, fftfreq
from scipy.optimize import minimize
import matplotlib.pyplot as plt


A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
 
solution = solve(A, b)
print("Problem 1:")
print("x =", solution[0])
print("y =", solution[1])

def f(x):
    return x[0] ** 2 + 2 * x[0]
 
 
result = minimize(f, x0 = np.array([0.0]))
print("\nProblem 2:")
print("Minimum value =", result.fun)
print("At x =", result.x[0])

fs = 1000
n = 2000
x = np.arange(n) / fs
 
f = np.sin(100 * np.pi * x) + 0.5 * np.sin(160 * np.pi * x)
 
yf = fft(f)
xf = fftfreq(n, 1 / fs)
 
plt.figure(figsize = (10, 5))
plt.plot(xf[:n // 2], np.abs(yf[:n // 2]) * 2 / n)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Problem 4: Frequency Response")
plt.grid(True)
plt.show()
