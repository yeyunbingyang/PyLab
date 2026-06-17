"""
函数与模块综合示例
-----------------
本示例展示以下知识点：
1. 定义函数并实现代码复用
2. 导入模块与函数（import / from ... import / as）
3. 函数参数类型：
   - 位置参数
   - 关键字参数
   - 强制位置参数(/)
   - 命名关键字参数(*)
   - 默认参数
   - 可变参数(*args)
   - 可变关键字参数(**kwargs)
"""

# ===============================
# 1️⃣ 自定义函数：求阶乘
# ===============================
def fac(num):
    """求阶乘函数 - 参数 num 为非负整数"""
    result = 1
    for n in range(2, num + 1):
        result *= n
    return result


# 输入两个整数 m 和 n，计算组合数 C(m, n)
# m = int(input('请输入 m = '))
# n = int(input('请输入 n = '))
# print("C(m, n) =", fac(m) // fac(n) // fac(m - n))


# ===============================
# 2️⃣ 使用模块函数：math.factorial
# ===============================
# 导入 math 模块中的 factorial 函数
from math import factorial

# print("\n使用 math.factorial 计算组合数：")
# m = int(input('请输入 m = '))
# n = int(input('请输入 n = '))
# print("C(m, n) =", factorial(m) // factorial(n) // factorial(m - n))


# 也可以使用别名（as）导入
# from math import factorial as f
# print("\n使用别名 f 计算组合数：")
# m = int(input('请输入 m = '))
# n = int(input('请输入 n = '))
# print("C(m, n) =", f(m) // f(n) // f(m - n))


# ===============================
# 3️⃣ 函数参数类型
# ===============================

# --- (1) 普通位置参数 ---
def make_judgement(a, b, c):
    """判断三条边是否能构成三角形"""
    return a + b > c and b + c > a and a + c > b

print("\n普通位置参数调用:")
print(make_judgement(1, 2, 3))  # False
print(make_judgement(4, 5, 6))  # True

# --- (2) 关键字参数 ---
print("\n关键字参数调用:")
print(make_judgement(b=2, c=3, a=1))  # False
print(make_judgement(c=6, b=4, a=5))  # True

# --- (3) 强制位置参数 (Python 3.8+ 支持) ---
def make_judgement_strict(a, b, c, /):
    """强制位置参数版本 - 不能使用关键字形式传参"""
    return a + b > c and b + c > a and a + c > b

print("\n强制位置参数:")
print(make_judgement_strict(4, 5, 6))  # ✅
# print(make_judgement_strict(a=4,b=5,c=6))  # ❌ 会报错

# --- (4) 命名关键字参数 ---
def make_judgement_named(*, a, b, c):
    """命名关键字参数版本 - 必须使用关键字形式传参"""
    return a + b > c and b + c > a and a + c > b

print("\n命名关键字参数:")
print(make_judgement_named(a=4, b=5, c=6))  # ✅
# print(make_judgement_named(4,5,6))  # ❌ 会报错

# --- (5) 参数默认值 ---
from random import randrange

def roll_dice(n=2):
    """摇色子函数，默认摇两颗色子"""
    total = 0
    for _ in range(n):
        total += randrange(1, 7)
    return total

print("\n参数默认值:")
print(roll_dice())     # 默认2颗
print(roll_dice(3))    # 摇3颗

# --- (6) 可变参数 *args ---
def add(*args):
    """可变参数求和函数"""
    total = 0
    for val in args:
        if isinstance(val, (int, float)):
            total += val
    return total

print("\n可变参数 *args:")
print(add())                   # 0
print(add(1, 2, 3))            # 6
print(add(1, 2, 'x', 3.5, 4))  # 10.5

# --- (7) 可变关键字参数 **kwargs ---
def foo(*args, **kwargs):
    """可变位置参数 + 可变关键字参数"""
    print("\n位置参数 args =", args)
    print("关键字参数 kwargs =", kwargs)

foo(3, 2.1, True, name='张三', age=25, score=99.5)

# ===============================
# 4️⃣ 模块调用演示
# ===============================
# 假设我们有两个文件：
# module1.py:
#   def foo(): print("hello, world!")
# module2.py:
#   def foo(): print("goodbye, world!")

# 以下伪代码演示：
"""
import module1
import module2

module1.foo()  # hello, world!
module2.foo()  # goodbye, world!

# 使用别名导入
import module1 as m1
import module2 as m2
m1.foo()
m2.foo()

# 从模块中直接导入函数
from module1 import foo as f1
from module2 import foo as f2
f1()
f2()
"""
