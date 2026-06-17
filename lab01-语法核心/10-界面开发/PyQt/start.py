"""
PyQt6 快速入门教程

PyQt6 是 Python 最强大的 GUI 库之一，基于 Qt6 框架。
本教程从基础到进阶，全面介绍 PyQt6 的使用方法。

安装：pip install PyQt6

核心概念：
- QApplication：应用实例，管理程序生命周期
- QWidget：基础窗口类，所有控件的基类
- 事件循环：处理用户交互和系统事件
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QMainWindow, QMessageBox,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QRadioButton,
    QProgressBar, QSlider, QSpinBox, QDockWidget, QMenuBar,
    QStatusBar, QToolBar, QFileDialog, QColorDialog, QFontDialog
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread, QDateTime
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction, QPainter, QColor

# ==================== 1. 基础窗口示例 ====================
def basic_window_demo():
    """最基础的 PyQt6 窗口示例"""
    print("=== 基础窗口示例 ===")
    
    # 创建应用实例（每个程序必须有且只有一个）
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle('Hello, PyQt6 - 基础窗口')
    window.setGeometry(100, 100, 400, 300)  # (x, y, width, height)
    
    # 设置窗口图标（如果有的话）
    # window.setWindowIcon(QIcon('icon.png'))
    
    # 创建标签并添加到窗口
    label = QLabel('Hello, PyQt6 World! 👋', window)
    label.setGeometry(50, 50, 300, 50)
    label.setFont(QFont('Arial', 16))
    label.setStyleSheet("color: #2E86AB; font-weight: bold;")
    
    # 创建按钮
    button = QPushButton('点击我!', window)
    button.setGeometry(50, 120, 120, 40)
    button.setStyleSheet("""
        QPushButton {
            background-color: #A23B72;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #C73E1D;
        }
    """)
    
    # 按钮点击事件
    def on_button_click():
        label.setText("按钮被点击了! 🎉")
        button.setText('已点击!')
        
    button.clicked.connect(on_button_click)
    
    # 创建第二个标签显示点击计数
    click_count = 0
    count_label = QLabel('点击次数: 0', window)
    count_label.setGeometry(50, 170, 200, 30)
    
    def count_clicks():
        nonlocal click_count
        click_count += 1
        count_label.setText(f'点击次数: {click_count}')
    
    button2 = QPushButton('计数', window)
    button2.setGeometry(200, 120, 120, 40)
    button2.clicked.connect(count_clicks)
    
    # 显示窗口
    window.show()
    
    # 进入应用主循环
    return app.exec()

# ==================== 2. 布局管理示例 ====================
def layout_demo():
    """布局管理示例 - QVBoxLayout, QHBoxLayout"""
    print("\n=== 布局管理示例 ===")
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle('PyQt6 布局管理')
    window.setGeometry(200, 200, 500, 400)
    
    # 创建垂直布局
    main_layout = QVBoxLayout()
    
    # 标题
    title_label = QLabel('🎨 PyQt6 布局管理演示')
    title_label.setFont(QFont('Arial', 18, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("color: #2E86AB; margin: 10px;")
    main_layout.addWidget(title_label)
    
    # 水平布局1：输入框和按钮
    h_layout1 = QHBoxLayout()
    
    input_label = QLabel('输入内容:')
    input_label.setStyleSheet("font-weight: bold;")
    line_edit = QLineEdit()
    line_edit.setPlaceholderText('请输入文本...')
    line_edit.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
    
    submit_btn = QPushButton('提交')
    submit_btn.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    
    def show_input():
        text = line_edit.text()
        if text:
            QMessageBox.information(window, '输入内容', f'您输入了: {text}')
        else:
            QMessageBox.warning(window, '警告', '请先输入内容!')
    
    submit_btn.clicked.connect(show_input)
    
    h_layout1.addWidget(input_label)
    h_layout1.addWidget(line_edit)
    h_layout1.addWidget(submit_btn)
    main_layout.addLayout(h_layout1)
    
    # 水平布局2：下拉框和复选框
    h_layout2 = QHBoxLayout()
    
    combo_label = QLabel('选择选项:')
    combo = QComboBox()
    combo.addItems(['选项1', '选项2', '选项3', '选项4'])
    combo.setStyleSheet("padding: 5px;")
    
    checkbox = QCheckBox('启用功能')
    checkbox.setStyleSheet("font-size: 12px;")
    
    radio1 = QRadioButton('选项A')
    radio2 = QRadioButton('选项B')
    
    h_layout2.addWidget(combo_label)
    h_layout2.addWidget(combo)
    h_layout2.addWidget(checkbox)
    h_layout2.addWidget(radio1)
    h_layout2.addWidget(radio2)
    main_layout.addLayout(h_layout2)
    
    # 进度条和滑块
    progress_label = QLabel('进度演示:')
    main_layout.addWidget(progress_label)
    
    progress_bar = QProgressBar()
    progress_bar.setValue(30)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 3px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 2px;
        }
    """)
    main_layout.addWidget(progress_bar)
    
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(100)
    slider.setValue(30)
    
    def update_progress(value):
        progress_bar.setValue(value)
    
    slider.valueChanged.connect(update_progress)
    main_layout.addWidget(slider)
    
    # 文本编辑区域
    text_label = QLabel('文本编辑区:')
    main_layout.addWidget(text_label)
    
    text_edit = QTextEdit()
    text_edit.setPlaceholderText('在这里输入多行文本...')
    text_edit.setMaximumHeight(100)
    text_edit.setStyleSheet("""
        QTextEdit {
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 5px;
        }
    """)
    main_layout.addWidget(text_edit)
    
    # 按钮组
    button_layout = QHBoxLayout()
    
    def show_about():
        QMessageBox.about(window, '关于', 'PyQt6 布局管理演示程序\n\n作者：Python学习者\n版本：1.0')
    
    def close_app():
        window.close()
    
    about_btn = QPushButton('关于')
    about_btn.clicked.connect(show_about)
    
    exit_btn = QPushButton('退出')
    exit_btn.setStyleSheet("background-color: #f44336; color: white;")
    exit_btn.clicked.connect(close_app)
    
    button_layout.addWidget(about_btn)
    button_layout.addWidget(exit_btn)
    button_layout.addStretch()  # 添加弹性空间
    main_layout.addLayout(button_layout)
    
    window.setLayout(main_layout)
    window.show()
    return app.exec()

