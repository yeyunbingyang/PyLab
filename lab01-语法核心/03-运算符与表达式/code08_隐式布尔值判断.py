# 数字类型 0, 0.0, 0j
if 0:
    print("这不会执行")
if 3.14:
    print("浮点数非零视为 True")

# 字符串类型 ""（空字符串）
name = ""
if not name:
    print("空字符串为 False")

# 列表类型 []（空列表）
items = []
if items:
    print("有内容")
else:
    print("空列表为 False")

# 字典类型 {}（空字典）
config = {}
if not config:
    print("空字典为 False")

# None
data = None
if data:
    print("有数据")
else:
    print("data 是 None，为 False")
