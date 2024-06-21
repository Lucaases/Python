class Rational:
    def __init__(self, p, q):
        self.numerator = p #p为分子
        if q == 0:
            raise ValueError("分母不能为0")
        self.denominator = q #q为分母
        self.simpilify()
    
    def simpilify(self):
        gcd = self.gcd(self.numerator, self.denominator)
        self.numerator //= gcd #分子除以最大公约数
        self.denominator //= gcd #分母除以最大公约数
    
    def gcd(self, a, b):#欧几里得算法求最大公约数
        while b:
            a, b = b, a % b
        return a

    def __str__(self):#返回分数的字符串表示
        return f"{self.numerator}/{self.denominator}"
    
    def __add__(self, other):#重载加法运算符
        return Rational(self.numerator * other.denominator + other.numerator * self.denominator, self.denominator * other.denominator)
    
    def __sub__(self, other):#重载减法运算符
        return Rational(self.numerator * other.denominator - other.numerator * self.denominator, self.denominator * other.denominator)
    
    def __mul__(self, other):#重载乘法运算符
        return Rational(self.numerator * other.numerator, self.denominator * other.denominator)
    
    def __truediv__(self, other):#重载除法运算符
        return Rational(self.numerator * other.denominator, self.denominator * other.numerator)
    
    def __eq__(self, other):#重载等于运算符
        return self.numerator == other.numerator and self.denominator == other.denominator
    
    def __float__(self):#返回浮点数
        return self.numerator / self.denominator
    
a=Rational(1,2)
b=Rational(1,3)
#c=Rational(1,0)  分母为0报错
print(f"有理数{a}和{b}相加:{a+b}")
print(f"有理数{a}和{b}相减:{a-b}")
print(f"有理数{a}和{b}相乘:{a*b}")
print(f"有理数{a}和{b}相除:{a/b}")
print(f"判断有理数{a}和{b}是否相等:{a==b}")