'''
============================================================
 pip 包管理与镜像源配置
============================================================
对照笔记: 01 包管理-pip/包管理与安装.md
  — pip install / uninstall / list / freeze
  — 国内镜像源: 清华/阿里/中科大/豆瓣
  — 永久配置 pip.ini (Windows) / pip.conf (Linux/Mac)
  — .whl 本地安装 / timeout 超时设置
============================================================
'''

import sys
import subprocess

# ═══════════════════════════════════════════════════════════════
# 1. pip 常用命令（命令行演示）
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【pip 常用命令】")
print("=" * 50)

commands = [
    ("安装包", "pip install requests"),
    ("指定版本", "pip install requests==2.28.0"),
    ("卸载", "pip uninstall requests -y"),
    ("列出已安装", "pip list"),
    ("搜索包", "pip search requests  # (新版已废弃)"),
    ("查看包信息", "pip show requests"),
    ("导出依赖", "pip freeze > requirements.txt"),
    ("批量安装", "pip install -r requirements.txt"),
    ("升级 pip", "python -m pip install --upgrade pip"),
]
for label, cmd in commands:
    print(f"  {label:12}  →  {cmd}")

# ═══════════════════════════════════════════════════════════════
# 2. 临时使用国内镜像源
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【国内镜像源 — 临时加速】")
print("=" * 50)

mirrors = [
    ("清华", "https://pypi.tuna.tsinghua.edu.cn/simple"),
    ("阿里", "http://mirrors.aliyun.com/pypi/simple/"),
    ("中科大", "https://pypi.mirrors.ustc.edu.cn/simple/"),
    ("豆瓣", "http://pypi.douban.com/simple/"),
]
for name, url in mirrors:
    print(f"  {name:6}  →  pip install 包名 -i {url}")

# ═══════════════════════════════════════════════════════════════
# 3. 永久配置镜像源
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【永久配置镜像源】")
print("=" * 50)

import os

if os.name == 'nt':
    print("  Windows:")
    print("    1. 创建 C:\\Users\\用户名\\pip\\pip.ini")
    print("    2. 内容:")
    print("       [global]")
    print("       index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
    print("       [install]")
    print("       trusted-host = pypi.tuna.tsinghua.edu.cn")
    print()
    print("    阿里云源同理:")
    print("       index-url = https://mirrors.aliyun.com/pypi/simple/")
    print("       trusted-host = mirrors.aliyun.com")
    print()
    print("    注意: pip.ini 需使用 ANSI 编码")
else:
    print("  Linux/Mac:")
    print("    mkdir ~/.pip")
    print("    vim ~/.pip/pip.conf")
    print("    内容同上")

# ═══════════════════════════════════════════════════════════════
# 4. 其他优化
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【其他优化方法】")
print("=" * 50)
print("  1. .whl 本地安装:")
print("     pip install /path/to/package.whl")
print()
print("  2. 超时设置 (pip.ini / pip.conf):")
print("     [global]")
print("     timeout = 10000  # 毫秒")
print()
print("  3. 虚拟环境:")
print("     python -m venv venv")
print("     .\\venv\\Scripts\\activate     # Windows")
print("     source venv/bin/activate    # Linux/Mac")
print("     deactivate                  # 退出")

# ═══════════════════════════════════════════════════════════════
# 5. 查看当前 Python 环境信息
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【当前 Python 环境】")
print("=" * 50)

print(f"Python 路径: {sys.executable}")
print(f"安装目录: {sys.prefix}")
print(f"site-packages: {sys.prefix}\\Lib\\site-packages" if os.name == 'nt' else "")

# 列出已安装的包（前15个）
try:
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list', '--format=columns'],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split('\n')
    print(f"\n已安装包 (共 {len(lines)-2} 个, 显示前10):")
    for line in lines[:12]:
        print(f"  {line}")
except Exception as e:
    print(f"  无法获取 pip list: {e}")
