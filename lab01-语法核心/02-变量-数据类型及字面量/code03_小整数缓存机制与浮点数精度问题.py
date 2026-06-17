# small_int_and_float_demo.py
"""
演示 Python 中的小整数缓存机制与浮点数精度问题
"""

# -------------------------------
# 一、小整数缓存机制（-5 ~ 256）
# -------------------------------
a = 100
b = 100
c = 1000
d = 1000

print("a == b:", a == b)      # True，值相等
print("a is b:", a is b)      # True，共用同一对象（缓存）
print("id(a):", id(a))
print("id(b):", id(b))

print("c == d:", c == d)      # True，值相等
print("c is d:", c is d)      # False，地址不同（未缓存）
print("id(c):", id(c))
print("id(d):", id(d))

# 小整数缓存范围：-5 到 256
x = -5
y = -5
z = 257
t = 257
print("\n-5 地址相同?", id(x) == id(y))
print("257 地址相同?", id(z) == id(t))

# -------------------------------
# 二、浮点数不会缓存
# -------------------------------
f1 = 3.14
f2 = 3.14
print("\n浮点数值相等:", f1 == f2)
print("浮点数地址相同?", f1 is f2)  # False（每次创建新对象）

# -------------------------------
# 三、浮点数精度问题
# -------------------------------
result = 0.1 + 0.2
print("\n0.1 + 0.2 =", result)           # 0.30000000000000004
print("是否等于 0.3:", result == 0.3)    # False（浮点误差）

# 精度处理方法一：round 四舍五入
print("round(result, 2):", round(result, 2))  # 0.3

# 精度处理方法二：decimal 精确运算
from decimal import Decimal
res_decimal = Decimal("0.1") + Decimal("0.2")
print("使用 Decimal:", res_decimal)  # 0.3

# -------------------------------
# 四、说明
# -------------------------------
"""
结论：
1️⃣ Python 会缓存 -5~256 的整数，重复使用相同对象；
2️⃣ 超出范围的整数会创建新对象；
3️⃣ 浮点数每次都会新建对象（不缓存）；
4️⃣ 浮点运算存在二进制精度误差，可用 round() 或 decimal 模块处理。
"""
