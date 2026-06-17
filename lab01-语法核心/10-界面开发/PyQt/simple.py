import sys
from PyQt6.QtWidgets import QApplication, QWidget


def main():

    app = QApplication(sys.argv) # 创建应用程序对象

    w = QWidget() # 创建窗口对象
    w.resize(768, 512) # 设置窗口大小  250 像素宽，200像素高。
    w.move(100, 300) # 设置窗口位置

    w.setWindowTitle('Simple') # 设置窗口标题
    w.show() # 显示窗口

    sys.exit(app.exec()) # 运行应用程序


if __name__ == '__main__': # 如果当前模块是主模块，则运行主函数
    main()
