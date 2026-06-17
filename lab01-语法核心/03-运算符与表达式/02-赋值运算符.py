print("\n=== 赋值与复合赋值 ===")
a = 10
b = 3
a += b        # 相当于 a = a + b → 13
a *= a + 2    # 相当于 a = a * (a + 2) → 13 * 15 = 195
print("a =", a)

print("\n=== 海象运算符 ===")
# 普通赋值不能直接放在表达式中，会报错
# print((a = 10))  # SyntaxError

# 使用海象运算符可在表达式中赋值
print((a := 10))  # 输出 10
print("a =", a)

# 典型应用：在循环或条件中使用
print("=== 海象运算符应用示例 ===")
while (num := int(input("输入数字(0退出)："))) != 0:
    print("你输入了：", num)
print("循环结束")