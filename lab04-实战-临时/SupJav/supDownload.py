"""
SupJav 视频下载器 — PyQt6 GUI
基于 DrissionPage + yt-dlp，从 supjav 页面自动跳转到 fc2stream 并下载 HLS 视频流

功能:
  1. 输入 supjav/fc2stream 页面 URL，自动捕获 m3u8 流
  2. 画质选择（自动检测可用画质）
  3. 实时下载进度（百分比 + 速度 + ETA + 文件大小）
  4. 暗色主题 GUI
  5. 预留批量下载接口（供 supByName 集成）

依赖:
  pip install PyQt6 DrissionPage yt-dlp
"""

import sys
import os
import re
from datetime import datetime
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QGroupBox, QSpinBox, QCheckBox, QMessageBox,
    QComboBox, QSplitter, QStatusBar, QMenuBar, QMenu,
    QFrame, QSizePolicy, QGridLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QUrl, QTimer
from PyQt6.QtGui import QFont, QAction, QDesktopServices, QClipboard

from services.theme import get_dark_qss
from services.download_manager import YtDlpDownloader
from services.m3u8_capture import M3U8CaptureService
from workers.download_worker import CaptureWorker


# ══════════════════════════════════════════════
# 批量下载接口（供 supByName 调用）
# ══════════════════════════════════════════════

def batch_download(tasks: list, save_dir: str, browser_port: int = 9333):
    """
    批量下载接口 — 供 supByName.py 等外部模块调用

    Args:
        tasks: 下载任务列表，每个元素为 dict:
               {'url': 'https://supjav.com/ja/xxx.html', 'code': 'ABC-123', 'title': '...'}
        save_dir: 保存目录
        browser_port: Chrome 调试端口

    Returns:
        DownloadManager 实例（需保持引用以接收信号）
    """
    from PyQt6.QtWidgets import QApplication
    # 确保 Qt Application 存在
    app = QApplication.instance()
    if not app:
        raise RuntimeError("需要先创建 QApplication")

    manager = BatchDownloadManager(tasks, save_dir, browser_port)
    return manager


