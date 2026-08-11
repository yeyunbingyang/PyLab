"""
yt-dlp 下载管理器 — QProcess 封装
使用 Qt 原生 QProcess 替代 subprocess.run()，支持实时进度、取消操作

进度输出格式:
  yt-dlp --newline --progress-template "%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s|%(progress._total_bytes_str)s"
  示例输出: "  12.3%|    2.5MiB/s|00:45|~500.00MiB"
"""

import re
import os
from typing import Optional, Dict

from PyQt6.QtCore import QObject, QProcess, pyqtSignal


# ── 进度解析正则 ──
# 自定义模板格式: "  12.3%|    2.5MiB/s|00:45|~500.00MiB"
# 注: yt-dlp 的 Unknown 值会输出 "Unknown B/s" 等，需要兼容
PROGRESS_TEMPLATE_PATTERN = re.compile(
    r'\s*([\d.]+)%\s*\|\s*'          # 百分比 (group 1)
    r'([^|]+)\s*\|\s*'               # 速度 (group 2) — 可能是 "Unknown B/s"
    r'([^|]+)\s*\|\s*'               # ETA (group 3) — 可能是 "Unknown"
    r'(~?[^|]+)'                      # 总大小 (group 4) — 宽松匹配
)

# yt-dlp 默认格式: "[download]  12.3% of ~500.00MiB at  2.5MiB/s ETA 00:45"
# 注意: speed 和 ETA 都可能是 "Unknown"
DEFAULT_PROGRESS_PATTERN = re.compile(
    r'\[download\]\s+([\d.]+)%\s+of\s+(~?[\d.]+[KMG]iB)\s+at\s+'
    r'(.+?)\s+ETA\s+(.+)'         # speed(3) 和 ETA(4) 都宽松匹配
)

# 下载完成行: "[download] 100% of  500.00MiB in 00:03:12"
COMPLETE_PATTERN = re.compile(
    r'\[download\]\s+100%\s+of\s+[\d.]+[KMG]iB\s+in\s+([\d:]+)'
)

# 合并完成: "[Merger] Merging formats into ..."
MERGE_PATTERN = re.compile(r'\[Merger\]|\[ExtractAudio\]|\[VideoRemuxer\]')


