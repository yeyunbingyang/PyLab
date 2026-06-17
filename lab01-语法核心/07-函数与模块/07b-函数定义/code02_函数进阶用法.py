"""
功能说明：演示 Python 函数进阶用法，包括高阶函数、lambda 表达式与偏函数。
"""

# =======================
# 一、函数作为参数与返回值（高阶函数）
# =======================

def calc(init_value, op_func, *args, **kwargs):
    """
    通用计算函数：
    接收一个运算函数作为参数，对所有 int/float 元素进行累积计算。
    - init_value: 初始值
    - op_func: 运算函数，如 operator.add / operator.mul
    - *args, **kwargs: 参与计算的多个数
    """
    items = list(args) + list(kwargs.values())
    result = init_value
    for item in items:
        if isinstance(item, (int, float)):  # 判断是否为数字
            result = op_func(result, item)
    return result


# 定义两个普通函数（运算函数）
def add(x, y):
    """加法"""
    return x + y


def mul(x, y):
    """乘法"""
    return x * y


# 测试高阶函数 calc()
print("👉 高阶函数 calc 示例：")
print(calc(0, add, 1, 2, 3, 4, 5))  # 输出: 15
print(calc(1, mul, 1, 2, 3, 4, 5))  # 输出: 120


# =======================
# 二、使用 Python 内置的高阶函数 map / filter
# =======================

def is_even(num):
    """判断是否为偶数"""
    return num % 2 == 0


def square(num):
    """返回平方"""
    return num ** 2


old_nums = [35, 12, 8, 99, 60, 52]

# 使用 filter 过滤出偶数，再使用 map 求平方
new_nums = list(map(square, filter(is_even, old_nums)))
print("\n👉 使用 filter + map：", new_nums)

# 使用列表生成式实现相同功能
new_nums2 = [num ** 2 for num in old_nums if num % 2 == 0]
print("👉 使用列表生成式：", new_nums2)


# =======================
# 三、Lambda 表达式（匿名函数）
# =======================
print("\n👉 Lambda 表达式示例：")

# 普通 lambda 示例
add_lambda = lambda x, y: x + y
print("3 + 5 =", add_lambda(3, 5))

# 带条件的 lambda
is_even_lambda = lambda x: 'Even' if x % 2 == 0 else 'Odd'
print("4 是：", is_even_lambda(4))
print("5 是：", is_even_lambda(5))

# 与 map + filter 一起使用
nums = [35, 12, 8, 99, 60, 52]
result = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, nums)))
print("偶数平方：", result)


# =======================
# 四、Lambda + reduce 的进阶用法
# =======================
import functools
import operator

# 计算阶乘函数
fac = lambda n: functools.reduce(operator.mul, range(2, n + 1), 1)

# 判断素数函数
is_prime = lambda x: all(map(lambda f: x % f, range(2, int(x ** 0.5) + 1)))

print("\n👉 Lambda + reduce：")
print("6 的阶乘 =", fac(6))         # 720
print("37 是否为素数：", is_prime(37))  # True


# =======================
# 五、偏函数 partial() 作用：固定某些参数，返回一个新的函数
# =======================
from functools import partial
import os

print("\n👉 偏函数 partial 示例：")

# 示例1：固定参数
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
print("3 的平方 =", square(3))  # 输出：9

# 示例2：二进制字符串转整数
int2 = partial(int, base=2)
print("二进制 '1010101' =", int2('1010101'))  # 输出：85

# 示例3：固定目录路径拼接
def path_join(dest, folder):
    return os.path.join(dest, folder)

dest_join = partial(path_join, './dest')
print(dest_join('images'))  # 输出：./dest/images

