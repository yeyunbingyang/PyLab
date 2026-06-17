"""============================================================
 graphic/shapes/circle.py —— 嵌套包中的圆形模块
============================================================
知识点: 嵌套包的导入方式
  import graphic.shapes.circle
  from graphic.shapes import circle
============================================================"""

import math


def area(radius):
    return math.pi * radius * radius


def circumference(radius):
    return 2 * math.pi * radius


def info():
    return "graphic.shapes.circle —— 嵌套包示例"


if __name__ == "__main__":
    print(f"area(3) = {area(3):.2f}")
