import sys

# sys.exit([arg])
# 程序退出控制
def process_data(data):
    if not data:
        print("错误：数据为空", file=sys.stderr)
        sys.exit(1)  # 非零退出码表示错误
    return data.upper()

# sys.stdout
# sys.stdout 和 sys.stdin 示例
name = input("请输入您的名字: ")  # 使用input()，底层是sys.stdin
print(f"你好, {name}!")  # 使用print()，底层是sys.stdoutprint(f"你好, {name}!")  # 使用print()，底层是sys.stdout

# 添加更多 sys 模块常用功能示例
print("\n系统相关信息:")
print(f"Python 版本: {sys.version}")
print(f"平台: {sys.platform}")
print(f"默认编码: {sys.getdefaultencoding()}")

# 命令行参数处理示例
print("\n命令行参数:")
for i, arg in enumerate(sys.argv):
    print(f"参数 {i}: {arg}")

# 路径处理
print("\nPython 模块搜索路径:")
for path in sys.path:
    print(f"  - {path}")