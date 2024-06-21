def collatz1(x):
    if x%2==0:
        return x/2
    else:
        return 3*x+1

def collatz2(x):
    while x!=1:
        print(int(collatz1(x)),end=" ")
        x = collatz1(x)

collatz2(103)