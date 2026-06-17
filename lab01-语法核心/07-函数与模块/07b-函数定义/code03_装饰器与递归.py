"""
功能说明：
    演示 Python 装饰器与递归调用的核心用法。
    包含 functools.wraps、__wrapped__、lru_cache 等高级特性。
"""

# functools.wraps函数主要用于在定义装饰器时保留被装饰函数的元数据（如函数名、文档字符串等），以避免装饰器对原函数造成不必要的影响。
from functools import wraps, lru_cache


# =========================================================
# 一、装饰器基础：保留原函数信息 + 取消装饰效果
# =========================================================

def my_decorator(func):  # my_decorator 是一个装饰器工厂函数
    """
    自定义装饰器：
    - 在函数调用前后打印提示信息。
    - 使用 @wraps(func) 确保保留被装饰函数的元数据（__name__、__doc__ 等）。
    """
    @wraps(func)
    def wrapper(*args, **kwargs):  # wrapper 是实际的包装函数，负责添加额外功能 使用 *args, **kwargs 确保能处理任意参数
        print(">>> 装饰器开始执行：before function call")
        result = func(*args, **kwargs)
        print("<<< 装饰器执行结束：after function call")
        return result
    return wrapper


@my_decorator
def say_hello(name):
    """这个函数会向指定的人打招呼"""
    print(f"Hello, {name}!")


print("=" * 60)
print("【装饰器演示】")

# 调用被装饰的函数
say_hello("Alice")

# 查看被装饰函数的元信息
print(f"函数名: {say_hello.__name__}")
print(f"文档字符串: {say_hello.__doc__}")

# 访问原函数（取消装饰器效果）
original_func = say_hello.__wrapped__
print(">>> 调用原始函数（未被装饰）:")
original_func("Bob")


# =========================================================
# 二、递归调用：计算阶乘
# =========================================================

print("\n" + "=" * 60)
print("【递归调用示例 - 阶乘】")


def fac(num):
    """
    递归实现阶乘：
    fac(n) = n * fac(n - 1)
    递归终止条件：当 n == 0 或 1 时返回 1。
    """
    if num in (0, 1):       # 收敛条件：停止递归
        return 1
    return num * fac(num - 1)


print(f"5! = {fac(5)}")  # 输出 120


# =========================================================
# 三、递归调用：生成斐波那契数列
# =========================================================

print("\n" + "=" * 60)
print("【递归调用示例 - 斐波那契数列】")


def fib1(n):
    """递归版斐波那契：f(n) = f(n-1) + f(n-2)"""
    if n in (1, 2):   # 终止条件
        return 1
    return fib1(n - 1) + fib1(n - 2)


print("前 10 个斐波那契数（递归方式）:")
for i in range(1, 11):
    print(fib1(i), end=" ")
print()


# =========================================================
# 四、优化递归：使用 lru_cache 缓存结果
# =========================================================

print("\n" + "=" * 60)
print("【使用 lru_cache 优化递归性能】")


@lru_cache(maxsize=None)  # 自动缓存函数结果
def fib2(n):
    """带缓存的递归版斐波那契"""
    if n in (1, 2):
        return 1
    return fib2(n - 1) + fib2(n - 2)


print("前 20 个斐波那契数（lru_cache 优化）:")
for i in range(1, 21):
    print(fib2(i), end=" ")
print()


# =========================================================
# 五、递归陷阱：栈溢出问题演示（谨慎执行）
# =========================================================

import sys
print("\n" + "=" * 60)
print("【递归深度与栈溢出】")

# 查看当前递归最大深度
print(f"系统默认递归深度限制：{sys.getrecursionlimit()}")

# 说明：可以通过 setrecursionlimit 修改，但不推荐！
# sys.setrecursionlimit(2000)

# 如果执行 fac(5000) 会触发 RecursionError：
# RecursionError: maximum recursion depth exceeded
# print(fac(5000))

print("（提示）递归层数过深可能导致栈溢出，应避免无终止条件的递归。")


# =========================================================
# 六、非递归版本的斐波那契（推荐做法）
# =========================================================

print("\n" + "=" * 60)
print("【非递归版斐波那契（性能更好）】")


def fib_iter(n):
    """迭代实现斐波那契数列"""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print("前 20 个斐波那契数（迭代方式）:")
for i in range(1, 21):
    print(fib_iter(i), end=" ")
print("\n")

