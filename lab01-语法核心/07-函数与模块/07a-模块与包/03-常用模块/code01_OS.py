"""
Python OS 模块核心函数学习笔记

模块速查表：
模块1：路径与目录操作 - os.getcwd(), os.chdir(), os.listdir(), os.mkdir(), os.makedirs()
模块2：路径处理 - os.path.join(), os.path.abspath(), os.path.basename(), os.path.exists()
模块3：文件与目录遍历 - os.walk(), os.scandir()
模块4：系统与进程信息 - os.system(), os.environ, os.getpid()
模块5：文件状态与权限 - os.stat(), os.access(), os.chmod()
"""

import os
import shutil
import stat
import time
from datetime import datetime

# ==================== 模块1：路径与目录操作 ====================
print("=== 模块1：路径与目录操作 ===")
print("函数速查：os.getcwd(), os.chdir(), os.listdir(), os.mkdir(), os.makedirs()")

# 1. 获取和改变工作目录
print("当前目录:", os.getcwd())
try:
    original_dir = os.getcwd()
    os.chdir("..")  # 切换到上级目录（谨慎使用）
    print("上级目录:", os.getcwd())
    os.chdir(original_dir)  # 切换回原目录
except Exception as e:
    print(f"目录切换出错: {e}")

# 2. 列出目录内容
print("\n当前目录内容:")
for item in os.listdir('')[:10]:  # 只显示前10个
    if not item.startswith('.'):  # 跳过隐藏文件
        print(f"  - {item}")

# 3. 创建目录示例
test_dir = "test_dir_demo"
nested_dir = "a/b/c/d"

# 创建单层目录
if not os.path.exists(test_dir):
    os.mkdir(test_dir)
    # 查看当前目录下文件夹及文件（1级）
    print(f"\n创建后当前目录内容:")
    for item in os.listdir('')[:10]:  # 只显示前10个
        if not item.startswith('.'):  # 跳过隐藏文件
            print(f"  - {item}")
    print(f"创建单层目录: {test_dir}")

# 递归创建多层目录
if not os.path.exists(nested_dir):
    os.makedirs(nested_dir, exist_ok=True)  # 存在则跳过
    print(f"递归创建多层目录: {nested_dir}")

# 4. 重命名操作
if os.path.exists(test_dir):
    renamed_dir = "renamed_dir_demo"
    if not os.path.exists(renamed_dir):
        os.rename(test_dir, renamed_dir)
        print(f"重命名目录: {test_dir} -> {renamed_dir}")

print("\n" + "="*60)

# ==================== 模块2：路径处理 (os.path 子模块) ====================
print("=== 模块2：路径处理 ===")
print("函数速查：os.path.join(), os.path.abspath(), os.path.basename(), os.path.exists()")

# 1. 路径拼接与拆分示例
sample_path = "/home/user/documents/report.pdf"
print(f"原始路径: {sample_path}")
print(f"目录部分: {os.path.dirname(sample_path)}")
print(f"文件名部分: {os.path.basename(sample_path)}")
print(f"分割结果: {os.path.split(sample_path)}")
print(f"扩展名分割: {os.path.splitext(sample_path)}")

# 2. 安全路径拼接（跨平台）
path_parts = ["data", "2024", "reports", "january", "report.pdf"]
joined_path = os.path.join(*path_parts)
print(f"\n拼接路径: {joined_path}")
print(f"当前系统路径分隔符: {repr(os.sep)}")

# 3. 路径检查与转换示例
test_file = "example_test.txt"

# 创建测试文件
if not os.path.exists(test_file):
    with open(test_file, 'w', encoding='utf-8') as f:  # with 语句自动关闭文件
        f.write("测试文件内容")

print(f"\n路径检查结果:")
print(f"'{test_file}' 是否存在: {os.path.exists(test_file)}")
print(f"是文件吗: {os.path.isfile(test_file)}")
print(f"是目录吗: {os.path.isdir(test_file)}")
print(f"绝对路径: {os.path.abspath(test_file)}")

# 4. 文件信息获取
if os.path.exists(test_file):
    file_size = os.path.getsize(test_file)
    mtime = os.path.getmtime(test_file)
    print(f"文件大小: {file_size} 字节")
    print(f"最后修改: {time.ctime(mtime)}")

print("\n" + "="*60)

# ==================== 模块3：文件与目录遍历 ====================
print("=== 模块3：文件与目录遍历 ===")
print("函数速查：os.walk(), os.scandir()")

