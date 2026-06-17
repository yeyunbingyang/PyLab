'''
============================================================
 socket 网络编程
============================================================
对照笔记: 05 网络编程-socket/网络编程.md
  — IP/端口/协议 三要素
  — TCP 服务端: socket → bind → listen → accept → recv/send
  — TCP 客户端: socket → connect → send/recv
  — gethostname / gethostbyname / DNS 解析
  — HTTP 请求 + requests 库
  — Starlette Web 服务
============================================================
'''

import socket

# ═══════════════════════════════════════════════════════════════
# 1. 获取本机信息
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【本机网络信息】")
print("=" * 50)

hostname = socket.gethostname()
print(f"  主机名: {hostname}")
try:
    ip = socket.gethostbyname(hostname)
    print(f"  IP 地址: {ip}")
except Exception as e:
    print(f"  IP 获取失败: {e}")

# ═══════════════════════════════════════════════════════════════
# 2. DNS 解析
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【DNS 解析】")
print("=" * 50)

for domain in ['www.baidu.com', 'www.python.org', 'localhost']:
    try:
        addr = socket.gethostbyname(domain)
        print(f"  {domain:25} → {addr}")
    except socket.gaierror as e:
        print(f"  {domain:25} → 解析失败")

# ═══════════════════════════════════════════════════════════════
# 3. TCP 服务端
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【TCP 服务端 — 核心步骤】")
print("=" * 50)

server_steps = [
    "sk = socket.socket()            # 1. 创建 socket 对象",
    "sk.bind(('0.0.0.0', 8995))      # 2. 绑定 IP 和端口",
    "sk.listen(5)                     # 3. 设置监听 (最多5个等待连接)",
    "conn, addr = sk.accept()         # 4. 等待客户端连接",
    "data = conn.recv(1024)           # 5. 接收数据 (最多1024字节)",
    "conn.send(data)                  # 6. 发送数据",
    "conn.close()                     # 7. 关闭连接",
    "sk.close()                       # 8. 关闭 socket",
]
for s in server_steps:
    print(f"  {s}")

# ═══════════════════════════════════════════════════════════════
# 4. TCP 客户端
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【TCP 客户端 — 核心步骤】")
print("=" * 50)

client_steps = [
    "sk = socket.socket()             # 1. 创建 socket 对象",
    "sk.connect(('127.0.0.1', 8995))  # 2. 连接服务器",
    "sk.send(data)                    # 3. 发送数据",
    "data = sk.recv(1024)             # 4. 接收响应",
    "sk.close()                       # 5. 关闭连接",
]
for s in client_steps:
    print(f"  {s}")

# ═══════════════════════════════════════════════════════════════
# 5. 完整 TCP 回显演示 (echo)
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【TCP Echo 演示代码】")
print("=" * 50)

import threading

def echo_server():
    """回显服务端: 接收什么就返回什么"""
    sk = socket.socket()
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sk.bind(('127.0.0.1', 18995))
    sk.listen(1)
    print("  [服务端] 启动，等待连接...")
    conn, addr = sk.accept()
    print(f"  [服务端] 连接来自: {addr}")
    while True:
        data = conn.recv(1024).decode('utf-8')
        if data.strip().lower() == 'quit':
            print(f"  [服务端] 收到 quit，关闭")
            break
        print(f"  [服务端] 收到: {data}")
        conn.send(('Echo: ' + data).encode('utf-8'))
    conn.close()
    sk.close()

def echo_client():
    """回显客户端: 发送消息，打印响应"""
    import time
    time.sleep(0.2)  # 等服务器启动
    sk = socket.socket()
    sk.connect(('127.0.0.1', 18995))
    print("  [客户端] 已连接")
    messages = ['你好', 'Python Socket', 'quit']
    for msg in messages:
        print(f"  [客户端] 发送: {msg}")
        sk.send(msg.encode('utf-8'))
        if msg.lower() == 'quit':
            break
        data = sk.recv(1024).decode('utf-8')
        print(f"  [客户端] 响应: {data}")
    sk.close()

# 启动服务端线程
t = threading.Thread(target=echo_server, daemon=True)
t.start()
import time
time.sleep(0.1)
echo_client()
t.join(timeout=1)

# ═══════════════════════════════════════════════════════════════
# 6. HTTP 请求 + Starlette 简介
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【HTTP / Starlette Web 服务】")
print("=" * 50)

print("  HTTP 请求 (requests 库):")
print("    pip install requests")
print("    resp = requests.get('https://v1.hitokoto.cn/?c=a&encode=json')")
print("    data = resp.json()")
print()
print("  Starlette Web 服务:")
print("    pip install starlette uvicorn")
print("    app = Starlette(routes=[Route('/', homepage)])")
print("    uvicorn.run(app, host='0.0.0.0', port=8000)")
print()
print("  网络编程三要素: IP (定位计算机) + 端口 (定位进程) + 协议 (通信规则)")
