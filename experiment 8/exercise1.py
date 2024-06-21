class Iterator_prime:#迭代器类
    def __init__(self, n):
        if not isinstance(n, int):
            raise TypeError("n必须为整数")
        if n < 1:
            raise ValueError("n必须大于0")
        self.n = n
        self.i = 1#迭代次数
        self.prime = 1#迭代初始值

    def __iter__(self):#返回迭代器对象
        return self

    def __next__(self):#返回下一个元素,如果没有下一个元素则抛出StopIteration异常
        if self.i > self.n:
            raise StopIteration
        else:
            self.i += 1
            while True:
                self.prime += 1
                for i in range(2, int(self.prime**0.5+1)):
                    if self.prime % i == 0:
                        break
                else:
                    break
            return self.prime
        
def iterator_prime(n):#生成器函数,相比迭代器类更加简洁,且一次生成一个元素,内存占用更小
    if not isinstance(n, int):
        raise TypeError("n必须为整数")
    if n < 1:
        raise ValueError("n必须大于0")
    i = 1#迭代次数
    prime = 1#迭代初始值
    while i <= n:
        i += 1
        while True:
            prime += 1
            for j in range(2, int(prime**0.5+1)):
                if prime % j == 0:
                    break
            else:
                break
        yield prime

a=[]       
b=iterator_prime(10)
for i in Iterator_prime(10):
    a.append(i)
 
print(f"使用迭代器类实现{a}")
print(f"使用生成器函数实现{list(b)}")