# 1. 使用 os.walk 递归遍历（限制深度避免输出过多）
print("使用 os.walk 递归遍历（前2层）:")
walk_count = 0
# os.walk 作用：遍历目录树，返回每个目录的根目录、子目录列表、文件列表
for root, dirs, files in os.walk(''):  # walk 函数返回3个值：根目录、子目录列表、文件列表
    if walk_count >= 10:  # 限制输出数量
        break
    
    # 跳过隐藏目录和 __pycache__
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    level = root.count(os.sep)
    indent = '  ' * level
    print(f"{indent}{os.path.basename(root) or '.'}/")
    
    sub_indent = '  ' * (level + 1)
    for file in files[:2]:  # 每个目录最多显示2个文件
        if not file.startswith('.') and not file.endswith('.pyc'):
            print(f"{sub_indent}{file}")
    
    walk_count += 1

# 2. 使用 os.scandir（更高效）
print("\n使用 os.scandir 高效遍历:")
scandir_count = 0
with os.scandir('') as entries:
    for entry in entries: # entry 是 os.DirEntry 对象
        if scandir_count >= 5:  # 限制输出
            break
        
        try:
            if entry.is_file():
                size = entry.stat().st_size  # 获取文件大小
                print(f"文件: {entry.name} ({size} 字节)")
            elif entry.is_dir() and not entry.name.startswith('.'):  # 跳过隐藏目录
                print(f"目录: {entry.name}/")
            scandir_count += 1
        except OSError:
            pass  # 忽略访问权限错误

# 3. 查找特定类型文件的函数示例
def find_files_by_extension(directory, extension, max_results=5):
    """查找指定扩展名的文件"""
    found = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                found.append(os.path.join(root, file))
                if len(found) >= max_results:
                    return found
    return found

py_files = find_files_by_extension('.', '.py')
print(f"\n找到 {len(py_files)} 个Python文件:")
for file in py_files:
    print(f"  - {file}")

print("\n" + "="*60)

# ==================== 模块4：系统与进程信息 ====================
print("=== 模块4：系统与进程信息 ===")
print("函数速查：os.system(), os.environ, os.getenv(), os.getpid()")

# 1. 系统信息
print(f"操作系统名称: {os.name}")
print(f"路径分隔符: {repr(os.sep)}")
print(f"行结束符: {repr(os.linesep)}")

# 2. 进程信息
print(f"\n当前进程ID: {os.getpid()}")
try:
    print(f"父进程ID: {os.getppid()}")
except AttributeError:
    print("当前系统不支持获取父进程ID")

# 3. 环境变量操作
print(f"\n重要环境变量:")
important_vars = ['HOME', 'USERPROFILE', 'PATH', 'PYTHONPATH', 'TEMP', 'TMP']
for var in important_vars:
    value = os.getenv(var)
    if value:
        # 截断过长的值
        display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {var}: {display_value}")

# 4. 环境变量遍历（前5个）
print(f"\n环境变量总数: {len(os.environ)}")
print("前5个环境变量:")
for i, (key, value) in enumerate(sorted(os.environ.items())):
    if i >= 5:
        break
    display_value = value[:30] + "..." if len(value) > 30 else value
    print(f"  {key}: {display_value}")

# 5. 自定义环境变量
os.environ['DEMO_VAR'] = 'Hello from OS module demo'
print(f"\n设置的环境变量: {os.getenv('DEMO_VAR')}")

print("\n" + "="*60)

# ==================== 模块5：文件状态与权限 ====================
print("=== 模块5：文件状态与权限 ===")
print("函数速查：os.stat(), os.access(), os.chmod(), os.utime()")

# 使用之前创建的测试文件
if os.path.exists(test_file):
    # 1. 获取文件状态信息
    file_stat = os.stat(test_file)
    print("文件状态信息:")
    print(f"  大小: {file_stat.st_size} 字节")
    print(f"  最后访问时间: {time.ctime(file_stat.st_atime)}")
    print(f"  最后修改时间: {time.ctime(file_stat.st_mtime)}")
    print(f"  最后状态变更时间: {time.ctime(file_stat.st_ctime)}")
    print(f"  权限模式 (八进制): {oct(file_stat.st_mode)}")

    # 2. 权限检查
    print("\n文件权限检查:")
    print(f"  可读 (R_OK): {os.access(test_file, os.R_OK)}")
    print(f"  可写 (W_OK): {os.access(test_file, os.W_OK)}")
    print(f"  可执行 (X_OK): {os.access(test_file, os.X_OK)}")
    print(f"  文件存在 (F_OK): {os.access(test_file, os.F_OK)}")

    # 3. 修改权限（仅适用于 Linux/Unix 系统）
    if os.name == 'posix':
        original_mode = file_stat.st_mode
        # 添加用户执行权限
        new_mode = original_mode | stat.S_IXUSR
        os.chmod(test_file, new_mode)
        print(f"\n已添加用户执行权限")
        print(f"原权限: {oct(original_mode)}")
        print(f"新权限: {oct(new_mode)}")
        
        # 检查修改结果
        updated_stat = os.stat(test_file)
        print(f"验证权限: {oct(updated_stat.st_mode)}")

    # 4. 修改文件时间戳
    print("\n修改文件时间戳:")
    current_time = time.time()
    os.utime(test_file, (current_time, current_time))  # 设置访问和修改时间为当前时间
    updated_stat = os.stat(test_file)
    print(f"更新后的修改时间: {time.ctime(updated_stat.st_mtime)}")

