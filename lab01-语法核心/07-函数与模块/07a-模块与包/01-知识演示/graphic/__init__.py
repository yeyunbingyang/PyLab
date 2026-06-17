"""============================================================
 graphic/__init__.py
============================================================
知识点: 包的 __init__.py —— 标识文件夹为 Python 包
  __all__ = ["circle", "rectangle"] 控制 from graphic import *
  triangle 不在 __all__ 中，from graphic import * 不会导入
============================================================"""

__all__ = ["circle", "rectangle"]

print(f"[graphic 包加载, __name__ = {__name__}]")
