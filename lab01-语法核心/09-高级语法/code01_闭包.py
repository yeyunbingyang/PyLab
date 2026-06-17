# 闭包：函数内部定义函数，内层函数引用外层变量，外层函数返回内层函数 【白话 函数可】
# 作用：数据封装、装饰器基础、延迟计算

# === 基本闭包 ===
def outer(x):
    def inner(y):
        return x + y   # inner 引用了 outer 的变量 x
    return inner       # outer 返回 inner 函数本身

add_5 = outer(5)       # add_5 是一个闭包，记住了 x=5
print(add_5(3))        # 8
print(add_5(10))       # 15

# === 闭包保存状态 ===
def make_counter(start=0):
    count = [start]    # 用列表包装可变状态
    def counter():
        count[0] += 1
        return count[0]
    return counter

c1 = make_counter()
print(c1())  # 1
print(c1())  # 2
print(c1())  # 3

c2 = make_counter(100)
print(c2())  # 101 — 独立状态
