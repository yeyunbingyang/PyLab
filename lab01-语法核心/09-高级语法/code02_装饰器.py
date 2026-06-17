# 装饰器：在不修改原函数的前提下，给函数添加额外功能
# 本质：接收函数作为参数，返回一个新函数

import time
import functools

# === 无参装饰器 ===
def timer(func):
    '''测量函数执行时间的装饰器'''
    @functools.wraps(func)   # 保留原函数的元信息
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'{func.__name__} 执行耗时: {end - start:.6f} 秒')
        return result
    return wrapper

@timer
def slow_func(n):
    total = 0
    for i in range(n):
        total += i ** 2
    return total

print(slow_func(1000000))  # 自动打印耗时

# === 带参装饰器 ===
def repeat(times):
    '''重复执行函数 times 次的装饰器'''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f'Hello, {name}!')

greet('World')  # 打印 3 次

# === 类装饰器 ===
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f'{self.func.__name__} 被调用了 {self.count} 次')
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print('Hi!')

say_hi()
say_hi()
say_hi()
