"""============================================================
 graphic/rectangle.py —— 矩形模块
============================================================"""


def area(width, height):
    """矩形面积 = 宽 × 高"""
    return width * height


def perimeter(width, height):
    """矩形周长 = 2 × (宽 + 高)"""
    return 2 * (width + height)


if __name__ == "__main__":
    print(f"rectangle.area(4, 6)      = {area(4, 6)}")
    print(f"rectangle.perimeter(4, 6) = {perimeter(4, 6)}")
