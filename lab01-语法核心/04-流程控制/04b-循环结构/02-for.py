"""
for - in 循环
用于遍历（迭代）可迭代对象的每个元素
语法：
for 变量 in 可迭代对象:
    循环体代码
"""

# 1. 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
# 输出：
# apple
# banana
# cherry

print("-" * 30)

# 2. 使用 range() 生成数字序列
# range(stop) —— 从 0 开始到 stop（不含 stop）
for i in range(5):
    print(i)
# 输出：0, 1, 2, 3, 4

print("-" * 30)

# range(start, stop, step) —— 从 start 开始，每次步进 step，直到 stop（不含 stop）
for i in range(2, 10, 2):
    print(i)
# 输出：2, 4, 6, 8

print("-" * 30)

# 3. 遍历字符串
for char in "Hello":
    print(char)
# 输出：
# H
# e
# l
# l
# o

print("-" * 30)

# 4. 遍历字典
person = {"name": "Bob", "age": 25}
for key, value in person.items():
    print(f"{key}: {value}")
# 输出：
# name: Bob
# age: 25

print("-" * 30)

# 5. 结合 range() 和 len() 遍历列表索引和值
for i in range(len(fruits)):
    print(f"第 {i} 个水果是 {fruits[i]}")
# 输出：
# 第 0 个水果是 apple
# 第 1 个水果是 banana
# 第 2 个水果是 cherry

print("-" * 30)

# 6. 使用 enumerate() 同时取出索引和值（更Pythonic）
for index, fruit in enumerate(fruits):
    print(f"索引 {index} -> {fruit}")
# 输出：
# 索引 0 -> apple
# 索引 1 -> banana
# 索引 2 -> cherry

print("-" * 30)

# 7. 嵌套 for 循环示例
for x in range(1, 4):
    for y in range(1, 4):
        print(f"{x} * {y} = {x * y}")
    print("-" * 10)
# 输出：
# 1 * 1 = 1
# 1 * 2 = 2
# 1 * 3 = 3
# ----------
# 2 * 1 = 2
# 2 * 2 = 4
# 2 * 3 = 6
# ----------
# 3 * 1 = 3
# 3 * 2 = 6
# 3 * 3 = 9
# ----------

print("-" * 30)

# ======================================
# 8. 使用技巧
# ======================================


# --- 8.1 break — 提前终止循环 ---
# 找到目标元素后立即退出，避免不必要的遍历
numbers = [1, 3, 4, 7, 8, 10]
print("找到第一个偶数：", end="")
for n in numbers:
    if n % 2 == 0:
        print(n)
        break
# 输出：找到第一个偶数：4

print("-" * 30)


# --- 8.2 continue — 跳过当前迭代 ---
# 跳过符合条件的元素，继续下一次循环
print("1-9 中的奇数：", end="")
for n in range(1, 10):
    if n % 2 == 0:
        continue
    print(n, end=" ")
print()
# 输出：1-9 中的奇数：1 3 5 7 9

print("-" * 30)


# --- 8.3 for...else — 循环正常结束才执行 else ---
# else 块只在循环未被 break 中断时执行
# 适合"查找未找到"的场景
target = "grape"
for fruit in fruits:
    if fruit == target:
        print(f"找到了 {target}")
        break
else:
    print(f"没找到 {target}")  # 未 break 才执行
# 输出：没找到 grape

# 对比：能找到的情况
for fruit in fruits:
    if fruit == "banana":
        print("找到了 banana")
        break
else:
    print("没找到 banana")  # 不会执行
# 输出：找到了 banana

print("-" * 30)


# --- 8.4 zip() — 并行遍历多个序列 ---
# 将多个可迭代对象按索引一一配对，以最短的为准
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
grades = ["A", "A-", "B+"]

for name, score, grade in zip(names, scores, grades):
    print(f"{name}: {score} 分 ({grade})")
# 输出：
# Alice: 85 分 (A)
# Bob: 92 分 (A-)
# Charlie: 78 分 (B+)

# zip 可处理不等长序列，默认截断到最短
short = [1, 2]
long_ = ["a", "b", "c", "d"]
for a, b in zip(short, long_):
    print(a, b)
# 输出：1 a / 2 b（只取前两个）

# zip_longest 可填充到最长（需导入）
from itertools import zip_longest
for a, b in zip_longest(short, long_, fillvalue=None):
    print(a, b)
# 输出：1 a / 2 b / None c / None d

print("-" * 30)


# --- 8.5 reversed() — 反向遍历 ---
print("反向遍历：", end="")
for fruit in reversed(fruits):
    print(fruit, end=" ")
print()
# 输出：cherry banana apple

# 也支持字符串
for char in reversed("Python"):
    print(char, end=" ")
print()
# 输出：n o h t y P

print("-" * 30)


# --- 8.6 sorted() — 排序后遍历 ---
# 不修改原序列，返回新列表
nums = [3, 1, 4, 1, 5, 9, 2]
print("升序：", sorted(nums))
print("降序：", sorted(nums, reverse=True))
# 输出：
# 升序： [1, 1, 2, 3, 4, 5, 9]
# 降序： [9, 5, 4, 3, 2, 1, 1]

# 自定义排序 key
words = ["apple", "Banana", "cherry", "Date"]
print("忽略大小写排序：", sorted(words, key=str.lower))
# 输出：['apple', 'Banana', 'cherry', 'Date']

print("-" * 30)


# --- 8.7 列表推导式（List Comprehension）---
# Python 特色写法，用一行代码生成新列表

# 传统写法
squares = []
for n in range(5):
    squares.append(n ** 2)
print("传统写法：", squares)  # [0, 1, 4, 9, 16]

# 推导式写法（推荐）
squares = [n ** 2 for n in range(5)]
print("推导式写法：", squares)  # [0, 1, 4, 9, 16]

# 带条件过滤
evens = [n for n in range(10) if n % 2 == 0]
print("0-9 中的偶数：", evens)  # [0, 2, 4, 6, 8]

# 嵌套推导式（等价于嵌套 for）
matrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]
print("乘法表矩阵：", matrix)  # [[1, 2, 3], [2, 4, 6], [3, 6, 9]]

# 字典推导式
square_dict = {n: n ** 2 for n in range(5)}
print("平方字典：", square_dict)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

print("-" * 30)


# --- 8.8 for 与 else 配合的实用模式 ---
# 经典场景：检查列表是否全部满足条件
def all_positive(numbers):
    for n in numbers:
        if n <= 0:
            print("存在非正数")
            break
    else:
        print("全部为正数")

all_positive([1, 2, 3, 4])    # 全部为正数
all_positive([1, -2, 3])      # 存在非正数
