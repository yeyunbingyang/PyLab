'''
============================================================
 Pillow 图像处理
============================================================
对照笔记: 07 Pillow-图像处理.md
  — Image.open/format/size/mode/show
  — crop 裁剪, thumbnail 缩略, rotate 旋转, filter 滤镜
  — ImageDraw 绘图, ImageFont 文字
============================================================
'''

from PIL import Image, ImageFilter, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════
# 1. 创建演示图片（无需外部文件即可运行）
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【1. 创建图片 Image.new()】")
print("=" * 50)

img = Image.new('RGB', (400, 300), color='#3498db')
draw = ImageDraw.Draw(img)

# 绘制矩形和文字
draw.rectangle([50, 50, 350, 250], outline='white', width=3)
draw.text((120, 120), 'Hello Pillow!', fill='white')
img.save('demo_created.png')
print(f"  已创建 demo_created.png: {img.size} {img.mode}")
print(f"  格式: PNG")

# ═══════════════════════════════════════════════════════════════
# 2. 图像基本信息
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【2. 图像基本信息】")
print("=" * 50)

img = Image.open('demo_created.png')
print(f"  format  : {img.format}       # 图像格式")
print(f"  size    : {img.size}         # 宽度 x 高度 (像素)")
print(f"  mode    : {img.mode}         # 颜色模式 (RGB/RGBA/L)")
# img.show()  # 调用系统默认图片查看器

# ═══════════════════════════════════════════════════════════════
# 3. 缩略图 thumbnail
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【3. 缩略图 thumbnail()】")
print("=" * 50)

img_thumb = img.copy()
img_thumb.thumbnail((100, 100))
img_thumb.save('demo_thumb.png')
print(f"  原始尺寸: {img.size}")
print(f"  缩略尺寸: {img_thumb.size}")

# ═══════════════════════════════════════════════════════════════
# 4. 裁剪 crop
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【4. 裁剪 crop()】")
print("=" * 50)

# crop((left, upper, right, lower))
cropped = img.crop((50, 50, 200, 200))
cropped.save('demo_cropped.png')
print(f"  裁剪区域: (50, 50, 200, 200)")
print(f"  裁剪结果: {cropped.size}")

# ═══════════════════════════════════════════════════════════════
# 5. 旋转 rotate
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【5. 旋转 rotate()】")
print("=" * 50)

rotated = img.rotate(45, expand=True, fillcolor='white')
rotated.save('demo_rotated.png')
print(f"  旋转 45°, expand=True")

# ═══════════════════════════════════════════════════════════════
# 6. 滤镜 filter
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【6. 滤镜 filter()】")
print("=" * 50)

blurred = img.filter(ImageFilter.BLUR)
blurred.save('demo_blurred.png')
print(f"  已应用模糊滤镜 BLUR → demo_blurred.png")

# ═══════════════════════════════════════════════════════════════
# 7. 颜色模式转换 convert
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【7. 颜色模式转换 convert()】")
print("=" * 50)

gray = img.convert('L')
gray.save('demo_gray.png')
print(f"  RGB → L (灰度): {gray.mode}")

print()
print("总结: open/size/mode/format | thumbnail/crop/rotate/filter | convert | ImageDraw 绘图")
