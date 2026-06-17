"""
    动态语言 在运行时可以改变其结构的语言 py js
    可以动态为对象添加属性
"""

# 对象属性
    # 后续添加
class Player(object):
    def __init__(self,name,age,city):  # 初始化函数（构造函数）
        self.name = name
        self.age = age
        self.city = city

mia = Player('mia',24,'上海')
mia.city = '杭州'
tom = Player('tom',34,'重庆')
tom.height = 180
tom.age = 32
print(tom.__dict__) # 获取实例（对象）的所有属性

    # 初始化方法中的参数就是对象属性
class weapon(object):
    # 武器： 名字 攻击值 等级
    def __init__(self,name,damage,level):
        self.name = name
        self.damage = damage
        self.level = level

gun = weapon('magic',1000,3)
print(gun.__dict__)

# 类属性
class Player(object):
    numbers = 0   # 类属性
    def __init__(self,name,age,city):  # 初始化函数（构造函数）
        self.name = name  # 实例属性
        self.age = age
        self.city = city
        Player.numbers += 1

mia = Player('mia',24,'上海')
print(mia.__dict__)
print('欢迎荣耀王者的第 %d 个玩家注册！' % Player.numbers)
tom = Player('tom',32,'重庆')
print('欢迎荣耀王者的第 %d 个玩家注册！' % Player.numbers)

class weapon(object):
    numbers = 0
    max_damage = 10000
    levels = ['青铜','白银','黄金','钻石','王者']
    def __init__(self,name,damage,level):
        self.name = name
        self.damage = damage
        self.level = level
        weapon.numbers += 1
        if damage>weapon.max_damage:
            raise Exception('最大的伤害值是10000，请重试！')
        if level not in weapon.levels:
            raise Exception('段位设置错误！')
try:
    gun = weapon('magic',10000,'王者')
    print(weapon.numbers)
    arrow = weapon('arrow',450,'青铜')
    print(weapon.numbers)
except Exception as e:
    print(e)