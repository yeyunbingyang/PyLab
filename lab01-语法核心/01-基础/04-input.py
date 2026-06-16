# ===============================
# Python input() 用户输入与类型转换示例
# ===============================

# ========== 任务1：输入并输出字符串 ==========
name = input("请输入你的名字：")  # 默认返回字符串类型
print("你的名字是：", name)
print(type(name))  # <class 'str'>

# ========== 任务2：输入年龄并计算出生年份 ==========
age = input("请输入你的年龄：")
# input() 默认返回字符串，需要转换为整数
try:
    age = int(age)
    year = 2024
    birth = year - age
    print("你的出生年份是：", birth)
except ValueError:
    print("输入的年龄无效，请输入数字。")

# 说明：
# 1. input() 录入的永远是字符串类型
# 2. 在需要数学计算时，必须进行类型转换（int、float 等）

# ========== 任务3：输入反馈（可留空） ==========
response = input("请输入您的反馈（可留空）：")
if response:
    print("您输入的反馈是：", response)
else:
    print("您没有输入任何反馈。")

# ========== 任务4：数字输入与表达式计算 ==========
# （展示 float() 与 eval() 的区别）

# --- 使用 float() 进行安全的数字输入 ---
number = input("请输入一个数字（例如 3.14）：")
try:
    number = float(number)  # 转换为浮点数
    print("您输入的数字是：", number)
except ValueError:
    print("输入无效，请输入一个有效的数字。")

# --- 使用 eval() 计算数学表达式 ---
# ⚠ eval() 可执行任意 Python 代码，存在安全隐患！
expression = input("请输入一个数学表达式（如 2 + 3 * 4）：")
try:
    result = eval(expression)  # 计算表达式的值
    print("您输入的表达式结果是：", result)
except (SyntaxError, NameError):
    print("输入无效，请输入一个有效的数学表达式。")
except Exception as e:
    print("发生错误：", e)

# ===============================
# 注意事项
# ===============================
"""
● input() 始终返回字符串类型，无论用户输入什么。
● 进行类型转换时，需确保输入格式正确，否则会引发 ValueError。
● float()、int() 用于安全的数值转换。
● eval() 能计算表达式，但有安全风险，禁止用于不可信输入。
● Python 2.x 中：
    - input() 会执行表达式求值；
    - raw_input() 才是纯字符串输入。
    - Python 3.x 已统一为 input()。
"""

# ===============================
# 总结
# ===============================
"""
input() 是 Python 获取用户输入的核心函数。
通过配合类型转换（int/float/eval）与异常处理（try...except），
可以安全地接收用户输入并执行对应逻辑。
"""
