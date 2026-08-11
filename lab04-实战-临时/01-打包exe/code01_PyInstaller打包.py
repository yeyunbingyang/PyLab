# PyInstaller 打包 Python 为 exe

# === 安装 ===
# pip install pyinstaller

# === 基本打包（命令行） ===
# pyinstaller -F -w --clean --noconfirm supByName.py
# pyinstaller --onefile --windowed --icon=app.ico main.py
#   --onefile: 打包成单个 exe 文件
#   --windowed: 不显示命令行窗口（GUI 程序）
#   --icon: 指定图标

# === 打包测试脚本 ===
import sys
import os

def main():
    print('=== PyInstaller 打包测试 ===')
    print(f'Python 版本: {sys.version}')
    print(f'运行目录: {os.getcwd()}')
    print(f'参数: {sys.argv}')

    # 获取资源路径（打包后路径会变）
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f'基础目录: {base_dir}')

    input('按回车退出...')

if __name__ == '__main__':
    main()

# === 常见问题 ===
# 1. 找不到资源文件：用 sys._MEIPASS 或上述 frozen 判断
# 2. 被杀毒软件误报：正常现象，可加 --clean 重试
# 3. 文件太大：用虚拟环境只装必要依赖，或用 --exclude-module 排除
# 4. 控制台闪退：去掉 --windowed 看报错，或用 input() 卡住窗口
