# 生成器：用 yield 关键字定义的函数，惰性产出值——省内存
# yield：暂停函数，返回一个值，下次调用从暂停处继续

# === 基本生成器 ===
def count_up_to(n):
    i = 1
    while i <= n:
        yield i
        i += 1

gen = count_up_to(3)
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3

# === 斐波那契生成器 ===
def fibonacci(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

print(list(fibonacci(100)))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# === 生成器表达式（类似列表推导式但惰性） ===
squares = (x ** 2 for x in range(5))
print(list(squares))  # [0, 1, 4, 9, 16]

# === 大文件逐行处理（内存友好） ===
def read_large_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 用法: for line in read_large_file('big_file.txt'): process(line)

# === yield from：委托给子生成器 ===
def chain_generators(*gens):
    for gen in gens:
        yield from gen   # 等价于 for x in gen: yield x

g1 = (x for x in range(3))
g2 = (x for x in range(3, 6))
print(list(chain_generators(g1, g2)))  # [0, 1, 2, 3, 4, 5]

# === 生成器内存对比 ===
import sys
lst = [i for i in range(1000000)]
gen = (i for i in range(1000000))
print(f'列表内存: {sys.getsizeof(lst):,} bytes')
print(f'生成器内存: {sys.getsizeof(gen):,} bytes')  # 固定 ~200 bytes！
