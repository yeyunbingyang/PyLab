"""
Python Turtle 模块完整学习示例

Turtle 模块是 Python 内置的图形绘制库，通过控制海龟在画布上移动来绘制图形。
适合初学者学习编程概念和图形绘制。

主要功能：
- 基本绘图（线条、形状）
- 颜色和样式设置
- 动画和交互
- 窗口和画布控制
"""

import turtle
import time
from my_package import my_tools

# ==================== 基础设置和窗口控制 ====================
print("=== Turtle 基础设置 ===")

# 创建画布和海龟
screen = turtle.Screen()
screen.title("Turtle 绘图学习示例")
screen.bgcolor("white")
screen.setup(width=800, height=600)

# 创建多个海龟对象
pen = turtle.Turtle()
pen.shape("turtle")  # 设置海龟形状：turtle, arrow, circle, square, triangle, classic
pen.speed(5)  # 设置速度：1-10，0最快

# 基础移动命令示例
print("演示基础移动...")
pen.penup()  # 抬起画笔
pen.goto(-200, 200)  # 移动到指定位置
pen.pendown()  # 放下画笔
pen.write("基础移动示例", font=("Arial", 16, "bold"))

time.sleep(2)

# ==================== 1. 基本绘图命令 ====================
def basic_drawing_demo():
    """演示基本绘图命令"""
    print("\n=== 基本绘图命令演示 ===")
    
    # 创建新的海龟用于基础绘图
    basic_pen = turtle.Turtle()
    basic_pen.speed(5)
    basic_pen.color("blue")
    basic_pen.pensize(3)
    
    # 前进、后退、左转、右转
    basic_pen.penup()
    basic_pen.goto(-300, 100)
    basic_pen.pendown()
    basic_pen.write("前进/转向", font=("Arial", 12))
    
    # 画正方形
    basic_pen.color("red")
    for i in range(4):
        basic_pen.forward(50)
        basic_pen.left(90)
    
    # 画三角形
    basic_pen.penup()
    basic_pen.goto(-200, 100)
    basic_pen.pendown()
    basic_pen.color("green")
    for i in range(3):
        basic_pen.forward(50)
        basic_pen.left(120)
    
    # 画圆形
    basic_pen.penup()
    basic_pen.goto(-100, 50)
    basic_pen.pendown()
    basic_pen.color("blue")
    basic_pen.circle(30)  # 半径为30的圆
    
    # 画半圆
    basic_pen.penup()
    basic_pen.goto(0, 50)
    basic_pen.pendown()
    basic_pen.color("purple")
    basic_pen.circle(30, 180)  # 半径30，角度180度的弧
    
    # 画多边形
    basic_pen.penup()
    basic_pen.goto(100, 50)
    basic_pen.pendown()
    basic_pen.color("orange")
    sides = 6
    for i in range(sides):
        basic_pen.forward(40)
        basic_pen.left(360/sides)
    
    basic_pen.hideturtle()

basic_drawing_demo()

# ==================== 2. 颜色和样式设置 ====================
def color_and_style_demo():
    """演示颜色和样式设置"""
    print("\n=== 颜色和样式演示 ===")
    
    style_pen = turtle.Turtle()
    style_pen.speed(6)
    
    # 不同画笔粗细
    style_pen.penup()
    style_pen.goto(-300, -50)
    style_pen.pendown()
    
    colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    sizes = [1, 3, 5, 7, 10, 15]
    
    for i, (color, size) in enumerate(zip(colors, sizes)):
        style_pen.pensize(size)
        style_pen.color(color)
        style_pen.forward(50)
    
    # 填充示例
    style_pen.penup()
    style_pen.goto(-100, -50)
    style_pen.pendown()
    
    # 填充矩形
    style_pen.pensize(2)
    style_pen.color("darkgreen")
    style_pen.begin_fill()
    for i in range(2):
        style_pen.forward(80)
        style_pen.left(90)
        style_pen.forward(60)
        style_pen.left(90)
    style_pen.end_fill()
    
    # 填充圆形
    style_pen.penup()
    style_pen.goto(50, -80)
    style_pen.pendown()
    
    style_pen.color("darkblue", "lightblue")  # 边框色，填充色
    style_pen.begin_fill()
    style_pen.circle(40)
    style_pen.end_fill()
    
    style_pen.hideturtle()

