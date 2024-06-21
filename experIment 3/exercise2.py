def print_list(a):
    for i in a:
        print(i, end="  ")

def set_first_elem_to_zero(a):
    a[0]=0
    return a

a =  ["apple", "banana", "cherry",123, 123.4,453.543284, 123j, True, False]
b=a
b[1]= "mango"
print_list(a)
print("\n")
c=a[:]
c[2]= "mango"
print_list(a)
set_first_elem_to_zero(a)
print("\n")
print_list(a)