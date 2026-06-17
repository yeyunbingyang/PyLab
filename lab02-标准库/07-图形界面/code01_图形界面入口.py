'''
============================================================
 图形界面 — wxPython / PyQt
============================================================
对照笔记: 07 图形界面/wxPython.md + PyQt6.md
  — wxPython: wx.App / wx.Frame / wx.Panel / sizer
  — PyQt6: QApplication / QWidget / QLabel / QPushButton / layout
  — 详细练习见: lab01-语法核心/10-界面开发/
============================================================
'''

# ═══════════════════════════════════════════════════════════════
# 1. wxPython 入门
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【wxPython 入门】")
print("=" * 50)

print("  安装: pip install wxPython")
print()
print("  基本结构:")
print("    import wx")
print("    app = wx.App()")
print("    frame = wx.Frame(None, title='Hello wxPython', size=(400, 300))")
print("    panel = wx.Panel(frame)")
print("    frame.Show()")
print("    app.MainLoop()")
print()
print("  常用控件:")
print("    wx.Button   — 按钮")
print("    wx.TextCtrl — 文本框")
print("    wx.StaticText — 标签")
print("    wx.ListBox  — 列表框")
print("    wx.CheckBox — 复选框")
print()
print("  布局管理:")
print("    wx.BoxSizer(wx.HORIZONTAL)  — 水平布局")
print("    wx.BoxSizer(wx.VERTICAL)    — 垂直布局")
print("    wx.GridSizer(rows, cols)    — 网格布局")

# ═══════════════════════════════════════════════════════════════
# 2. PyQt6 入门
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【PyQt6 入门】")
print("=" * 50)

print("  安装: pip install PyQt6")
print()
print("  基本结构:")
print("    from PyQt6.QtWidgets import QApplication, QWidget, QLabel")
print("    app = QApplication([])")
print("    window = QWidget()")
print("    window.setWindowTitle('Hello PyQt6')")
print("    label = QLabel('Hello World', window)")
print("    window.show()")
print("    app.exec()")
print()
print("  信号与槽:")
print("    button.clicked.connect(on_click)  # 按钮点击 → 处理函数")
print()
print("  常用控件:")
print("    QPushButton / QLineEdit / QLabel / QComboBox")
print("    QCheckBox / QRadioButton / QTextEdit / QTableWidget")

# ═══════════════════════════════════════════════════════════════
# 3. wxPython 完整示例 (抽奖器)
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【完整示例: wxPython 抽奖器】")
print("=" * 50)

lottery_code = r"""
import wx
import random

class LotteryFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='抽奖器', size=(300, 200))
        panel = wx.Panel(self)
        self.label = wx.StaticText(panel, label='点击按钮抽奖', pos=(80, 30))
        btn = wx.Button(panel, label='抽奖', pos=(100, 80))
        btn.Bind(wx.EVT_BUTTON, self.on_lottery)

    def on_lottery(self, event):
        prizes = ['一等奖', '二等奖', '三等奖', '谢谢参与']
        self.label.SetLabel(random.choice(prizes))

app = wx.App()
LotteryFrame().Show()
app.MainLoop()
"""
print(lottery_code.strip())

# ═══════════════════════════════════════════════════════════════
# 4. 导航
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【练习代码位置】")
print("=" * 50)
print("  lab01-语法核心/10-界面开发/")
print("    code01_第1个wx程序.py")
print("    code02_窗口类.py")
print("    code03_抽奖器.py")
print("    code04_计算器.py")
