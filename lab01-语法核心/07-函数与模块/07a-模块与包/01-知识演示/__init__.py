"""
======================================================================
  07a-模块与包 —— 知识演示
======================================================================
基于笔记「01 模块和包.md」知识点的可运行示例代码

运行方式:
  cd 01-知识演示
  python code01_模块导入方式.py
  python code02___all__变量演示.py
  python code03_包的使用.py
  python code04_标准库总览.py

目录结构:
  modules/              # 被导入的示例模块
    module_a.py         # 模块基本概念 (PI, add, sub, greet...)
    module_b.py         # 同名函数区分 (PI, multi, greet...)
    module_calc.py      # __all__ 用法示例
  graphic/              # 包示例
    circle.py           # 圆形模块
    rectangle.py        # 矩形模块
    triangle.py         # 三角形模块 (不在 __all__ 中)
    shapes/             # 嵌套子包
      circle.py

知识点覆盖:
  code01_模块导入方式.py     → 5种导入方式 + 同名区分 + 搜索顺序 + __name__
  code02___all__变量演示.py   → __all__ 控制 import *
  code03_包的使用.py         → 包/嵌套包/__init__.py
  code04_标准库总览.py       → math/random/time/datetime/os/sys/re/json/urllib

  ※ socket 演示见 ../03-常用模块/code07_server.py / code08_client.py
======================================================================
"""

