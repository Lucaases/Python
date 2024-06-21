def textfile(filename):
  with open(filename, 'r') as f:#使用with语句打开文件,不需要再使用close()方法关闭文件,with语句会自动关闭文件
    text=f.read()#读取文件内容
  words=text.lower().split()#将文本转换为小写,方便进行单词重复检测,并将文本分割成单词
  print(f"txt一共有{str(len(words))}个单词")
  print("单词如下：")
  print(words)
  word_counts = {}#以单词为键,单词出现的次数为值构建字典
  for word in words:
      if word in word_counts:#以字典的形式存储单词和单词出现的次数
         word_counts[word] += 1#如果单词已经在字典中,就将单词的次数加1
      else:
         word_counts[word] = 1#如果单词不在字典中,就将单词的次数设为1
  common=sorted(word_counts.items(), key=lambda counts: counts[1], reverse=True)#lambda表达式中的counts[1]表示对字典中的值进行排序，reverse=True表示降序排列
  #sorted函数类似于C++algorithm库中的sort函数,都是对可迭代器进行排序,并且都存在cmp参数,可以自定义排序规则
  common20=common[:20]#取出前20个出现次数最多的单词
  unique=len(set(words))#set()函数用于创建一个无序不重复元素集,可以通过set()函数将列表转换为集合,然后通过len()函数计算集合中元素的个数,即不重复单词的个数
  fivemore=sum(count >= 5 for count in word_counts.values())#统计单词出现5次及以上的个数,sum()参数实际上是一个bool类型,如果为True,则返回1,否则返回0
  return common,common20, unique, fivemore

def write_word_counts(filename, common, scale=40):#将40个单词出现的次数写入文件
  with open(filename, 'w') as f:
    f.write("Word\t\t\tCount\n")
    for word, count in common[:scale]:
      f.write(f"{word:<15}\t{count:>5}\n")#f-string格式化字符串,用于格式化字符串,在字符串前加f,然后在字符串中使用{}来引用变量,非常方便!!!

common,common20,unique,fivemore = textfile("I:\\Python\\experiment 6\\testfile.txt")
print("\n")
print(f"20个出现次数最多的单词:{common20}" )
print(f"不重复出现单词个数:{unique}")
print(f"单词出现5次及以上的个数:{fivemore}")
write_word_counts("I:\\Python\\experiment 6\\exercise2-write.txt", common)
