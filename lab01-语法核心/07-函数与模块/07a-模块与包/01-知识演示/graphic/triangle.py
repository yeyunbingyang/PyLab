"""============================================================
 graphic/triangle.py —— 三角形模块
============================================================
未列入 __init__.py 的 __all__
from graphic import * 不会导入本模块
但 from graphic import triangle 仍然可以
============================================================"""

import math


def area(a, b, c):
    """三角形面积 (海伦公式)"""
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def perimeter(a, b, c):
    """三角形周长 = a + b + c"""
    return a + b + c


if __name__ == "__main__":
    print(f"triangle.area(3, 4, 5)       = {area(3, 4, 5):.2f}")
    print(f"triangle.perimeter(3, 4, 5)  = {perimeter(3, 4, 5)}")
