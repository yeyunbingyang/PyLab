class Animal:
    species = "Animal"  # 类属性

    def __init__(self, name, age):
        self.name = name  # 实例属性
        self.age = age

    # 实例方法（普通方法）
    def speak(self):
        return f"{self.name} 发出了叫声！"

    # 类方法（操作类属性） 类方法(cls)
    @classmethod
    def set_species(cls, new_species):
        cls.species = new_species  # 修改类属性

    # 静态方法（与类无关）静态方法(age)：
    @staticmethod
    def is_adult(age):
        return age >= 1  # 判断是否成年


# 创建实例
dog = Animal("Buddy", 2)

# 调用实例方法
print(dog.speak())  # "Buddy 发出了叫声！"

# 调用类方法修改类属性
Animal.set_species("Mammal")
print(Animal.species)  # "Mammal"

# 调用静态方法
print(Animal.is_adult(2))  # True
