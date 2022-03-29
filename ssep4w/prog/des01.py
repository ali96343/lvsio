class MyDescriptor:
    _val = 0
    def __get__(self, instance, owner):
        print('Getting Descriptor')
        return self._val
    def __set__(self, instance, value):
        print('Setting Value')
        self._val = value
class MyClass:
    var = MyDescriptor()


my_class = MyClass()
my_class.var
my_class.var = 2
my_class.var


class MyClass2:
    var = MyDescriptor()
    var1 = MyDescriptor()
    var2 = MyDescriptor()
