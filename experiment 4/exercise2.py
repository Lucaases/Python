x = (1,5)
y = (7,13)#n没有给出,但肯定是确定的,因为元组是静态的,不可变的,不能随意添加或删除元素

def L2_compution(x,y):#欧式距离,两点之间直线距离
    dis = 0
    for i,j in zip(x,y):
        dis+=(i-j)**2
    return dis**(1/2)

print(L2_compution(x,y))

def L1_compution(x,y):#曼哈顿距离,两个点在标准坐标系上的绝对轴距总和
    dis = 0
    for i,j in zip(x,y):
        dis+=abs(i-j)
    return dis

print(L1_compution(x,y))