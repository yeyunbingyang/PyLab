"""

序列： 有序 有索引 元素可重复
Python 列表（List）学习示例
"""

# =========================================================
# 一、列表的创建与类型转换
# =========================================================

# 创建空列表
list1 = []  # 空列表
print("空列表：", list1)

# 创建带元素的列表
items1 = [35, 12, 99, 68, 55, 35, 87]
items2 = ['Python', 'Java', 'Go', 'Kotlin']
items3 = [100, 12.3, 'Python', True]
print("数字列表:", items1)
print("字符串列表:", items2)
print("混合类型列表:", items3)

# 使用 list() 构造函数
list4 = list(range(1, 10))   # 将 range 对象转为列表
list5 = list("hello")        # 将字符串拆解为字符列表
print("range 转换:", list4)
print("字符串转列表:", list5)

# =========================================================
# 二、列表加法、乘法、成员判断
# =========================================================
items5 = [35, 12, 99, 45, 66]
items6 = [45, 58, 29]
items7 = ['Python', 'Java', 'JavaScript']

print("加法:", items5 + items6)  # 拼接两个列表
print("乘法:", items6 * 2)       # 重复两次
print("成员判断:", 29 in items6, 99 in items6)  # True False
print("非成员判断:", 'C++' not in items7)

# =========================================================
# 三、索引与切片操作
# =========================================================
items8 = ['apple', 'waxberry', 'pitaya', 'peach', 'watermelon']
print("\n原列表:", items8)

# 正向索引（从0开始）
print("第一个元素:", items8[0])
print("第三个元素:", items8[2])

# 修改元素
items8[2] = 'durian'
print("修改后:", items8)

# 负向索引（从末尾-1开始）
print("最后一个元素:", items8[-1])

# 切片 [start:end:step]
print("1:3:", items8[1:3])
print("0:5:2:", items8[0:5:2])
print("-4:-2:", items8[-4:-2])
print("逆序切片:", items8[-1:-6:-1])

# =========================================================
# 四、列表的遍历
# =========================================================
languages = ['Python', 'Java', 'C++', 'Kotlin']

print("\n方式一：使用索引遍历")
for i in range(len(languages)):
    print(i, "=>", languages[i])

print("\n方式二：直接遍历元素")
for lang in languages:
    print(lang)

print("\n方式三：使用 enumerate() 同时取索引与元素")
for index, value in enumerate(languages):
    print(index, value)

# =========================================================
# 五、二维列表
# =========================================================
scores = [
    [95, 83, 92],
    [80, 75, 82],
    [92, 97, 90],
    [80, 78, 69],
    [65, 66, 89]
]
print("\n二维列表示例：")
print("第1个学生成绩:", scores[0])
print("第1个学生第2门成绩:", scores[0][1])

# =========================================================
# 六、列表的常见方法
# =========================================================
my_list = [1, 3, 5, 7, 9]
print("\n原列表:", my_list)

# 插入元素
my_list.insert(1, 2)  # 在索引1插入2
my_list.append(11)    # 尾部追加
my_list.extend([13, 15])  # 追加另一个列表
print("插入后:", my_list)

# 修改元素
my_list[2] = 4
print("修改后:", my_list)

# 删除元素
del my_list[0]        # 删除索引0的值 据索引删除
my_list.remove(11)    # 删除第一个出现的11 据值删除
my_list.pop()         # 删除最后一个元素 默认删除最后一个
print("删除后:", my_list)

# 统计与排序
print("长度:", len(my_list))
print("5出现次数:", my_list.count(5))

my_list.sort()               # 升序
print("升序排序:", my_list)
my_list.sort(reverse=True)   # 降序
print("降序排序:", my_list)
my_list.reverse()            # 反转
print("反转:", my_list)

# =========================================================
# 七、列表生成式（List Comprehension） 遍历时对元素进行操作【前操作 后过滤】
# =========================================================
# 示例1：1~99中能被3或5整除的数
items = [i for i in range(1, 100) if i % 3 == 0 or i % 5 == 0]
print("\n能被3或5整除的数:", items[:10], "...")

# 示例2：平方
nums1 = [35, 12, 97, 64, 55]
nums2 = [num ** 2 for num in nums1]
print("平方结果:", nums2)

# 示例3：过滤大于50的数
nums3 = [num for num in nums1 if num > 50]
print("大于50的数:", nums3)

# =========================================================
# 八、双色球随机选号程序
# =========================================================
import random

print("\n=== 双色球随机选号程序 ===")
n = int(input("生成几注号码: "))
red_balls = [i for i in range(1, 34)]
blue_balls = [i for i in range(1, 17)]

for index in range(n):
    selected_reds = random.sample(red_balls, 6)  # 无放回抽样
    selected_reds.sort()
    blue = random.choice(blue_balls)

    print(f"第{index + 1}注:", end=" ")
    # 红球输出（红色字体）
    for ball in selected_reds:
        print(f'\033[31m{ball:0>2d}\033[0m', end=" ")
    # 蓝球输出（蓝色字体）
    print(f'\033[34m{blue:0>2d}\033[0m')

# =========================================================
# 九、总结说明
# =========================================================
"""
列表是 Python 中最常用的数据结构之一：
✅ 支持存储任意类型
✅ 支持随机访问（通过索引）
✅ 可变对象，支持增删改查
✅ 可用列表生成式简洁构造
✅ 可嵌套实现二维或多维结构
"""
