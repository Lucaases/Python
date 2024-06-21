def transfrom(filename1,filename2):#大小写转换
    with open(filename1, 'r') as f:
        text=f.read()#使用swapcase()函数将文本中的大小写字母互换
        print(text)
        print(text.swapcase())
    with open(filename2, 'w') as f1:#将转换后的文本写入文件
        f1.write(text.swapcase())

transfrom("I:\\Python\\experiment 6\\testfile.txt","I:\\Python\\experiment 6\\Result.txt")