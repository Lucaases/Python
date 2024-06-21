def Repeated(list):
    list1=[]
    for i in list:#外层循环控制次数(直接得到元素值,python相比C确实更加灵活)
        t=0
        for j in list:#内层循环将外层得到元素值与其他元素一一比较,相同则使临时变量t加1
            if j == i:
                t+=1
        list1.append(t)
    d=dict(zip(list,list1))
    return d

a=[1,1,1,3,2,5,6,6,"s","s"]
print(Repeated(a))