print("\n" + "="*60)

# ==================== 综合应用示例 ====================
print("=== 综合应用示例 ===")

# 示例1：简单的文件整理工具
def simple_file_organizer(source_dir):
    """简单文件整理工具 - 按扩展名分类"""
    if not os.path.exists(source_dir):
        print(f"目录不存在: {source_dir}")
        return
    
    organized_dir = os.path.join(source_dir, "Organized")
    os.makedirs(organized_dir, exist_ok=True)
    
    categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.md'],
        'code': ['.py', '.js', '.html', '.css', '.java'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
    }
    
    moved_count = 0
    
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        
        # 跳过目录
        if os.path.isdir(item_path):
            continue
        
        # 确定文件类别
        _, ext = os.path.splitext(item.lower())
        target_category = 'others'
        
        for category, extensions in categories.items():
            if ext in extensions:
                target_category = category
                break
        
        # 创建目标目录
        target_dir = os.path.join(organized_dir, target_category)
        os.makedirs(target_dir, exist_ok=True)
        
        # 移动文件
        target_path = os.path.join(target_dir, item)
        if not os.path.exists(target_path):
            shutil.move(item_path, target_path)
            moved_count += 1
    
    print(f"整理完成！移动了 {moved_count} 个文件")
    return organized_dir

# 示例2：跨平台路径处理
def cross_platform_path_demo():
    """跨平台路径处理演示"""
    print("\n跨平台处理演示:")
    
    # 正确的路径拼接方式
    config_path = os.path.join("config", "settings", "app.json")
    print(f"配置文件路径: {config_path}")
    
    # 路径规范化
    messy_path = "./folder//subfolder/../file.txt"
    clean_path = os.path.normpath(messy_path)
    print(f"规范化前: {messy_path}")
    print(f"规范化后: {clean_path}")
    
    # 获取相对路径
    try:
        abs_path = os.path.abspath(__file__)
        rel_path = os.path.relpath(abs_path, ".")
        print(f"绝对路径: {abs_path}")
        print(f"相对路径: {rel_path}")
    except:
        pass

# 运行演示
cross_platform_path_demo()

print("\n" + "="*60)

# ==================== 最佳实践提醒 ====================
print("=== 最佳实践总结 ===")
best_practices = [
    "✓ 使用 os.path.join() 进行路径拼接，而不是字符串拼接",
    "✓ 优先使用 os.scandir() 而不是 os.listdir()，性能更好",
    "✓ 对文件操作添加 try-except 块处理异常",
    "✓ 使用 with 语句确保文件正确关闭",
    "✓ 操作前检查文件权限和存在性",
    "✓ 使用 os.path 处理跨平台路径差异",
    "✓ 谨慎使用 os.system()，考虑使用 subprocess 模块替代",
    "✓ 及时清理创建的临时文件和目录"
]

for practice in best_practices:
    print(f"  {practice}")

# ==================== 清理工作 ====================
print("\n=== 清理测试文件 ===")

cleanup_items = [
    test_file,
    "renamed_dir_demo" if os.path.exists("renamed_dir_demo") else test_dir,
    nested_dir
]

for item in cleanup_items:
    try:
        if os.path.isfile(item):
            os.remove(item)
            print(f"删除文件: {item}")
        elif os.path.isdir(item):
            shutil.rmtree(item, ignore_errors=True)
            print(f"删除目录: {item}")
    except Exception as e:
        print(f"清理 {item} 时出错: {e}")

# 清理环境变量
if 'DEMO_VAR' in os.environ:
    del os.environ['DEMO_VAR']
    print("清理环境变量: DEMO_VAR")

print("\nOS 模块演示完成！")
print("="*60)