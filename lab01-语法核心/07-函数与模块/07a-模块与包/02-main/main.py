"""
main.py 主程序
演示模块的导入与使用。
"""

# 方式一：导入整个模块
import math_utils
print(math_utils.add(3, 5))  # 输出 8
print(math_utils.area_of_circle(3))

# 方式二：导入模块中的部分成员
from math_utils import sub, PI
print(sub(10, 4))  # 输出 6
print(PI)          # 输出 3.1415926

# 方式三：使用别名导入模块
import math_utils as mu
print(mu.area_of_circle(1))


# 方式四：使用 from ... import * 无需使用模块名访问成员
from math_utils import *
print(add(1, 2))



print("当前模块名："+__name__)