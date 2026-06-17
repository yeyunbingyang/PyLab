''' 给每个 Python 项目一个"独立房间"，想装什么包装什么包，关起门来互不影响。
project_demo/
│
├── .venv/                     # 虚拟环境目录（由 venv 创建） 在虚拟环境中安装依赖，不污染系统全局环境⭐
│   ├── Scripts/（Windows）     # 可执行文件，如 python.exe、pip.exe
│   └── lib/                   # 虚拟环境中安装的第三方包 安装后第三方包会出现在 .venv/lib/... 目录下，而不会影响全局 Python 环境。
│
├── mypackage/                 # 自定义包
│   ├── __init__.py            # 包的初始化文件
│   ├── module1.py             # 模块1
│   └── module2.py             # 模块2
│
└── main.py                    # 程序入口文件


1️⃣ 创建虚拟环境
在命令行中执行（推荐在项目根目录下）：
# 创建虚拟环境
python -m venv .venv

2️⃣ 激活虚拟环境
Windows:
.venv\Scripts\activate

Linux / macOS:
source .venv/bin/activate

✅ 激活后命令行会显示虚拟环境前缀 (venv)，此时安装的依赖将仅作用于该项目。

3️⃣ 安装依赖
pip install requests
安装后第三方包会出现在 .venv/lib/... 目录下，而不会影响全局 Python 环境。
'''