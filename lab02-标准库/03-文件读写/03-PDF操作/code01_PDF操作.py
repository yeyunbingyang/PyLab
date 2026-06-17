'''
============================================================
 PDF 操作: PyPDF2 + reportlab
============================================================
对照笔记: 6.PyPDF2-操作PDF文件.md
  — PdfReader 读取文本/页数
  — PdfWriter 创建/合并/旋转/加密
  — merge_page 添加水印
  — reportlab 创建 PDF + 中文支持
============================================================
'''

# ═══════════════════════════════════════════════════════════════
# 1. PdfReader — 读取 PDF
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【1. PyPDF2 读取 PDF】")
print("=" * 50)

try:
    from PyPDF2 import PdfReader, PdfWriter

    print("  PyPDF2 已安装")
    print("  基本用法:")
    print("    reader = PdfReader('test.pdf')")
    print("    print(f'页数: {len(reader.pages)}')")
    print("    page = reader.pages[0]")
    print("    text = page.extract_text()")
    print()
    print("  注意: 中文 PDF 提取文本可能需要 pdfminer.six")
    print("    pip install pdfminer.six")
    print("    pdf2text.py test.pdf")

except ImportError:
    print("  PyPDF2 未安装")
    print("  安装: pip install PyPDF2")

# ═══════════════════════════════════════════════════════════════
# 2. PdfWriter — 创建空白 PDF
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【2. PdfWriter 创建 PDF】")
print("=" * 50)

try:
    from PyPDF2 import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)  # A4 尺寸
    with open('output_blank.pdf', 'wb') as f:
        writer.write(f)
    print("  已创建 output_blank.pdf (空白A4页)")

except ImportError:
    print("  需要 PyPDF2")

# ═══════════════════════════════════════════════════════════════
# 3. 页面旋转
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【3. 页面旋转】")
print("=" * 50)

print("  用法:")
print("    reader = PdfReader('input.pdf')")
print("    writer = PdfWriter()")
print("    for no, page in enumerate(reader.pages):")
print("        if no % 2 == 0:")
print("            new_page = page.rotate(-90)  # 偶数页逆时针")
print("        else:")
print("            new_page = page.rotate(90)   # 奇数页顺时针")
print("        writer.add_page(new_page)")
print("    writer.write('rotated.pdf')")

# ═══════════════════════════════════════════════════════════════
# 4. PDF 加密
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【4. PDF 加密】")
print("=" * 50)

print("  用法:")
print("    writer = PdfWriter()")
print("    for page in reader.pages:")
print("        writer.add_page(page)")
print("    writer.encrypt('mypassword')")
print("    writer.write('encrypted.pdf')")

# ═══════════════════════════════════════════════════════════════
# 5. 添加水印
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【5. 添加水印】")
print("=" * 50)

print("  用法:")
print("    reader1 = PdfReader('original.pdf')")
print("    reader2 = PdfReader('watermark.pdf')")
print("    watermark_page = reader2.pages[0]")
print("    for page in reader1.pages:")
print("        page.merge_page(watermark_page)")
print("        writer.add_page(page)")
print("    writer.write('watermarked.pdf')")

# ═══════════════════════════════════════════════════════════════
# 6. reportlab — 创建 PDF + 中文
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【6. reportlab 创建 PDF】")
print("=" * 50)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    c = canvas.Canvas('demo_reportlab.pdf', pagesize=A4)
    w, h = A4
    c.drawString(100, h - 100, 'Hello from reportlab!')
    c.drawString(100, h - 130, 'Python 生成 PDF')
    c.save()
    print("  已生成 demo_reportlab.pdf")

except ImportError:
    print("  reportlab 未安装")
    print("  安装: pip install reportlab")

print()
print("总结: PyPDF2 → 读取/创建/旋转/加密/水印 | reportlab → 从头创建PDF")
