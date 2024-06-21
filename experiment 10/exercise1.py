import numpy as np
import scipy.optimize as op

xi = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])#x数据源
yi = np.array([2.3201, 2.6470, 2.9707, 3.2885, 3.60085, 3.9090, 4.2147, 4.5191, 4.8232, 5.1275])#y数据源

def fun(p,x,y):#定义拟合函数(模型)
    a=p[0]
    b=p[1]
    c=p[2]
    d=p[3]
    return a*x+b*x**2*np.exp(-c*x)+d-y

result1=op.least_squares(fun,[0,0,0,0],args=(xi,yi),method="trf",ftol=1e-12,gtol=1e-12,xtol=1e-12)#Trust Region Reflective算法
result2=op.least_squares(fun,[0,0,0,0],args=(xi,yi),method="lm",ftol=1e-12,gtol=1e-12,xtol=1e-12)#Levenberg-Marquardt算法
result3=op.least_squares(fun,[0,0,0,0],args=(xi,yi),method="dogbox",ftol=1e-12,gtol=1e-12,xtol=1e-12)#Dogleg和Box结合算法
print(f"使用Trust Region Reflective算法:\n{result1.x}")
print(f"使用Levenberg-Marquardt算法:\n{result2.x}")
print(f"使用Dogleg和Box结合算法:\n{result3.x}")