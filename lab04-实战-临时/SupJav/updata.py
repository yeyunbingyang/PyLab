import sys
import os
import re
import time
import io
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Set, Dict, Optional, Tuple

import requests
from PIL import Image as PILImage, ExifTags

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QGroupBox, QSpinBox, QCheckBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QStatusBar, QMenuBar, QMenu, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QUrl, QSize
from PyQt6.QtGui import QColor, QBrush, QFont, QAction, QDesktopServices
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font as OpenpyxlFont, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.drawing.xdr import XDRPoint2D, XDRPositiveSize2D
from openpyxl.utils.units import pixels_to_EMU
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from DrissionPage import Chromium


# ==================== 配色常量（暗色主题）====================
DARK_BG = "#1e1e2e"
DARK_CARD = "#2a2a3c"
DARK_INPUT = "#313244"
TEXT_PRIMARY = "#cdd6f4"
TEXT_SECONDARY = "#a6adc8"
ACCENT_GREEN = "#a6e3a1"
ACCENT_RED = "#f38ba8"
ACCENT_BLUE = "#89b4fa"
ACCENT_YELLOW = "#f9e2af"
ACCENT_PURPLE = "#cba6f7"
BORDER_COLOR = "#45475a"


# ==================== 图片嵌入配置常量 ====================
CELL_MAX_WIDTH = 140
CELL_MAX_HEIGHT = 180
EMU_PER_PIXEL = 9525


# ==================== 数据模型 ====================
@dataclass
class VideoInfo:
    code: str
    title: str
    url: str
    img_url: str
    update_date: str
    views: str
    is_local: bool = False
    is_new: bool = False
    fetch_time: str = ""

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "url": self.url,
            "img_url": self.img_url,
            "update_date": self.update_date,
            "views": self.views,
            "is_local": self.is_local,
            "is_new": self.is_new,
            "fetch_time": self.fetch_time,
        }
    def get_date_obj(self) -> Optional[datetime]:
        if not self.update_date:
            return None
        for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(self.update_date, fmt)
            except ValueError:
                continue
        return None

    @classmethod
    def from_dict(cls, d: dict) -> "VideoInfo":
        return cls(
            code=d.get("code", ""),
            title=d.get("title", ""),
            url=d.get("url", ""),
            img_url=d.get("img_url", ""),
            update_date=d.get("update_date", ""),
            views=d.get("views", ""),
            is_local=d.get("is_local", False),
            is_new=d.get("is_new", False),
            fetch_time=d.get("fetch_time", ""),
        )


# ==================== 工具函数 ====================
def parse_meta_text(meta_text: str, meta_html: str = "") -> tuple:
    update_date, views = "", ""
    txt = meta_text.strip()
    if not txt:
        return update_date, views
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    if len(lines) >= 2:
        update_date = lines[0]
        views = lines[1]
        return update_date, views
    if len(lines) == 1:
        line = lines[0]
        m = re.search(r'(\d{4}/\d{2}/\d{2})(\d+[\s\w]*)', line)
        if m:
            update_date = m.group(1)
            views = m.group(2).strip()
            if not re.search(r'Views', views, re.I):
                views_match = re.search(r'(\d+\s*Views)', line, re.I)
                if views_match:
                    views = views_match.group(1)
            return update_date, views
        if meta_html:
            date_m = re.search(r'(\d{4}/\d{2}/\d{2})', meta_html)
            if date_m:
                update_date = date_m.group(1)
            views_m = re.search(r'(\d+)\s*Views', meta_html, re.I)
            if views_m:
                views = views_m.group(0)
            if update_date or views:
                return update_date, views
        update_date = line
    return update_date, views


def extract_actress_name(folder_name: str) -> str:
    """从文件夹名提取女优名。去掉前缀编号和尾部emoji标记。"""
    import unicodedata
    cleaned = folder_name.strip()
    while cleaned:
        last_char = cleaned[-1]
        cat = unicodedata.category(last_char)
        if cat in ('So', 'Sk') or last_char in '\U0001f4cc\U00002b50\U00002728\U0001f525\U0001f4ab\U0001f31f\U00002764\U0001f499\U0001f49a\U0001f49b\U0001f49c\U0001f5a4\U0001f90d\U0001f90e\U0001f494\U0001f493\U0001f495\U0001f496\U0001f497\U0001f498\U0001f499\U0001f49d':
            cleaned = cleaned[:-1]
        else:
            break
    cleaned = cleaned.strip()
    cleaned = re.sub(r'[\s\-_.]+$', '', cleaned)
    cleaned = re.sub(r'^[A-Z0-9\-]+\-', '', cleaned, flags=re.I)
    cleaned = re.sub(r'^\d+[\-_.\s]+', '', cleaned)
    return cleaned.strip()


