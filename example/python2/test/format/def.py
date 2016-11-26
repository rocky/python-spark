def f0():
    pass

def f1(n):
    return n

def f2(a, b):
    return 2 // 3

def f3(a, b=3):
    return 3

class Foo:
    pass

class Bar(object):
    pass

class Baz(Foo, Bar):
    pass

# NOT YET
# def fact(n):
#     if n <= 0: return 1
#     return n * fact(n-1)

def fact2(n):
    if n <= 0:
        return 1
    else:
        return n * fact2(n - 1)
