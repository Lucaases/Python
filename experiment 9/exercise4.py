import numpy as np
A=np.random.normal(size=(10,10))
B=np.random.normal(size=(10,10))
A_norm = np.linalg.norm(A,'fro')#F范数
B_norm = np.linalg.norm(B,np.inf)#无穷范数
print(f"该矩阵的Frobenius范数为:{A_norm}")
print(f"该矩阵的无穷范数为:{B_norm}")