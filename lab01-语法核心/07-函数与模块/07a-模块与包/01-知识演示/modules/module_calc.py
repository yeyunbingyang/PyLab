"""============================================================
 module_calc.py —— 知识点: __all__ 变量
============================================================
__all__ 设置 from xxx import * 时哪些成员可被导入
对 from ... import 具体成员 无效

运行:  from module_calc import *   → 只能导入 add, sub
       from module_calc import multi, divide  → 仍可导入
============================================================"""

__all__ = ["add", "sub"]

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def multi(a, b):
    """不在 __all__ 中，from xxx import * 无法导入"""
    return a * b

def divide(a, b):
    """不在 __all__ 中"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


if __name__ == "__main__":
    print("=== module_calc 自测 ===")
    print(f"__all__ = {__all__}")
    print(f"add(3,5)     = {add(3, 5)}")
    print(f"sub(10,4)    = {sub(10, 4)}")
    print(f"multi(3,7)   = {multi(3, 7)}")
    print(f"divide(10,2) = {divide(10, 2)}")
    print()
    print("from module_calc import *  → 只能 add, sub")
    print("from module_calc import multi, divide → 仍可导入")
