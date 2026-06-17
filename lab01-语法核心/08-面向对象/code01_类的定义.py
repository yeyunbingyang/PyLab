"""
    类的定义
"""

# 基础格式
# object 是基类 默认是object 可以不写
class Student(object):
    # pass 不做任何事情 保证类、函数或其他代码块的程序结构完整性
    # 如果不立即编写具体的实现，可以先用 pass 占位。
    pass

# 带类属性 类属性是所有实例共享的
class Student01:
    """学生"""
    name = '小明'
    age = 18

# 带方法
# self 是第一个参数、代表操作的当前实例【对象】
class Student02:
    """学生"""
    def study(self, course_name):
        """学习"""
        print(f'{self.name}正在学习{course_name}.')

    def play(self):
        """玩耍"""
        print(f'{self.name}正在玩游戏.')

# 带属性和初始化方法【构造方法】
# __init__ 代表初始化方法 用于初始化属性【属于实例属性】
class Student03:
    """学生"""

    def __init__(self, name, age):
        """初始化方法"""
        self.name = name
        self.age = age

    def study(self, course_name):
        """学习"""
        print(f'{self.name}正在学习{course_name}.')

    def play(self):
        """玩耍"""
        print(f'{self.name}正在玩游戏.')