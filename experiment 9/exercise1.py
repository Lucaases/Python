import numpy as np
from scipy.linalg import toeplitz
n=200
m=500
A=np.random.normal(size=(n,m))
B=toeplitz([i for i in range(1,m+1)],[i for i in range(1,n+1)])
print(f"满足正态分布的矩阵A=\n{A}")
print(f"T型矩阵B=\n{B}")