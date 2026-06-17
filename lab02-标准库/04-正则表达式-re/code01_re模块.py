'''
============================================================
 正则表达式 re 模块
============================================================
对照笔记: 04 正则表达式-re/re模块.md
  — match/search/findall/finditer/fullmatch/sub/subn/split/compile
  — 字符类: . \d \D \w \W \s \S [a-z] [^...]
  — 量词: * + ? {n} {n,m} (贪婪/非贪婪)
  — 分组: (...) (?P<name>...) | (?:...)
  — 边界: ^ $ \b \B
  — 标志: re.I re.S re.M re.VERBOSE
============================================================
'''

import re

# ═══════════════════════════════════════════════════════════════
# 1. 原始字符串 — 避免转义混淆
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【原始字符串 r'...'】")
print("=" * 50)
print(f"  r'\\d+' 等价于 '\\\\d+'  → 推荐用 r 前缀")

# ═══════════════════════════════════════════════════════════════
# 2. 核心匹配函数
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【match / search / findall / finditer / fullmatch】")
print("=" * 50)

text = "今天是2025年12月26日，温度是25℃"

# re.match — 从开头匹配
m1 = re.match(r"今天", text)
m2 = re.match(r"2025", text)
print(f"  re.match('今天') → {'✓ 匹配' if m1 else '✗ None'} (必须开头)")
print(f"  re.match('2025') → {'✓ 匹配' if m2 else '✗ None'} (不在开头)")

# re.search — 搜索任意位置
m3 = re.search(r"\d+", text)
print(f"  re.search(r'\\d+') → '{m3.group()}' (第一个匹配)")

# re.findall — 所有匹配
numbers = re.findall(r"\d+", text)
print(f"  re.findall(r'\\d+') → {numbers}")

# re.finditer — 迭代器（含位置信息）
print(f"  re.finditer(r'\\d+') →")
for m in re.finditer(r"\d+", text):
    print(f"    找到 '{m.group()}' 位置: {m.span()}")

# re.fullmatch — 完全匹配
print(f"  re.fullmatch(r'\\d{{4}}-\\d{{2}}-\\d{{2}}', '2025-12-26') →", end=" ")
print(("✓" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", "2025-12-26") else "✗"))

# ═══════════════════════════════════════════════════════════════
# 3. 字符类与预定义字符集
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【字符类: \\d \\D \\w \\W \\s \\S . [abc] [^abc]】")
print("=" * 50)

char_classes = [
    (r"\d", "[0-9] 数字", "test123"),
    (r"\D", "[^0-9] 非数字", "test123"),
    (r"\w", "[a-zA-Z0-9_] 单词字符", "hello_123!@#"),
    (r"\W", "[^a-zA-Z0-9_] 非单词字符", "hello_123!@#"),
    (r"\s", "空白字符", "a b\tc\nd"),
    (r"\S", "非空白字符", "a b\tc\nd"),
    (r"[aeiou]", "自定义字符类", "hello world"),
    (r"[^aeiou]", "排除字符类", "hello world"),
    (r".", "除换行外任意字符", "a1@"),
]
for pat, desc, sample in char_classes:
    result = re.findall(pat, sample)
    print(f"  {desc:28}  r'{pat:10}'  →  {result}")

# ═══════════════════════════════════════════════════════════════
# 4. 量词 — 贪婪 vs 非贪婪
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【量词 * + ? {n} {n,m} — 贪婪 vs 非贪婪】")
print("=" * 50)

html = "<div>内容1</div><div>内容2</div>"
print(f"  HTML: {html}")
print(f"  贪婪 <.*>   → {re.findall(r'<.*>', html)}   (最长匹配)")
print(f"  非贪婪 <.*?> → {re.findall(r'<.*?>', html)}   (最短匹配)")

# 量词示例
quantifiers = [
    (r"a*", "零次或多次", "aaab"),
    (r"a+", "一次或多次", "aaab"),
    (r"a?", "零次或一次", "aaab"),
    (r"a{2}", "恰好2次", "aaab"),
    (r"a{2,3}", "2-3次", "aaab"),
]
for pat, desc, sample in quantifiers:
    m = re.search(pat, sample)
    print(f"  {desc:12}  r'{pat:6}' on '{sample}' → '{m.group() if m else ''}'")

# ═══════════════════════════════════════════════════════════════
# 5. 分组 — 捕获 / 命名 / 非捕获
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【分组: (...) (?P<name>...) (?:...) |】")
print("=" * 50)

# 捕获分组
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "日期: 2025-12-26")
if m:
    print(f"  日期全部: {m.group(0)}")
    print(f"  年: {m.group(1)}, 月: {m.group(2)}, 日: {m.group(3)}")

# 命名分组
m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "2025-12-26")
if m:
    print(f"  命名分组: year={m.group('year')}, month={m.group('month')}")

