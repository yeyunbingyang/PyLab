import os
import re

# =========================
# 配置你的目录
# =========================
ROOT = r"F:\yeyunby的软件便利店\漫画\02 韩漫"

# =========================
# 提取序号 + 名称
# =========================
def parse_folder(name):
    """
    005.xxx【完結】 → (5, xxx【完結】)
    """
    m = re.match(r"(\d+)\.(.*)", name)
    if m:
        idx = int(m.group(1))
        rest = m.group(2).strip()
        return idx, rest
    else:
        return 10**9, name  # 没编号的排最后


# =========================
# 获取所有文件夹
# =========================
folders = [
    f for f in os.listdir(ROOT)
    if os.path.isdir(os.path.join(ROOT, f))
]

# =========================
# 排序（按原序号）
# =========================
folders.sort(key=lambda x: parse_folder(x)[0])

print("\n===== 排序结果 =====")
for f in folders:
    print(f)


# =========================
# 生成新名字映射
# =========================
mapping = []
for i, name in enumerate(folders, start=1):
    _, rest = parse_folder(name)

    new_name = f"{i:03d}.{rest}"
    old_path = os.path.join(ROOT, name)
    new_path = os.path.join(ROOT, new_name)

    mapping.append((old_path, new_path))

# =========================
# 两阶段重命名（防冲突）
# =========================
print("\n===== 第一步：临时重命名 =====")

temp_map = []

for old, new in mapping:
    tmp = old + "__tmp__"
    os.rename(old, tmp)
    temp_map.append((tmp, new))
    print(f"{old} -> TMP")

print("\n===== 第二步：正式命名 =====")

for tmp, new in temp_map:
    os.rename(tmp, new)
    print(f"{tmp} -> {new}")

print("\n===== 完成 =====")