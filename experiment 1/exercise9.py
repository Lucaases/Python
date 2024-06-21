def hello_world():
    print("Hello, world!")


def hello_name(name):
    print("Hello,", name + "!")


def hello_name1(name):
    return "Hello, " + name + "!"


hello_world()

hello_name("Alice")

greeting = hello_name1("Alice")
print(greeting)
