import random
# 生成随机小数 random
a = random.random() # [0-1)
print(a)
# 生成随机整数 randint
a = random.randint(1,200) # [1-200]
print(a)

# 获取列表中的随机元素
list1 = [1,2,3,4,5,6]
print(list1[random.randint(0,len(list1)-1)])
# 随机获取一个列表中的元素 choice
print(random.choice(list1))
print(random.choice('hello'))
print(ord('A'),ord('Z'))

# 生成一个随机字母组成的列表
from my_package import my_tools,my_games
print(my_tools.random_string(5))

# 打乱列表顺序
random.shuffle(list1)
print(list1)
my_games.guess_number(1, 1000)