# 非捕获分组 (?:...)
print(f"  非捕获 (?:ab)+ → {re.findall(r'(?:ab)+', 'abababc')}")

# 或 |
print(f"  或 cat|dog   → {re.findall(r'cat|dog', 'cat and dog')}")

# ═══════════════════════════════════════════════════════════════
# 6. 边界: ^ $ \b \B
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【边界: ^ $ \\b \\B】")
print("=" * 50)

print(f"  'hello' 中 \\bhell\\b  → {re.findall(r'\bhell\b', 'hello hell')}")
print(f"  '123abc' 中 \\b\\d+\\b → {re.findall(r'\b\d+\b', '123 abc 456')}")
print(f"  '^Hello' 匹配开头     → {'✓' if re.match(r'^Hello', 'Hello World') else '✗'}")
print(f"  'end$' 匹配结尾       → {'✓' if re.search(r'end$', 'the end') else '✗'}")

# ═══════════════════════════════════════════════════════════════
# 7. sub / subn / split / compile
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【sub / subn / split / compile】")
print("=" * 50)

# sub — 替换
text2 = "电话: 138-1234-5678"
print(f"  sub 脱敏: {re.sub(r'\d', '*', text2)}")

# subn — 替换+计数
new, count = re.subn(r'\d', '*', text2)
print(f"  subn 脱敏: '{new}' (替换了{count}处)")

# split — 分割
text3 = "苹果;香蕉,橙子 西瓜|葡萄"
parts = re.split(r'[;, |]+', text3)
print(f"  split: {parts}")

# compile — 预编译
phone_pattern = re.compile(r'1[345789]\d{9}')
for phone in ['13812345678', '12345678901', '19912345678']:
    ok = "✓" if phone_pattern.fullmatch(phone) else "✗"
    print(f"  compile验证 {phone} → {ok}")

# ═══════════════════════════════════════════════════════════════
# 8. 标志: re.I / re.S / re.M / re.VERBOSE
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【标志: re.I / re.S / re.M / re.VERBOSE】")
print("=" * 50)

print(f"  re.I 忽略大小写: {re.findall(r'python', 'Python PYTHON python', re.I)}")
print(f"  re.S .匹配换行:  {re.findall(r'<p>.*?</p>', '<p>a\\nb</p>', re.S)}")

# re.VERBOSE — 可写注释的正则
pattern = re.compile(r"""
    ^               # 字符串开头
    1               # 1 开头
    [345789]         # 第二位
    \d{9}            # 后面 9 位数字
    $                # 字符串结尾
""", re.VERBOSE)
print(f"  re.VERBOSE 验手机号 13812345678 → {'✓' if pattern.match('13812345678') else '✗'}")

# ═══════════════════════════════════════════════════════════════
# 9. 综合示例: 提取标签中的网址
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【综合: 提取标签中的网址】")
print("=" * 50)

html = '''<link rel="alternate" hreflang="zh" href="https://zh.wikipedia.org/wiki/正则表达式">
<link rel="alternate" hreflang="zh-Hans" href="https://zh.wikipedia.org/zh-hans/正则">'''

urls = re.findall(r'href="(.+?)"', html)
for u in urls:
    print(f"  {u}")

# 替换数字为对应英文
num_map = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five"}
text4 = "I have 2 apples and 3 oranges."
result = re.sub(r"\d", lambda x: num_map[x.group(0)], text4)
print()
print(f"  替换数字: {result}")
