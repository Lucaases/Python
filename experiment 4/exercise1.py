x = [1,5,4,9,10,3]
y = [7,13,41,8,7,6]
coo = zip(x,y) #zip类型使用一次就会销毁,要复制一份,不然会报错
coo1 = zip(x,y)
print(list(coo1))
x,y= zip(*coo)
print(x)
print(y)
