"""============================================================
 graphic/circle.py —— 圆形模块
============================================================"""

import math

PI = 3.1415926


def area(radius):
    """圆的面积 = πr²"""
    return PI * radius * radius


def circumference(radius):
    """圆的周长 = 2πr"""
    return 2 * PI * radius


if __name__ == "__main__":
    print(f"circle.area(5)          = {area(5):.2f}")
    print(f"circle.circumference(5) = {circumference(5):.2f}")
