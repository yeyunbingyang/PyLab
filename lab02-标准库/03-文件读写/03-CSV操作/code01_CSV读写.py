'''
============================================================
 CSV 完整演示: reader / writer / DictReader / DictWriter
============================================================
对照笔记: 3.csv-读写CSV文件.md
============================================================
'''

import csv
import random

# ═══════════════════════════════════════════════════════════════
# 1. csv.writer 写入
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【csv.writer — 写入 CSV】")
print("=" * 50)

with open('students.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '语文', '数学', '英语'])
    names = ['关羽', '张飞', '赵云', '马超', '黄忠']
    for name in names:
        scores = [random.randrange(50, 101) for _ in range(3)]
        scores.insert(0, name)
        writer.writerow(scores)
print("  students.csv 已生成 (默认逗号分隔)")

# 自定义分隔符和引号
with open('students_delim.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='|', quoting=csv.QUOTE_ALL)
    writer.writerow(['姓名', '语文', '数学', '英语'])
    for name in names:
        writer.writerow([name] + [str(random.randrange(50, 101)) for _ in range(3)])
print("  students_delim.csv 已生成 (| 分隔, 全部加引号)")

# ═══════════════════════════════════════════════════════════════
# 2. csv.reader 读取
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【csv.reader — 读取 CSV】")
print("=" * 50)

with open('students.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    print(f"  表头: {header}")
    for row in reader:
        print(f"  行{reader.line_num}: {row}")

# ═══════════════════════════════════════════════════════════════
# 3. DictWriter / DictReader
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【DictWriter / DictReader — 字典方式】")
print("=" * 50)

fieldnames = ['姓名', '语文', '数学', '英语']
with open('students_dict.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for name in names:
        writer.writerow({
            '姓名': name,
            '语文': random.randrange(50, 101),
            '数学': random.randrange(50, 101),
            '英语': random.randrange(50, 101),
        })

with open('students_dict.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"  {row['姓名']}: 语{row['语文']} 数{row['数学']} 英{row['英语']}")

# ═══════════════════════════════════════════════════════════════
# 4. 数据分析: 平均分
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【数据分析: 计算各科平均分】")
print("=" * 50)

with open('students.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    all_scores = []
    for row in reader:
        all_scores.append([int(s) for s in row[1:]])

averages = [sum(c) / len(c) for c in zip(*all_scores)]
for i, subj in enumerate(header[1:]):
    print(f"  {subj} 平均分: {averages[i]:.1f}")
