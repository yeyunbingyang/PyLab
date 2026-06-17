'''
============================================================
 turtle 海龟绘图
============================================================
对照笔记: 09 绘图-turtle/turtle.md
  — 标准库, 无需安装
  — 动作: forward/backward/right/left/goto
  — 画笔: penup/pendown/pensize/pencolor
  — 图形: circle/dot/begin_fill/end_fill
  — 文字: write
  — 控制: speed/hideturtle/done
============================================================
'''

import turtle

# ═══════════════════════════════════════════════════════════════
# 1. 创建画布 + 海龟对象
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【turtle 海龟绘图 — 运行中...】")
print("=" * 50)

t = turtle.Turtle()
t.speed(5)
t.pensize(2)

# ═══════════════════════════════════════════════════════════════
# 2. 基本动作: forward / backward / right / left
# ═══════════════════════════════════════════════════════════════

# 正方形 (从原点开始)
t.penup()
t.goto(-250, 150)
t.pendown()
t.pencolor('blue')
for _ in range(4):
    t.forward(100)
    t.right(90)

# 标注
t.penup()
t.goto(-220, 110)
t.write('正方形', font=('Arial', 10, 'normal'))

# ═══════════════════════════════════════════════════════════════
# 3. circle 画圆 + 半圆
# ═══════════════════════════════════════════════════════════════

t.penup()
t.goto(-50, 180)
t.pendown()
t.pencolor('red')
t.circle(50)               # 逆时针画圆
t.penup()
t.goto(-50, 150)
t.write('circle(50)', font=('Arial', 10, 'normal'))

# 半圆
t.penup()
t.goto(100, 180)
t.pendown()
t.pencolor('green')
t.circle(50, 180)          # 180度 = 半圆
t.penup()
t.goto(100, 150)
t.write('circle(50,180)', font=('Arial', 10, 'normal'))

# ═══════════════════════════════════════════════════════════════
# 4. 五角星 (right 144°)
# ═══════════════════════════════════════════════════════════════

t.penup()
t.goto(-250, -50)
t.pendown()
t.pencolor('orange')
t.begin_fill()
t.fillcolor('yellow')
for _ in range(5):
    t.forward(120)
    t.right(144)
t.end_fill()

t.penup()
t.goto(-220, -90)
t.write('五角星 (right 144°)', font=('Arial', 10, 'normal'))

# ═══════════════════════════════════════════════════════════════
# 5. 多边形 + 填充
# ═══════════════════════════════════════════════════════════════

t.penup()
t.goto(50, -80)
t.pendown()
t.pencolor('purple')
t.begin_fill()
t.fillcolor('pink')
for _ in range(6):
    t.forward(60)
    t.right(60)
t.end_fill()

t.penup()
t.goto(60, -30)
t.write('六边形', font=('Arial', 10, 'normal'))

# ═══════════════════════════════════════════════════════════════
# 6. goto 坐标移动
# ═══════════════════════════════════════════════════════════════

t.penup()
t.goto(-250, -200)
t.pendown()
t.pencolor('brown')
points = [(-250, -200), (-150, -150), (-200, -250), (-250, -200)]
for p in points:
    t.goto(p)

t.penup()
t.goto(-250, -260)
t.write('goto 坐标连线', font=('Arial', 10, 'normal'))

# ═══════════════════════════════════════════════════════════════
# 7. 嵌套正方形 (数学之美)
# ═══════════════════════════════════════════════════════════════

t.penup()
t.goto(180, -250)
t.pendown()
t.pencolor('teal')
size = 20
for _ in range(20):
    for _ in range(4):
        t.forward(size)
        t.right(90)
    size += 5
    t.right(10)

# ═══════════════════════════════════════════════════════════════
# 8. 完成
# ═══════════════════════════════════════════════════════════════

t.hideturtle()
turtle.done()

print("  已绘制:")
print("    正方形、圆/半圆、五角星(填充)、六边形(填充)")
print("    goto 坐标连线、嵌套正方形")
print()
print("  turtle 命令速查:")
print("    forward(n)  backward(n)  right(deg)  left(deg)")
print("    penup()  pendown()  pensize(n)  pencolor('...')")
print("    circle(r, angle)  dot(size)")
print("    begin_fill()  fillcolor('...')  end_fill()")
print("    goto(x,y)  write('text')  speed(n)")
print("    hideturtle()  done()  clear()  reset()")