class YtDlpDownloader(QObject):
    """
    yt-dlp 下载管理器

    信号:
        progress_signal(int, str, str, str)  -- 百分比, 速度, ETA, 总大小
        log_signal(str)                       -- 日志消息
        finished_signal(bool, str)            -- 成功/失败, 消息
        formats_signal(list)                  -- --list-formats 解析结果
    """

    progress_signal = pyqtSignal(int, str, str, str)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    formats_signal = pyqtSignal(list)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._process: Optional[QProcess] = None
        self._expected_output: str = ""       # 预期的输出文件路径
        self._canceled: bool = False
        self._mode: str = "download"          # "download" | "list_formats"
        self._stderr_buffer: str = ""

    # ══════════════════════════════════════════════
    # 公开 API
    # ══════════════════════════════════════════════

    def start_download(
        self,
        m3u8_url: str,
        output_dir: str = ".",
        output_name: str = "%(title)s.%(ext)s",
        referer: str = None,
        quality: str = None,
        extra_headers: Dict[str, str] = None,
    ):
        """
        启动 yt-dlp 下载

        Args:
            m3u8_url: m3u8 流地址
            output_dir: 输出目录
            output_name: 输出文件名模板（支持 yt-dlp 变量）
            referer: Referer header
            quality: 画质格式代码，如 'best' 或 '137+140'
            extra_headers: 额外的 HTTP 请求头
        """
        self._canceled = False
        self._mode = "download"
        self._expected_output = os.path.join(output_dir, output_name)

        cmd = ['yt-dlp', '--newline', '--no-check-certificates']

        # ── 进度模板 ──
        cmd += [
            '--progress-template',
            '%(progress._percent_str)s|%(progress._speed_str)s|'
            '%(progress._eta_str)s|%(progress._total_bytes_str)s'
        ]

        # ── Referer ──
        if referer:
            cmd += ['--referer', referer]

        # ── User-Agent ──
        cmd += [
            '--add-header',
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
        ]

        # ── turboviplay 特殊 Accept header ──
        if any(kw in m3u8_url for kw in ['turboviplay', 'turbosplayer', 'turbovid']):
            cmd += ['--add-header', 'Accept:application/vnd.t1c.int-12594']

        # ── 额外请求头 ──
        if extra_headers:
            for k, v in extra_headers.items():
                cmd += ['--add-header', f'{k}:{v}']

        # ── 画质 ──
        if quality and quality != 'best':
            cmd += ['-f', quality]

        # ── 输出 ──
        cmd += ['--merge-output-format', 'mp4']
        cmd += ['-o', os.path.join(output_dir, output_name)]
        cmd += ['--']         # 防止 URL 中 - 被解析为参数
        cmd += [m3u8_url]

        # ── 启动 QProcess ──
        # 使用 MergedChannels: yt-dlp 的进度输出同时走 stdout 和 stderr，
        # 合并到同一个通道避免遗漏任何一行
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.finished.connect(self._on_process_finished)

        self.log_signal.emit(f"启动下载: yt-dlp ...")
        self.log_signal.emit(f"  输出目录: {output_dir}")
        self.log_signal.emit(f"  画质: {quality or 'best'}")

        self._process.start(cmd[0], cmd[1:])

    def list_formats(self, m3u8_url: str, referer: str = None):
        """
        列出可用格式（内部通过 QProcess 异步执行，结果通过 formats_signal 返回）

        Args:
            m3u8_url: m3u8 URL
            referer: Referer header
        """
        self._canceled = False
        self._mode = "list_formats"

        cmd = ['yt-dlp', '--list-formats', '--no-check-certificates']
        if referer:
            cmd += ['--referer', referer]
        cmd += ['--', m3u8_url]

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.finished.connect(self._on_process_finished)

        self.log_signal.emit("正在获取可用画质列表...")
        self._process.start(cmd[0], cmd[1:])

    def cancel(self):
        """取消当前下载"""
        self._canceled = True
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self.log_signal.emit("正在取消下载...")
            self._process.terminate()
            # 给 3 秒优雅关闭时间
            if not self._process.waitForFinished(3000):
                self._process.kill()
                self._process.waitForFinished(2000)
            self.log_signal.emit("下载已取消")

    def is_running(self) -> bool:
        """检查是否有正在运行的任务"""
        return (self._process is not None and
                self._process.state() != QProcess.ProcessState.NotRunning)

    # ══════════════════════════════════════════════
    # QProcess 回调（MergedChannels 模式，stdout+stderr 合并）
    # ══════════════════════════════════════════════

    def _on_stdout(self):
        """MergedChannels 模式：stdout+stderr 合并输出到此"""
        if not self._process:
            return
        raw = bytes(self._process.readAllStandardOutput()).decode('utf-8', errors='replace')

        if self._mode == "list_formats":
            self._stderr_buffer += raw
            return

        # ── 将 \r 替换为 \n 以便逐行处理 ──
        # yt-dlp 用 \r 覆盖同一行输出进度，这里拆开即可逐行匹配
        text = raw.replace('\r\n', '\n').replace('\r', '\n')

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            # 去除 ANSI 转义码
            line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
            if not line or line.isspace():
                continue

            # 1) 默认 [download] 进度行（最常见）
            m2 = DEFAULT_PROGRESS_PATTERN.match(line)
            if m2:
                try:
                    pct = int(float(m2.group(1)))
                except ValueError:
                    continue
                total = m2.group(2).strip()
                speed = m2.group(3).strip()
                eta = m2.group(4).strip()
                self.progress_signal.emit(pct, speed, eta, total)
                continue

            # 2) 自定义 --progress-template 行
            m = PROGRESS_TEMPLATE_PATTERN.match(line)
            if m:
                try:
                    pct = int(float(m.group(1)))
                except ValueError:
                    continue
                speed = m.group(2).strip()
                eta = m.group(3).strip()
                total = m.group(4).strip()
                self.progress_signal.emit(pct, speed, eta, total)
                continue

            # 3) 下载完成 / 合并完成行
            if '[download] 100%' in line or 'has already been downloaded' in line:
                self.log_signal.emit(line)
                continue
            if MERGE_PATTERN.search(line):
                self.log_signal.emit(line)
                continue

            # 4) 常规日志
            self.log_signal.emit(line)

    def _on_process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        """QProcess 完成"""
        if self._mode == "list_formats":
            self._parse_formats_output()
            return

        if self._canceled:
            self.finished_signal.emit(False, "用户取消")
        elif exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0:
            self.finished_signal.emit(True, self._expected_output)
        elif exit_status == QProcess.ExitStatus.CrashExit:
            self.finished_signal.emit(False, "yt-dlp 进程崩溃")
        else:
            self.finished_signal.emit(False, f"yt-dlp 退出码: {exit_code}")

    # ══════════════════════════════════════════════
    # 格式解析
    # ══════════════════════════════════════════════

    def _parse_formats_output(self):
        """解析 yt-dlp --list-formats 的输出"""
        combined = self._stderr_buffer
        if not self._process:
            return
        stdout_data = bytes(self._process.readAllStandardOutput()).decode('utf-8', errors='replace')
        combined += stdout_data

        formats = []

        # 解析格式行: "ID  EXT  RESOLUTION  FPS │  FILESIZE  TBR  PROTO  VCODEC  ..."
        # 例如: "137 mp4 1920x1080  30  │ ~500.00MiB 2500k https  avc1.640028 ..."
        format_line_pattern = re.compile(
            r'^(\d+)\s+'              # ID
            r'(\w+)\s+'               # EXT
            r'(\d+x\d+|\w+ only)\s+'  # RESOLUTION
            r'[^\│]*\│\s+'            # 分隔符前的内容
            r'.*'                     # 其余内容
        )

        has_formats = False
        for line in combined.splitlines():
            line = line.strip()
            if not line:
                continue
            m = format_line_pattern.match(line)
            if m:
                has_formats = True
                format_id = m.group(1)
                ext = m.group(2)
                resolution = m.group(3)
                quality_label = self._resolution_to_quality(resolution)
                if quality_label:
                    formats.append({
                        'format_code': format_id,
                        'ext': ext,
                        'resolution': resolution,
                        'quality': quality_label,
                        'label': f'{quality_label} ({resolution}) - {ext}'
                    })

        if has_formats:
            self.log_signal.emit(f"解析到 {len(formats)} 种画质")
            self.formats_signal.emit(formats)
        else:
            self.log_signal.emit("未能解析画质列表，使用默认选项")
            self.formats_signal.emit([
                {'format_code': 'best', 'quality': 'best', 'label': '最佳画质 (自动)'}
            ])

        self._stderr_buffer = ""

    @staticmethod
    def _resolution_to_quality(resolution: str) -> str:
        """将分辨率字符串转换为画质标签"""
        if 'only' in resolution:
            return 'audio_only'
        try:
            w, h = resolution.split('x')
            height = int(h)
        except (ValueError, AttributeError):
            return ''

        if height >= 2160:
            return '4K'
        elif height >= 1440:
            return '2K'
        elif height >= 1080:
            return '1080p'
        elif height >= 720:
            return '720p'
        elif height >= 480:
            return '480p'
        elif height >= 360:
            return '360p'
        return f'{height}p'
