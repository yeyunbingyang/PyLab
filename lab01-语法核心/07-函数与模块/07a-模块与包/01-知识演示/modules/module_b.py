"""============================================================
 module_b.py —— 知识点: 同名函数区分
============================================================
不同模块中可以有同名函数/变量
通过 import 导入后使用"完全限定名" (模块名.函数名) 区分
============================================================"""

PI = 3.14
author = "module_b"

def multi(a, b):
    """两数之积 —— 与 module_a 同名"""
    return a * b

def greet(name):
    """module_b 的问候 —— 与 module_a 同名但行为不同"""
    return f"[module_b] Hello, {name}!"

def power(base, exp):
    """base 的 exp 次方"""
    return base ** exp


if __name__ == "__main__":
    print("=== module_b 自测 ===")
    print(f"PI         = {PI}")
    print(f"multi(3,7) = {multi(3, 7)}")
    print(f"greet('小明') = {greet('小明')}")
    print(f"power(2,10) = {power(2, 10)}")
