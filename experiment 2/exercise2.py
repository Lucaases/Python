def loop1():
    print("输出1-100数字:")  
    for i in range(100):
        print(i,end=" ")      
    print("\n")
    print("输出1-100数字中能被7整除的数字:")  
    for i in range(100):
        if i%7==0:
            print(i,end=" ")
    print("\n")
    print("输出1-100数字中能被5整除但不能被3整除的数字:")
    for i in range(1,100):
        if i%5==0 and i%3!=0:
         print(i,end=" ")
    print("\n")
    print("输出2-20数字中每个数字的因子:")
    
    for i in range(2,20):    
        print("\n",i,"的因子有:",end=" ")
        for j in range(2,20):
            if i%j==0 and j!=i:
                print(j,end=" ")
loop1()