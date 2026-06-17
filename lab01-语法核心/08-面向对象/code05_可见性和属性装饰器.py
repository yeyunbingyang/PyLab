class Person:
    def __init__(self, name, age):
        self.name = name  # 公有属性
        self._salary = 5000  # 受保护属性（约定：不能直接访问）
        self.__bank_balance = 10000  # 私有属性（不能直接访问）

    # 公有方法
    def show_info(self):
        return f"姓名: {self.name}, 薪资: {self._salary}"

    # 受保护方法
    def _show_salary(self):
        return f"薪资: {self._salary}"

    # 私有方法
    def __show_bank_balance(self):
        return f"银行余额: {self.__bank_balance}"

    # 访问私有属性的方法
    def get_bank_balance(self):
        return self.__show_bank_balance()

    # 使用 property 装饰器封装访问
    @property
    def salary(self):
        return self._salary


    @salary.setter
    def salary(self, value):
        print("设置薪资")
        if value > 0:
            self._salary = value
        else:
            raise ValueError("薪资必须为正数！")

    @property
    def bank_balance(self):
        return "隐私数据，不可访问！"


# 测试
p = Person("张三", 30)
print(p.show_info())  # 可以访问公有方法

# 访问受保护属性（不建议，但可以）
print(p._salary)

# 访问私有属性（错误）
# print(p.__bank_balance)  # AttributeError

# 通过公有方法访问私有数据
print(p.get_bank_balance())

# 使用 @property 访问薪资
print(p.salary)

# 修改薪资
p.salary = 6000
print(p.salary)

# 访问 bank_balance（@property 控制输出）
print(p.bank_balance)
