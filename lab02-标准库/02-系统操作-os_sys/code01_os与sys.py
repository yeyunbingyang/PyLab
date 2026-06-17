'''
============================================================
 os 与 sys 模块 —— 操作系统交互 + 解释器交互
============================================================
对照笔记: 02 系统操作-os_sys/01 os.md + 02 sys.md
覆盖知识点: 目录操作、路径处理、文件遍历、系统信息、
           文件权限、跨平台判断、命令行参数、模块路径、
           输入输出流、版本信息、递归深度、文件搜索综合
============================================================
'''

import os, sys

# ═══════════════════════════════════════════════════════════════
# 一、路径与目录操作
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【一、路径与目录操作】")
print("=" * 50)

print(f"当前工作目录: {os.getcwd()}")
print(f"目录内容    : {os.listdir('.')[:5]}...")
# os.chdir("..")        # 改变工作目录
# os.mkdir("test_dir")  # 创建单层目录
# os.makedirs("a/b/c", exist_ok=True)  # 递归创建，跳过已存在
# os.rename("old", "new")   # 重命名
# os.rmdir("empty_dir")     # 删除空目录
# os.remove("file.txt")     # 删除文件

# ═══════════════════════════════════════════════════════════════
# 二、路径处理 os.path
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【二、路径处理 os.path】")
print("=" * 50)

path = "/home/user/documents/report.pdf"
print(f"示例路径        : {path}")
print(f"dirname         : {os.path.dirname(path)}")
print(f"basename        : {os.path.basename(path)}")
print(f"splitext        : {os.path.splitext(path)}")
print(f"split           : {os.path.split(path)}")
print()

# 跨平台拼接 —— 永不手写分隔符
config_path = os.path.join("config", "settings", "app.ini")
print(f"os.path.join拼接: {config_path}")
print()

# 判断
print(f"当前目录 . 存在吗  : {os.path.exists('.')}")
print(f". 是文件吗         : {os.path.isfile('.')}")
print(f". 是目录吗         : {os.path.isdir('.')}")
print()

# 绝对路径
abs_current = os.path.abspath('.')
print(f"绝对路径        : {abs_current}")
# os.path.getsize(path)     # 文件大小(字节)
# os.path.getmtime(path)    # 最后修改时间

# ═══════════════════════════════════════════════════════════════
# 三、os.walk 递归遍历
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【三、os.walk 递归遍历目录树】")
print("=" * 50)

# os.walk 返回 (root, dirs, files) 三元组
print("当前目录前 3 层结构:")
count = 0
for root, dirs, files in os.walk('.'):
    if count >= 3:
        break
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    level = root.replace('.', '').count(os.sep)
    indent = '  ' * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in files[:3]:
        print(f"{indent}  {f}")
    count += 1

# os.scandir (Python 3.5+, 更高效)
print()
print("os.scandir 当前目录:")
try:
    with os.scandir('.') as entries:
        cnt = 0
        for entry in entries:
            if cnt >= 5:
                break
            if entry.is_file():
                size = entry.stat().st_size
                print(f"  [文件] {entry.name} ({size} 字节)")
            elif entry.is_dir():
                if not entry.name.startswith('.'):
                    print(f"  [目录] {entry.name}/")
            cnt += 1
except Exception as e:
    print(f"  scandir 错误: {e}")

# ═══════════════════════════════════════════════════════════════
# 四、系统与进程信息
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【四、系统与进程信息】")
print("=" * 50)

print(f"os.name             = {os.name}    # 'nt'=Windows, 'posix'=Linux/Mac")
print(f"os.sep              = '{os.sep}'")
print(f"os.linesep(转义)    = {repr(os.linesep)}")
print(f"os.getpid()         = {os.getpid()}")
print()

# 环境变量
print("环境变量示例:")
print(f"  USERNAME(win)     = {os.getenv('USERNAME', 'N/A')}")
print(f"  HOME(posix)       = {os.getenv('HOME', 'N/A')}")
print(f"  PATH(前60字)      = {(os.environ.get('PATH', '')[:60])}...")

# ═══════════════════════════════════════════════════════════════
# 五、文件操作与权限
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【五、文件操作与权限】")
print("=" * 50)

this_file = __file__
print(f"当前文件: {os.path.basename(this_file)}")
try:
    st = os.stat(this_file)
    print(f"  大小     : {st.st_size} 字节")
    print(f"  修改时间 : {st.st_mtime}")
except Exception as e:
    print(f"  stat 错误: {e}")
print(f"  可读?    : {os.access(this_file, os.R_OK)}")
print(f"  可写?    : {os.access(this_file, os.W_OK)}")

