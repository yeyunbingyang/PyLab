"""============================================================
 02-__all__变量演示.py
============================================================
覆盖笔记知识点:
  - __all__ 控制 from xxx import * 的行为
  - __all__ 只对 import * 有效
  - from xxx import 具体成员 不受 __all__ 限制
============================================================"""

print("=" * 50)
print("【__all__ 变量】")
print("=" * 50)

# ── 实验 1: from module_calc import * ──
# module_calc.__all__ = ["add", "sub"]
# 所以只导入 add 和 sub
print()
print("── 实验1: from module_calc import *")
from modules.module_calc import *

print(f"  add(3, 5)  = {add(3, 5)}    ✅ 在 __all__ 中")
print(f"  sub(10, 4) = {sub(10, 4)}    ✅ 在 __all__ 中")
# print(multi(3, 7))   ❌ NameError: 不在 __all__ 中
# print(divide(10, 2)) ❌ NameError: 不在 __all__ 中

# ── 实验 2: from module_calc import multi, divide ──
# 显式导入不受 __all__ 限制
print()
print("── 实验2: from module_calc import multi, divide（显式导入不受限）")
from modules.module_calc import multi, divide

print(f"  multi(3, 7)   = {multi(3, 7)}    ✅ 显式导入")
print(f"  divide(10, 2) = {divide(10, 2)}    ✅ 显式导入")

# ── 实验 3: import module_calc 不受限制 ──
print()
print("── 实验3: import module_calc（import 不受限）")
import modules.module_calc as mc
print(f"  mc.multi(3, 7)   = {mc.multi(3, 7)}")
print(f"  mc.divide(10, 2) = {mc.divide(10, 2)}")

# ── 总结 ──
print()
print("── 总结 ──")
print("  from xxx import *     → 只导入 __all__ 中的成员")
print("  from xxx import 成员  → 不受 __all__ 限制")
print("  import xxx            → 不受 __all__ 限制")

if __name__ == "__main__":
    pass  # 演示代码在模块顶层执行