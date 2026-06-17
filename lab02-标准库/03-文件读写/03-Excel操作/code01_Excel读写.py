'''
============================================================
 Excel 读写: openpyxl
============================================================
对照笔记: 4.读写Excel文件.md
  — xlrd/xlwt 操作 .xls (旧格式)
  — openpyxl 操作 .xlsx (新格式)
  — 样式: Font, Alignment, Border
  — 公式计算 + 图表 BarChart
============================================================
'''

import random
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side

# ═══════════════════════════════════════════════════════════════
# 1. 创建工作簿 + 写入数据
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【1. openpyxl 创建 + 写入】")
print("=" * 50)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = '期末成绩'

# 写入表头
titles = ('姓名', '语文', '数学', '英语')
for col_i, title in enumerate(titles, 1):
    ws.cell(1, col_i, title)

# 写入学生数据
names = ('关羽', '张飞', '赵云', '马超', '黄忠')
for row_i, name in enumerate(names, 2):
    ws.cell(row_i, 1, name)
    for col_i in range(2, 5):
        ws.cell(row_i, col_i, random.randrange(50, 101))

wb.save('考试成绩表.xlsx')
print("  已生成 考试成绩表.xlsx")

# ═══════════════════════════════════════════════════════════════
# 2. 读取 Excel
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【2. openpyxl 读取】")
print("=" * 50)

wb = openpyxl.load_workbook('考试成绩表.xlsx')
ws = wb.active
print(f"  工作表: {ws.title}")
print(f"  行数: {ws.max_row}, 列数: {ws.max_column}")
print(f"  表头: {[ws.cell(1, c).value for c in range(1, ws.max_column+1)]}")
print("  前3行:")
for row in ws.iter_rows(min_row=1, max_row=3, values_only=True):
    print(f"    {row}")

# ═══════════════════════════════════════════════════════════════
# 3. 公式计算
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【3. 公式 + 样式】")
print("=" * 50)

wb = openpyxl.load_workbook('考试成绩表.xlsx')
ws = wb.worksheets[0]

# 添加平均分列
ws['E1'] = '平均分'
ws.cell(1, 5).font = Font(size=12, bold=True, color='ff0000')

for i in range(2, 7):
    ws[f'E{i}'] = f'=AVERAGE(B{i}:D{i})'

wb.save('考试成绩表.xlsx')
print("  已添加平均分列 (公式 =AVERAGE)")

# ═══════════════════════════════════════════════════════════════
# 4. 使用 xlwt / xlrd (旧格式 .xls)
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【4. xlwt/xlrd — 旧 .xls 格式】")
print("=" * 50)

try:
    import xlwt
    import xlrd

    # 写入 .xls
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('一年级二班')
    titles = ('姓名', '语文', '数学', '英语')
    for i, t in enumerate(titles):
        sheet.write(0, i, t)
    for row_i, name in enumerate(names, 1):
        sheet.write(row_i, 0, name)
        for col_i in range(1, 4):
            sheet.write(row_i, col_i, random.randrange(50, 101))
    wb.save('考试成绩表_xlwt.xls')
    print("  已生成 考试成绩表_xlwt.xls (旧格式)")

    # 读取 .xls
    wb = xlrd.open_workbook('考试成绩表_xlwt.xls')
    sheet = wb.sheet_by_index(0)
    print(f"  工作表: {sheet.name}, 行数: {sheet.nrows}, 列数: {sheet.ncols}")
    print(f"  第1行数据: {sheet.row_values(0)}")

except ImportError:
    print("  xlwt/xlrd 未安装，跳过 .xls 演示")
    print("  安装: pip install xlwt xlrd")

# ═══════════════════════════════════════════════════════════════
# 5. 图表 BarChart
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【5. 图表 BarChart】")
print("=" * 50)

from openpyxl.chart import BarChart, Reference

wb = openpyxl.load_workbook('考试成绩表.xlsx')
ws = wb.active

chart = BarChart()
chart.type = 'col'
chart.style = 10
chart.title = '期末成绩统计'
chart.y_axis.title = '分数'
chart.x_axis.title = '科目'

data = Reference(ws, min_col=2, min_row=1, max_row=6, max_col=4)
cats = Reference(ws, min_col=1, min_row=2, max_row=6)

chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4
ws.add_chart(chart, 'A10')

wb.save('考试成绩表.xlsx')
print("  已向 考试成绩表.xlsx 添加柱状图")

print()
print("总结: openpyxl → 创建/读取/公式/样式/图表 | xlwt/xlrd → 旧 .xls 格式")
