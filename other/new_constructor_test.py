class A:

    def __new__(cls, *args, **kwargs):
        n = super().__new__(cls)
        print(cls)
        print(type(cls))
        print(n)
        print(type(n))
        return n

    def __init__(self, arg=None):
        # if arg:
        print('Method init with arg =', arg)


a = A()
b = A('B')
