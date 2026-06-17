"""
异常（Exception）是程序在运行时遇到的错误。
例如除以0、访问不存在的索引、打开不存在的文件等情况。

本示例展示 Python 中的常见异常类型、try-except结构的使用、
raise语句手动抛出异常，以及finally清理机制。
"""

# 一、常见异常类型举例
print("===== 一、常见异常演示 =====")
try:
    result = 10 / 0  # ZeroDivisionError：除数为0
except ZeroDivisionError as e:
    print("出现异常：", e)

try:
    numbers = [1, 2, 3]
    print(numbers[5])  # IndexError：下标越界
except IndexError as e:
    print("出现异常：", e)

try:
    person = {"name": "Alice"}
    print(person["age"])  # KeyError：key不存在
except KeyError as e:
    print("出现异常：", e)

# try:
#     print(undeclared_variable)  # NameError：变量未定义
# except NameError as e:
#     print("出现异常：", e)

print()  # 空行分隔输出


# 二、try-except-else-finally 结构
print("===== 二、try-except-else-finally 结构演示 =====")
try:
    num = int(input("请输入一个整数："))
    result = 100 / num
except ZeroDivisionError:
    print("错误：除数不能为0！")
except ValueError:
    print("错误：请输入正确的整数！")
else:
    print(f"计算结果为：{result}")
finally:
    print("程序执行完毕，无论是否出错都会执行 finally 块。")

print()


# 三、多个异常合并处理
print("===== 三、多个异常合并处理 =====")
try:
    a = int("abc")  # ValueError
    b = 10 / 0      # ZeroDivisionError（不会执行到）
except (ValueError, ZeroDivisionError) as e:  # 是或的关系、有顺序
    print("捕获到异常：", e)
print()


# 四、手动抛出异常 raise
print("===== 四、raise 主动抛出异常 =====")

def divide(a, b):
    """手动检测除数是否为0，如果是，则主动抛出异常"""
    if b == 0:
        raise ZeroDivisionError("除数不能为0（手动抛出）")
    return a / b

try:
    print(divide(10, 0))
except ZeroDivisionError as e:
    print("捕获到手动抛出的异常：", e)

print()


# 五、自定义异常类（可选进阶）
print("===== 五、自定义异常类 =====")

class AgeError(Exception):
    """自定义异常：年龄错误"""
    def __init__(self, age, message="年龄必须在0~150之间"):
        self.age = age
        self.message = message
        super().__init__(self.message)

def set_age(age):
    if age < 0 or age > 150:
        raise AgeError(age)
    print(f"年龄设置成功：{age}")

try:
    set_age(200)
except AgeError as e:
    print(f"捕获到自定义异常：{e}（输入年龄：{e.age}）")

print("\n=== 程序正常结束 ===")
