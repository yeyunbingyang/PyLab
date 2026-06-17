'''
============================================================
 with 上下文管理器 + 异常处理
============================================================
对照笔记: 1.文件读写和异常处理.md
  — with 自动关闭文件（不需要 finally）
  — try/except 处理文件异常
============================================================
'''

# ═══════════════════════════════════════════════════════════════
# 1. with open() — 自动关闭文件
#    离开 with 代码块时自动调用 f.close()
#    等价于 try/finally 但更优雅
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【with open() — 自动关闭】")
print("=" * 50)

# 创建演示文件
with open('test_with.txt', 'w', encoding='utf-8') as f:
    f.write('with 上下文管理器示例\n')
    f.write('自动关闭，无需 f.close()\n')

with open('test_with.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"  读取内容:\n{content}")

print("  (文件已在 with 块结束后自动关闭)")

# ═══════════════════════════════════════════════════════════════
# 2. try/except 异常处理
#    捕获 FileNotFoundError / IOError / UnicodeDecodeError
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【异常处理 try/except】")
print("=" * 50)

# 场景1: 文件不存在
print("\n--- 文件不存在 ---")
try:
    with open('不存在的文件.txt', 'r', encoding='utf-8') as f:
        print(f.read())
except FileNotFoundError:
    print("  ✗ 错误: 文件未找到，请检查路径")

# 场景2: 编码错误
print("\n--- 编码错误 ---")
try:
    with open('test_with.txt', 'r', encoding='gbk') as f:
        print(f.read())
except UnicodeDecodeError:
    print("  ✗ 错误: 编码不匹配，不能用 GBK 读 UTF-8 文件")

# 场景3: 正常文件 + else/finally
print("\n--- try/except/else/finally ---")
try:
    f = open('test_with.txt', 'r', encoding='utf-8')
except FileNotFoundError:
    print("  文件不存在")
else:
    print("  ✓ 文件打开成功 (else 块在 try 成功时执行)")
finally:
    print("  finally 块始终执行 (释放资源)")
    try:
        f.close()
    except:
        pass

# ═══════════════════════════════════════════════════════════════
# 3. 异常处理最佳实践: with + try 组合
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【推荐写法: try + with】")
print("=" * 50)

try:
    with open('test_with.txt', 'r', encoding='utf-8') as f:
        print(f.read())
except FileNotFoundError:
    print('无法打开指定的文件!')
except LookupError:
    print('指定了未知的编码!')
except UnicodeDecodeError:
    print('读取文件时解码错误!')
else:
    print('✓ 文件读取完毕')

print()
print("总结:")
print("  with 替代 try/finally — 自动释放资源")
print("  try/except 处理可预见的异常")
print("  不要用异常机制做正常流程控制")