color_and_style_demo()

# ==================== 3. 坐标和角度系统 ====================
def coordinate_demo():
    """演示坐标和角度系统"""
    print("\n=== 坐标和角度系统演示 ===")
    
    coord_pen = turtle.Turtle()
    coord_pen.speed(7)
    coord_pen.pensize(1)
    
    # 绘制坐标轴
    coord_pen.penup()
    coord_pen.goto(-200, 0)
    coord_pen.pendown()
    coord_pen.color("black")
    coord_pen.forward(400)  # X轴
    
    coord_pen.penup()
    coord_pen.goto(0, -150)
    coord_pen.pendown()
    coord_pen.left(90)
    coord_pen.forward(300)  # Y轴
    
    # 标记原点
    coord_pen.penup()
    coord_pen.goto(-10, -10)
    coord_pen.write("O", font=("Arial", 12))
    
    # 演示绝对坐标移动
    coord_pen.penup()
    coord_pen.goto(100, 100)
    coord_pen.pendown()
    coord_pen.color("red")
    coord_pen.dot(10)  # 画一个点
    coord_pen.write("(100, 100)", font=("Arial", 10))
    
    # 演示相对坐标移动
    coord_pen.penup()
    coord_pen.goto(-100, -100)
    coord_pen.pendown()
    coord_pen.color("blue")
    coord_pen.setheading(45)  # 设置朝向45度
    coord_pen.forward(100)
    coord_pen.write("45度方向", font=("Arial", 10))
    
    # 演示角度设置
    coord_pen.penup()
    coord_pen.goto(-150, 50)
    coord_pen.pendown()
    coord_pen.color("green")
    
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    for angle in angles:
        coord_pen.setheading(angle)
        coord_pen.forward(30)
        coord_pen.backward(30)
    
    coord_pen.hideturtle()

coordinate_demo()

# ==================== 4. 图案绘制示例 ====================
def pattern_drawing_demo():
    """演示复杂图案绘制"""
    print("\n=== 图案绘制演示 ===")
    
    pattern_pen = turtle.Turtle()
    pattern_pen.speed(8)
    pattern_pen.pensize(2)
    
    # 绘制星形
    pattern_pen.penup()
    pattern_pen.goto(-200, -250)
    pattern_pen.pendown()
    pattern_pen.color("gold")
    
    for i in range(5):
        pattern_pen.forward(100)
        pattern_pen.right(144)  # 144度形成五角星
    
    # 绘制螺旋
    pattern_pen.penup()
    pattern_pen.goto(-50, -250)
    pattern_pen.pendown()
    pattern_pen.color("purple")
    
    for i in range(50):
        pattern_pen.forward(i * 2)
        pattern_pen.right(91)
    
    # 绘制花朵图案
    pattern_pen.penup()
    pattern_pen.goto(100, -200)
    pattern_pen.pendown()
    pattern_pen.color("pink")
    
    for i in range(36):
        pattern_pen.circle(20)
        pattern_pen.right(10)
    
    # 绘制万花筒图案
    pattern_pen.penup()
    pattern_pen.goto(200, -200)
    pattern_pen.pendown()
    pattern_pen.color("cyan")
    
    for i in range(6):
        pattern_pen.circle(30)
        pattern_pen.left(60)
        for j in range(6):
            pattern_pen.forward(20)
            pattern_pen.backward(20)
            pattern_pen.right(60)
    
    pattern_pen.hideturtle()

pattern_drawing_demo()

