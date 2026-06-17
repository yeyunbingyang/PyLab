'''
============================================================
 文件追加: open(mode='a') + 二进制读写
============================================================
对照笔记: 1.文件读写和异常处理.md — a 追加 / b 二进制
============================================================
'''

# ═══════════════════════════════════════════════════════════════
# 1. mode='a' — 追加写（不截断，写入到文件末尾）
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【追加 mode='a'】")
print("=" * 50)

f = open('test_append.txt', mode='a', encoding='utf-8')
f.write('第一行追加\n')
f.write('第二行追加\n')
a_list = ['a\n', 'bb\n', 'ccc\n']
f.writelines(a_list)
f.close()
print("  已追加到 test_append.txt")

# 验证追加内容
f = open('test_append.txt', mode='r', encoding='utf-8')
print("  文件当前内容:")
print(f.read().rstrip())
f.close()

# ═══════════════════════════════════════════════════════════════
# 2. mode='rb' / 'wb' — 二进制读写
#    read/write 的参数和返回值是 bytes 对象
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【二进制读写 rb / wb】")
print("=" * 50)

# 创建二进制文件演示
data = b'Hello, Binary World!\x00\x01\x02'
with open('test_binary.bin', 'wb') as f:
    f.write(data)
print(f"  写入二进制数据: {data}")

# 读取二进制
with open('test_binary.bin', 'rb') as f:
    result = f.read()
    print(f"  读取二进制数据: {result}")

# ═══════════════════════════════════════════════════════════════
# 3. 分块读取文件（大文件拷贝）
#    避免一次性全部读入内存
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【分块读取 — 大文件友好】")
print("=" * 50)

def copy_file_chunked(src, dst, chunk_size=1024):
    """分块拷贝文件 — 避免内存爆炸"""
    with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
        while True:
            chunk = f_src.read(chunk_size)
            if not chunk:
                break
            f_dst.write(chunk)
    return True

# 用当前脚本自身做演示
import os
src = __file__
dst = 'code03_copy.py'
ok = copy_file_chunked(src, dst)
print(f"  复制 {os.path.basename(src)} → {dst} : {'✓' if ok else '✗'}")
print(f"  源大小: {os.path.getsize(src)} 字节")
print(f"  目标大小: {os.path.getsize(dst)} 字节")

# 清理演示文件
os.remove(dst)
