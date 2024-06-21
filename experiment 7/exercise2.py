class Densevector:
  def __init__(self, data):#data为列表
    self.data = data

  def __str__(self):#返回向量的字符串表示
    return f"{self.data}"

  def __add__(self, other):#重载加法运算符
    if not isinstance(other, (Sparsevector,Densevector)):#使用isinstance函数判断other是否为向量
      raise TypeError("只能相加向量")
    if isinstance(other, Sparsevector):
      other = Densevector([other.data.get(i, 0) for i in range(len(self.data))])#使用get函数找到other中的非零元素
    return Densevector([x + y for x, y in zip(self.data, other.data)])

  def __mul__(self, other):#重载乘法运算符
    if not isinstance(other, (int, float, Densevector,Sparsevector)):
      raise TypeError("只能乘以整数、浮点数或向量")
    if isinstance(other, (int, float)):#判断other是否为整数或浮点数
        return Densevector([x * other for x in self.data])
    if isinstance(other, Densevector):#判断other是否为稠密向量
        return sum(x * y for x, y in zip(self.data, other.data))
    if isinstance(other, Sparsevector):#判断other是否为稀疏向量
        other = Densevector([other.data.get(i, 0) for i in range(len(self.data))])#使用get函数找到other中的非零元素
        return sum(x * y for x, y in zip(self.data, other.data))

class Sparsevector:
  def __init__(self, data):#data为字典
    self.data = {key:value for key, value in data.items() if value != 0}

  def __str__(self):#返回向量的字符串表示
    return f"{self.data}"

  def __add__(self, other):#重载加法运算符
    if not isinstance(other, (Sparsevector,Densevector)):
      raise TypeError("只能相加向量")
    def add_fn(a, b):#定义一个函数，用于两个数相加
        if a is None:
            return b
        if b is None:
            return a
        return a + b
    if isinstance(other, Densevector):
      other = Sparsevector({i: other.data[i] for i in range(len(other.data))})#
    new_data = {key: add_fn(self.data.get(key), other.data.get(key)) for key in set(self.data.keys()) | set(other.data.keys())}#使用set函数找到两个向量中的非零元素,|为并集运算符
    return Sparsevector(new_data)

  def __mul__(self, other):#重载乘法运算符
    if not isinstance(other, (int, float, Densevector,Sparsevector)):
      raise TypeError("只能乘以整数、浮点数或向量")
    if isinstance(other, (int, float)):
        return Sparsevector({key:value * other for key, value in self.data.items()})
    if isinstance(other, Densevector):
        other = Sparsevector({i:other.data[i] for i in range(len(other.data))})
        return sum(self.data.get(i, 0) * other.data.get(i, 0) for i in set(self.data.keys()) & set(other.data.keys()))#使用get函数找到两个向量中的非零元素,&为交集运算符
    if isinstance(other, Sparsevector):
        return sum(self.data.get(i, 0) * other.data.get(i, 0) for i in set(self.data.keys()) & set(other.data.keys()))

a=Densevector([8,4,3,9])#稠密向量
b=Sparsevector({0:1,1:2,2:3})#稀疏向量
print(f"稠密向量:{a}")
print(f"稀疏向量:{b}")
print(f"稠密向量相加:{a+a}")
print(f"稀疏向量相加:{b+b}")
print(f"稠密向量相乘:{a*a}")
print(f"稀疏向量相乘:{b*b}")
print(f"稠密向量和稀疏向量相加结果:{a+b}")
print(f"稀疏向量和稠密向量相加结果:{b+a}")
print(f"稠密向量和稀疏向量相乘结果:{a*b}")
print(f"稀疏向量和稠密向量相乘结果:{b*a}")
print(f"稠密向量和浮点数相乘结果:{a*1.5}")
print(f"稀疏向量和浮点数相乘结果:{b*1.5}")
print(f"稠密向量和整数相乘结果:{a*2}")
print(f"稀疏向量和整数相乘结果:{b*2}")