# ==================== 5. 交互和动画 ====================
def interactive_demo():
    """演示交互功能和动画"""
    print("\n=== 交互和动画演示 ===")
    
    # 创建动画海龟
    animated_pen = turtle.Turtle()
    animated_pen.shape("turtle")
    animated_pen.color("red")
    animated_pen.speed(1)
    
    # 动画：画正方形
    animated_pen.penup()
    animated_pen.goto(-100, -350)
    animated_pen.pendown()
    
    for i in range(4):
        animated_pen.forward(60)
        animated_pen.left(90)
        time.sleep(0.5)  # 延迟产生动画效果
    
    # 彩虹圆动画
    rainbow_pen = turtle.Turtle()
    rainbow_pen.speed(8)
    rainbow_pen.pensize(3)
    
    rainbow_pen.penup()
    rainbow_pen.goto(50, -380)
    rainbow_pen.pendown()
    
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "purple"]
    for i, color in enumerate(colors):
        rainbow_pen.color(color)
        rainbow_pen.circle(30 + i*5)
    
    # 文字动画效果
    text_pen = turtle.Turtle()
    text_pen.penup()
    text_pen.hideturtle()
    text_pen.color("black")
    
    messages = ["Python", "Turtle", "绘图", "学习", "示例"]
    for i, msg in enumerate(messages):
        text_pen.clear()
        text_pen.goto(200, -350 + i*20)
        text_pen.write(msg, font=("Arial", 16, "bold"), align="center")
        time.sleep(0.8)
    
    text_pen.clear()

interactive_demo()

# ==================== 6. 时间显示（保留原代码功能） ====================
def digital_clock_demo():
    """数字时钟演示 - 基于原代码改进"""
    print("\n=== 数字时钟演示 ===")
    
    clock_pen = turtle.Turtle()
    clock_pen.hideturtle()
    clock_pen.penup()
    clock_pen.goto(0, 0)
    
    # 时钟边框
    border_pen = turtle.Turtle()
    border_pen.hideturtle()
    border_pen.penup()
    border_pen.goto(-150, 50)
    border_pen.pendown()
    border_pen.pensize(3)
    border_pen.color("navy")
    
    for i in range(2):
        border_pen.forward(300)
        border_pen.right(90)
        border_pen.forward(100)
        border_pen.right(90)
    
    # 显示时间（运行5次后停止）
    for i in range(5):
        time.sleep(1)
        times = my_tools.get_time()
        clock_pen.clear()
        clock_pen.write(times, font=("Courier", 36, "bold"), align="center")
        print(f"显示时间: {times}")

digital_clock_demo()

# ==================== 7. 键盘和鼠标交互 ====================
def mouse_keyboard_demo():
    """演示键盘鼠标交互"""
    print("\n=== 键盘鼠标交互演示 ===")
    print("点击屏幕或按方向键进行交互...")
    
    # 创建交互海龟
    interactive_pen = turtle.Turtle()
    interactive_pen.shape("turtle")
    interactive_pen.color("darkgreen")
    interactive_pen.speed(0)
    
    # 定义键盘响应函数
    def move_up():
        interactive_pen.setheading(90)
        interactive_pen.forward(20)
    
    def move_down():
        interactive_pen.setheading(270)
        interactive_pen.forward(20)
    
    def move_left():
        interactive_pen.setheading(180)
        interactive_pen.forward(20)
    
    def move_right():
        interactive_pen.setheading(0)
        interactive_pen.forward(20)
    
    def change_color():
        import random
        colors = ["red", "blue", "green", "purple", "orange", "pink"]
        interactive_pen.color(random.choice(colors))
    
    def toggle_pen():
        if interactive_pen.isdown():
            interactive_pen.penup()
        else:
            interactive_pen.pendown()
    
    # 绑定键盘事件
    screen.onkey(move_up, "Up")
    screen.onkey(move_down, "Down")
    screen.onkey(move_left, "Left")
    screen.onkey(move_right, "Right")
    screen.onkey(change_color, "c")
    screen.onkey(toggle_pen, "space")
    
    # 鼠标点击事件
    def on_click(x, y):
        interactive_pen.penup()
        interactive_pen.goto(x, y)
        interactive_pen.pendown()
        interactive_pen.dot(20, "red")
    
    screen.onclick(on_click)
    
    # 等待用户交互
    screen.listen()
    
    # 3秒后结束交互
    time.sleep(3)
    screen.onclick(None)  # 取消点击事件

