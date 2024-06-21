from scipy.optimize import fmin
import numpy as np
from matplotlib import pyplot as plt 
result = fmin(lambda x:(-1)*np.sin(x - 2)**2 * np.exp(-x**2),0,xtol=1e-12)
result1 = fmin(lambda x:np.sin(x - 2)**2 * np.exp(-x**2),0,xtol=1e-12)
result2 = fmin(lambda x:np.sin(x - 2)**2 * np.exp(-x**2),1,xtol=1e-12)
print(f"f(x)在x={list(result).__str__()}取得最大值为0.911685,在x={list(result1).__str__()}和x={list(result2).__str__()}取得最小值为0")

#使用matplotlib绘制f(x)的图像
x = np.linspace(-20,20,500)
y = np.sin(x-2) * np.sin(x-2) * np.exp(-x**2)
plt.figure(1)
plt.xlabel("x")
plt.ylabel("y")
plt.ylim(-0.1, 1)
plt.title(r"$f(x) = sin^2(x-2)e^{-x^2}$")
plt.plot(x,y)
plt.show()