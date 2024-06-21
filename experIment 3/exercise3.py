def is_prime(n):
    if n == 2:
        return True  
    elif n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):#以2为步进跳过偶数,减少循环次数;对于任何自然数n，其所有非1和n的因数m，都满足m<=n/2
        if n % i == 0:
            return False
    return True

def is_prime1(n):
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(n**0.5) + 1, 6):#以6为步进,6k+1和6k-1的形式
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True

print(is_prime(97))
print(is_prime1(97))

print(is_prime(30))
print(is_prime1(30))

def prime_list(n):
    prime_list = []
    for i in range(2, n+1):
        if is_prime(i):
            prime_list.append(i)
    return prime_list

print(prime_list(100))

def prime_list1(n):
    prime_list1 = []
    i=1
    while(True):
        i+=1
        if is_prime(i):
            prime_list1.append(i)
        if len(prime_list1) == n:
            break
    return prime_list1

print(prime_list1(20))