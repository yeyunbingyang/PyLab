# ================================================
# Python 类型检查示例：type() 与 isinstance()
# ================================================

# ========== 示例 1：使用 type() 检查类型 ==========
print("=== 示例1：type() 检查类型 ===")
value = 10

if type(value) == int:
    print("value 是整数")
elif type(value) == float:
    print("value 是浮点数")
elif type(value) == str:
    print("value 是字符串")
else:
    print("value 是其他类型")

# 说明：
# type() 比较的是“精确类型”，不会考虑继承关系。
# 如果一个类继承自 int，那么 type(对象) == int 将返回 False。


# ========== 示例 2：使用 isinstance() 检查类型 ==========
print("\n=== 示例2：isinstance() 检查类型 ===")
value = 10.5

if isinstance(value, int):
    print("value 是整数")
elif isinstance(value, float):
    print("value 是浮点数")
elif isinstance(value, str):
    print("value 是字符串")
else:
    print("value 是其他类型")

# 说明：
# isinstance(obj, 类型) 可以判断一个对象是否属于指定类型，
# 也可以判断是否属于该类型的子类实例。


# ========== 示例 3：同时检查多个类型 ==========
print("\n=== 示例3：检查多个类型 ===")
value = "Hello"

if isinstance(value, (int, float)):
    print("value 是数字")
elif isinstance(value, str):
    print("value 是字符串")
else:
    print("value 是其他类型")

# 说明：
# isinstance() 可以接收一个类型元组，表示“匹配任意一个类型即可”。


# ========== 示例 4：继承关系中的区别 ==========
print("\n=== 示例4：继承关系示例 ===")

# 定义一个父类与子类
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()

# 使用 type()
if type(dog) == Animal:
    print("type(): dog 是 Animal 类型")
else:
    print("type(): dog 不是 Animal 类型")

# 使用 isinstance()
if isinstance(dog, Animal):
    print("isinstance(): dog 是 Animal 类型或其子类")
else:
    print("isinstance(): dog 不是 Animal 类型")

# 说明：
# type() 只判断“是否是同一类型”，不会认出继承关系。
# isinstance() 会认出“子类继承自父类”的情况，更常用。


# ================================================
# 小结
# ================================================
"""
✅ type(obj)
   - 精确判断类型（不考虑继承）
   - 适合基础类型判断，如 int、str、float 等
   - 不推荐在复杂对象系统中使用

✅ isinstance(obj, class)
   - 更灵活：支持继承关系
   - 支持多类型检测（isinstance(obj, (int, float))）
   - 推荐用于面向对象编程或类型安全检查

⭐ 实际开发建议：
   - 检查基础数据类型时：isinstance(value, (int, float, str))
   - 检查对象类型时：isinstance(obj, BaseClass)
   - 避免过度依赖类型判断，尽量使用“鸭子类型”（行为判断）
"""