def _apply_exif_orientation(img: PILImage.Image) -> PILImage.Image:
    try:
        exif = img._getexif()
        if exif is None:
            return img
        orientation = None
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == "Orientation":
                orientation = value
                break
        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(270, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img


def _calc_fit_size(orig_w: int, orig_h: int, max_w: int = CELL_MAX_WIDTH, max_h: int = CELL_MAX_HEIGHT) -> Tuple[int, int]:
    if orig_w <= 0 or orig_h <= 0:
        return max_w, max_h
    scale_w = max_w / orig_w
    scale_h = max_h / orig_h
    scale = min(scale_w, scale_h)
    new_w = max(1, int(round(orig_w * scale)))
    new_h = max(1, int(round(orig_h * scale)))
    return new_w, new_h


def download_and_fit_image(url: str, max_size: Tuple[int, int] = (CELL_MAX_WIDTH, CELL_MAX_HEIGHT)) -> Optional[Tuple[bytes, int, int]]:
    if not url:
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://supjav.com/"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        img = PILImage.open(io.BytesIO(resp.content))
        img = _apply_exif_orientation(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        orig_w, orig_h = img.size
        fit_w, fit_h = _calc_fit_size(orig_w, orig_h, max_size[0], max_size[1])
        img = img.resize((fit_w, fit_h), PILImage.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), fit_w, fit_h
    except Exception:
        return None


def embed_image_to_cell(ws, img_bytes: bytes, cell_ref: str, img_w: int, img_h: int):
    img = OpenpyxlImage(io.BytesIO(img_bytes))
    img.width = img_w
    img.height = img_h
    from openpyxl.utils import get_column_letter
    col_letter = ''.join([c for c in cell_ref if c.isalpha()])
    row_num = int(''.join([c for c in cell_ref if c.isdigit()]))
    col_idx = 0
    for i, ch in enumerate(reversed(col_letter)):
        col_idx += (ord(ch) - ord('A') + 1) * (26 ** i)
    marker = AnchorMarker(
        col=col_idx - 1, colOff=0,
        row=row_num - 1, rowOff=0
    )
    size = XDRPositiveSize2D(cx=img_w * EMU_PER_PIXEL, cy=img_h * EMU_PER_PIXEL)
    img.anchor = OneCellAnchor(_from=marker, ext=size)
    ws.add_image(img, cell_ref)


def get_image_cache_path(base_dir: str, img_url: str) -> str:
    if not img_url:
        return ""
    ext = os.path.splitext(img_url.split('?')[0])[1] or ".jpg"
    hash_name = hashlib.md5(img_url.encode()).hexdigest() + ext
    cache_dir = os.path.join(base_dir, "cache", "images")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, hash_name)


def load_cached_image(cache_path: str) -> Optional[bytes]:
    if cache_path and os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                return f.read()
        except Exception:
            pass
    return None


def save_image_cache(cache_path: str, img_bytes: bytes):
    if cache_path and img_bytes:
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "wb") as f:
                f.write(img_bytes)
        except Exception:
            pass


# ==================== 女优扫描器 ====================
class ActressScanner:
    @staticmethod
    def scan_unfinished_dir(unfinished_dir: str) -> List[Tuple[str, str]]:
        results = []
        if not os.path.exists(unfinished_dir):
            return results
        for entry in os.scandir(unfinished_dir):
            if entry.is_dir():
                actress_name = extract_actress_name(entry.name)
                if actress_name:
                    results.append((entry.path, actress_name))
        return results

    @staticmethod
    def get_local_codes_from_dir(directory: str) -> Set[str]:
        codes = set()
        pattern = re.compile(r'[A-Z]{2,8}-\d{2,5}', re.I)
        if not directory or not os.path.exists(directory):
            return codes
        for root, _, files in os.walk(directory):
            for file in files:
                m = pattern.search(file)
                if m:
                    codes.add(m.group().upper())
        return codes


