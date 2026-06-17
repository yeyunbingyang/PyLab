# demo_range.py

# 示例 1: 基本用法：从 0 到 4
print("示例 1: 基本用法")
for i in range(5):
    print(i)  # 输出 0 到 4

# 示例 2: 指定开始值和结束值：从 3 到 7
print("\n示例 2: 指定开始值和结束值")
for i in range(3, 8):
    print(i)  # 输出 3 到 7

# 示例 3: 指定步长：从 0 到 10，步长为 2
print("\n示例 3: 指定步长")
for i in range(0, 11, 2):
    print(i)  # 输出 0, 2, 4, 6, 8, 10

# 示例 4: 负数步长：从 10 到 1，步长为 -1
print("\n示例 4: 负数步长")
for i in range(10, 0, -1):
    print(i)  # 输出 10 到 1

# 示例 5: 创建 range 对象并转换为列表
print("\n示例 5: 创建 range 对象并转换为列表")
r = range(1, 6)
print(list(r))  # 输出 [1, 2, 3, 4, 5]

# 示例 6: 使用 range 计算索引
print("\n示例 6: 使用 range 计算索引")
fruits = ['apple', 'banana', 'cherry']
for i in range(len(fruits)):
    print(i, fruits[i])  # 输出每个元素的索引和值

# 示例 7: 使用 range 生成某些特定模式的数字（步长为负数）
print("\n示例 7: 步长为负数从大到小循环")
for i in range(10, 0, -2):
    print(i)  # 输出 10, 8, 6, 4, 2