mouse_keyboard_demo()

# ==================== 8. 高级绘图示例 ====================
def advanced_drawing_demo():
    """高级绘图示例 - 分形树"""
    print("\n=== 高级绘图：分形树 ===")
    
    def draw_tree(pen, branch_length, angle, level):
        """递归绘制分形树"""
        if level == 0:
            return
        
        # 绘制树干
        pen.forward(branch_length)
        
        # 右分支
        pen.right(angle)
        draw_tree(pen, branch_length * 0.7, angle, level - 1)
        
        # 左分支
        pen.left(angle * 2)
        draw_tree(pen, branch_length * 0.7, angle, level - 1)
        
        # 回到原位
        pen.right(angle)
        pen.backward(branch_length)
    
    # 创建树的海龟
    tree_pen = turtle.Turtle()
    tree_pen.speed(0)
    tree_pen.color("brown")
    tree_pen.pensize(2)
    
    # 绘制多棵树
    positions = [(-200, -400), (0, -400), (200, -400)]
    for pos in positions:
        tree_pen.penup()
        tree_pen.goto(pos)
        tree_pen.setheading(90)  # 向上
        tree_pen.pendown()
        
        # 树干用棕色
        tree_pen.color("brown")
        draw_tree(tree_pen, 80, 25, 5)
        
        # 在顶部画绿色的树冠
        tree_pen.penup()
        tree_pen.goto(pos[0], pos[1] + 80)
        tree_pen.pendown()
        tree_pen.color("green")
        tree_pen.begin_fill()
        tree_pen.circle(30)
        tree_pen.end_fill()
    
    tree_pen.hideturtle()

advanced_drawing_demo()

# ==================== 总结和API速查 ====================
def api_summary():
    """显示API速查表"""
    print("\n" + "="*50)
    print("=== Turtle API 速查表 ===")
    print("\n🖊️ 画笔控制:")
    print("  pen.penup() - 抬起画笔")
    print("  pen.pendown() - 放下画笔")
    print("  pen.pensize(width) - 设置画笔粗细")
    print("  pen.color(color) / pen.color(pen, fill) - 设置颜色")
    print("  pen.speed(speed) - 设置速度(0-10)")
    
    print("\n📍 移动控制:")
    print("  pen.forward(distance) - 前进")
    print("  pen.backward(distance) - 后退")
    print("  pen.right(angle) - 右转")
    print("  pen.left(angle) - 左转")
    print("  pen.goto(x, y) - 移动到坐标")
    print("  pen.setheading(angle) - 设置朝向")
    
    print("\n📐 图形绘制:")
    print("  pen.circle(radius) - 画圆")
    print("  pen.circle(radius, extent) - 画弧")
    print("  pen.dot(size) - 画点")
    print("  pen.write(text) - 写文字")
    print("  pen.begin_fill() / pen.end_fill() - 填充")
    
    print("\n🖼️ 窗口控制:")
    print("  screen.title(title) - 设置标题")
    print("  screen.bgcolor(color) - 设置背景色")
    print("  screen.setup(width, height) - 设置窗口大小")
    print("  screen.onclick(function) - 鼠标点击事件")
    print("  screen.onkey(function, key) - 键盘事件")

api_summary()

# ==================== 最终画面 ====================
print("\n=== 绘图完成 ===")
print("所有示例已绘制完成！")
print("按任意键关闭窗口...")

# 添加标题和说明
title_pen = turtle.Turtle()
title_pen.hideturtle()
title_pen.penup()
title_pen.goto(0, 250)
title_pen.color("darkblue")
title_pen.write("Python Turtle 模块学习示例", font=("Arial", 20, "bold"), align="center")

title_pen.goto(0, 220)
title_pen.color("black")
title_pen.write("包含基础绘图、颜色样式、坐标系统、图案绘制、交互动画等示例", 
                font=("Arial", 12), align="center")

# 保持窗口打开
input("按回车键退出程序...")

# 关闭窗口
turtle.bye()