#1.is_prime=lambda n: n>1 and all(n%i!=0 for i in range(2,int(n**0.5)+1)) 
#判断质数,all()函数用于判断给定的可迭代参数iterable中的所有元素是否都为True,如果是返回True,否则返回False
#当n>1且n不能被2到n的平方根之间的数整除时,返回True,否则返回False
#2.prime_list1=lambda n: [i for i in range(2,n+1) if is_prime(i)]
prime_list=lambda n: [i for i in range(2,n+1) if i>1 and all(i%j!=0 for j in range(2,int(i**0.5)+1))]
#返回2到n之间的质数,[]表示返回一个列表,即列表推导式
print(f"返回一个包含2到11之间的质数的列表:{prime_list(11)}")
print(f"返回一个包含2到23之间的质数的列表:{prime_list(23)}")
