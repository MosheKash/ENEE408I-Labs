import numpy as np

# Problem 3:

a = np.array([1, 2, 3, 4])
print(f"Problem 3: {a}")

# Problem 4:

one = np.ones([3, 4])
zero = np.zeros([4, 3])

print(f"Problem 4:\n\n{one}\n\n{zero}\n")

# Problem 5:

A = np.arange(6).reshape(2,3)
B = np.arange(12).reshape(3,4)

result = np.matmul(A,B)

print(f"Problem 5:\n{result}\n")

# Problem 6:

mat = np.array([[3, 1],[1, 2]])

val, vec = np.linalg.eig(mat)

print(f"Problem 6:\n\nEigenvalues: {val}\n\nEigenvectors:\n{vec}")