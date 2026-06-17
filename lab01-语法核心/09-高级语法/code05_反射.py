# 反射：运行时动态获取/修改对象的属性和方法
# 四大函数：hasattr、getattr、setattr、delattr

# === 基本反射 ===
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f'Hello, I am {self.name}'

p = Person('Alice', 25)

# 检查属性是否存在
print(hasattr(p, 'name'))     # True
print(hasattr(p, 'email'))    # False

# 动态获取属性
print(getattr(p, 'name'))                            # Alice
print(getattr(p, 'email', 'no email'))               # 默认值

# 动态设置属性
setattr(p, 'city', 'Beijing')
print(p.city)  # Beijing

# 动态删除属性
delattr(p, 'city')
print(hasattr(p, 'city'))     # False

# === 动态调用方法 ===
method = getattr(p, 'greet')
print(method())   # Hello, I am Alice

# === 动态导入模块 ===
module_name = 'math'
math = __import__(module_name)
print(math.sqrt(16))  # 4.0

# === 实用：根据配置动态创建对象 ===
class Dog:
    def speak(self): return 'Woof!'

class Cat:
    def speak(self): return 'Meow!'

animal_class = globals()['Dog']  # 或 getattr(sys.modules[__name__], 'Dog')
animal = animal_class()
print(animal.speak())  # Woof!
