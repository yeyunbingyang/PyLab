# 面向对象特点：继承、多态、封装

# 定义一个父类 Player
class Player:
    numbers = 0  # 类属性，统计玩家总数
    levels = ['青铜', '白银', '黄金', '钻石', '王者']  # 定义不同的段位

    def __init__(self, name, age, city, level):  # 初始化函数（构造函数）
        self.name = name  # 实例属性：玩家姓名
        self.age = age  # 实例属性：玩家年龄
        self.city = city  # 实例属性：玩家所在城市
        if level not in Player.levels:
            raise Exception('段位设置错误！')  # 确保输入的段位合法
        else:
            self.level = level  # 记录玩家当前段位
        Player.numbers += 1  # 每创建一个玩家，玩家数量增加

    def show(self):  # 实例方法：展示玩家信息
        print(f'我是荣耀王者的第{Player.numbers}个玩家，我的名字是{self.name}，我来自 {self.city}，我的段位是{self.level}')

    def level_up(self):  # 实例方法：提升玩家段位
        index = Player.levels.index(self.level)
        if index < len(Player.levels) - 1:
            self.level = Player.levels[index + 1]

    def get_weapon(self, weapon):  # 绑定玩家的武器
        self.weapon = weapon

    def show_weapon(self):  # 展示玩家的武器
        return self.weapon.show_weapon()

    @classmethod
    def get_players(cls):  # 类方法：统计当前玩家数量
        print(f'荣耀王者的用户数量已经达到了{cls.numbers}人')

    @staticmethod
    def isvalid(**kwargs):  # 静态方法：判断玩家是否满足条件
        return kwargs['age'] > 18  # 仅允许18岁以上的玩家


# 定义子类 VIP，继承自 Player
class VIP(Player):

    def __init__(self, name, age, city, level, coin):  # 构造函数重写
        super().__init__(name, age, city, level)  # 调用父类构造函数
        self.coin = coin  # VIP 专属属性：金币余额

    def show(self):  # 实例方法重写，添加 VIP 专属信息
        print(
            f'我是荣耀王者的第{Player.numbers}个玩家，我的名字是{self.name}，我来自 {self.city}，我的段位是{self.level}，我的余额是{self.coin}')


# 多态演示函数
def display_player_info(player):
    # 接受 Player 类型的对象，并调用其 show 方法
    player.show()


# 创建普通玩家实例
player1 = Player('Tom', 22, '北京', '白银')
# 创建 VIP 玩家实例
mia = VIP('mia', 24, '哈尔滨', '黄金', 100)

# 通过多态调用不同子类的方法
display_player_info(player1)  # 调用 Player 的 show 方法
display_player_info(mia)  # 调用 VIP 重写的 show 方法
