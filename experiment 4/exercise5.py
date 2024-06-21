x = (1,5,9,4,3,8,6,10,52,32,64,14,12,19,20,1,8,23,80,9)
y = (7,13,41,8,7,6,9,10,12,14,16,18,20,22,24,26,28,30,32,34)#x,y为稠密向量

a = (1,0,0,0,5,9,0,6,8,0,0,2,0,7,0,0,6,0,1,0)#a为稀疏向量
b = (2,0,9,0,0,0,0,6,8,0,10,0,0,0,0,1,0,9,1,0)#b为稀疏向量

c = (1,5,3,4,5,9,8,6,8,1,3,2,4,7,7,5,6,6,1,9)#c为稠密向量


def dense_vector_add(x,y):
    list1=[]
    if len(x)!=len(y):
        raise ValueError("两向量长度不同,无法进行加法运算!!!")
    for i,j in zip(x,y):
        list1.append(i+j)
    return tuple(list1)

print("稠密向量相加:")
print(dense_vector_add(x,y))
print("\n")
print("稠密向量相乘:")

def dense_vector_multiply(x,y):
    result = 0
    if len(x)!=len(y):
        raise ValueError("两向量长度不同,无法进行乘法运算!!!")
    for i,j in zip(x,y):
        result+= i*j
    return result

print(dense_vector_multiply(x,y))
print("\n")
print("稀疏向量相加:")

def sparse_vector_add(a,b):
    list1=[]
    list2=[]
    if len(a)!=len(b):
        raise ValueError("两向量长度不同,无法进行加法运算!!!")
    
    for i in range(len(a)):
        list1.append(i)
    
    dic1=dict(zip(list1,a))
    dic11=dict((key, value) for key, value in dic1.items() if value != 0)#对稀疏向量进行去0操作
    dic2=dict(zip(list1,b))
    dic22=dict((key, value) for key, value in dic2.items() if value != 0)
    print(dic11)
    print(dic22)

    dic3={}
    
    for k1, v1 in dic11.items():
        for k2, v2 in dic22.items():
                if k1 == k2 :
                    dic3[k1] = v1 + v2 #相同键值对直接相加
                else:
                    dic3.setdefault(k2, v2) #使用setdefault函数避免覆盖现有键值对
                    dic3.setdefault(k1, v1)

    return dict(sorted(dic3.items()))

print(sparse_vector_add(a,b))
print("\n")
print("稀疏向量相乘:")

def sparse_vector_mutiply(a,b):
    list1=[]
    result=0
    if len(a)!=len(b):
        raise ValueError("两向量长度不同,无法进行乘法运算!!!")
    
    for i in range(len(a)):
         list1.append(i)
    
    dic1=dict(zip(list1,a))
    dic11=dict((key, value) for key, value in dic1.items() if value != 0)#对稀疏向量进行去0操作
    dic2=dict(zip(list1,b))
    dic22=dict((key, value) for key, value in dic2.items() if value != 0)
    print(dic11)
    print(dic22)

    for k1, v1 in dic11.items():
        for k2, v2 in dic22.items():
                if k1 == k2 and v1 != 0 and v2 != 0:
                    result+= v1 * v2 #相同键值对直接相乘累加
    
    return result
                
print(sparse_vector_mutiply(a,b))
print("\n")
print("稠密向量与稀疏向量相加:")

def dense_sparse_vector_add(c,a):#c为稠密向量,a为稀疏向量
    list1=[]
    if len(a)!=len(b):
        raise ValueError("两向量长度不同,无法进行加法运算!!!")
    
    for i in range(len(a)):
        list1.append(i)

    dic1=dict(zip(list1,a))
    dic11=dict((key, value) for key, value in dic1.items() if value != 0)#对稀疏向量进行去0操作
    dic22=dict(zip(list1,c))
    print(dic11)
    print(dic22)

    dic3={}
    
    for k1, v1 in dic11.items():
        for k2, v2 in dic22.items():
                if k1 == k2 :
                    dic3[k1] = v1 + v2 #相同键值对直接相加
                else:
                    dic3.setdefault(k2, v2) #使用setdefault函数避免覆盖现有键值对
                    dic3.setdefault(k1, v1)
    
    return dict(sorted(dic3.items()))

print(dense_sparse_vector_add(c,a))#c为稠密向量,a为稀疏向量
print("\n")
print("稠密向量与稀疏向量相乘:")

def dense_sparse_vector_mutiply(c,a):
    list1=[]
    result=0
    if len(a)!=len(b):
        raise ValueError("两向量长度不同,无法进行乘法运算!!!")
    
    for i in range(len(a)):
        list1.append(i)
    
    dic1=dict(zip(list1,a))
    dic11=dict((key, value) for key, value in dic1.items() if value != 0)#对稀疏向量进行去0操作
    dic22=dict(zip(list1,c))
    print(dic11)
    print(dic22)

    for k1, v1 in dic11.items():
        for k2, v2 in dic22.items():
                if k1 == k2 and v1 != 0 and v2 != 0:
                    result+= v1 * v2 #相同键值对直接相乘累加
    
    return result

print(dense_sparse_vector_mutiply(c,a))

#任意向量相加函数可以这样写,先判断输入向量是否为稀疏向量,若是则去0再转换成以index为键,元素值为值字典,若不是则直接转换成以index为键,元素值为值的字典,
#然后再通过items()函数将字典转换成元组方便遍历比较两字典键值对,最后再通过setdefault函数避免覆盖现有键值对,最后再通过sorted函数对字典进行排序输出.

#任意向量相乘函数可以这样写,先判断输入向量是否为稀疏向量,若是则去0再转换成以index为键,元素值为值字典,若不是则直接转换成以index为键,元素值为值的字典,
#然后再通过items()函数将字典转换成元组方便遍历比较两字典键值对,最后累加得到结果(0*N=0)