list1 =  ["apple", "banana", "cherry",123, 123.4,453.543284, 123j, True, False]

def print_list(a):
    for i in a:
        print(i, end="  ")

def print_list_in_reverse(a):
    for i in a[::-1]:
        print(i, end="  ")

print_list(list1)
print("\n")
print_list_in_reverse(list1)

def own_len(a):
    count = 0
    for _ in a:
        count += 1
    return count

print("\n")
print(len(list1))
print(own_len(list1))