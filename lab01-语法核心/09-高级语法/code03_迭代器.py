# 迭代器：实现 __iter__ 和 __next__ 方法的对象，支持 for 循环遍历

# === 自定义迭代器 ===
class CountDown:
    '''倒数迭代器'''
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for n in CountDown(5):
    print(n, end=' ')  # 5 4 3 2 1
print()

# === 可迭代对象 vs 迭代器 ===
lst = [1, 2, 3]
it = iter(lst)        # iter() 获取迭代器
print(next(it))       # 1
print(next(it))       # 2
print(next(it))       # 3
# next(it) → StopIteration

# === itertools 工具 ===
import itertools

# 无限迭代
counter = itertools.count(10, 2)
print([next(counter) for _ in range(5)])  # [10, 12, 14, 16, 18]

# 循环
colors = itertools.cycle(['红', '绿', '蓝'])
print([next(colors) for _ in range(6)])   # ['红','绿','蓝','红','绿','蓝']

# 排列组合
for p in itertools.permutations('AB', 2):
    print(p, end=' ')  # ('A','B') ('B','A')
print()
