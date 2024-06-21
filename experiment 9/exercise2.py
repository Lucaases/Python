import numpy as np
A=np.random.normal(size=(3,3))
B=np.random.normal(size=(3,3))
print(f"A={A}")
print(f"B={B}")
print(f"A加上A的转置=\n{A+A.T}")
print(f"A乘以A的转置=\n{A@A.T}")
print(f"A的转置乘以A=\n{A.T@A}")
print(f"A乘以B=\n{A@B}")

def compute(lamda):
    return A*(B-lamda*np.eye(3))

print(f"当lamda=3时,A(B-lambda I)=\n{compute(3)}")

