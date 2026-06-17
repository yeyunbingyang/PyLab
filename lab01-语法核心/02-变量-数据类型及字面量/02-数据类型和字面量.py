# =====================================================
# Python 数据类型与字面量综合示例
# =====================================================
from decimal import Decimal

# Python 是弱类型语言，不需要声明类型
# 数据类型决定了变量能保存什么样的数据

# =====================================================
# 一、数字类型（int、float、complex）
# =====================================================

print("=== 数字类型 ===")

# 整型 int
a = 42
b = -3
binary = 0b1010   # 二进制
octal = 0o755     # 八进制
hexadecimal = 0xFF # 十六进制
print("int 示例：", a, b, binary, octal, hexadecimal)

# 浮点型 float
pi = 3.14159
scientific = 1.23e-5   # 科学计数法
print("float 示例：", pi, scientific)
# 浮点问题：浮点数精度问题
print("浮点数精度问题：", 0.1 + 0.2)
# 解决
print("Decimal浮点数精度问题解决：", Decimal(str(0.1)) + Decimal(str(0.2)))  # 必须用字符串传入

# 复数 complex
z = 1 + 2j
print("complex 示例：", z, "实部:", z.real, "虚部:", z.imag)

# math 数学函数
import math
num = 3.6
print("向上取整 ceil:", math.ceil(num))
print("向下取整 floor:", math.floor(num))
print("四舍五入 round:", round(num))

# =====================================================
# 二、布尔类型 bool
# =====================================================

print("\n=== 布尔类型 ===")

t = True
f = False
print("True == 1:", True == 1)
print("False == 0:", False == 0)
print("布尔值运算：", t and f, t or f, not f)

# =====================================================
# 三、序列类型（str, list, tuple）
# =====================================================

print("\n=== 序列类型 ===")

# 字符串 str（不可变）
s1 = "Python"
s2 = 'Hello'
s3 = """多行
字符串"""
print("字符串示例：", s1, s2, s3)

# 字符串拼接与重复
print("拼接：", s1 + " " + s2)
print("重复：", s2 * 3)

# 索引与切片
print("索引 s1[0]：", s1[0])
print("倒序索引 s1[-1]：", s1[-1])

# 切片 变量名[起始索引:结束索引+1:步数]
# 步数默认为1，可省略不写
# 起始索引默认为0，可省略不写
# 结束索引默认为-1,可省略不写
print("切片 s1[1:4]：", s1[1:4])  # 切片 变量名[起始索引:结束索引+1:步数]   范围包头不包尾部
print("反转 s1[::-1]：", s1[::-1])

# 列表 list（可变）
lst = [1, 2, 3]
lst.append(4)
print("列表示例：", lst)

# 元组 tuple（不可变）
tpl = (1, "A", True)
print("元组示例：", tpl)

# 单元素元组必须加逗号
single_tpl = (42,)
print("单元素元组：", single_tpl)

# =====================================================
# 四、集合类型（set, frozenset）
# =====================================================

print("\n=== 集合类型 ===")

set_a = {1, 2, 3}
set_b = {2, 3, 4}
print("并集：", set_a | set_b)
print("交集：", set_a & set_b)
print("差集：", set_a - set_b)
print("对称差集：", set_a ^ set_b)

# 不可变集合
frozen = frozenset({1, 2, 3})
print("不可变集合 frozenset：", frozen)

# =====================================================
# 五、映射类型（dict）
# =====================================================

print("\n=== 映射类型 ===")

user = {"name": "Alice", "age": 25}
print("字典：", user)
print("访问键值：", user["name"])

# 添加与修改
user["city"] = "Shanghai"
user["age"] = 26
print("更新后：", user)

# =====================================================
# 六、特殊类型（None）
# =====================================================

print("\n=== 特殊类型 ===")

nothing = None
print("None 示例：", nothing)
print("None 的布尔值：", bool(nothing))

# =====================================================
# 七、字面量（Literal）
# =====================================================

print("\n=== 字面量示例 ===")

# 数字字面量
decimal = 123
binary = 0b1101
octal = 0o755
hexadecimal = 0xFF
print("进制字面量：", decimal, binary, octal, hexadecimal)

# 字符串字面量
single_line = "Hello\nWorld"
multi_line = """Line 1
Line 2"""
raw_str = r"C:\User\data"
print("字符串字面量：", single_line, multi_line, raw_str)

# 集合与字典字面量
numbers = [1, 2, 3]
coordinates = (10, 20)
user = {"id": 1, "name": "Bob"}
unique_nums = {1, 2, 2, 3}
unique_nums1 = {1,}  # 元组单元素必须加逗号：(1,) vs (1)（后者视为整型）。
print("字典与集合字面量：", user, unique_nums)

# 其他字面量
boolean = True
bytes_data = b"binary"
bytearray_data = bytearray(b"abc")
print("布尔与字节类型：", boolean, bytes_data, bytearray_data)

# =====================================================
# 八、类型推断与类型转换
# =====================================================

print("\n=== 类型推断与转换 ===")

print(type(42), type(3.14), type("text"))
print(type([1, 2, 3]), type({1, 2, 3}), type(None))

# chr() 与 ord()
char_a = chr(97)  # 97 → 'a' 将整数（字符编码）转换成对应的（一个字符的）字符串。
code_a = ord('a') # 'a' → 97 ● 将（一个字符的）字符串转换成对应的整数（字符编码）。
print("chr(97):", char_a, "| ord('a'):", code_a)

# =====================================================
# 九、可变性对比
# =====================================================

print("\n=== 可变性对比 ===")

x = [1, 2, 3]
y = x
y.append(4)
print("列表修改后：", x)  # 同步变化，可变

s = "abc"
t = s
t = t + "d"
print("字符串修改后：", s, t)  # 原字符串不变，不可变

# =====================================================
# 十、注意事项总结
# =====================================================
"""
1️⃣ 不可变类型：int、float、bool、str、tuple、frozenset
2️⃣ 可变类型：list、dict、set、bytearray
3️⃣ 空集合必须用 set()，因为 {} 表示空字典。
4️⃣ 元组单元素需加逗号：(1,)。
5️⃣ 使用 round / ceil / floor 处理浮点数。
6️⃣ 合理选择类型：唯一性→set；键值映射→dict；
   不可变配置→tuple；普通序列→list。
7️⃣ chr()/ord() 用于字符与编码转换。
"""

print("\n✅ 数据类型与字面量演示完毕 ✅")
