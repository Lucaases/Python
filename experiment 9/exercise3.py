import numpy as np
m = 5
b = np.random.rand(m)
B=np.random.randint(0, 10, size=(5, 5))#行和列要保证相等,满足方阵,才能判断是否奇异矩阵
print(f"向量b=\n{b}")
print(f"矩阵B=\n{B}")
if np.linalg.det(B) != 0:#判断矩阵B是否是奇异矩阵(行列式是否为0)
  x = np.linalg.inv(B) @ b
  print(f"Bx=b的解为:\n{x}")
else:
  print("矩阵B是奇异矩阵,该方程组无解或有无穷解")
