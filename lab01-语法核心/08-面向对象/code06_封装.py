# py通常不会选择让对象的属性私有或受保护
class Person:
    """
    Python 面向对象编程中的封装特性示例：
    - 公有属性和方法：可以直接访问。
    - 受保护属性和方法：以 _ 开头，约定内部使用。
    - 私有属性和方法：以 __ 开头，外部无法直接访问。
    - 使用 @property 装饰器封装属性访问。
    """

    def __init__(self, name, age):
        self.name = name  # 公有属性
        self._salary = 5000  # 受保护属性（约定内部使用）
        self.__bank_balance = 10000  # 私有属性（外部无法直接访问）

    # 公有方法
    def show_info(self):
        """返回人员基本信息"""
        return f"姓名: {self.name}, 薪资: {self._salary}"

    # 受保护方法
    def _show_salary(self):
        """受保护方法，仅供内部或子类访问"""
        return f"薪资: {self._salary}"

    # 私有方法
    def __show_bank_balance(self):
        """私有方法，仅限类内部访问"""
        return f"银行余额: {self.__bank_balance}"

    # 通过公有方法访问私有属性（封装访问）
    def get_bank_balance(self):
        """提供访问私有银行余额的安全方法"""
        return self.__show_bank_balance()

    # 使用 property 装饰器封装访问
    @property
    def salary(self):
        """工资的 getter 方法（封装访问）"""
        return self._salary

    @salary.setter
    def salary(self, value):
        """工资的 setter 方法，添加数据验证"""
        if value > 0:
            self._salary = value
        else:
            raise ValueError("薪资必须为正数！")

    @property
    def bank_balance(self):
        """银行余额的封装，禁止外部访问实际数据"""
        return "隐私数据，不可访问！"


# 测试封装特性
p = Person("张三", 30)
print(p.show_info())  # 访问公有方法

# 访问受保护属性（虽然可以，但不建议）
print(p._salary)

# 访问私有属性（错误）
# print(p.__bank_balance)  # AttributeError: 'Person' object has no attribute '__bank_balance'

# 通过公有方法访问私有数据
print(p.get_bank_balance())

# 使用 @property 访问薪资
print(p.salary)

# 修改薪资
p.salary = 6000
print(p.salary)

# 访问 bank_balance（@property 控制输出）
print(p.bank_balance)
