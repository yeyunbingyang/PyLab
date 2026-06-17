'''
============================================================
 CSV 读写: csv.reader / csv.writer
============================================================
对照笔记: 3.csv-读写CSV文件.md
  — csv.writer() 写入, csv.reader() 读取
  — delimiter, quotechar, quoting 参数
============================================================
'''

import csv
import random

# ═══════════════════════════════════════════════════════════════
# 1. csv.writer — 写入 CSV 文件
#    writerow()  — 写入一行
#    writerows() — 写入多行
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【csv.writer 写入】")
print("=" * 50)

with open('scores.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '语文', '数学', '英语'])
    names = ['关羽', '张飞', '赵云', '马超', '黄忠']
    for name in names:
        scores = [random.randrange(50, 101) for _ in range(3)]
        scores.insert(0, name)
        writer.writerow(scores)
print("  已生成 scores.csv (默认逗号分隔)")

# 写入时指定分隔符和引用方式
with open('scores_pipe.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='|', quoting=csv.QUOTE_ALL)
    writer.writerow(['姓名', '语文', '数学', '英语'])
    for name in names:
        scores = [random.randrange(50, 101) for _ in range(3)]
        scores.insert(0, name)
        writer.writerow(scores)
print("  已生成 scores_pipe.csv (| 分隔, 全部加引号)")

# ═══════════════════════════════════════════════════════════════
# 2. csv.reader — 读取 CSV 文件
#    reader 对象是迭代器, 每次返回一行列表
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【csv.reader 读取】")
print("=" * 50)

with open('scores.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(f"  {reader.line_num} | {'、'.join(row)}")

# 读取 pipe 分隔的文件
print()
print("--- 读取 pipe 分隔文件 ---")
with open('scores_pipe.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='|')
    for row in reader:
        print(f"  {row}")

# ═══════════════════════════════════════════════════════════════
# 3. csv.DictReader / DictWriter — 字典方式
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【DictReader / DictWriter — 字典方式】")
print("=" * 50)

# 写入
with open('scores_dict.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['姓名', '语文', '数学', '英语']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for name in names:
        writer.writerow({
            '姓名': name,
            '语文': random.randrange(50, 101),
            '数学': random.randrange(50, 101),
            '英语': random.randrange(50, 101),
        })
print("  已生成 scores_dict.csv")

# 读取
with open('scores_dict.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"  {row['姓名']}: 语文{row['语文']} 数学{row['数学']} 英语{row['英语']}")

# ═══════════════════════════════════════════════════════════════
# 4. 计算平均分
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【数据分析: 计算平均分】")
print("=" * 50)

with open('scores.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # 跳过表头
    scores_all = []
    for row in reader:
        scores = [int(s) for s in row[1:]]
        scores_all.append(scores)

averages = [sum(c) / len(c) for c in zip(*scores_all)]
for i, subj in enumerate(header[1:]):
    print(f"  {subj} 平均分: {averages[i]:.1f}")
