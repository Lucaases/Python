i=0#全局变量,记录递归次数
j=0
def recursive_root(a,b):#使用递归法找到函数零点(二分法递归版)
    global i
    if abs(b - a) < 1e-7:#递归法有风险,由于有可能出现无限递归,当递归次数过多时,会出现栈溢出(输入函数连续,必须与x轴有交点)
        return (a+b)/2,i
    else:
        if f(a) * f((a+b)/2) < 0:#函数连续,如果中点和f(a)异号，说明零点在a和midpoint之间
            i+=1
            return recursive_root(a, (a+b)/2)
        else:#如果中点和f(a)同号，说明零点在midpoint和b之间
            i+=1
            return recursive_root((a+b)/2, b) 
f=lambda x: x**5+10*x**3+20*x-4
x,y=recursive_root(0,1)
print("使用二分法递归求得该函数的零点为:",x)
print("使用二分法递归次数为:",y)

import sympy#使用sympy库方便数学运算
def recursive_root1(f0,x0):#使用递归法找到函数零点(牛顿迭代法递归版)
    x = sympy.symbols('x')
    f = eval(f0)# 将字符串转换为表达式
    f_1 = sympy.diff(f, x)# 求一阶导
    if f_1==0:
        return "No root found!!"
    f = sympy.lambdify(x, f) # 将符号表达式转换为可调用的函数
    f_1 = sympy.lambdify(x, f_1)
    def recursive_root2(x0):
        global j
        if abs(f(x0)) < 1e-7:#递归法有风险,由于有可能出现无限递归,当递归次数过多时,会出现栈溢出(输入函数连续,必须与x轴有交点)
            return x0,j
        else:
            j+=1
            return recursive_root2(x0-f(x0)/f_1(x0))
    return recursive_root2(x0)
x1,y2=recursive_root1("x**5+10*x**3+20*x-4", 0)
print("使用牛顿迭代法递归求得该函数的零点为:",x1)
print("使用牛顿迭代法递归次数为:",y2)