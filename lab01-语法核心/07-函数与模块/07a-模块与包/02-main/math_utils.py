"""
math_utils 模块
用于提供一些常用的数学计算函数示例。
"""

# 模块变量（相当于全局常量）
PI = 3.1415926

# 模块函数
def add(a, b):
    """返回两个数的和"""
    return a + b

def sub(a, b):
    """返回两个数的差"""
    return a - b

def area_of_circle(r):
    """根据半径计算圆的面积"""
    return PI * r * r

# 模块中的执行逻辑
if __name__ == "__main__":
    # 当直接运行该模块文件时执行的代码
    print("当前模块名："+__name__)
    print("模块被直接运行")
    print(f"半径为2的圆面积：{area_of_circle(2)}")
else:
    # 当被导入时不会执行
    print("math_utils 模块被导入")
    print("导入模块名："+__name__)

