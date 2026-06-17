"""============================================================
 04-标准库总览.py
============================================================
覆盖笔记知识点 —— 9 大标准库典型用法:
  math     — 数学函数（sqrt, sin, cos, pi, ceil, floor...）
  random   — 随机数（random, randint, choice, shuffle, seed...）
  time     — 时间戳、结构化时间、格式化
  datetime — 日期时间计算、时差
  os       — 操作系统交互（路径、环境变量、文件操作）
  sys      — Python 解释器信息
  re       — 正则表达式（search, findall, sub, split）
  json     — JSON 编解码
  urllib   — URL 处理

额外: socket, turtle 简介
============================================================"""

import math, random, time, datetime, os, sys, re, json
from urllib.parse import urlparse, urlencode

DIV = "─" * 50

# ═══════════════════════════════════════════════════════════════
# math —— 数学函数
# ═══════════════════════════════════════════════════════════════
print(f"\n{' math — 数学函数 ':=^50}")
print(f"  pi              = {math.pi}")
print(f"  e               = {math.e}")
print(f"  sqrt(16)        = {math.sqrt(16)}")
print(f"  sin(pi/2)       = {math.sin(math.pi/2)}")
print(f"  log(e)          = {math.log(math.e)}")
print(f"  ceil(3.14)      = {math.ceil(3.14)}")
print(f"  floor(3.14)     = {math.floor(3.14)}")
print(f"  pow(2, 10)      = {math.pow(2, 10)}")
print(f"  factorial(5)    = {math.factorial(5)}")
print(f"  degrees(pi)     = {math.degrees(math.pi)}°")

# ═══════════════════════════════════════════════════════════════
# random —— 随机数
# ═══════════════════════════════════════════════════════════════
print(f"\n{' random — 随机数 ':=^50}")
print(f"  random()                = {random.random():.4f}  # [0, 1)")
print(f"  randint(1, 100)         = {random.randint(1, 100)}  # 整数 [1,100]")
print(f"  uniform(1, 10)          = {random.uniform(1, 10):.2f}  # 浮点 [1,10]")
print(f"  choice('ABCDE')         = '{random.choice('ABCDE')}'")
items = [1, 2, 3, 4, 5]
random.shuffle(items)
print(f"  shuffle([1..5])         = {items}")
print(f"  sample(range(100), 5)   = {random.sample(range(100), 5)}  # 不放回")
random.seed(42)
print(f"  seed(42) → random()     = {random.random():.4f}  # 可复现")

# ═══════════════════════════════════════════════════════════════
# time —— 时间处理
# ═══════════════════════════════════════════════════════════════
print(f"\n{' time — 时间处理 ':=^50}")
timestamp = time.time()
print(f"  time() 时间戳           = {timestamp:.0f}")
local = time.localtime()
print(f"  localtime()")
print(f"    年={local.tm_year} 月={local.tm_mon} 日={local.tm_mday}")
print(f"    时={local.tm_hour} 分={local.tm_min} 秒={local.tm_sec}")
print(f"  strftime('%Y-%m-%d %H:%M:%S') = {time.strftime('%Y-%m-%d %H:%M:%S', local)}")
print(f"  strftime('%A')                 = {time.strftime('%A')}")

# ═══════════════════════════════════════════════════════════════
# datetime —— 高级日期时间
# ═══════════════════════════════════════════════════════════════
print(f"\n{' datetime — 高级日期时间 ':=^50}")
now = datetime.datetime.now()
print(f"  now()                    = {now}")
print(f"  .date()                  = {now.date()}")
print(f"  .time()                  = {now.time()}")
d1 = datetime.datetime(2026, 6, 17)
d2 = datetime.datetime(2026, 12, 31)
delta = d2 - d1
print(f"  距 2026-12-31 还有       {delta.days} 天")
print(f"  strftime('%Y年%m月%d日') = {now.strftime('%Y年%m月%d日')}")

# ═══════════════════════════════════════════════════════════════
# os —— 操作系统交互
# ═══════════════════════════════════════════════════════════════
print(f"\n{' os — 操作系统交互 ':=^50}")
print(f"  os.name                 = {os.name}")
print(f"  os.getcwd()             = {os.path.basename(os.getcwd())}")
print(f"  os.listdir('.')[:3]     = {os.listdir('.')[:3]}")
print(f"  os.path.join('a','b')   = {os.path.join('a', 'b')}")
print(f"  os.path.basename(...)   = {os.path.basename('/path/to/file.txt')}")
print(f"  临时路径追加:  sys.path.append('./..')")

# ═══════════════════════════════════════════════════════════════
# sys —— 解释器信息
# ═══════════════════════════════════════════════════════════════
print(f"\n{' sys — 解释器信息 ':=^50}")
print(f"  sys.version[:20]        = {sys.version[:20]}...")
print(f"  sys.platform            = {sys.platform}")
print(f"  sys.path[:2]            = {sys.path[:2]}")
print(f"  sys.argv                = {sys.argv}")

# ═══════════════════════════════════════════════════════════════
# re —— 正则表达式
# ═══════════════════════════════════════════════════════════════
print(f"\n{' re — 正则表达式 ':=^50}")
text = "联系电话: 138-1234-5678 和 010-88886666"
pattern = r'\d{3,4}-\d{7,8}'
matches = re.findall(pattern, text)
print(f"  findall 提取电话         = {matches}")

email = "user@example.com"
ok = re.match(r'^[\w.]+@[\w.]+\.[a-zA-Z]+$', email)
print(f"  match 验证邮箱 '{email}' = {'✓ 有效' if ok else '✗ 无效'}")

result = re.sub(r'\d', 'X', "密码: 123456")
print(f"  sub 替换数字            = {result}")
print(f"  split 分割              = {re.split(r'[,;\\s]+', '苹果,香蕉;橘子 西瓜')}")

# ═══════════════════════════════════════════════════════════════
# json —— JSON 编解码
# ═══════════════════════════════════════════════════════════════
print(f"\n{' json — JSON 编解码 ':=^50}")
data = {"name": "张三", "age": 25, "skills": ["Python", "Linux"]}
j = json.dumps(data, ensure_ascii=False, indent=2)
print(f"  dumps:\n{j}")
parsed = json.loads(j)
print(f"  loads: name={parsed['name']}, age={parsed['age']}")

# ═══════════════════════════════════════════════════════════════
# urllib —— URL 处理
# ═══════════════════════════════════════════════════════════════
print(f"\n{' urllib — URL 处理 ':=^50}")
p = urlparse("https://example.com/search?q=python&page=1")
print(f"  urlparse → scheme={p.scheme}  host={p.hostname}  path={p.path}  query={p.query}")
print(f"  urlencode → {urlencode({'q': 'python模块', 'page': 1})}")

# ═══════════════════════════════════════════════════════════════
# 附: socket 简介
# ═══════════════════════════════════════════════════════════════
print(f"\n{' socket — 网络编程 ':=^50}")
print("  核心步骤:")
print("    服务端: socket() → bind() → listen() → accept() → recv()/send()")
print("    客户端: socket() → connect() → send()/recv()")

# ═══════════════════════════════════════════════════════════════
# 附: turtle 简介
# ═══════════════════════════════════════════════════════════════
print(f"\n{' turtle — 海龟绘图 ':=^50}")
print("  入门级图形库 (1969年诞生)")
print("  turtle.forward(100)  # 前进 100")
print("  turtle.right(90)     # 右转 90°")
print("  turtle.circle(50)    # 画圆")
print("  turtle.done()        # 保持窗口")

if __name__ == "__main__":
    pass  # 演示代码在模块顶层执行