# ==================== JSON 数据库管理 ====================
class JsonDatabase:
    def __init__(self, output_dir: str, actress_name: str):
        self.output_dir = output_dir
        self.actress_name = actress_name
        self.json_path = os.path.join(output_dir, f"{actress_name}.json")
        self.data: List[VideoInfo] = []
        self._load()

    def _load(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    raw_list = json.load(f)
                self.data = [VideoInfo.from_dict(d) for d in raw_list]
            except Exception:
                self.data = []

    def save(self):
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump([d.to_dict() for d in self.data], f, ensure_ascii=False, indent=2)

    def get_existing_codes(self) -> Set[str]:
        return {item.code for item in self.data if item.code}


    def merge_new_data(self, new_items: List[VideoInfo]) -> Tuple[List[VideoInfo], List[VideoInfo]]:
        existing_map = {item.code: item for item in self.data if item.code}
        latest_date = self.get_latest_date()  # 数据库最新日期
        truly_new = []

        for new_item in new_items:
            if not new_item.code:
                continue
            item_date = new_item.get_date_obj()

            if new_item.code in existing_map:
                # 已存在，更新信息但不标记为新增
                old = existing_map[new_item.code]
                old.title = new_item.title
                # ... 更新其他字段
            else:
                # 新番号：判断是否在数据库最新日期之后
                if latest_date is None or (item_date and item_date > latest_date):
                    new_item.is_new = True  # 真正的新增
                    truly_new.append(new_item)
                else:
                    new_item.is_new = False  # 补充旧数据
                existing_map[new_item.code] = new_item

        self.data = list(existing_map.values())
        self.data.sort(key=lambda x: x.get_date_obj() or datetime.min, reverse=True)
        return truly_new, self.data

# ==================== 更新报告生成器 ====================
class UpdateReportGenerator:
    @staticmethod
    def generate_updata_json(output_dir: str, all_updates: Dict[str, List[VideoInfo]]):
        updata = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {},
            "updates": {}
        }
        total_new = 0
        for actress, items in all_updates.items():
            updata["updates"][actress] = [item.to_dict() for item in items]
            updata["summary"][actress] = len(items)
            total_new += len(items)
        updata["summary"]["_total"] = total_new
        updata_path = os.path.join(output_dir, "updata.json")
        with open(updata_path, "w", encoding="utf-8") as f:
            json.dump(updata, f, ensure_ascii=False, indent=2)
        return updata_path

    @staticmethod
    def generate_updata_html(output_dir: str):
        html_path = os.path.join(output_dir, "updata.html")
        html_lines = []
        html_lines.append('<!DOCTYPE html>')
        html_lines.append('<html lang="zh-CN">')
        html_lines.append('<head>')
        html_lines.append('<meta charset="UTF-8">')
        html_lines.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_lines.append('<title>更新报告</title>')
        html_lines.append('<style>')
        html_lines.append(':root { --bg: #1e1e2e; --card: #2a2a3c; --input: #313244; --text: #cdd6f4; --text2: #a6adc8; --green: #a6e3a1; --red: #f38ba8; --blue: #89b4fa; --yellow: #f9e2af; --purple: #cba6f7; --border: #45475a; }')
        html_lines.append('* { margin: 0; padding: 0; box-sizing: border-box; }')
        html_lines.append('body { font-family: "Segoe UI", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }')
        html_lines.append('.container { max-width: 1400px; margin: 0 auto; padding: 20px; }')
        html_lines.append('header { text-align: center; padding: 30px 0; border-bottom: 1px solid var(--border); margin-bottom: 20px; }')
        html_lines.append('header h1 { font-size: 28px; color: var(--blue); margin-bottom: 8px; }')
        html_lines.append('header .meta { color: var(--text2); font-size: 14px; }')
        html_lines.append('.summary-bar { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }')
        html_lines.append('.summary-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 24px; min-width: 140px; text-align: center; flex: 1; }')
        html_lines.append('.summary-card .num { font-size: 32px; font-weight: bold; color: var(--green); }')
        html_lines.append('.summary-card .label { font-size: 13px; color: var(--text2); margin-top: 4px; }')
        html_lines.append('.actress-section { background: var(--card); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 16px; overflow: hidden; }')
        html_lines.append('.actress-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; background: var(--input); cursor: pointer; user-select: none; }')
        html_lines.append('.actress-header:hover { background: #3a3a50; }')
        html_lines.append('.actress-name { font-size: 16px; font-weight: bold; color: var(--blue); }')
        html_lines.append('.actress-count { background: var(--red); color: var(--bg); font-size: 12px; font-weight: bold; padding: 2px 10px; border-radius: 12px; }')
        html_lines.append('.actress-body { display: none; padding: 12px; }')
        html_lines.append('.actress-body.open { display: block; }')
        html_lines.append('.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }')
        html_lines.append('.card { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: transform .15s, box-shadow .15s; }')
        html_lines.append('.card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.35); }')
        html_lines.append('.card-img { width: 100%; aspect-ratio: 3/4; object-fit: cover; background: var(--input); display: block; }')
        html_lines.append('.card-body { padding: 10px 12px; }')
        html_lines.append('.card-code { font-size: 13px; font-weight: bold; color: var(--yellow); margin-bottom: 4px; }')
        html_lines.append('.card-title { font-size: 12px; color: var(--text2); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 6px; }')
        html_lines.append('.card-meta { display: flex; justify-content: space-between; font-size: 11px; color: var(--text2); }')
        html_lines.append('.card-tag { display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 4px; margin-top: 6px; }')
        html_lines.append('.tag-new { background: var(--green); color: var(--bg); }')
        html_lines.append('.tag-local { background: var(--yellow); color: var(--bg); }')
        html_lines.append('.empty-state { text-align: center; padding: 60px 20px; color: var(--text2); }')
        html_lines.append('footer { text-align: center; padding: 20px; color: var(--text2); font-size: 12px; border-top: 1px solid var(--border); margin-top: 20px; }')
        html_lines.append('.filter-bar { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }')
        html_lines.append('.filter-bar input, .filter-bar select { background: var(--input); border: 1px solid var(--border); color: var(--text); padding: 8px 14px; border-radius: 8px; font-size: 13px; outline: none; }')
        html_lines.append('.filter-bar input:focus, .filter-bar select:focus { border-color: var(--blue); }')
        html_lines.append('.filter-bar input { flex: 1; min-width: 200px; }')
        html_lines.append('</style>')
        html_lines.append('</head>')
        html_lines.append('<body>')
        html_lines.append('<div class="container">')
        html_lines.append('  <header>')
        html_lines.append('    <h1>资源更新报告</h1>')
        html_lines.append('    <div class="meta" id="meta">加载中...</div>')
        html_lines.append('  </header>')
        html_lines.append('  <div class="summary-bar" id="summary"></div>')
        html_lines.append('  <div class="filter-bar">')
        html_lines.append('    <input type="text" id="searchInput" placeholder="搜索番号或标题...">')
        html_lines.append('    <select id="actressFilter"><option value="">全部女优</option></select>')
        html_lines.append('  </div>')
        html_lines.append('  <div id="content"></div>')
        html_lines.append('  <footer>Supjav Manager 自动生成</footer>')
        html_lines.append('</div>')
        html_lines.append('<script>')
        html_lines.append('let updata = null;')
        html_lines.append('async function loadData() {')
        html_lines.append('  try { const res = await fetch("updata.json?t=" + Date.now()); updata = await res.json(); render(); }')
        html_lines.append('  catch(e) { document.getElementById("content").innerHTML = "<div class=\\"empty-state\\"><p>无法加载 updata.json，请确保文件存在。</p></div>"; }')
        html_lines.append('}')
        html_lines.append('function render() {')
        html_lines.append('  document.getElementById("meta").textContent = "生成时间: " + (updata.generated_at || "未知");')
        html_lines.append('  const total = updata.summary._total || 0;')
        html_lines.append('  const actresses = Object.keys(updata.updates || {});')
        html_lines.append('  document.getElementById("summary").innerHTML = "<div class=\\"summary-card\\"><div class=\\"num\\">" + total + "</div><div class=\\"label\\">新增总数</div></div><div class=\\"summary-card\\"><div class=\\"num\\">" + actresses.length + "</div><div class=\\"label\\">涉及女优</div></div>";')
        html_lines.append('  const sel = document.getElementById("actressFilter");')
        html_lines.append('  sel.innerHTML = "<option value=\\"\\">全部女优</option>" + actresses.map(function(a) { return "<option value=\\"" + a + "\\">" + a + "</option>"; }).join("");')
        html_lines.append('  applyFilter();')
        html_lines.append('}')
        html_lines.append('function applyFilter() {')
        html_lines.append('  const q = document.getElementById("searchInput").value.toLowerCase().trim();')
        html_lines.append('  const actressSel = document.getElementById("actressFilter").value;')
        html_lines.append('  const content = document.getElementById("content");')
        html_lines.append('  content.innerHTML = "";')
        html_lines.append('  for (const [actress, items] of Object.entries(updata.updates || {})) {')
        html_lines.append('    if (actressSel && actress !== actressSel) continue;')
        html_lines.append('    let filteredItems = items;')
        html_lines.append('    if (q) { filteredItems = items.filter(function(it) { return (it.code || "").toLowerCase().includes(q) || (it.title || "").toLowerCase().includes(q); }); }')
        html_lines.append('    if (filteredItems.length === 0) continue;')
        html_lines.append('    const section = document.createElement("div");')
        html_lines.append('    section.className = "actress-section";')
        html_lines.append('    section.innerHTML = "<div class=\\"actress-header\\" onclick=\\"toggle(this)\\"><span class=\\"actress-name\\">" + actress + "</span><span class=\\"actress-count\\">" + filteredItems.length + "</span></div><div class=\\"actress-body open\\"><div class=\\"grid\\">" + filteredItems.map(function(it) { return "<div class=\\"card\\"><a href=\\"" + it.url + "\\" target=\\"_blank\\"><img class=\\"card-img\\" src=\\"" + (it.img_url || "") + "\\" alt=\\"" + it.code + "\\" loading=\\"lazy\\" onerror=\\"this.style.display=\'none\'\\"></a><div class=\\"card-body\\"><div class=\\"card-code\\">" + it.code + "</div><div class=\\"card-title\\">" + it.title + "</div><div class=\\"card-meta\\"><span>" + (it.update_date || "") + "</span><span>" + (it.views || "") + "</span></div>" + (it.is_new ? "<span class=\\"card-tag tag-new\\">新增</span>" : "") + (it.is_local ? "<span class=\\"card-tag tag-local\\">已有</span>" : "") + "</div></div>"; }).join("") + "</div></div>";')
        html_lines.append('    content.appendChild(section);')
        html_lines.append('  }')
        html_lines.append('  if (!content.innerHTML) { content.innerHTML = "<div class=\\"empty-state\\"><p>没有匹配的数据</p></div>"; }')
        html_lines.append('}')
        html_lines.append('function toggle(header) { header.nextElementSibling.classList.toggle("open"); }')
        html_lines.append('document.getElementById("searchInput").addEventListener("input", applyFilter);')
        html_lines.append('document.getElementById("actressFilter").addEventListener("change", applyFilter);')
        html_lines.append('loadData();')
        html_lines.append('</script>')
        html_lines.append('</body>')
        html_lines.append('</html>')

        with open(html_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_lines))
        return html_path


