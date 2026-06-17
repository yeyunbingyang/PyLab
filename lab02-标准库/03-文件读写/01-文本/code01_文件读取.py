'''
============================================================
 文件读取: open + read/readline/readlines
============================================================
对照笔记: 1.文件读写和异常处理.md — 打开文件 / 读取文本
============================================================
'''

import os

# ═══════════════════════════════════════════════════════════════
# 1. open() 打开文件
#    mode='r'  只读（默认）
#    encoding 指定字符编码（文本文件必须）
# ═══════════════════════════════════════════════════════════════
path = os.getcwd()
filename = os.path.join(path, 'test.txt')
print(f"当前目录: {path}")
print(f"文件路径: {filename}")
print()

# 创建演示文件（如果不存在）
if not os.path.exists(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('第一行: Python 文件操作\n')
        f.write('第二行: read/readline/readlines\n')
        f.write('第三行: 文件读取的三种方式\n')

# ═══════════════════════════════════════════════════════════════
# 2. read(n) — 读取指定字符数
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【read(n) — 读取指定字符数】")
print("=" * 50)
f = open(filename, mode='r', encoding='utf-8')
content = f.read(10)       # 读取前 10 个字符
print(f"  f.read(10) → {content}")
f.close()

# ═══════════════════════════════════════════════════════════════
# 3. read() — 读取全部内容
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【read() — 读取全部】")
print("=" * 50)
f = open(filename, mode='r', encoding='utf-8')
content = f.read()
print(f"  f.read() →\n{content}")
f.close()

# ═══════════════════════════════════════════════════════════════
# 4. readline() — 逐行读取
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【readline() — 逐行读取】")
print("=" * 50)
f = open(filename, mode='r', encoding='utf-8')
print(f"  第1行: {f.readline().strip()}")
print(f"  第2行: {f.readline().strip()}")
print(f"  第3行: {f.readline().strip()}")
f.close()

# ═══════════════════════════════════════════════════════════════
# 5. readlines() — 读取所有行到列表
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【readlines() — 读取所有行到列表】")
print("=" * 50)
f = open(filename, mode='r', encoding='utf-8')
lines = f.readlines()
print(f"  f.readlines() → {lines}")
for i, line in enumerate(lines):
    print(f"  行{i+1}: {line.strip()}")
f.close()

# ═══════════════════════════════════════════════════════════════
# 6. 遍历文件对象（推荐方式）
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【直接遍历文件对象（推荐）】")
print("=" * 50)
f = open(filename, mode='r', encoding='utf-8')
for line in f:
    print(f"  → {line.strip()}")
f.close()

print()
print("总结: read(n) 指定字符 | read() 全读 | readline() 单行 | readlines() 列表 | 直接遍历最省内存")