# ═══════════════════════════════════════════════════════════════
# 六、跨平台判断
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【六、跨平台判断】")
print("=" * 50)

if sys.platform == 'win32':
    default_path = os.path.join('C:', 'Users', 'Public')
    home_var = 'USERPROFILE'
elif sys.platform == 'darwin':
    default_path = os.path.join('/Users', os.environ.get('USER', 'user'))
    home_var = 'HOME'
else:
    default_path = os.path.join('/home', os.environ.get('USER', 'user'))
    home_var = 'HOME'

print(f"sys.platform       = {sys.platform}")
print(f"平台默认路径       = {default_path}")
print(f"HOME 变量名        = {home_var}")
print(f"HOME 变量值        = {os.getenv(home_var, 'N/A')}")

# ═══════════════════════════════════════════════════════════════
# 七、sys.argv 命令行参数
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【七、sys.argv 命令行参数】")
print("=" * 50)

print(f"脚本名 sys.argv[0]: {sys.argv[0]}")
print(f"参数   sys.argv[1:]: {sys.argv[1:]}")
first_arg = sys.argv[1] if len(sys.argv) > 1 else None
print(f"第一个参数(安全取): {first_arg if first_arg else '(无)'}")

# ═══════════════════════════════════════════════════════════════
# 八、sys.path 模块搜索路径
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【八、sys.path 模块搜索路径】")
print("=" * 50)

print("模块搜索路径:")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}] {p}")
print(f"  ... (共 {len(sys.path)} 个)")
print()
print("运行时添加路径:")
print("  sys.path.append('/my/modules')      # 追加到末尾")
print("  sys.path.insert(0, '/my/modules')   # 插到最前, 优先搜索")

print()
print(f"'os' 已加载?     : {'os' in sys.modules}")
print(f"模块总数         : {len(sys.modules)}")

# ═══════════════════════════════════════════════════════════════
# 九、sys.stdout / stderr 流
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【九、sys.stdout / stderr 流】")
print("=" * 50)

sys.stdout.write("  stdout.write: 正常输出\n")
sys.stderr.write("  stderr.write: 错误输出\n")
print("  print() 默认输出到 sys.stdout")
print()
print("  重定向示例模式:")
print("    old = sys.stdout")
print("    sys.stdout = open('out.txt', 'w')")
print("    print('写入文件')")
print("    sys.stdout = old  # 恢复")

# ═══════════════════════════════════════════════════════════════
# 十、解释器与版本信息
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【十、解释器与版本信息】")
print("=" * 50)

print(f"sys.version       : {sys.version.split(chr(10))[0]}")
print(f"sys.version_info  : {sys.version_info}")
print(f"sys.maxsize       : {sys.maxsize}")
print(f"sys.executable    : {sys.executable}")
print()

if sys.version_info < (3, 8):
    print("⚠ 需要 Python 3.8+")
else:
    print("✓ Python 版本满足 3.8+ 要求")

print()
print(f"'hello' 内存占用   : {sys.getsizeof('hello')} 字节")
print(f"[1,2,3] 内存占用   : {sys.getsizeof([1, 2, 3])} 字节")

# ═══════════════════════════════════════════════════════════════
# 十一、递归深度与退出
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【十一、递归深度与退出】")
print("=" * 50)

print(f"递归深度上限 (get) : {sys.getrecursionlimit()}")
# sys.setrecursionlimit(2000)  # 修改上限
print()
print("退出方式:")
print("  sys.exit()            # 正常退出 (返回码 0)")
print("  sys.exit(1)           # 异常退出 (调用方可检测)")
print("  sys.exit('错误信息')   # 打印信息后退出 (返回码 1)")

# ═══════════════════════════════════════════════════════════════
# 十二、综合示例: 跨平台文件搜索
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【十二、综合示例: 文件搜索】")
print("=" * 50)


def search_files(root_dir, keyword, case_sensitive=False):
    """递归搜索文件名包含关键词的文件"""
    if not os.path.isdir(root_dir):
        print(f"错误: {root_dir} 不是有效目录", file=sys.stderr)
        return []
    results = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            target = file if case_sensitive else file.lower()
            kw = keyword if case_sensitive else keyword.lower()
            if kw in target:
                results.append(os.path.join(root, file))
        if len(results) >= 10:
            break
    return results


py_files = search_files('.', '.py')
print(f"找到 {len(py_files)} 个 .py 文件 (示例前5个):")
for f in py_files[:5]:
    print(f"  {f}")

print()
print("=" * 50)
print("演示完毕 — os + sys 模块知识总览")
print("=" * 50)
