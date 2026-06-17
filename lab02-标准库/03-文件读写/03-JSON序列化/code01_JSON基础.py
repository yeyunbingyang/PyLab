'''
============================================================
 JSON 序列化与反序列化
============================================================
对照笔记: 2.json-对象的序列化和反序列化.md
  — json.dumps/dump  Python→JSON
  — json.loads/load  JSON→Python
  — ensure_ascii/indent 参数
  — 自定义序列化 default 参数
  — requests 请求 HTTP API
============================================================
'''

import json
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 1. json.dumps — Python → JSON 字符串
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【json.dumps — Python → JSON 字符串】")
print("=" * 50)

my_dict = {
    'name': '骆昊',
    'age': 40,
    'friends': ['王大锤', '白元芳'],
    'cars': [
        {'brand': 'BMW', 'max_speed': 240},
        {'brand': 'Audi', 'max_speed': 280},
        {'brand': 'Benz', 'max_speed': 280}
    ]
}

# 默认输出（中文会转 Unicode 编码）
print("  默认输出:")
print(f"  {json.dumps(my_dict)[:80]}...")
print()

# ensure_ascii=False 保留中文
print("  ensure_ascii=False + indent=2:")
print(json.dumps(my_dict, ensure_ascii=False, indent=2))

# ═══════════════════════════════════════════════════════════════
# 2. json.dump — Python → JSON 文件
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【json.dump — 写入文件】")
print("=" * 50)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(my_dict, f, ensure_ascii=False, indent=2)
print("  已写入 data.json")

# ═══════════════════════════════════════════════════════════════
# 3. json.loads — JSON 字符串 → Python
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【json.loads — JSON 字符串 → Python】")
print("=" * 50)

json_str = '{"name": "Bob", "age": 30, "scores": [90, 85, 92]}'
obj = json.loads(json_str)
print(f"  解析结果: {obj}")
print(f"  name = {obj['name']}, age = {obj['age']}")

# ═══════════════════════════════════════════════════════════════
# 4. json.load — 从文件读取 JSON
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【json.load — 从文件读取】")
print("=" * 50)

with open('data.json', 'r', encoding='utf-8') as f:
    loaded = json.load(f)
print(f"  读取成功: name={loaded['name']}, cars={len(loaded['cars'])} 辆")

# ═══════════════════════════════════════════════════════════════
# 5. 自定义序列化（datetime 等不可直接序列化的对象）
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【自定义序列化 default】")
print("=" * 50)

class User:
    def __init__(self, name, created):
        self.name = name
        self.created = created

def custom_encoder(obj):
    """自定义编码器: 处理 User 和 datetime"""
    if isinstance(obj, User):
        return {'name': obj.name, 'created': obj.created.isoformat()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'无法序列化 {type(obj)}')

user = User('Charlie', datetime(2025, 3, 15, 10, 30))
user_json = json.dumps(user, default=custom_encoder, ensure_ascii=False)
print(f"  User → JSON: {user_json}")

# ═══════════════════════════════════════════════════════════════
# 6. JSON 类型对应表
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【JSON ↔ Python 类型对应】")
print("=" * 50)
print("  JSON object  → Python dict")
print("  JSON array   → Python list")
print("  JSON string  → Python str")
print("  JSON number  → Python int / float")
print("  JSON true    → Python True")
print("  JSON false   → Python False")
print("  JSON null    → Python None")

# ═══════════════════════════════════════════════════════════════
# 7. 综合: 读写配置
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【综合: JSON 配置文件】")
print("=" * 50)

config = {
    'app_name': 'MyPythonApp',
    'version': '1.0.0',
    'settings': {
        'debug': True,
        'port': 8080,
        'allowed_hosts': ['localhost', '127.0.0.1']
    }
}

# 写配置
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)
print("  配置已写入 config.json")

# 读配置
with open('config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)
print(f"  读取: app={cfg['app_name']}, port={cfg['settings']['port']}")