class BatchDownloadManager(QThread):
    """批量下载管理器 — 外部集成用"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)    # (current, total)
    task_finished = pyqtSignal(str, bool)     # (code, success)
    all_finished = pyqtSignal(int, int)        # (success_count, fail_count)

    def __init__(self, tasks: list, save_dir: str, browser_port: int = 9333):
        super().__init__()
        self.tasks = tasks
        self.save_dir = save_dir
        self.browser_port = browser_port

    def run(self):
        """顺序处理每个任务"""
        success = 0
        fail = 0
        total = len(self.tasks)

        for idx, task in enumerate(self.tasks):
            self.progress_signal.emit(idx + 1, total)
            url = task.get('url', '')
            code = task.get('code', '')

            self.log_signal.emit(f"[{idx+1}/{total}] 正在处理: {code or url}")

            try:
                # 1. 捕获 m3u8
                capture_service = M3U8CaptureService(self.browser_port)
                captured = capture_service.capture(url)
                if not captured:
                    self.log_signal.emit(f"  ✗ 未发现 m3u8: {code}")
                    fail += 1
                    self.task_finished.emit(code, False)
                    continue

                # 2. 获取最佳 URL
                best_url = capture_service.get_best_url()
                if not best_url:
                    fail += 1
                    self.task_finished.emit(code, False)
                    continue

                # 3. 下载（同步，在 QThread 中不阻塞 GUI）
                # 使用 subprocess 同步调用（简单可靠）
                import subprocess
                output_name = code or 'video'
                output_path = os.path.join(self.save_dir, f'{output_name}.%(ext)s')
                referer = capture_service.referer

                cmd = [
                    'yt-dlp', '--no-check-certificates',
                    '--referer', referer,
                    '--add-header',
                    'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    '--merge-output-format', 'mp4',
                    '-o', output_path,
                    '--', best_url
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
                if result.returncode == 0:
                    self.log_signal.emit(f"  ✓ 完成: {code}")
                    success += 1
                    self.task_finished.emit(code, True)
                else:
                    self.log_signal.emit(f"  ✗ 失败: {code} (返回码 {result.returncode})")
                    fail += 1
                    self.task_finished.emit(code, False)

                capture_service.cleanup()

            except Exception as e:
                self.log_signal.emit(f"  ✗ 异常: {code} - {e}")
                fail += 1
                self.task_finished.emit(code, False)

        self.all_finished.emit(success, fail)


# ══════════════════════════════════════════════
# 主窗口
# ══════════════════════════════════════════════

class MainWindow(QMainWindow):
    """SupJav 视频下载器主窗口"""

    # ── 窗口状态枚举 ──
    STATE_IDLE = "idle"
    STATE_CAPTURING = "capturing"
    STATE_READY = "ready"         # 捕获完成，等待确认下载
    STATE_DOWNLOADING = "downloading"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SupJav 视频下载器")
        self.setMinimumSize(1000, 750)

        # 持久化设置
        self.settings = QSettings("SupjavDownloader", "Settings")

        # 组件引用
        self.capture_worker: Optional[CaptureWorker] = None
        self.downloader: Optional[YtDlpDownloader] = None
        self.captured_formats: List[dict] = []
        self.referer_url: str = ""
        self._state: str = self.STATE_IDLE

        # 初始化 UI
        self._init_ui()
        self._load_settings()
        self._set_state(self.STATE_IDLE)

    # ══════════════════════════════════════════════
    # UI 构建
    # ══════════════════════════════════════════════

    def _init_ui(self):
        """构建完整 UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ═══ 1. URL 输入区 ═══
        url_group = QGroupBox("📋 视频页面 URL")
        url_group.setObjectName("configGroup")
        url_layout = QVBoxLayout(url_group)
        url_layout.setSpacing(8)

        url_row = QHBoxLayout()
        url_label = QLabel("URL:")
        url_label.setObjectName("label")
        url_label.setFixedWidth(40)
        url_row.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "输入 supjav 或 fc2stream 视频页面 URL..."
        )
        self.url_input.setObjectName("lineEdit")
        url_row.addWidget(self.url_input)

        self.paste_btn = QPushButton("📋 粘贴")
        self.paste_btn.setObjectName("accentBtn")
        self.paste_btn.setFixedWidth(80)
        self.paste_btn.clicked.connect(self._paste_url)
        url_row.addWidget(self.paste_btn)

        url_layout.addLayout(url_row)

        # 手动 m3u8 URL（备选输入）
        manual_row = QHBoxLayout()
        self.manual_check = QCheckBox("手动指定 m3u8 URL")
        self.manual_check.setObjectName("checkBox")
        self.manual_check.toggled.connect(self._toggle_manual_mode)
        manual_row.addWidget(self.manual_check)
        manual_row.addStretch()
        url_layout.addLayout(manual_row)

        self.manual_url_input = QLineEdit()
        self.manual_url_input.setPlaceholderText("直接输入 m3u8 URL...")
        self.manual_url_input.setObjectName("lineEdit")
        self.manual_url_input.setVisible(False)
        url_layout.addWidget(self.manual_url_input)

        main_layout.addWidget(url_group)

        # ═══ 2. 配置区（画质 + 保存目录 + 浏览器端口）═══
        config_group = QGroupBox("⚙️ 下载配置")
        config_group.setObjectName("configGroup")
        config_layout = QGridLayout(config_group)
        config_layout.setSpacing(10)

        # 画质选择
        quality_label = QLabel("画质:")
        quality_label.setObjectName("label")
        config_layout.addWidget(quality_label, 0, 0)

        self.quality_combo = QComboBox()
        self.quality_combo.setObjectName("comboBox")
        self.quality_combo.setMinimumWidth(200)
        self.quality_combo.addItem("（请先捕获 m3u8）", None)
        config_layout.addWidget(self.quality_combo, 0, 1)

        # 保存目录
        dir_label = QLabel("保存到:")
        dir_label.setObjectName("label")
        config_layout.addWidget(dir_label, 1, 0)

        dir_row = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("选择保存目录...")
        self.dir_input.setReadOnly(True)
        self.dir_input.setObjectName("lineEdit")
        dir_row.addWidget(self.dir_input)

        self.browse_btn = QPushButton("📁 浏览")
        self.browse_btn.setObjectName("accentBtn")
        self.browse_btn.clicked.connect(self._browse_directory)
        dir_row.addWidget(self.browse_btn)
        config_layout.addLayout(dir_row, 1, 1)

        # 浏览器端口
        port_label = QLabel("浏览器端口:")
        port_label.setObjectName("label")
        config_layout.addWidget(port_label, 2, 0)

        port_row = QHBoxLayout()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(9333)
        self.port_spin.setObjectName("spinBox")
        port_row.addWidget(self.port_spin)

        self.auto_start_check = QCheckBox("捕获后自动开始下载")
        self.auto_start_check.setChecked(True)
        self.auto_start_check.setObjectName("checkBox")
        port_row.addWidget(self.auto_start_check)

        port_row.addStretch()
        config_layout.addLayout(port_row, 2, 1)

        main_layout.addWidget(config_group)

        # ═══ 3. 按钮区 ═══
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.start_btn = QPushButton("▶️ 开始捕获")
        self.start_btn.setObjectName("greenBtn")
        self.start_btn.setMinimumHeight(42)
        self.start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setObjectName("redBtn")
        self.stop_btn.setMinimumHeight(42)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_layout.addWidget(self.stop_btn)

        self.open_dir_btn = QPushButton("📂 打开目录")
        self.open_dir_btn.setObjectName("blueBtn")
        self.open_dir_btn.setMinimumHeight(42)
        self.open_dir_btn.clicked.connect(self._open_download_dir)
        btn_layout.addWidget(self.open_dir_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ═══ 4. 进度显示区 ═══
        progress_group = QGroupBox("📊 下载进度")
        progress_group.setObjectName("configGroup")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progressBar")
        progress_layout.addWidget(self.progress_bar)

        info_row = QHBoxLayout()
        self.speed_label = QLabel("速度: --")
        self.speed_label.setObjectName("speedLabel")
        info_row.addWidget(self.speed_label)

        self.eta_label = QLabel("ETA: --")
        self.eta_label.setObjectName("etaLabel")
        info_row.addWidget(self.eta_label)

        self.size_label = QLabel("大小: --")
        self.size_label.setObjectName("sizeLabel")
        info_row.addWidget(self.size_label)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        info_row.addWidget(self.status_label)

        info_row.addStretch()
        progress_layout.addLayout(info_row)

        main_layout.addWidget(progress_group)

        # ═══ 5. 日志区 ═══
        splitter = QSplitter(Qt.Orientation.Vertical)

        log_group = QGroupBox("📝 日志")
        log_group.setObjectName("logGroup")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(0, 0, 0, 0)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("JetBrains Mono", 10))
        self.log_text.setObjectName("logText")
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)
        splitter.addWidget(log_group)

        main_layout.addWidget(splitter, 1)

        # ═══ 6. 状态栏 ═══
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 — 请先输入视频页面 URL")

        # ═══ 7. 菜单栏 ═══
        menubar = self.menuBar()
        menubar.setObjectName("menuBar")

        file_menu = menubar.addMenu("文件")
        file_menu.setObjectName("menu")
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("帮助")
        help_menu.setObjectName("menu")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ══════════════════════════════════════════════
    # 设置持久化
    # ══════════════════════════════════════════════

    def _load_settings(self):
        """加载持久化设置"""
        saved_dir = self.settings.value("download_dir", "")
        if saved_dir and os.path.exists(saved_dir):
            self.dir_input.setText(saved_dir)

        saved_port = self.settings.value("browser_port", 9333)
        self.port_spin.setValue(int(saved_port))

        auto = self.settings.value("auto_start", "true")
        self.auto_start_check.setChecked(auto.lower() == "true")

        # 不恢复 URL（安全考虑）

    def _save_settings(self):
        """保存设置"""
        self.settings.setValue("download_dir", self.dir_input.text())
        self.settings.setValue("browser_port", self.port_spin.value())
        self.settings.setValue("auto_start", str(self.auto_start_check.isChecked()).lower())

    # ══════════════════════════════════════════════
    # UI 状态管理
    # ══════════════════════════════════════════════

    def _set_state(self, state: str):
        """统一管理 UI 状态"""
        self._state = state

        if state == self.STATE_IDLE:
            self.start_btn.setText("▶️ 开始捕获")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.url_input.setEnabled(True)
            self.manual_url_input.setEnabled(True)
            self.progress_bar.setValue(0)
            self.speed_label.setText("速度: --")
            self.eta_label.setText("ETA: --")
            self.size_label.setText("大小: --")
            self.status_label.setText("")

        elif state == self.STATE_CAPTURING:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.url_input.setEnabled(False)
            self.manual_url_input.setEnabled(False)
            self.status_label.setText("🔍 正在捕获 m3u8...")

        elif state == self.STATE_READY:
            self.start_btn.setText("⬇️ 开始下载")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("✅ m3u8 就绪，点击开始下载")

        elif state == self.STATE_DOWNLOADING:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("📥 正在下载...")

    def _toggle_manual_mode(self, checked: bool):
        """切换手动 m3u8 URL 输入模式"""
        self.manual_url_input.setVisible(checked)
        if checked:
            self.url_input.setPlaceholderText("（手动模式下忽略页面 URL）")
        else:
            self.url_input.setPlaceholderText(
                "输入 supjav 或 fc2stream 视频页面 URL..."
            )

    # ══════════════════════════════════════════════
    # 用户操作
    # ══════════════════════════════════════════════

    def _paste_url(self):
        """从剪贴板粘贴 URL"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self._append_log(f"已粘贴 URL: {text}")

    def _browse_directory(self):
        """选择保存目录"""
        current_dir = self.dir_input.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self, "选择保存目录", current_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.dir_input.setText(directory)
            self._save_settings()

    def _on_start(self):
        """开始按钮 — 根据当前状态决定行为"""
        if self._state == self.STATE_IDLE:
            # 阶段1: 捕获 m3u8
            self._start_capture()
        elif self._state == self.STATE_READY:
            # 阶段2: 开始下载
            self._start_download()

    def _start_capture(self):
        """启动 m3u8 捕获"""

        # ── 手动模式: 直接用输入的 m3u8 URL ──
        if self.manual_check.isChecked():
            m3u8_url = self.manual_url_input.text().strip()
            if not m3u8_url:
                QMessageBox.warning(self, "警告", "请输入 m3u8 URL！")
                return
            if '.m3u8' not in m3u8_url:
                reply = QMessageBox.question(
                    self, "确认", "输入的 URL 不包含 .m3u8，确定继续吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            self.captured_formats = [{
                'quality': 'manual',
                'url': m3u8_url,
                'label': '手动输入 (m3u8)',
                'headers': {},
            }]
            self.referer_url = ''
            self._populate_quality_combo()
            self._append_log(f"手动模式: {m3u8_url}")
            self._set_state(self.STATE_READY)

            if self.auto_start_check.isChecked():
                self._start_download()
            return

        # ── 正常模式: 浏览器捕获 ──
        page_url = self.url_input.text().strip()
        if not page_url:
            QMessageBox.warning(self, "警告", "请输入视频页面 URL！")
            return

        save_dir = self.dir_input.text().strip()
        if not save_dir:
            reply = QMessageBox.question(
                self, "确认", "未选择保存目录，将使用当前目录。是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            save_dir = os.getcwd()
            self.dir_input.setText(save_dir)

        self._save_settings()

        # 清空之前的状态
        self.captured_formats = []
        self.referer_url = ""
        self.log_text.clear()

        self._set_state(self.STATE_CAPTURING)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("正在连接浏览器捕获 m3u8...")

        # 创建并启动捕获 Worker
        self.capture_worker = CaptureWorker(
            page_url=page_url,
            browser_port=self.port_spin.value(),
        )
        self.capture_worker.log_signal.connect(self._append_log)
        self.capture_worker.m3u8_found_signal.connect(self._on_m3u8_captured)
        self.capture_worker.finished_signal.connect(self._on_capture_finished)
        self.capture_worker.start()

    def _start_download(self):
        """启动 yt-dlp 下载"""
        if not self.captured_formats:
            QMessageBox.warning(self, "警告", "没有可用的 m3u8 流！")
            return

        save_dir = self.dir_input.text().strip() or os.getcwd()
        selected = self.quality_combo.currentData()

        if not selected:
            selected = self.captured_formats[0]

        m3u8_url = selected.get('url', '')
        quality = selected.get('quality', 'best')

        if not m3u8_url:
            QMessageBox.warning(self, "警告", "未选择有效的 m3u8 URL！")
            return

        self._set_state(self.STATE_DOWNLOADING)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("正在下载...")

        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"video_{timestamp}.%(ext)s"

        # 创建下载器
        self.downloader = YtDlpDownloader(self)
        self.downloader.log_signal.connect(self._append_log)
        self.downloader.progress_signal.connect(self._on_download_progress)
        self.downloader.finished_signal.connect(self._on_download_finished)

        self.downloader.start_download(
            m3u8_url=m3u8_url,
            output_dir=save_dir,
            output_name=output_name,
            referer=self.referer_url,
            quality=quality if quality != 'best' else None,
            extra_headers=selected.get('headers'),
        )

    def _on_stop(self):
        """停止当前操作"""
        if self._state == self.STATE_CAPTURING:
            if self.capture_worker:
                self.capture_worker.stop()
                self.capture_worker.wait(5000)
            self._set_state(self.STATE_IDLE)
            self.status_bar.showMessage("已停止捕获")
            self._append_log("捕获已取消")

        elif self._state == self.STATE_DOWNLOADING:
            if self.downloader:
                self.downloader.cancel()
            self._set_state(self.STATE_IDLE)
            self.status_bar.showMessage("已停止下载")
            self._append_log("下载已取消")

        elif self._state == self.STATE_READY:
            self._set_state(self.STATE_IDLE)
            self.status_bar.showMessage("已取消")

    def _open_download_dir(self):
        """打开下载目录"""
        save_dir = self.dir_input.text().strip()
        if save_dir and os.path.exists(save_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(save_dir))
        else:
            QMessageBox.warning(self, "提示", "请先选择保存目录！")

    # ══════════════════════════════════════════════
    # 回调 — 捕获阶段
    # ══════════════════════════════════════════════

    def _on_m3u8_captured(self, formats: list):
        """
        收到捕获的 m3u8 画质列表（在 CaptureWorker 线程中回调）
        formats = [{'quality': '1080p', 'url': '...', 'label': '...', 'headers': {...}}, ...]
        """
        self.captured_formats = formats
        if self.capture_worker:
            self.referer_url = self.capture_worker.get_referer()
        self._populate_quality_combo()

        # 如果有具体流 URL，用第一个作为默认下载源
        if formats:
            first = formats[0]
            self._append_log(f"就绪画质: {first.get('label', first.get('quality', '?'))}")

    def _on_capture_finished(self, success: bool, msg: str):
        """捕获完成"""
        if success:
            if self.captured_formats:
                self._set_state(self.STATE_READY)
                self.status_bar.showMessage(f"捕获完成 — {msg}")

                if self.auto_start_check.isChecked():
                    # 稍等让 UI 更新
                    QTimer.singleShot(500, self._start_download)
            else:
                # 没有捕获到任何格式
                self._set_state(self.STATE_IDLE)
                self.status_bar.showMessage("捕获失败 — 未发现 m3u8 流，请尝试手动输入 m3u8 URL")
                # 不弹窗，改成在日志区提示，方便用户直接用"手动模式"
                self._append_log("提示: 可勾选「手动指定 m3u8 URL」直接输入 m3u8 地址下载")
        else:
            # 出错也不弹窗阻塞，改为日志提示
            self._set_state(self.STATE_IDLE)
            self.status_bar.showMessage(f"捕获失败 — {msg}")
            self._append_log(f"捕获失败: {msg}")
            self._append_log("提示: 可尝试手动模式（勾选复选框输入 m3u8 URL）")

        # 清理 Worker
        if self.capture_worker:
            self.capture_worker.cleanup_service()

    def _populate_quality_combo(self):
        """用捕获到的画质填充下拉框"""
        self.quality_combo.clear()

        if not self.captured_formats:
            self.quality_combo.addItem("（无可用画质）", None)
            return

        for fmt in self.captured_formats:
            label = fmt.get('label', fmt.get('quality', 'unknown'))
            self.quality_combo.addItem(label, fmt)

        # 默认选第一个（最佳画质）
        self.quality_combo.setCurrentIndex(0)

    # ══════════════════════════════════════════════
    # 回调 — 下载阶段
    # ══════════════════════════════════════════════

    def _on_download_progress(self, percent: int, speed: str, eta: str, size: str):
        """下载进度更新"""
        self.progress_bar.setValue(percent)
        self.speed_label.setText(f"速度: {speed}")
        self.eta_label.setText(f"ETA: {eta}")
        self.size_label.setText(f"大小: {size}")

        if percent >= 100:
            self.status_label.setText("🔧 正在合并文件...")

    def _on_download_finished(self, success: bool, msg: str):
        """下载完成"""
        self._set_state(self.STATE_IDLE)

        if success:
            self.progress_bar.setValue(100)
            self.status_bar.showMessage("下载完成!")
            self.status_label.setText("✅ 下载完成")
            self._append_log(f"✅ 下载完成!")
            QMessageBox.information(self, "完成", "视频下载完成！")
        else:
            self.status_bar.showMessage(f"下载失败: {msg}")
            self.status_label.setText("❌ 下载失败")
            self._append_log(f"❌ {msg}")
            if "用户取消" not in msg:
                QMessageBox.critical(self, "下载失败", msg)

        # 停止按钮恢复为不可用
        self.stop_btn.setEnabled(False)

    # ══════════════════════════════════════════════
    # 日志
    # ══════════════════════════════════════════════

    def _append_log(self, msg: str):
        """追加日志"""
        self.log_text.append(msg)
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ══════════════════════════════════════════════
    # 关于 / 关闭
    # ══════════════════════════════════════════════

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "<h2>SupJav 视频下载器</h2>"
            "<p>基于 PyQt6 + yt-dlp 的视频下载工具</p>"
            "<p><b>功能:</b></p>"
            "<ul>"
            "<li>自动从 supjav 页面跳转到 fc2stream 播放页</li>"
            "<li>多策略捕获 m3u8 HLS 视频流</li>"
            "<li>实时下载进度显示（速度 / ETA / 大小）</li>"
            "<li>支持画质选择（1080p / 720p / 480p）</li>"
            "<li>手动指定 m3u8 URL 模式</li>"
            "</ul>"
            "<p><b>使用前提:</b></p>"
            "<ol>"
            "<li>先启动带调试端口的 Chrome:<br>"
            "<code>chrome.exe --remote-debugging-port=9333</code></li>"
            "<li>确保已安装 yt-dlp: <code>pip install yt-dlp</code></li>"
            "</ol>"
        )

    def closeEvent(self, event):
        """关闭窗口前确认"""
        if self._state in (self.STATE_CAPTURING, self.STATE_DOWNLOADING):
            reply = QMessageBox.question(
                self, "确认", "任务正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

            # 尝试停止
            self._on_stop()

        self._save_settings()
        event.accept()


# ══════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════

def main():
    """主入口"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(get_dark_qss())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
