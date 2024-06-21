def root(f, a, b):#使用二分法找到函数零点(bisection method)
  i=0
  if f(a) * f(b) > 0:#根据零点存在定理,函数连续,且两个端点的函数值同号，说明没有零点
    return "No root found!!"
  while abs(b - a) > 1e-7 :#当两端点值无限接近于0.0000001(0)时，停止迭代
    i+=1#记录迭代次数
    midpoint = (a + b) / 2
    if f(a) * f(midpoint) < 0:#函数连续,如果中点和f(a)异号，说明零点在a和midpoint之间
      b = midpoint
    else:#如果中点和f(a)同号，说明零点在midpoint和b之间
      a = midpoint
  return midpoint,i

f=lambda x: x**5+10*x**3+20*x-4#(单调函数,只有1个零点)使用Lamda表达式定义函数,简便易读
x,y=root(f,1,0)
print("使用二分法求得该函数的零点为：",x)
print("使用二分法迭代次数为：",y)

import sympy#使用sympy库方便数学运算
def root1(f0,x0):# 牛顿迭代法(Newton's method)
    x = sympy.symbols('x')
    f = eval(f0)# 将字符串转换为表达式
    f_1 = sympy.diff(f, x)# 求一阶导
    f = sympy.lambdify(x, f) # 将符号表达式转换为可调用的函数
    f_1 = sympy.lambdify(x, f_1)
    x = x0
    i=0
    while abs(f(x)) >= 1e-7:
        x=x-f(x)/f_1(x)#迭代公式
        i+=1
    if abs(f(x)) < 1e-7:
        return x,i
    else:
        return "No root found!!"

x1,y1 = root1("x**5+10*x**3+20*x-4", 0)#形参直接为字符串,函数可直接写入
print("使用牛顿迭代法求得该函数的零点为：",x1)
print("使用牛顿迭代法迭代次数为：",y1)


      


