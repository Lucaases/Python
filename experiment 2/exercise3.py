def loop2():
    m=0
    list1=[]
    while(True):
        m+=1
        if m%5==0 and m%7==0 and m%11==0:
            list1.append(m)
        if len(list1)>=20:
            break
    for k in list1:
        print(k)

print("输出前20个能被5,7,11整除的数:")
loop2()