# ==================== 批量抓取工作线程 ====================
class BatchScrapyWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    actress_progress_signal = pyqtSignal(str, int, int)
    finished_signal = pyqtSignal(bool, str, dict)

    def __init__(self, actress_list: List[Tuple[str, str]], base_dir: str, output_dir: str,
                 finished_dir: str, browser_port: int = 9333,
                 embed_images: bool = True, export_excel: bool = False):
        super().__init__()
        self.actress_list = actress_list
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.finished_dir = finished_dir
        self.browser_port = browser_port
        self.embed_images = embed_images
        self.export_excel = export_excel
        self._is_running = True
        self.browser = None
        self.tab = None

    def log(self, msg: str):
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def stop(self):
        self._is_running = False
        self.log("正在停止...")

    def run(self):
        try:
            all_updates: Dict[str, List[VideoInfo]] = {}
            total = len(self.actress_list)
            self.browser = Chromium(self.browser_port)
            self.tab = self.browser.new_tab()
            for idx, (folder_path, actress_name) in enumerate(self.actress_list, 1):
                if not self._is_running:
                    break
                self.progress_signal.emit(idx, total)
                self.log(f"=" * 50)
                self.log(f"[{idx}/{total}] 开始处理: {actress_name}")
                local_codes = ActressScanner.get_local_codes_from_dir(folder_path)
                finished_codes = ActressScanner.get_local_codes_from_dir(self.finished_dir)
                all_local_codes = local_codes | finished_codes
                self.log(f"  本地已有番号: {len(all_local_codes)} 个")
                db = JsonDatabase(self.output_dir, actress_name)
                existing_codes = db.get_existing_codes()
                self.log(f"  JSON数据库已有: {len(existing_codes)} 条")
                raw_data = self._fetch_actress_data(actress_name)
                if not self._is_running:
                    break
                self.log(f"  抓取到原始数据: {len(raw_data)} 条")
                deduped = self._deduplicate_by_code(raw_data)
                self.log(f"  去重后: {len(deduped)} 条")
                for item in deduped:
                    item.is_local = item.code in all_local_codes
                new_items = db.merge_new_data(deduped)
                self.log(f"  新增数据: {len(new_items)} 条")
                db.save()
                self.log(f"  已保存 JSON: {db.json_path}")
                if self.export_excel and db.data:
                    excel_path = self._save_to_excel(actress_name, db.data)
                    self.log(f"  已导出 Excel: {excel_path}")
                if self.embed_images:
                    self._cache_images(actress_name, db.data)
                if new_items:
                    all_updates[actress_name] = new_items
                self.log(f"  完成: {actress_name}")
            if all_updates:
                updata_json = UpdateReportGenerator.generate_updata_json(self.output_dir, all_updates)
                updata_html = UpdateReportGenerator.generate_updata_html(self.output_dir)
                self.log(f"更新报告已生成: {updata_html}")
                self.log(f"更新数据已生成: {updata_json}")
            else:
                self.log("没有新增数据，跳过报告生成")
            self.finished_signal.emit(True, f"完成！处理了 {total} 位女优", all_updates)
        except Exception as e:
            self.log(f"错误: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            self.finished_signal.emit(False, f"发生错误: {str(e)}", {})
        finally:
            if self.tab:
                try:
                    self.tab.close()
                except:
                    pass

    def _fetch_actress_data(self, actress_name: str) -> List[VideoInfo]:
        self.tab.get(f'https://supjav.com/ja/?s={actress_name}')
        time.sleep(2)
        lis = self.tab.eles('xpath://ul/li')
        page_count = 1
        for li in lis:
            text = li.text.strip()
            if text.isdigit():
                page_count = max(page_count, int(text))
        self.log(f"  总页数: {page_count}")
        all_posts = []
        for page in range(1, page_count + 1):
            if not self._is_running:
                break
            self.actress_progress_signal.emit(actress_name, page, page_count)
            self.log(f"  正在抓取第 {page}/{page_count} 页...")
            self.tab.get(f'https://supjav.com/ja/page/{page}?s={actress_name}')
            time.sleep(1.5)
            posts = self.tab.eles('css:div.post')
            for post in posts:
                if not self._is_running:
                    break
                a = post.ele('css:h3 a')
                if not a:
                    continue
                title = a.attr('title') or a.text
                if '[モザイク破壊]' not in title:
                    continue
                pattern = re.compile(r'[A-Z]{2,8}-\d{2,5}', re.I)
                m = pattern.search(title)
                code = m.group().upper() if m else ''
                url = a.attr('href')
                img = post.ele('css:img.thumb')
                img_url = ''
                if img:
                    img_url = img.attr('data-original') or img.attr('src') or ''
                meta = post.ele('css:div.meta')
                update_date, views = '', ''
                if meta:
                    meta_text = meta.text or ''
                    meta_html = getattr(meta, 'html', '') or ''
                    update_date, views = parse_meta_text(meta_text, meta_html)
                all_posts.append(VideoInfo(
                    code=code, title=title, url=url, img_url=img_url,
                    update_date=update_date, views=views
                ))
        return all_posts

    def _deduplicate_by_code(self, posts: List[VideoInfo]) -> List[VideoInfo]:
        code_map: Dict[str, VideoInfo] = {}
        for post in posts:
            if not post.code:
                continue
            try:
                current_date = datetime.strptime(post.update_date, "%Y/%m/%d")
            except (ValueError, TypeError):
                current_date = datetime.min
            if post.code not in code_map:
                code_map[post.code] = post
            else:
                try:
                    existing_date = datetime.strptime(code_map[post.code].update_date, "%Y/%m/%d")
                except (ValueError, TypeError):
                    existing_date = datetime.min
                if current_date > existing_date:
                    code_map[post.code] = post
        return list(code_map.values())

    def _save_to_excel(self, actress_name: str, data: List[VideoInfo]) -> str:
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{actress_name}-{today}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        wb = Workbook()
        ws = wb.active
        ws.title = "搜索结果"
        header_fill = PatternFill(start_color="585b70", end_color="585b70", fill_type="solid")
        header_font = OpenpyxlFont(bold=True, color="cdd6f4", size=11)
        header_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style='thin', color="45475a"),
            right=Side(style='thin', color="45475a"),
            top=Side(style='thin', color="45475a"),
            bottom=Side(style='thin', color="45475a")
        )
        yellow_fill = PatternFill(start_color="f9e2af", end_color="f9e2af", fill_type="solid")
        yellow_font = OpenpyxlFont(color="1e1e2e")
        headers = ["番号", "标题", "URL", "图片", "更新日期", "查看量", "本地已存在"]
        ws.append(headers)
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border
        ws.row_dimensions[1].height = 25
        for item in data:
            row_idx = ws.max_row + 1
            ws.cell(row=row_idx, column=1, value=item.code)
            ws.cell(row=row_idx, column=2, value=item.title)
            ws.cell(row=row_idx, column=3, value=item.url)
            ws.cell(row=row_idx, column=5, value=item.update_date)
            ws.cell(row=row_idx, column=6, value=item.views)
            ws.cell(row=row_idx, column=7, value="是" if item.is_local else "否")
            if item.is_local:
                for col in range(1, len(headers) + 1):
                    cell = ws.cell(row=row_idx, column=col)
                    cell.fill = yellow_fill
                    cell.font = yellow_font
                    cell.border = thin_border
            else:
                for col in range(1, len(headers) + 1):
                    ws.cell(row=row_idx, column=col).border = thin_border
            if self.embed_images and item.img_url:
                cache_path = get_image_cache_path(self.output_dir, item.img_url)
                img_bytes = load_cached_image(cache_path)
                if not img_bytes:
                    result = download_and_fit_image(item.img_url)
                    if result:
                        img_bytes, img_w, img_h = result
                        save_image_cache(cache_path, img_bytes)
                if img_bytes:
                    try:
                        embed_image_to_cell(ws, img_bytes, f"D{row_idx}", img_w, img_h)
                        ws.row_dimensions[row_idx].height = CELL_MAX_HEIGHT
                    except Exception as e:
                        self.log(f"    图片嵌入失败 {item.code}: {e}")
                        ws.cell(row=row_idx, column=4, value=item.img_url)
                else:
                    ws.cell(row=row_idx, column=4, value=item.img_url)
            else:
                ws.cell(row=row_idx, column=4, value=item.img_url)
        col_widths = {"A": 12, "B": 50, "C": 40, "D": 22, "E": 14, "F": 14, "G": 12}
        for col_letter, width in col_widths.items():
            ws.column_dimensions[col_letter].width = width
        ws.freeze_panes = "A2"
        wb.save(filepath)
        return filepath

    def _cache_images(self, actress_name: str, data: List[VideoInfo]):
        for item in data:
            if not item.img_url:
                continue
            cache_path = get_image_cache_path(self.output_dir, item.img_url)
            if os.path.exists(cache_path):
                continue
            result = download_and_fit_image(item.img_url)
            if result:
                img_bytes, _, _ = result
                save_image_cache(cache_path, img_bytes)
                self.log(f"    缓存图片: {item.code}")


# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supjav Manager - 女优资源管理器")
        self.setMinimumSize(1400, 900)
        self.settings = QSettings("SupjavManager", "Settings")
        self.worker: Optional[BatchScrapyWorker] = None
        self.actress_list: List[Tuple[str, str]] = []
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === 目录配置区域 ===
        dir_group = QGroupBox("目录配置")
        dir_group.setObjectName("configGroup")
        dir_layout = QVBoxLayout(dir_group)
        dir_layout.setSpacing(10)

        root_layout = QHBoxLayout()
        root_label = QLabel("根目录 (😍):")
        root_label.setObjectName("label")
        root_layout.addWidget(root_label)
        self.root_input = QLineEdit()
        self.root_input.setPlaceholderText("选择包含 1已完成 / 2未完成 / 3持续更新 的根目录...")
        self.root_input.setReadOnly(True)
        self.root_input.setObjectName("lineEdit")
        root_layout.addWidget(self.root_input)
        self.root_browse_btn = QPushButton("浏览...")
        self.root_browse_btn.setObjectName("accentBtn")
        self.root_browse_btn.clicked.connect(self._browse_root)
        root_layout.addWidget(self.root_browse_btn)
        dir_layout.addLayout(root_layout)

        sub_layout = QHBoxLayout()
        self.finished_label = QLabel("1 已完成: 未设置")
        self.finished_label.setObjectName("label")
        sub_layout.addWidget(self.finished_label)
        sub_layout.addSpacing(20)
        self.unfinished_label = QLabel("2 未完成: 未设置")
        self.unfinished_label.setObjectName("label")
        sub_layout.addWidget(self.unfinished_label)
        sub_layout.addSpacing(20)
        self.output_label = QLabel("3 持续更新: 未设置")
        self.output_label.setObjectName("label")
        sub_layout.addWidget(self.output_label)
        sub_layout.addStretch()
        dir_layout.addLayout(sub_layout)

        scan_layout = QHBoxLayout()
        self.scan_btn = QPushButton("扫描未完成目录")
        self.scan_btn.setObjectName("blueBtn")
        self.scan_btn.setMinimumHeight(38)
        self.scan_btn.clicked.connect(self._scan_unfinished)
        scan_layout.addWidget(self.scan_btn)
        scan_layout.addStretch()
        dir_layout.addLayout(scan_layout)

        main_layout.addWidget(dir_group)

        # === 女优列表区域 ===
        list_group = QGroupBox("识别到的女优")
        list_group.setObjectName("configGroup")
        list_layout = QVBoxLayout(list_group)

        self.actress_list_widget = QListWidget()
        self.actress_list_widget.setObjectName("actressList")
        self.actress_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.actress_list_widget.setMinimumHeight(150)
        list_layout.addWidget(self.actress_list_widget)

        list_btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(lambda: self.actress_list_widget.selectAll())
        list_btn_layout.addWidget(self.select_all_btn)
        self.select_none_btn = QPushButton("全不选")
        self.select_none_btn.clicked.connect(lambda: self.actress_list_widget.clearSelection())
        list_btn_layout.addWidget(self.select_none_btn)
        list_btn_layout.addStretch()
        self.actress_count_label = QLabel("共 0 位女优")
        self.actress_count_label.setObjectName("label")
        list_btn_layout.addWidget(self.actress_count_label)
        list_layout.addLayout(list_btn_layout)

        main_layout.addWidget(list_group)

        # === 控制选项 ===
        options_group = QGroupBox("抓取选项")
        options_group.setObjectName("configGroup")
        options_layout = QHBoxLayout(options_group)
        options_layout.setSpacing(20)

        port_layout = QHBoxLayout()
        port_label = QLabel("浏览器端口:")
        port_label.setObjectName("label")
        port_layout.addWidget(port_label)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(9333)
        self.port_spin.setObjectName("spinBox")
        port_layout.addWidget(self.port_spin)
        options_layout.addLayout(port_layout)

        self.embed_img_check = QCheckBox("嵌入图片到Excel")
        self.embed_img_check.setChecked(True)
        self.embed_img_check.setObjectName("checkBox")
        options_layout.addWidget(self.embed_img_check)

        self.export_excel_check = QCheckBox("导出Excel（可选）")
        self.export_excel_check.setChecked(False)
        self.export_excel_check.setObjectName("checkBox")
        options_layout.addWidget(self.export_excel_check)

        self.open_report_check = QCheckBox("完成后打开报告")
        self.open_report_check.setChecked(True)
        self.open_report_check.setObjectName("checkBox")
        options_layout.addWidget(self.open_report_check)

        options_layout.addStretch()
        main_layout.addWidget(options_group)

        # === 控制按钮 ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.start_btn = QPushButton("开始批量抓取")
        self.start_btn.setObjectName("greenBtn")
        self.start_btn.setMinimumHeight(42)
        self.start_btn.clicked.connect(self._start_batch)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("redBtn")
        self.stop_btn.setMinimumHeight(42)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_batch)
        btn_layout.addWidget(self.stop_btn)

        self.open_report_btn = QPushButton("打开更新报告")
        self.open_report_btn.setObjectName("blueBtn")
        self.open_report_btn.setMinimumHeight(42)
        self.open_report_btn.clicked.connect(self._open_report)
        btn_layout.addWidget(self.open_report_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # === 进度条 ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("女优 %v/%m: %p%")
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progressBar")
        main_layout.addWidget(self.progress_bar)

        self.actress_progress_label = QLabel("")
        self.actress_progress_label.setObjectName("label")
        self.actress_progress_label.setVisible(False)
        main_layout.addWidget(self.actress_progress_label)

        # === 分割器 ===
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.update_table = QTableWidget()
        self.update_table.setColumnCount(4)
        self.update_table.setHorizontalHeaderLabels(["女优", "新增数量", "JSON路径", "操作"])
        self.update_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.update_table.horizontalHeader().setStretchLastSection(True)
        self.update_table.setAlternatingRowColors(True)
        self.update_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.update_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.update_table.setObjectName("dataTable")
        splitter.addWidget(self.update_table)

        log_group = QGroupBox("日志")
        log_group.setObjectName("logGroup")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("JetBrains Mono", 10))
        self.log_text.setObjectName("logText")
        log_layout.addWidget(self.log_text)
        splitter.addWidget(log_group)

        splitter.setSizes([300, 400])
        main_layout.addWidget(splitter, 1)

        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 请先选择根目录")

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

    def _load_settings(self):
        saved_root = self.settings.value("root_dir", "")
        if saved_root and os.path.exists(saved_root):
            self.root_input.setText(saved_root)
            self._update_subdirs(saved_root)
        saved_port = self.settings.value("browser_port", 9333)
        self.port_spin.setValue(int(saved_port))
        embed = self.settings.value("embed_images", "true")
        self.embed_img_check.setChecked(embed.lower() == "true")
        export = self.settings.value("export_excel", "false")
        self.export_excel_check.setChecked(export.lower() == "true")

    def _save_settings(self):
        self.settings.setValue("root_dir", self.root_input.text())
        self.settings.setValue("browser_port", self.port_spin.value())
        self.settings.setValue("embed_images", str(self.embed_img_check.isChecked()).lower())
        self.settings.setValue("export_excel", str(self.export_excel_check.isChecked()).lower())

    def _browse_root(self):
        current_dir = self.root_input.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self, "选择根目录 (包含 1已完成/2未完成/3持续更新)", current_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.root_input.setText(directory)
            self._update_subdirs(directory)
            self._save_settings()

    def _update_subdirs(self, root_dir: str):
        finished = os.path.join(root_dir, "1 已完成")
        unfinished = os.path.join(root_dir, "2 未完成")
        output = os.path.join(root_dir, "3 持续更新")
        self.finished_dir = finished if os.path.exists(finished) else ""
        self.unfinished_dir = unfinished if os.path.exists(unfinished) else ""
        self.output_dir = output
        self.finished_label.setText(f"1 已完成: {'✓' if self.finished_dir else '✗'} {finished}")
        self.unfinished_label.setText(f"2 未完成: {'✓' if self.unfinished_dir else '✗'} {unfinished}")
        self.output_label.setText(f"3 持续更新: {output}")
        if self.unfinished_dir:
            self._scan_unfinished()

    def _scan_unfinished(self):
        if not hasattr(self, 'unfinished_dir') or not self.unfinished_dir:
            QMessageBox.warning(self, "警告", "请先选择根目录！")
            return
        self.actress_list = ActressScanner.scan_unfinished_dir(self.unfinished_dir)
        self.actress_list_widget.clear()
        for folder_path, actress_name in self.actress_list:
            item = QListWidgetItem(f"{actress_name}  ({os.path.basename(folder_path)})")
            item.setData(Qt.ItemDataRole.UserRole, (folder_path, actress_name))
            self.actress_list_widget.addItem(item)
        self.actress_count_label.setText(f"共 {len(self.actress_list)} 位女优")
        self.log(f"扫描完成，发现 {len(self.actress_list)} 位女优")

    def _start_batch(self):
        if not hasattr(self, 'unfinished_dir') or not self.unfinished_dir:
            QMessageBox.warning(self, "警告", "请先选择根目录！")
            return
        selected_items = self.actress_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请至少选择一位女优！")
            return
        selected = []
        for item in selected_items:
            data = item.data(Qt.ItemDataRole.UserRole)
            selected.append(data)
        os.makedirs(self.output_dir, exist_ok=True)
        self._save_settings()
        self.update_table.setRowCount(0)
        self.log_text.clear()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(selected))
        self.actress_progress_label.setVisible(True)
        self.status_bar.showMessage(f"正在处理 {len(selected)} 位女优...")
        self.worker = BatchScrapyWorker(
            selected, self.root_input.text(), self.output_dir,
            getattr(self, 'finished_dir', ""),
            self.port_spin.value(),
            self.embed_img_check.isChecked(),
            self.export_excel_check.isChecked()
        )
        self.worker.log_signal.connect(self._append_log)
        self.worker.progress_signal.connect(self._update_progress)
        self.worker.actress_progress_signal.connect(self._update_actress_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _stop_batch(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait(5000)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.actress_progress_label.setVisible(False)
        self.status_bar.showMessage("已停止")

    def _update_progress(self, current: int, total: int):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def _update_actress_progress(self, actress_name: str, current: int, total: int):
        self.actress_progress_label.setText(f"{actress_name}: 第 {current}/{total} 页")

    def _append_log(self, msg: str):
        self.log_text.append(msg)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_finished(self, success: bool, msg: str, all_updates: dict):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.actress_progress_label.setVisible(False)
        if success:
            self.status_bar.showMessage(f"完成 - {msg}")
            self._populate_update_table(all_updates)
            if self.open_report_check.isChecked() and all_updates:
                self._open_report()
            QMessageBox.information(self, "完成", msg)
        else:
            self.status_bar.showMessage(f"失败 - {msg}")
            QMessageBox.critical(self, "错误", msg)

    def _populate_update_table(self, all_updates: Dict[str, List[VideoInfo]]):
        self.update_table.setRowCount(0)
        for actress, items in all_updates.items():
            row = self.update_table.rowCount()
            self.update_table.insertRow(row)
            self.update_table.setItem(row, 0, QTableWidgetItem(actress))
            self.update_table.setItem(row, 1, QTableWidgetItem(str(len(items))))
            json_path = os.path.join(self.output_dir, f"{actress}.json")
            self.update_table.setItem(row, 2, QTableWidgetItem(json_path))
            open_btn = QPushButton("打开JSON")
            open_btn.clicked.connect(lambda checked, p=json_path: self._open_file(p))
            self.update_table.setCellWidget(row, 3, open_btn)
        self.update_table.resizeColumnsToContents()

    def _open_report(self):
        report_path = os.path.join(self.output_dir, "updata.html")
        if os.path.exists(report_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(report_path))
        else:
            QMessageBox.warning(self, "提示", "更新报告不存在，请先运行抓取。")

    def _open_file(self, path: str):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "提示", f"文件不存在: {path}")

    def log(self, msg: str):
        self._append_log(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def _show_about(self):
        QMessageBox.about(self, "关于",
                          "<h2>Supjav Manager</h2>"
                          "<p>女优资源批量管理工具</p>"
                          "<p>功能：自动扫描、批量抓取、JSON数据库、增量更新、HTML报告</p>")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "确认", "任务正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self.worker.stop()
            self.worker.wait(3000)
        self._save_settings()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(f"""
        QMainWindow {{
            background-color: {DARK_BG};
        }}
        QWidget {{
            background-color: {DARK_BG};
            color: {TEXT_PRIMARY};
        }}
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
        QLabel#label {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
        }}
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
        QSpinBox#spinBox {{
            background-color: {DARK_INPUT};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
            color: {TEXT_PRIMARY};
        }}
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
        QPushButton {{
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: bold;
            color: {DARK_BG};
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
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
        QProgressBar#progressBar {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            background-color: {DARK_INPUT};
            text-align: center;
            color: {TEXT_PRIMARY};
            font-size: 12px;
            height: 24px;
        }}
        QProgressBar#progressBar::chunk {{
            background-color: {ACCENT_BLUE};
            border-radius: 6px;
        }}
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
        QTextEdit#logText {{
            background-color: {DARK_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            color: {TEXT_PRIMARY};
            font-size: 12px;
            padding: 10px;
            selection-background-color: {ACCENT_BLUE};
        }}
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
        QStatusBar#statusBar {{
            background-color: {DARK_BG};
            color: {TEXT_SECONDARY};
            border-top: 1px solid {BORDER_COLOR};
        }}
        QSplitter::handle {{
            background-color: {BORDER_COLOR};
        }}
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
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()