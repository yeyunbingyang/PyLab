"""
    类的实例创建
"""
from code01_类的定义 import Student, Student01, Student02, Student03

# 创建不同类的对象示例
# 1. 基础空类
s = Student()
print(s)

# 2. 带类属性的类
s1 = Student01()
print(s1)
print(s1.name)  # 输出：小明

# 3. 带方法的类（注意：需要先设置实例属性）
s2 = Student02()
print(s2)
s2.name = "李雷"  # ⚠️需要手动添加属性（因为没有__init__）
s2.study("数学")

# 4. 带构造方法的类（推荐方式）
s3 = Student03("韩梅梅", 18)
print(s3)
s3.play()  # 输出：韩梅梅正在玩游戏.


