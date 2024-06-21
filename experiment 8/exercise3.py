k=20
k1=10
import random
i = random.sample(range(1, k+1), k1)#random.sample()函数用于从指定序列中随机获取指定长度的片断,返回列表
j = random.sample(range(1, k+1), k1)
print(f"随机从1到{k}中抽取生成{k1}个数作为新列表i:{i}")
print(f"随机从1到{k}中抽取生成{k1}个数作为新列表j:{j}"+"\n")
is_prime=lambda n: n>1 and all(n%i!=0 for i in range(2,int(n**0.5)+1)) #上一题的用lambda表达式写的判断质数函数
prime_i=[]
prime_j=[]
for a in i:
    if is_prime(a):
        prime_i.append(a)
for b in j:
    if is_prime(b):
        prime_j.append(b)
list1=[[m,n] for m in i for n in j ]
list2=[[m,n] for m in i for n in j if n>m ]
list3=[m+n for m in i for n in j if m>n and is_prime(m) and is_prime(n)]
print(f"包含(i,j)的列表:{list1}"+"\n")
print(f"包含(i,j)且j>i的列表:{list2}"+"\n")
print(f"包含i列表中所有质数列表:{sorted(prime_i)}")
print(f"包含j列表中所有质数列表:{sorted(prime_j)}")
print(f"包含i序列中更大的质数与j序列中的质数的和的列表:{sorted(list3)}")