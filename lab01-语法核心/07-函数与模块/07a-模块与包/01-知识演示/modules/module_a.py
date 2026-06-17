"""============================================================
 module_a.py —— 知识点: 模块基本概念
============================================================
模块（module）：一个 .py 文件即为一个模块
模块 = "功能文件" / "工具包"，含变量、函数、类等
模块名区分大小写，不能与 Python 标准模块重名
============================================================"""

PI = 3.1415926
author = "module_a"

def add(a, b):
    """两数之和"""
    return a + b

def sub(a, b):
    """两数之差"""
    return a - b

def multi(a, b):
    """两数之积"""
    return a * b

def divide(a, b):
    """两数之商"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

def area_of_circle(radius):
    """圆面积 = PI * r²"""
    return PI * radius * radius

def greet(name):
    """module_a 的问候"""
    return f"[module_a] 你好, {name}!"


# ===== __name__ 用法 =====
if __name__ == "__main__":
    print("=== module_a 自测 ===")
    print(f"PI        = {PI}")
    print(f"add(3,5)  = {add(3, 5)}")
    print(f"sub(10,4) = {sub(10, 4)}")
    print(f"multi(3,7)= {multi(3, 7)}")
    print(f"divide(10,2) = {divide(10, 2)}")
    print(f"area_of_circle(3) = {area_of_circle(3):.2f}")
    print(f"greet('小明') = {greet('小明')}")
