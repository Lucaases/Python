import timeit

def Collatz(n):
    list1 = []
    while n != 1:
        if n % 2 == 0:
            n = n // 2 # //表示整数除法，返回不大于结果的一个最大整数
            list1.append(n)
        else:
            n = 3 * n + 1
            list1.append(n)
    return list1


print(Collatz(103))

def find_longest_Collatz_sequence(n):
    max_length = 0
    max_number = 0
    for i in range(1, n):
        length = len(Collatz(i))
        if length > max_length:
            max_length = length
            max_number = i
    return max_number

print(find_longest_Collatz_sequence(1000000))

print(timeit.timeit('find_longest_Collatz_sequence(1000000)', globals=globals(), number=1))
