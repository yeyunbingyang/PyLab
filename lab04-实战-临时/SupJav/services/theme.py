"""
共享 QSS 样式表 — Catppuccin Mocha 暗色主题
所有 PyQt6 GUI 文件统一引用此模块

用法:
    from services.theme import get_dark_qss
    app.setStyleSheet(get_dark_qss())
"""

from .constants import (
    DARK_BG, DARK_CARD, DARK_INPUT,
    TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_GREEN, ACCENT_RED, ACCENT_BLUE,
    ACCENT_YELLOW, ACCENT_PURPLE, BORDER_COLOR,
)


def get_dark_qss() -> str:
    """返回完整的暗色主题 QSS 样式表"""
    return f"""
        /* ===== 全局 ===== */
        QMainWindow {{
            background-color: {DARK_BG};
        }}
        QWidget {{
            background-color: {DARK_BG};
            color: {TEXT_PRIMARY};
        }}

        /* ===== 分组框 ===== */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 10px;
            background-color: {DARK_CARD};
            color: {TEXT_PRIMARY};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: {ACCENT_BLUE};
        }}

        /* ===== 标签 ===== */
        QLabel#label {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
        }}
        QLabel#speedLabel, QLabel#etaLabel, QLabel#sizeLabel {{
            color: {TEXT_SECONDARY};
            font-size: 12px;
            padding: 2px 0;
        }}
        QLabel#statusLabel {{
            color: {ACCENT_BLUE};
            font-size: 13px;
            font-weight: bold;
            padding: 4px 0;
        }}

        /* ===== 输入框 ===== */
        QLineEdit#lineEdit {{
            background-color: {DARK_INPUT};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px 12px;
            color: {TEXT_PRIMARY};
            font-size: 13px;
            selection-background-color: {ACCENT_BLUE};
        }}
        QLineEdit#lineEdit:focus {{
            border: 1px solid {ACCENT_BLUE};
        }}
        QLineEdit#lineEdit::placeholder {{
            color: {TEXT_SECONDARY};
        }}

        /* ===== 下拉框 ===== */
        QComboBox#comboBox {{
            background-color: {DARK_INPUT};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px 12px;
            color: {TEXT_PRIMARY};
            font-size: 13px;
            min-width: 160px;
        }}
        QComboBox#comboBox:hover {{
            border: 1px solid {ACCENT_BLUE};
        }}
        QComboBox#comboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox#comboBox::down-arrow {{
            image: none;
            border: none;
        }}
        QComboBox#comboBox QAbstractItemView {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            color: {TEXT_PRIMARY};
            selection-background-color: {ACCENT_BLUE};
            selection-color: {DARK_BG};
            outline: none;
        }}

        /* ===== 数字输入框 ===== */
        QSpinBox#spinBox {{
            background-color: {DARK_INPUT};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
            color: {TEXT_PRIMARY};
        }}
        QSpinBox#spinBox::up-button, QSpinBox#spinBox::down-button {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
        }}

        /* ===== 复选框 ===== */
        QCheckBox#checkBox {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
            spacing: 8px;
        }}
        QCheckBox#checkBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {BORDER_COLOR};
            background-color: {DARK_INPUT};
        }}
        QCheckBox#checkBox::indicator:checked {{
            background-color: {ACCENT_GREEN};
            border: 1px solid {ACCENT_GREEN};
        }}

        /* ===== 按钮 ===== */
        QPushButton {{
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 500;
            color: {DARK_BG};
        }}
        QPushButton#greenBtn {{
            background-color: {ACCENT_GREEN};
        }}
        QPushButton#greenBtn:hover {{
            background-color: #b4f0ae;
        }}
        QPushButton#greenBtn:disabled {{
            background-color: #3d5c3d;
            color: {TEXT_SECONDARY};
        }}
        QPushButton#redBtn {{
            background-color: {ACCENT_RED};
        }}
        QPushButton#redBtn:hover {{
            background-color: #f5a3b8;
        }}
        QPushButton#redBtn:disabled {{
            background-color: #5c3d45;
            color: {TEXT_SECONDARY};
        }}
        QPushButton#blueBtn {{
            background-color: {ACCENT_BLUE};
        }}
        QPushButton#blueBtn:hover {{
            background-color: #a3c8f5;
        }}
        QPushButton#blueBtn:disabled {{
            background-color: #3d4f5c;
            color: {TEXT_SECONDARY};
        }}
        QPushButton#accentBtn {{
            background-color: {ACCENT_PURPLE};
            color: {DARK_BG};
        }}
        QPushButton#accentBtn:hover {{
            background-color: #d4b5f9;
        }}

        /* ===== 进度条 ===== */
        QProgressBar#progressBar {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            background-color: {DARK_INPUT};
            text-align: center;
            color: {TEXT_PRIMARY};
            font-size: 12px;
            height: 28px;
        }}
        QProgressBar#progressBar::chunk {{
            background-color: {ACCENT_BLUE};
            border-radius: 6px;
        }}

        /* ===== 表格 ===== */
        QTableWidget#dataTable {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            gridline-color: {BORDER_COLOR};
            color: {TEXT_PRIMARY};
            font-size: 13px;
            selection-background-color: {ACCENT_BLUE};
            selection-color: {DARK_BG};
        }}
        QTableWidget#dataTable::item {{
            padding: 6px;
            border-bottom: 1px solid {BORDER_COLOR};
        }}
        QTableWidget#dataTable::item:alternate {{
            background-color: #32324a;
        }}
        QTableWidget#dataTable::item:selected {{
            background-color: {ACCENT_BLUE};
            color: {DARK_BG};
        }}
        QHeaderView::section {{
            background-color: {DARK_INPUT};
            color: {TEXT_SECONDARY};
            padding: 10px;
            border: none;
            border-bottom: 2px solid {BORDER_COLOR};
            font-weight: bold;
            font-size: 13px;
        }}

        /* ===== 列表 ===== */
        QListWidget#actressList {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            color: {TEXT_PRIMARY};
            font-size: 13px;
            padding: 6px;
        }}
        QListWidget#actressList::item {{
            padding: 8px 12px;
            border-radius: 6px;
        }}
        QListWidget#actressList::item:selected {{
            background-color: {ACCENT_BLUE};
            color: {DARK_BG};
        }}
        QListWidget#actressList::item:hover {{
            background-color: #3a3a50;
        }}

        /* ===== 日志文本 ===== */
        QTextEdit#logText {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            color: {TEXT_PRIMARY};
            font-size: 12px;
            padding: 10px;
            selection-background-color: {ACCENT_BLUE};
        }}

        /* ===== 菜单栏 ===== */
        QMenuBar#menuBar {{
            background-color: {DARK_BG};
            color: {TEXT_PRIMARY};
            border-bottom: 1px solid {BORDER_COLOR};
        }}
        QMenuBar#menuBar::item {{
            background-color: transparent;
            padding: 6px 16px;
        }}
        QMenuBar#menuBar::item:selected {{
            background-color: {DARK_INPUT};
            border-radius: 4px;
        }}
        QMenu#menu {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
        }}
        QMenu#menu::item {{
            color: {TEXT_PRIMARY};
            padding: 8px 24px;
            border-radius: 4px;
        }}
        QMenu#menu::item:selected {{
            background-color: {ACCENT_BLUE};
            color: {DARK_BG};
        }}
        QMenu#contextMenu {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
        }}
        QMenu#contextMenu::item {{
            color: {TEXT_PRIMARY};
            padding: 8px 24px;
            border-radius: 4px;
        }}
        QMenu#contextMenu::item:selected {{
            background-color: {ACCENT_BLUE};
            color: {DARK_BG};
        }}

        /* ===== 状态栏 ===== */
        QStatusBar#statusBar {{
            background-color: {DARK_BG};
            color: {TEXT_SECONDARY};
            border-top: 1px solid {BORDER_COLOR};
        }}

        /* ===== 分割器 ===== */
        QSplitter::handle {{
            background-color: {BORDER_COLOR};
        }}

        /* ===== 消息框 ===== */
        QMessageBox {{
            background-color: {DARK_CARD};
        }}
        QMessageBox QLabel {{
            color: {TEXT_PRIMARY};
        }}
        QMessageBox QPushButton {{
            background-color: {ACCENT_BLUE};
            color: {DARK_BG};
            padding: 8px 20px;
            border-radius: 6px;
        }}

        /* ===== 滚动条 ===== */
        QScrollBar:vertical {{
            background-color: {DARK_INPUT};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {BORDER_COLOR};
            border-radius: 6px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {ACCENT_BLUE};
        }}
        QScrollBar:horizontal {{
            background-color: {DARK_INPUT};
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {BORDER_COLOR};
            border-radius: 6px;
            min-width: 30px;
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            height: 0;
            width: 0;
        }}
    """
