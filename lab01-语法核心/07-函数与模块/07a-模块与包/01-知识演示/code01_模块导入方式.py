"""============================================================
 code01_模块导入方式.py
============================================================
覆盖笔记知识点:
  - import 模块名          (全部导入)
  - import 模块名 as 别名   (别名导入)
  - from 模块名 import 成员 (局部导入)
  - from 模块名 import *    (全部导入-不推荐)
  - 同名函数覆盖问题与别名解决方案
  - 模块搜索顺序 (sys.path)
  - __name__ 变量
============================================================"""

# ═══════════════════════════════════════════════════════════════
# 1. import 模块名 —— 全部导入
#    通过 模块名.成员名 访问，多次 import 只导入一次
# ═══════════════════════════════════════════════════════════════
import modules.module_a as mod_a
import modules.module_b as mod_b

print("=" * 50)
print("【1】 import 模块名 —— 完全限定名区分同名函数")
print("=" * 50)

# 同名 greet 函数，行为不同
print(f'  mod_a.greet("张三") → {mod_a.greet("张三")}')
print(f'  mod_b.greet("张三") → {mod_b.greet("张三")}')

# 同名 multi 函数
print(f'  mod_a.multi(3, 4)   → {mod_a.multi(3, 4)}')
print(f'  mod_b.multi(3, 4)   → {mod_b.multi(3, 4)}')

# 同名 PI 变量，值不同
print(f'  mod_a.PI  = {mod_a.PI}')
print(f'  mod_b.PI  = {mod_b.PI}')

# ═══════════════════════════════════════════════════════════════
# 2. import 模块名 as 别名
#    简化调用名，适合长模块名
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【2】 import ... as 别名")
print("=" * 50)
import modules.module_a as utils

print(f"  utils.add(1, 2)    = {utils.add(1, 2)}")
print(f"  utils.sub(10, 4)   = {utils.sub(10, 4)}")
print(f"  utils.area_of_circle(5) = {utils.area_of_circle(5):.2f}")

# ═══════════════════════════════════════════════════════════════
# 3. from 模块名 import 成员 —— 局部导入
#    只导入需要的，直接通过成员名访问；未导入的不能用
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【3】 from ... import 成员（局部导入）")
print("=" * 50)
from modules.module_a import add, sub, PI

print(f"  add(3, 5)  = {add(3, 5)}")
print(f"  sub(10, 4) = {sub(10, 4)}")
print(f"  PI         = {PI}")
# print(divide(10, 2))   ❌ NameError: name 'divide' is not defined

# 重名问题: 后一次导入覆盖前一次
print()
print("--- 重名变量覆盖 ---")
from modules.module_b import multi   # 覆盖 module_a 的 multi
print(f"  multi(3, 4) = {multi(3, 4)}  ← module_b 的 multi")

# 别名解决方案
print()
print("--- 别名区分同名变量 ---")
from modules.module_a import PI as PI_a
from modules.module_b import PI as PI_b
print(f"  PI_a (module_a) = {PI_a}")
print(f"  PI_b (module_b) = {PI_b}")

# ═══════════════════════════════════════════════════════════════
# 4. from 模块名 import * —— 全部导入（不推荐）
#    导入所有不以 _ 开头的成员，直接访问，易造成命名冲突
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【4】 from ... import * （不推荐）")
print("=" * 50)
from modules.module_a import *
print(f"  add(1, 2)            = {add(1, 2)}")
print(f"  area_of_circle(2)    = {area_of_circle(2):.2f}")

# ═══════════════════════════════════════════════════════════════
# 5. 模块搜索顺序
#    当前目录 → PYTHONPATH → 标准库 → site-packages
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【5】 模块搜索顺序 (sys.path)")
print("=" * 50)
import sys
print("  搜索路径:")
for i, p in enumerate(sys.path[:5]):
    print(f"    [{i}] {p}")
print("  ... (共 {} 个路径)".format(len(sys.path)))
print()
print("  临时添加路径:  sys.path.append('./..')")
print("  永久添加:      设置 PYTHONPATH 环境变量")

# ═══════════════════════════════════════════════════════════════
# 6. __name__ 变量
#    直接运行: __name__ == '__main__'
#    被导入:   __name__ == 模块名
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【6】 __name__ 变量")
print("=" * 50)
print(f"  当前: __name__ = {__name__}")
print("  直接运行  → '__main__'")
print("  被导入时  → 模块文件名")
print()
print("  典型用法:")
print("    if __name__ == '__main__':")
print("        测试代码  # 只在直接运行时执行")

