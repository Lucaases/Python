import numpy as np
def find_closest(Z, A):
  d = np.abs(A - Z)#
  closest_idx = np.argmin(d)#返回最小值的索引
  return A[closest_idx]
A = np.array([1.2, 3.5, 0.8, 2.1])
Z = 4
closest_value = find_closest(Z, A)
print(f"最接近{Z}的值是{closest_value}")
