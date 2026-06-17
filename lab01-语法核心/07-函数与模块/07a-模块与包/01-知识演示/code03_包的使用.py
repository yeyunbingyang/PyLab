"""============================================================
 03-包的使用.py
============================================================
覆盖笔记知识点:
  - 包（Package）: 含 __init__.py 的文件夹
  - __init__.py 的作用
  - import 包.模块
  - from 包 import 模块
  - from 包.模块 import 成员
  - __init__.py 中的 __all__ 控制 import *
  - 嵌套包（子包）
============================================================"""

# ═══════════════════════════════════════════════════════════════
# 1. 包的基本导入方式
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【1】 import 包.模块")
print("=" * 50)
import graphic.circle as circle_mod
import graphic.rectangle as rect_mod

print(f"  circle_mod.area(5)     = {circle_mod.area(5):.2f}")
print(f"  circle_mod.circumference(5) = {circle_mod.circumference(5):.2f}")
print(f"  rect_mod.area(4, 6)    = {rect_mod.area(4, 6)}")

# ═══════════════════════════════════════════════════════════════
# 2. from 包 import 模块
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【2】 from 包 import 模块")
print("=" * 50)
from graphic import triangle

print(f"  triangle.area(3, 4, 5)       = {triangle.area(3, 4, 5):.2f}")
print(f"  triangle.perimeter(3, 4, 5)  = {triangle.perimeter(3, 4, 5)}")

# ═══════════════════════════════════════════════════════════════
# 3. from 包.模块 import 成员 —— 直接访问函数
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【3】 from 包.模块 import 成员")
print("=" * 50)
from graphic.circle import area as circle_area, circumference

print(f"  circle_area(3)      = {circle_area(3):.2f}")
print(f"  circumference(3)    = {circumference(3):.2f}")

# ═══════════════════════════════════════════════════════════════
# 4. __init__.py 中的 __all__ 控制 import *
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【4】 __init__.py 的 __all__")
print("=" * 50)
# graphic/__init__.py: __all__ = ["circle", "rectangle"]
from graphic import *
print("  from graphic import *")
print("    → circle    ✅ (在 __all__ 中)")
print("    → rectangle ✅ (在 __all__ 中)")
print("    → triangle  ❌ (不在 __all__ 中)")
# 但显式导入仍然可以:
# from graphic import triangle  ✅

# ═══════════════════════════════════════════════════════════════
# 5. 嵌套包（子包）
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【5】 嵌套包")
print("=" * 50)
import graphic.shapes.circle as nested_circle

print(f"  nested_circle.area(3)        = {nested_circle.area(3):.2f}")
print(f"  nested_circle.circumference(3)= {nested_circle.circumference(3):.2f}")
print(f"  nested_circle.info()")
print()
print("  包结构:")
print("    graphic/")
print("    ├── __init__.py")
print("    ├── circle.py")
print("    ├── rectangle.py")
print("    ├── triangle.py")
print("    └── shapes/         ← 子包")
print("        ├── __init__.py")
print("        └── circle.py")

if __name__ == "__main__":
    pass  # 演示代码在模块顶层执行