# ==================== 3. 主窗口示例 ====================
class MainWindow(QMainWindow):
    """主窗口类 - 继承自 QMainWindow"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        """初始化用户界面"""
        # 窗口基本设置
        self.setWindowTitle('PyQt6 主窗口示例')
        self.setGeometry(300, 300, 800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标题
        title = QLabel('🏠 PyQt6 主窗口功能演示')
        title.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2E86AB; margin: 20px;")
        layout.addWidget(title)
        
        # 添加状态栏
        self.statusBar().showMessage('就绪 - PyQt6 主窗口程序运行中')
        
        # 创建菜单栏
        self.create_menus()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 添加控制面板
        self.create_control_panel(layout)
        
        # 创建停靠窗口
        self.create_dock_windows()
    
    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        new_action = QAction('新建(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('新建文件')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('打开文件')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        
        cut_action = QAction('剪切(&T)', self)
        cut_action.setShortcut('Ctrl+X')
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('复制(&C)', self)
        copy_action.setShortcut('Ctrl+C')
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('粘贴(&P)', self)
        paste_action.setShortcut('Ctrl+V')
        edit_menu.addAction(paste_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar('主工具栏')
        toolbar.setMovable(False)  # 固定工具栏
        
        # 新建按钮
        new_btn = QAction('新建', self)
        new_btn.setStatusTip('新建文件')
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)
        
        # 打开按钮
        open_btn = QAction('打开', self)
        open_btn.setStatusTip('打开文件')
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)
        
        toolbar.addSeparator()
        
        # 颜色选择按钮
        color_btn = QAction('颜色', self)
        color_btn.setStatusTip('选择颜色')
        color_btn.triggered.connect(self.choose_color)
        toolbar.addAction(color_btn)
        
        # 字体选择按钮
        font_btn = QAction('字体', self)
        font_btn.setStatusTip('选择字体')
        font_btn.triggered.connect(self.choose_font)
        toolbar.addAction(font_btn)
    
    def create_control_panel(self, layout):
        """创建控制面板"""
        # 信息显示区
        self.info_label = QLabel('欢迎使用 PyQt6 主窗口程序!')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.info_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        buttons_info = [
            ('显示消息', self.show_message),
            ('文件对话框', self.show_file_dialog),
            ('清空信息', self.clear_info),
            ('更新状态', self.update_status)
        ]
        
        for text, slot in buttons_info:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        # 文本编辑区
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('在这里输入文本内容...')
        self.text_edit.setMaximumHeight(200)
        layout.addWidget(self.text_edit)
    
    def create_dock_windows(self):
        """创建停靠窗口"""
        # 左侧停靠窗口
        left_dock = QDockWidget('工具箱', self)
        left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        dock_widget = QWidget()
        dock_layout = QVBoxLayout()
        
        # 添加一些工具按钮
        tools = ['画笔', '橡皮', '文字', '形状']
        for tool in tools:
            btn = QPushButton(tool)
            btn.clicked.connect(lambda checked, t=tool: self.info_label.setText(f'选择了工具: {t}'))
            dock_layout.addWidget(btn)
        
        dock_widget.setLayout(dock_layout)
        left_dock.setWidget(dock_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)
        
        # 右侧停靠窗口
        right_dock = QDockWidget('属性', self)
        right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        prop_widget = QWidget()
        prop_layout = QVBoxLayout()
        
        # 添加一些属性设置
        prop_labels = ['颜色:', '大小:', '透明度:', '边框:']
        for label in prop_labels:
            label_widget = QLabel(label)
            prop_layout.addWidget(label_widget)
        
        prop_widget.setLayout(prop_layout)
        right_dock.setWidget(prop_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
    
    # 事件处理方法
    def new_file(self):
        self.info_label.setText('新建文件操作')
        self.statusBar().showMessage('执行新建文件操作')
    
    def open_file(self):
        self.info_label.setText('打开文件操作')
        self.statusBar().showMessage('执行打开文件操作')
    
    def show_about(self):
        QMessageBox.about(self, '关于程序', 
                         'PyQt6 主窗口演示程序\n\n'
                         '功能演示：\n'
                         '• 菜单栏和工具栏\n'
                         '• 停靠窗口\n'
                         '• 状态栏\n'
                         '• 各种控件使用\n\n'
                         '版本：1.0')
    
    def show_message(self):
        QMessageBox.information(self, '提示', '这是一个信息对话框!')
    
    def show_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, '选择文件', '', 'All Files (*);;Python Files (*.py)')
        if filename:
            self.info_label.setText(f'选择了文件: {filename}')
    
    def clear_info(self):
        self.info_label.setText('信息已清空')
        self.text_edit.clear()
    
    def update_status(self):
        self.statusBar().showMessage(f'状态更新时间: {QDateTime.currentDateTime().toString()}')
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.info_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color.name()};
                    border: 1px solid #ccc;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }}
            """)
    
    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.info_label.setFont(font)

