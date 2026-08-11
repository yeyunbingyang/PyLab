"""
捕获 Worker — QThread 后台线程
将 M3U8 捕获服务（浏览器操作）放在后台线程执行，避免阻塞 GUI

遵循 supByName.py ScrapyWorker / updata.py BatchScrapyWorker 的信号命名规范:
  - log_signal(str)           日志
  - progress_signal(int, int) 进度
  - m3u8_found_signal(list)   捕获到的 m3u8 列表
  - finished_signal(bool, str) 完成状态
"""

from datetime import datetime
from typing import List, Dict, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from services.m3u8_capture import M3U8CaptureService


class CaptureWorker(QThread):
    """
    M3U8 捕获工作线程

    信号:
        log_signal(str)           — 日志消息
        m3u8_found_signal(list)   — 捕获到的画质列表 [{quality, url, label, headers}]
        finished_signal(bool, str) — (success, message)
    """

    log_signal = pyqtSignal(str)
    m3u8_found_signal = pyqtSignal(list)
    finished_signal = pyqtSignal(bool, str)

    def __init__(
        self,
        page_url: str,
        browser_port: int = 9333,
    ):
        """
        Args:
            page_url: supjav 或 fc2stream 视频页面 URL
            browser_port: Chrome 调试端口
        """
        super().__init__()
        self.page_url = page_url
        self.browser_port = browser_port
        self._is_running = True
        self._service: Optional[M3U8CaptureService] = None

    def _log(self, msg: str):
        """发送日志信号"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_signal.emit(f"[{timestamp}] {msg}")

    def stop(self):
        """停止工作线程（合作式取消）"""
        self._is_running = False
        self._log("正在停止...")

    def run(self):
        """
        在线程中执行 M3U8 捕获流程:
          1. 创建 M3U8CaptureService
          2. 连接浏览器 → 打开页面 → 点击FST → 监听m3u8
          3. 通过信号返回结果
        """
        try:
            self._service = M3U8CaptureService(self.browser_port)
            self._service.set_log_callback(self._log)

            if not self._is_running:
                return

            # 执行捕获
            self._log(f"开始捕获: {self.page_url}")
            captured = self._service.capture(self.page_url)

            if not self._is_running:
                return

            if captured:
                formats = self._service.get_available_formats()
                self._log(f"捕获成功! 发现 {len(formats)} 种画质")
                self.m3u8_found_signal.emit(formats)
                self.finished_signal.emit(True, f"捕获到 {len(formats)} 种画质")
            else:
                self._log("捕获失败：未发现任何 m3u8 流")
                self.finished_signal.emit(False, "未发现 m3u8 流，请检查页面或手动输入 m3u8 URL")

        except Exception as e:
            import traceback
            self._log(f"❌ 捕获异常: {e}")
            self._log(f"详细堆栈:\n{traceback.format_exc()}")

            # 诊断信息
            if self._service:
                try:
                    if self._service.tab:
                        self._log(f"[诊断] 当前标签页 URL: {self._service.tab.url}")
                    if self._service.browser:
                        tabs = self._service.browser.tabs
                        self._log(f"[诊断] 浏览器标签页数量: {len(tabs)}")
                        for i, t in enumerate(tabs):
                            self._log(f"  [{i}] {t.url[:100] if t.url else '(空)'}")
                except Exception:
                    pass

            self._log("[提示] 请确认:")
            self._log("  1. Chrome 已以调试模式启动: chrome.exe --remote-debugging-port=9333")
            self._log("  2. 目标页面可手动在 Chrome 中正常打开")
            self._log("  3. 若仍失败，可尝试 GUI 中的「手动指定 m3u8 URL」模式")

            self.finished_signal.emit(False, f"捕获出错: {str(e)}")

    def get_referer(self) -> str:
        """获取当前页面的 Referer URL（供下载时使用）"""
        if self._service:
            return self._service.referer
        return self.page_url

    def cleanup_service(self):
        """清理浏览器资源"""
        if self._service:
            try:
                self._service.cleanup()
            except Exception:
                pass