# ==================== 4. 主窗口示例运行函数 ====================
def main_window_demo():
    """主窗口示例"""
    print("\n=== 主窗口示例 ===")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

# ==================== 5. 实用工具函数 ====================
def show_quick_reference():
    """显示 PyQt6 快速参考"""
    reference = """
╔════════════════════════════════════════════════════════════╗
║                   PyQt6 快速参考                         ║
╠════════════════════════════════════════════════════════════╣
║ 常用控件:                                               ║
║   QWidget - 基础窗口类                                   ║
║   QLabel - 标签控件                                      ║
║   QPushButton - 按钮控件                                 ║
║   QLineEdit - 单行输入框                                 ║
║   QTextEdit - 多行文本编辑                               ║
║   QComboBox - 下拉框                                    ║
║   QCheckBox - 复选框                                    ║
║   QRadioButton - 单选按钮                               ║
║   QProgressBar - 进度条                                ║
║   QSlider - 滑块控件                                    ║
║                                                          ║
║ 布局管理:                                               ║
║   QVBoxLayout - 垂直布局                                 ║
║   QHBoxLayout - 水平布局                                 ║
║   QGridLayout - 网格布局                                ║
║   QFormLayout - 表单布局                                ║
║                                                          ║
║ 窗口类型:                                               ║
║   QWidget - 普通窗口                                    ║
║   QMainWindow - 主窗口                                   ║
║   QDialog - 对话框                                      ║
║                                                          ║
║ 样式设置:                                               ║
║   setStyleSheet() - 设置样式表                          ║
║   setFont() - 设置字体                                  ║
║   setGeometry() - 设置位置和大小                        ║
╚════════════════════════════════════════════════════════════╝
    """
    print(reference)

# ==================== 主函数 ====================
def main():
    """主函数 - 提供示例选择菜单"""
    print("🎯 PyQt6 快速入门教程")
    print("=" * 50)
    
    while True:
        print("\n请选择要运行的示例:")
        print("1. 基础窗口示例")
        print("2. 布局管理示例")
        print("3. 主窗口示例")
        print("4. 显示快速参考")
        print("0. 退出程序")
        
        choice = input("\n请输入选择 (0-4): ").strip()
        
        if choice == '1':
            return basic_window_demo()
        elif choice == '2':
            return layout_demo()
        elif choice == '3':
            return main_window_demo()
        elif choice == '4':
            show_quick_reference()
        elif choice == '0':
            print("感谢使用 PyQt6 教程!")
            return 0
        else:
            print("无效选择，请重新输入!")

if __name__ == '__main__':
    # 检查是否直接运行此文件
    try:
        result = main()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)