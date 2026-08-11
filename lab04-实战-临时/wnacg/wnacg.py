"""
wnacg 漫画下载器 — 单文件版（GUI + CLI + 批量）

Usage:
  python wnacg.py                     # 启动 GUI
  python wnacg.py --cli               # CLI 单漫画模式
  python wnacg.py --cli --name <xxx> --save-dir <dir>   # CLI 免交互
  python wnacg.py --batch <父文件夹>    # CLI 批量模式

打包：
  pyinstaller --onefile --windowed --icon=icon.ico --name=wnacg wnacg.py

架构（两阶段 + 状态文件）：
  ① 抓取阶段（单线程，DrissionPage 浏览器过 Cloudflare）：
     搜索 → 翻页 → 进详情页/下载页取真实 .zip 链接 → 写入 state.json
  ② 下载阶段（多线程 requests + 全局节流 + 429 长退避）：
     只下载 pending 且本地无有效文件的条目；下载完做大小校验 + zip 完整性校验

批量模式：
  扫描父文件夹下的子文件夹 → 解析文件夹名提取搜索关键词 →
  逐个调用单漫画流程，每个子文件夹独立保存 state.json
"""

from urllib.parse import quote
import os
import re
import sys
import io
import time
import json
import zipfile
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from DrissionPage import Chromium

import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ========================================================================
# 0. 全局配置
# ========================================================================

BASE = 'https://www.wnacg.com'

# — 默认配置（GUI / CLI 调用时通过 main(name, save_dir) 覆盖） —
DEFAULT_SAVE_DIR = './downloads'
SAVE_DIR = None            # 由 main() 设置
STATE_FILE = None          # 由 main() 设置
MAX_WORKERS = 2            # 下载并发数
MIN_REQUEST_INTERVAL = 3   # 全局节流：发起新下载请求的最小间隔（秒）
RETRY_ROUNDS = 2           # 一轮下载后，对失败项再重试的轮数

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0 Safari/537.36'),
    'Referer': 'https://www.wnacg.com/',
}

_state_lock = threading.Lock()   # 多线程读写 state 时加锁
_rate_lock = threading.Lock()    # 全局节流锁
_last_request = [0.0]            # 上一次发起下载请求的时间（monotonic）

# — 停止标志（跨线程） —
_stop_flag = False               # 在 main() 内检查，控制单个任务停止
_batch_stop = False              # 在批量循环间检查，控制批量任务停止

# — 浏览器（延迟初始化，可跨任务复用） —
browser = None
tab = None


# ========================================================================
# 1. 核心引擎（来自 byName.py，增加 _stop_flag 检查点）
# ========================================================================

# ——— 1.1 状态文件 ———

def load_state():
    """读取状态文件，返回 {gallery_url: {记录}}"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print('⚠ 状态文件损坏，重新开始')
    return {}


def save_state(state):
    """原子写状态文件（先写 .tmp 再 replace，避免写一半崩溃）"""
    with _state_lock:
        tmp = STATE_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STATE_FILE)


# ——— 1.2 工具函数 ———

def _abs(href):
    """相对 URL 转绝对（兼容协议相对 // 和站点相对 /）"""
    if not href:
        return None
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith('http'):
        return href
    return BASE + href


def clean_title(s):
    """清理标题用作文件名：去 <em> 等 HTML 标签 + 非法字符"""
    s = re.sub(r'<[^>]+>', '', s or '')
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        s = s.replace(ch, '_')
    return s.strip() or 'untitled'


def _throttle():
    """
    全局节流：确保任意两次「发起下载请求」之间至少间隔 MIN_REQUEST_INTERVAL 秒。
    多线程下，发起新请求被串行化间隔，但文件传输仍可并发——既控限流又保速度。
    """
    with _rate_lock:
        now = time.monotonic()
        wait = MIN_REQUEST_INTERVAL - (now - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()


def _retry_after(resp, default=20):
    """读取 429 响应的 Retry-After 头，没有或非法则用 default（上限 120s）"""
    ra = resp.headers.get('Retry-After')
    if ra:
        try:
            return min(float(ra), 120)
        except ValueError:
            pass
    return default


def _safe_remove(path):
    """删残文件，忽略错误"""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _zip_intact(path):
    """完整 zip 完整性校验（重，会读取整个压缩包内容）"""
    try:
        if not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path) as zf:
            return zf.testzip() is None
    except Exception:
        return False


def file_is_valid(path, rec):
    """
    二次检测本地文件是否有效。
    有缓存（verified_size / verified_mtime）且文件大小+修改时间未变 → 直接信任，
    跳过 testzip（快，只做 stat）。否则跑一次完整 testzip（慢），通过则回填缓存。
    这样日常启动不再对每个 done 文件重复读整个包。
    """
    if not path or not os.path.exists(path):
        return False
    try:
        st = os.stat(path)
    except OSError:
        return False
    if st.st_size == 0:
        return False
    if (rec.get('verified_size') == st.st_size
            and rec.get('verified_mtime') == int(st.st_mtime)):
        return True
    ok = _zip_intact(path)
    if ok:
        rec['verified_size'] = st.st_size
        rec['verified_mtime'] = int(st.st_mtime)
    else:
        rec.pop('verified_size', None)
        rec.pop('verified_mtime', None)
    return ok


def _aid_from_url(url):
    """从画廊/下载页 URL 提取 aid，用于文件名去重"""
    m = re.search(r'aid-(\d+)', url or '')
    return m.group(1) if m else ''


def _make_save_path(title_clean, gurl):
    """
    生成保存路径：标题_aid.zip（aid 保证不同本子即使同名也不会重名）。
    兼容旧版（仅标题.zip）：若新路径不存在但旧标题路径存在，则重命名过来，避免重复下载。
    """
    aid = _aid_from_url(gurl)
    new_path = os.path.join(SAVE_DIR, f'{title_clean}_{aid}.zip' if aid else f'{title_clean}.zip')
    if aid and not os.path.exists(new_path):
        old_path = os.path.join(SAVE_DIR, f'{title_clean}.zip')
        if os.path.exists(old_path):
            try:
                os.replace(old_path, new_path)
            except OSError:
                pass
    return new_path


# ——— 1.3 抓取阶段 ———

def parse_gallery_links(tab):
    """解析当前页所有画廊详情链接，返回 [(title, url), ...]"""
    items = tab.eles('xpath://li[contains(@class,"gallary_item")]')
    results = []
    for li in items:
        a = li.ele('xpath:.//a', timeout=1)
        if not a:
            continue
        href = a.attr('href') or ''
        if not href:
            continue
        title = a.attr('title') or a.text or ''
        href = _abs(href)
        if not href:
            continue
        results.append((title.strip(), href))
    return results


def get_page_urls(tab):
    """
    获取分页页码 URL（已验证：页码 <a> 无 class，靠文本是纯数字识别）。
    返回 [] 表示无分页。注意 paginator 只展示部分页码，非全部中间页。
    """
    page_items = tab.eles(
        "xpath://div[contains(@class,'bot_toolbar')]//div[contains(@class,'paginator')]//a"
    )
    urls = []
    for a in page_items:
        href = a.attr('href') or ''
        text = (a.text or '').strip()
        if href and text.isdigit():
            urls.append(_abs(href))
    return urls


def get_download_url(tab, gallery_url):
    """
    两步获取真实下载链接（.zip）：
    ① 详情页 <a href="/download-index-aid-XXX.html">下載漫畫</a>
    ② 下载页 <a class="ads" href="//dl1.wn01.download/.../x.zip?n=...">備用線路</a>
    """
    tab.get(gallery_url)
    dl_btn = tab.ele('xpath://a[contains(@href,"/download-index-aid-")]', timeout=8)
    if not dl_btn:
        dl_btn = tab.ele('xpath://a[contains(text(),"下载") or contains(text(),"下載")]', timeout=3)
    if not dl_btn:
        return None
    dl_page = _abs(dl_btn.attr('href'))
    if not dl_page or dl_page in ('javascript:;', '#'):
        return None

    tab.get(dl_page)
    a = tab.ele('xpath://a[contains(@href,".zip")]', timeout=8)
    if a:
        return _abs(a.attr('href'))
    # 兜底：onclick / 整页 grep（兼容 // 与 https:// 两种写法）
    for src in [dl_btn.attr('onclick') or '', tab.html or '']:
        m = re.search(r'((?:https?:)?//[^\s\'"<>]+\.zip)', src)
        if m:
            return _abs(m.group(1))
    return None


def scrape_galleries(tab, name):
    """搜索 + 翻页，收集所有画廊 (title, gallery_url)，去重保序"""
    global _stop_flag
    search_url = f'{BASE}/search/?q={quote(name)}&f=_all&s=create_time_DESC&syn=yes'
    tab.get(search_url)
    tab.wait.eles_loaded('xpath://li[contains(@class,"gallary_item")]', timeout=15)

    page_urls = get_page_urls(tab)
    all_pages = [search_url] + page_urls if page_urls else [search_url]
    print(f'共 {len(all_pages)} 页，开始抓取画廊列表...')

    seen, galleries = set(), []
    for i, url in enumerate(all_pages, start=1):
        if _stop_flag:
            print('⚠ 用户停止（翻页阶段）')
            break
        if i > 1:
            tab.get(url)
            tab.wait.eles_loaded('xpath://li[contains(@class,"gallary_item")]', timeout=15)
            time.sleep(1)
        for title, gurl in parse_gallery_links(tab):
            if gurl not in seen:
                seen.add(gurl)
                galleries.append((title, gurl))
        print(f'  第 {i} 页：累计 {len(galleries)} 条')
    return galleries


# ——— 1.4 下载阶段 ———

def download_file(url, save_path, max_retries=3, max_429=6):
    """
    流式下载单个文件：
      - 发起前 _throttle() 全局节流
      - 429：读 Retry-After / 默认 20s 长退避，单独计数（max_429），不消耗普通重试
      - 下完做大小校验（Content-Length）+ zip 完整性校验
      - 失败删残文件，普通异常按 3s/6s/9s 退避重试
    """
    clean_url = url.split('?')[0]
    attempt = 0
    r429 = 0
    while True:
        _throttle()
        try:
            with requests.get(clean_url, headers=HEADERS, stream=True, timeout=60) as resp:
                if resp.status_code == 429:
                    if r429 >= max_429:
                        raise requests.HTTPError('429 限流，重试次数耗尽')
                    wait = _retry_after(resp, 20)
                    r429 += 1
                    print(f'      429 限流，等待 {wait}s（第 {r429}/{max_429} 次）')
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                expected = resp.headers.get('Content-Length')
                with open(save_path, 'wb') as f:
                    for chunk in resp.iter_content(8192):
                        if chunk:
                            f.write(chunk)
            # 大小校验
            if expected:
                actual = os.path.getsize(save_path)
                if int(expected) != actual:
                    raise IOError(f'大小不符：预期 {expected} 实际 {actual}')
            # zip 完整性校验
            if not _zip_intact(save_path):
                raise IOError('zip 完整性校验失败')
            return
        except Exception as e:
            last_err = e
            _safe_remove(save_path)
            attempt += 1
            if attempt >= max_retries:
                raise
            time.sleep(3 * attempt)


def download_worker(rec):
    """单个下载任务：返回 (key, status, error)。已存在有效文件直接算成功。"""
    key = rec['gallery_url']
    save_path = rec['save_path']
    if file_is_valid(save_path, rec):     # 二次检测：已存在且完整 → 跳过
        return key, 'done', None
    try:
        download_file(rec['download_url'], save_path)
    except Exception as e:
        return key, 'failed', str(e)
    # 下载成功，回填完整性缓存
    try:
        st = os.stat(save_path)
        rec['verified_size'] = st.st_size
        rec['verified_mtime'] = int(st.st_mtime)
    except OSError:
        pass
    return key, 'done', None


def download_phase(state, items):
    """下载一批 items，返回本轮失败的 key 列表"""
    failed = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(download_worker, rec): rec['gallery_url'] for rec in items}
        for fut in as_completed(futs):
            key, status, err = fut.result()
            with _state_lock:
                state[key]['status'] = status
                state[key]['error'] = err
            mark = '✓' if status == 'done' else '✗'
            print(f'  {mark} {state[key]["title"]}{"  " + err if err else ""}')
            save_state(state)
            if status != 'done':
                failed.append(key)
    return failed


# ——— 1.5 主流程 ———

def main(name=None, save_dir=None):
    """入口函数。
    Args:
        name:     漫画名称。为 None 则弹出 input() 交互输入。
        save_dir: 保存目录。为 None 则弹出 input() 交互输入。
    Returns:
        True   — 正常完成
        False  — 被用户停止
    """
    global SAVE_DIR, STATE_FILE, browser, tab, _stop_flag

    name = name or input('漫画名称（回车默认"獵艷管理員"）：').strip() or '獵艷管理員'
    save_dir = save_dir or input('保存目录（回车默认 ./downloads）：').strip() or DEFAULT_SAVE_DIR
    SAVE_DIR = save_dir
    STATE_FILE = os.path.join(SAVE_DIR, 'state.json')
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 按需初始化浏览器（整个进程生命周期只创建一次）
    if browser is None:
        browser = Chromium(9333)
        tab = browser.latest_tab

    state = load_state()
    done_cnt = sum(1 for v in state.values() if v.get('status') == 'done')
    print(f'\n已有状态：{len(state)} 条（其中 done {done_cnt} 条）')

    # ==== ① 抓取阶段 ====
    galleries = scrape_galleries(tab, name)
    if _stop_flag:
        return False
    print(f'\n抓到 {len(galleries)} 个画廊，开始提取下载链接...')

    for idx, (title, gurl) in enumerate(galleries, start=1):
        if _stop_flag:
            print('⚠ 用户停止（提取下载链接阶段），已保存当前进度')
            save_state(state)
            return False

        rec = state.get(gurl)
        # 已完成且本地文件有效 → 跳过
        if rec and rec.get('status') == 'done' and file_is_valid(rec.get('save_path'), rec):
            continue
        # 其余（新 / pending / failed / done但文件损坏）→ (重新)抓下载链接
        dl_url = get_download_url(tab, gurl)
        title_clean = clean_title(title)
        state[gurl] = {
            'title': title_clean,
            'gallery_url': gurl,
            'download_url': dl_url,
            'status': 'pending' if dl_url else 'failed',
            'error': None if dl_url else '未找到下载链接',
            'save_path': _make_save_path(title_clean, gurl),
        }
        print(f'  [{idx}/{len(galleries)}] {title_clean} -> '
              f'{"已提取" if dl_url else "无下载链接"}')
        save_state(state)

    # ==== ② 下载阶段 ====
    # 校正：本地有效文件 → done；done 但文件损坏/丢失 → pending 重下
    for rec in state.values():
        if file_is_valid(rec.get('save_path'), rec):
            rec['status'] = 'done'
            rec['error'] = None
        elif rec.get('status') == 'done':
            rec['status'] = 'pending'
            rec['error'] = '本地文件损坏或丢失，重新下载'

    pending = [v for v in state.values()
               if v['status'] == 'pending' and v.get('download_url')]
    save_state(state)

    print(f'\n待下载：{len(pending)} 个，并发 {MAX_WORKERS}，'
          f'节流间隔 {MIN_REQUEST_INTERVAL}s，重试 {RETRY_ROUNDS} 轮')

    # 第一轮 + RETRY_ROUNDS 轮重试
    todo = pending
    for round_i in range(1, RETRY_ROUNDS + 2):
        if _stop_flag:
            print('⚠ 用户停止（下载阶段）')
            return False
        if not todo:
            break
        print(f'\n=== 下载第 {round_i} 轮，{len(todo)} 个 ===')
        failed_keys = download_phase(state, todo)
        if not failed_keys:
            break
        # 打印本轮失败清单
        print(f'\n第 {round_i} 轮失败 {len(failed_keys)} 个：')
        for k in failed_keys:
            print(f'  ✗ {state[k]["title"]}  ({state[k].get("error")})')
        # 下一轮重试
        todo = [state[k] for k in failed_keys]
        for k in failed_keys:
            state[k]['status'] = 'pending'
        save_state(state)
        if round_i <= RETRY_ROUNDS:
            time.sleep(5)   # 轮间喘息

    # ==== 汇总 ====
    failed_items = [v for v in state.values() if v['status'] == 'failed']
    if failed_items:
        print(f'\n===== 最终失败清单（{len(failed_items)} 个）====')
        for v in failed_items:
            print(f'  ✗ {v["title"]}  ({v.get("error")})')
    counts = {}
    for v in state.values():
        counts[v['status']] = counts.get(v['status'], 0) + 1
    print(f'\n全部完成。状态统计：{counts}')
    return True


# ========================================================================
# 2. 文件夹名解析
# ========================================================================

def extract_search_keyword(folder_name: str) -> str:
    """
    从子文件夹名提取搜索关键词。

    处理顺序（级联）：
      1. 去掉所有括注内容（适配【】[]() 全角/半角混合及未闭合情况）
      2. 去掉前导的数字+点（如 "020." → ""）
      3. 去掉剩余前导数字+分隔符（如 "001 " 或 "001-")
      4. 去掉首尾空白及尾部残留分隔符

    用例：
      "020.xxx【完結】"         → "xxx"
      "004.美麗新世界 【完結)"   → "美麗新世界"
      "005.富家女姐姐 【完结】"  → "富家女姐姐"
      "006.色轮眼 【完結】"      → "色轮眼"
      "007.人妻獵人 【连裁中】"  → "人妻獵人"
      "008.H校園不登出 [完结121】" → "H校園不登出"
      "009.test [完結12]"       → "test"
      "010.abc(完結)"           → "abc"
      "001.abc"                → "abc"
      "【完結】"                → "" (空，应跳过)
    """
    s = folder_name.strip()

    # 1. 去掉所有括注内容
    #    —— 匹配 【...】、[...]、(完結)、[...】、【...) 等混合/未闭合情况
    #    分两遍：先匹配成对（含混合配对），再扫尾残余括号前缀
    s = re.sub(r'[(（【\[]\s*[完连連載载结結续繼]?[中载結结]?\w*\s*[)）】\]\]]?', '', s)
    #    再去掉残余的半括号（开头/结尾未配对的）
    s = re.sub(r'^[)）】\]\]]', '', s)
    s = re.sub(r'[(（【\[]$', '', s)
    #    再去掉残余的尾部标注文字片段（没有括号包裹的 「完结121」之类）
    s = re.sub(r'\s*[（(【\[]?\s*(?:完[结結]|连[载裁][中]?|[Cc]omplete)\s*(?:[)）】\]\]]?\s*\d*\s*(?:话|回|集|頁|页|P)?\s*[)）】\]\]]?)?\s*$', '', s)

    # 2. 去掉前导数字 + 点
    s = re.sub(r'^\d+\.', '', s)
    # 3. 去掉剩余前导数字 + 分隔符
    s = re.sub(r'^\d+[-_.\s]+', '', s)
    # 4. 清理首尾
    s = s.strip(' -_.')
    return s


# ========================================================================
# 3. 批量处理
# ========================================================================

def scan_folder_tasks(parent_dir: str) -> list:
    """
    扫描父文件夹下的子文件夹，提取搜索关键词。

    Returns:
        [{keyword, folder, folder_name, status}, ...]
        跳过 keyword 为空的文件夹
    """
    if not os.path.isdir(parent_dir):
        print(f'✗ 目录不存在：{parent_dir}')
        return []

    tasks = []
    try:
        items = sorted(os.listdir(parent_dir))
    except OSError as e:
        print(f'✗ 无法读取目录：{e}')
        return []

    for item in items:
        full = os.path.join(parent_dir, item)
        if not os.path.isdir(full):
            continue
        keyword = extract_search_keyword(item)
        if not keyword:
            continue

        # 检查该子文件夹是否已完成
        state_file = os.path.join(full, 'state.json')
        status = 'pending'
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    st = json.load(f)
                if st and all(v.get('status') == 'done' for v in st.values()):
                    status = 'done'
            except (json.JSONDecodeError, OSError):
                pass

        tasks.append({
            'keyword': keyword,
            'folder': full,
            'folder_name': item,
            'status': status,
            'error': None,
        })

    return tasks


def run_batch(parent_dir: str, tasks: list = None) -> list:
    """
    批量下载入口。支持 CLI 和 GUI（后台线程）调用。

    Args:
        parent_dir: 父文件夹路径
        tasks:      可选，预扫描的任务列表。为 None 则自动扫描。

    Returns:
        [{...}]
        失败或停止的任务列表
    """
    global _batch_stop, _stop_flag
    _batch_stop = False

    if tasks is None:
        tasks = scan_folder_tasks(parent_dir)

    if not tasks:
        print('没有找到可处理的子文件夹')
        return []

    # 区分已完成与待处理
    pending_tasks = [t for t in tasks if t['status'] != 'done']
    print(f'\n批量任务：{len(tasks)} 个子文件夹（{len(pending_tasks)} 个待处理）')
    for t in tasks:
        tag = '✓ 已完成' if t['status'] == 'done' else '待处理'
        print(f'  [{tag}] {t["keyword"]}  ←  {t["folder_name"]}')

    if not pending_tasks:
        print('所有子文件夹已完成，无需下载')
        return []

    failed = []
    for i, t in enumerate(pending_tasks, start=1):
        if _batch_stop:
            print('\n⚠ 用户停止批量任务')
            # 剩余待处理项标记为 stopped
            for rt in pending_tasks[i - 1:]:
                rt['status'] = 'stopped'
            break

        print(f'\n{"=" * 60}')
        print(f'[{i}/{len(pending_tasks)}] {t["keyword"]}')
        print(f'文件夹：{t["folder"]}')
        print(f'{"=" * 60}')

        _stop_flag = False  # 每个任务前重置

        try:
            ok = main(name=t['keyword'], save_dir=t['folder'])
            if _stop_flag:
                t['status'] = 'stopped'
                failed.append(t)
            else:
                t['status'] = 'done'
        except Exception as e:
            print(f'✗ 任务异常：{e}')
            t['status'] = 'failed'
            t['error'] = str(e)
            failed.append(t)

    # 汇总
    done_count = sum(1 for t in tasks if t['status'] == 'done')
    fail_count = sum(1 for t in tasks if t['status'] == 'failed')
    stop_count = sum(1 for t in tasks if t['status'] == 'stopped')
    print(f'\n批量完成：{done_count} 成功  {fail_count} 失败  {stop_count} 停止')

    if failed:
        print(f'\n失败/停止清单：')
        for t in failed:
            print(f'  ✗ {t["keyword"]}  ({t["status"]}{" — " + t["error"] if t.get("error") else ""})')

    return failed


def close_browser():
    """安全关闭浏览器（供 GUI 退出时调用）"""
    global browser, tab
    if browser:
        try:
            browser.quit()
        except Exception:
            pass
        browser = None
        tab = None


# ========================================================================
# 4. GUI（ttk.Notebook 双标签页：单漫画 + 批量）
# ========================================================================

class TextRedirector(io.StringIO):
    """将 print 输出重定向到 tkinter Text 组件（线程安全）"""

    def __init__(self, text_widget, tag=None):
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag
        self._buffer = []

    def write(self, s):
        if not s:
            return
        self._buffer.append(s)
        self.text_widget.after_idle(self._flush)

    def _flush(self):
        text = ''.join(self._buffer)
        self._buffer.clear()
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', text, self.tag)
        self.text_widget.see('end')
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass


class WnacgGUI:
    """wnacg 漫画下载器 GUI"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('绅士漫画下载器 - wnacg')
        self.root.geometry('900x700')
        self.root.resizable(True, True)

        # 单漫画变量
        self.name_var = tk.StringVar(value='獵艷管理員')
        self.dir_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads', 'wnacg'))

        # 批量变量
        self.batch_parent_var = tk.StringVar(value='')
        self._batch_tasks = []       # [{keyword, folder, folder_name, status, error}, ...]
        self._batch_running = False
        self._tab_locked = False     # 禁止切换标签页
        self._last_tab = 0           # 上次选中的标签页索引

        # 运行状态
        self.running = False
        self._worker = None
        self._done = False           # 防 _on_done 多重调用

        self._build_ui()
        self._center_window()

    # ——— UI 构建 ———

    def _build_ui(self):
        # === 标签页 ===
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(10, 0))

        # 标签 1：单漫画
        self.tab_single = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_single, text='单漫画')
        self._build_single_tab(self.tab_single)

        # 标签 2：批量
        self.tab_batch = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_batch, text='批量文件夹')
        self._build_batch_tab(self.tab_batch)

        # === 共享日志区 ===
        frame_log = ttk.LabelFrame(self.root, text='运行日志', padding=5)
        frame_log.pack(fill='both', expand=True, padx=10, pady=(5, 5))

        self.log_text = tk.Text(frame_log, wrap='word', state='disabled',
                                font=('Consolas', 10), bg='#1e1e1e', fg='#d4d4d4',
                                insertbackground='white')
        scroll_y = ttk.Scrollbar(frame_log, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll_y.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')

        # === 底部状态栏 ===
        self.status_bar = ttk.Label(self.root, text='就绪', relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', padx=10, pady=(0, 5))

    def _build_single_tab(self, parent):
        """单漫画标签页 UI"""
        # 漫画名称
        frame_top = ttk.Frame(parent, padding=10)
        frame_top.pack(fill='x')

        ttk.Label(frame_top, text='漫画名称：').pack(side='left')
        entry = ttk.Entry(frame_top, textvariable=self.name_var, width=50)
        entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
        entry.bind('<Return>', lambda e: self._start_single())

        # 保存目录
        frame_dir = ttk.Frame(parent, padding=(10, 0, 10, 10))
        frame_dir.pack(fill='x')

        ttk.Label(frame_dir, text='保存目录：').pack(side='left')
        ttk.Entry(frame_dir, textvariable=self.dir_var).pack(side='left', padx=(5, 5), fill='x', expand=True)
        ttk.Button(frame_dir, text='浏览...', command=self._browse_save_dir).pack(side='left')

        # 操作按钮
        frame_btn = ttk.Frame(parent, padding=(10, 0, 10, 10))
        frame_btn.pack(fill='x')

        self.btn_start_single = ttk.Button(frame_btn, text='▶ 开始下载', command=self._start_single)
        self.btn_start_single.pack(side='left', padx=(0, 10))
        self.btn_stop_single = ttk.Button(frame_btn, text='■ 停止', command=self._stop,
                                          state='disabled')
        self.btn_stop_single.pack(side='left')

        # 说明
        ttk.Label(parent, text='输入漫画名称（如"獵艷管理員"），程序将搜索并下载所有匹配的画廊',
                  foreground='gray').pack(anchor='w', padx=10, pady=(0, 10))

    def _build_batch_tab(self, parent):
        """批量文件夹标签页 UI"""
        # 父文件夹选择
        frame_top = ttk.Frame(parent, padding=10)
        frame_top.pack(fill='x')

        ttk.Label(frame_top, text='父文件夹：').pack(side='left')
        ttk.Entry(frame_top, textvariable=self.batch_parent_var, width=50).pack(
            side='left', padx=(5, 5), fill='x', expand=True)
        ttk.Button(frame_top, text='浏览...', command=self._browse_parent_dir).pack(side='left')

        # 操作按钮
        frame_btn = ttk.Frame(parent, padding=(10, 0, 10, 10))
        frame_btn.pack(fill='x')

        self.btn_scan = ttk.Button(frame_btn, text='🔍 扫描子文件夹', command=self._scan_folder)
        self.btn_scan.pack(side='left', padx=(0, 10))

        self.btn_start_batch = ttk.Button(frame_btn, text='▶ 开始批量下载',
                                          command=self._start_batch, state='disabled')
        self.btn_start_batch.pack(side='left', padx=(0, 10))

        self.btn_stop_batch = ttk.Button(frame_btn, text='■ 停止', command=self._stop,
                                         state='disabled')
        self.btn_stop_batch.pack(side='left')

        # 子文件夹名解析说明
        ttk.Label(parent, text='解析规则："020.xxx【完結】" → 搜索 "xxx"；"001.abc" → 搜索 "abc"',
                  foreground='gray').pack(anchor='w', padx=10)

        # 任务列表 Treeview
        tree_frame = ttk.Frame(parent, padding=(10, 5, 10, 10))
        tree_frame.pack(fill='both', expand=True)

        self.batch_tree = ttk.Treeview(
            tree_frame,
            columns=('#', 'keyword', 'folder', 'status'),
            show='headings',
            height=10,
        )
        self.batch_tree.heading('#', text='序号')
        self.batch_tree.heading('keyword', text='搜索关键词')
        self.batch_tree.heading('folder', text='子文件夹')
        self.batch_tree.heading('status', text='状态')

        self.batch_tree.column('#', width=50, anchor='center')
        self.batch_tree.column('keyword', width=180)
        self.batch_tree.column('folder', width=280)
        self.batch_tree.column('status', width=100, anchor='center')

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.batch_tree.yview)
        self.batch_tree.configure(yscrollcommand=tree_scroll_y.set)
        self.batch_tree.pack(side='left', fill='both', expand=True)
        tree_scroll_y.pack(side='right', fill='y')

    # ——— 窗口居中 ———

    def _center_window(self):
        self.root.update_idletasks()
        w, h = 900, 700
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    # ——— 浏览目录 ———

    def _browse_save_dir(self):
        d = filedialog.askdirectory(title='选择保存目录', initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _browse_parent_dir(self):
        d = filedialog.askdirectory(title='选择父文件夹（包含各漫画子文件夹）',
                                    initialdir=self.batch_parent_var.get() or
                                    os.path.join(os.path.expanduser('~'), 'Downloads'))
        if d:
            self.batch_parent_var.set(d)

    def _veto_tab_switch(self, event):
        """拦截标签页切换（运行时禁止）"""
        if self._tab_locked:
            self.notebook.select(self._last_tab)
        else:
            self._last_tab = self.notebook.index('current')

    # ——— 扫描子文件夹 ———

    def _scan_folder(self):
        """扫描父文件夹下的子文件夹，填充 Treeview"""
        parent_dir = self.batch_parent_var.get().strip()
        if not parent_dir:
            messagebox.showwarning('提示', '请先选择父文件夹')
            return

        # 扫描（在主线程，很快）
        self._batch_tasks = scan_folder_tasks(parent_dir)

        # 清空 Treeview
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)

        if not self._batch_tasks:
            messagebox.showinfo('扫描结果', '未找到可处理的子文件夹（或所有子文件夹名提取的关键词为空）')
            self.btn_start_batch.configure(state='disabled')
            return

        # 填充 Treeview
        for i, t in enumerate(self._batch_tasks):
            status_display = '✓ 已完成' if t['status'] == 'done' else '待处理'
            self.batch_tree.insert('', 'end', iid=str(i),
                                   values=(i + 1, t['keyword'], t['folder_name'], status_display))

        pending = sum(1 for t in self._batch_tasks if t['status'] != 'done')
        self.btn_start_batch.configure(state='normal' if pending > 0 else 'disabled')
        self.status_bar.configure(
            text=f'扫描完成：{len(self._batch_tasks)} 个子文件夹，{pending} 个待处理')

    # ——— Treeview 状态更新（线程安全） ———

    def _update_batch_row(self, idx, status_display):
        """由后台线程调用，通过 after_idle 安全更新 Treeview"""
        self.root.after_idle(lambda: self._do_update_batch_row(idx, status_display))

    def _do_update_batch_row(self, idx, status_display):
        iid = str(idx)
        if self.batch_tree.exists(iid):
            values = list(self.batch_tree.item(iid, 'values'))
            values[-1] = status_display
            self.batch_tree.item(iid, values=values)
            self.batch_tree.see(iid)  # 滚动到当前行

    # ——— 启动 / 停止 ———

    def _set_ui_running(self, running):
        """统一管理 UI 控件状态"""
        state = 'disabled' if running else 'normal'
        # 单漫画按钮
        self.btn_start_single.configure(state=state)
        self.btn_stop_single.configure(state='normal' if running else 'disabled')
        # 批量按钮
        self.btn_scan.configure(state=state)
        self.btn_start_batch.configure(state=state)
        self.btn_stop_batch.configure(state='normal' if running else 'disabled')
        # 禁止切换标签页（用变量 + 事件拦截实现）
        self._tab_locked = running
        if running:
            self._last_tab = self.notebook.index('current')
            self.notebook.bind('<<NotebookTabChanged>>', self._veto_tab_switch)
        else:
            self.notebook.unbind('<<NotebookTabChanged>>')
        # 状态栏
        self.status_bar.configure(text='运行中…' if running else '就绪')

    def _prepare_run(self):
        """运行前的通用准备：清空日志，重定向 stdout，设置状态"""
        if self.running:
            return False
        self.running = True
        self._done = False
        self._set_ui_running(True)

        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')

        self._old_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log_text)
        return True

    # 单漫画启动
    def _start_single(self):
        name = self.name_var.get().strip()
        save_dir = self.dir_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请输入漫画名称')
            return
        if not save_dir:
            messagebox.showwarning('提示', '请选择保存目录')
            return
        if not self._prepare_run():
            return

        global _stop_flag
        _stop_flag = False

        self._worker = threading.Thread(
            target=self._run_single_task,
            args=(name, save_dir),
            daemon=True,
        )
        self._worker.start()
        self.root.after(100, self._poll_worker)

    def _run_single_task(self, name, save_dir):
        try:
            main(name=name, save_dir=save_dir)
        except Exception as e:
            print(f'\n✗ 程序异常退出：{e}')
        finally:
            self.root.after_idle(self._on_done)

    # 批量启动
    def _start_batch(self):
        parent_dir = self.batch_parent_var.get().strip()
        if not parent_dir:
            messagebox.showwarning('提示', '请先选择父文件夹')
            return

        # 收集待处理任务
        pending = [t for t in self._batch_tasks if t['status'] != 'done']
        if not pending:
            messagebox.showinfo('提示', '所有子文件夹已完成下载')
            return

        if not self._prepare_run():
            return

        global _stop_flag, _batch_stop
        _stop_flag = False
        _batch_stop = False

        self._worker = threading.Thread(
            target=self._run_batch_task,
            args=(parent_dir, pending),
            daemon=True,
        )
        self._worker.start()
        self.root.after(100, self._poll_worker)

    def _run_batch_task(self, parent_dir, pending_tasks):
        """后台线程：逐个执行批量任务"""
        global _stop_flag, _batch_stop
        try:
            for i, t in enumerate(pending_tasks):
                if _batch_stop:
                    print('\n⚠ 用户停止批量任务')
                    # 剩余标记为 stopped
                    for rt in pending_tasks[i:]:
                        rt['status'] = 'stopped'
                        # 找到该任务在 _batch_tasks 中的索引
                        try:
                            idx = self._batch_tasks.index(rt)
                            self._update_batch_row(idx, '⏹ 已停止')
                        except ValueError:
                            pass
                    break

                # 找到在完整列表中的索引
                try:
                    idx = self._batch_tasks.index(t)
                except ValueError:
                    idx = i
                self._update_batch_row(idx, '⏳ 下载中…')
                print(f'\n{"=" * 60}')
                print(f'[{i + 1}/{len(pending_tasks)}] {t["keyword"]}')
                print(f'文件夹：{t["folder"]}')
                print(f'{"=" * 60}')

                _stop_flag = False

                try:
                    ok = main(name=t['keyword'], save_dir=t['folder'])
                except Exception as e:
                    print(f'✗ 任务异常：{e}')
                    t['status'] = 'failed'
                    t['error'] = str(e)
                    self._update_batch_row(idx, '✗ 失败')
                    continue

                if _stop_flag:
                    t['status'] = 'stopped'
                    self._update_batch_row(idx, '⏹ 已停止')
                else:
                    t['status'] = 'done'
                    self._update_batch_row(idx, '✓ 完成')

            # 汇总
            done_count = sum(1 for t in self._batch_tasks if t['status'] == 'done')
            fail_count = sum(1 for t in self._batch_tasks if t['status'] == 'failed')
            stop_count = sum(1 for t in self._batch_tasks if t['status'] == 'stopped')
            print(f'\n批量完成：{done_count} 成功  {fail_count} 失败  {stop_count} 停止')
            if fail_count or stop_count:
                failed = [t for t in self._batch_tasks if t['status'] in ('failed', 'stopped')]
                print('\n失败/停止清单：')
                for t in failed:
                    print(f'  ✗ {t["keyword"]}  ({t["status"]}{" — " + t["error"] if t.get("error") else ""})')

        except Exception as e:
            print(f'\n✗ 批量任务异常退出：{e}')
        finally:
            self.root.after_idle(self._on_done)

    def _stop(self):
        """停止当前任务（设置标志位，线程会在下一个检查点响应）"""
        global _stop_flag, _batch_stop
        if not self.running:
            return
        _stop_flag = True
        _batch_stop = True
        # 先更新按钮状态，让用户知道已接收停止请求
        self.btn_stop_single.configure(state='disabled')
        self.btn_stop_batch.configure(state='disabled')
        self.status_bar.configure(text='正在停止…（等待当前步骤完成）')

    def _on_done(self):
        """恢复 stdout，更新 UI（防多重调用）"""
        if self._done:
            return
        self._done = True

        if hasattr(self, '_old_stdout') and self._old_stdout:
            sys.stdout = self._old_stdout

        self.running = False
        self._set_ui_running(False)
        self.btn_start_single.configure(state='normal')
        self.btn_stop_single.configure(state='disabled')
        self.btn_scan.configure(state='normal')
        # 恢复批量按钮状态（取决于是否有扫描结果）
        pending = sum(1 for t in self._batch_tasks if t['status'] != 'done') if self._batch_tasks else 0
        self.btn_start_batch.configure(state='normal' if pending > 0 else 'disabled')
        self.btn_stop_batch.configure(state='disabled')

    def _poll_worker(self):
        """定期检查 worker 是否已结束（意外退出兜底）"""
        if self._worker and self._worker.is_alive():
            self.root.after(500, self._poll_worker)
        elif self.running:
            # 线程挂了但 _on_done 没跑 → 兜底
            self._on_done()

    def run(self):
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.running:
            if not messagebox.askyesno('确认退出',
                                       '下载任务还在运行，确定要退出吗？\n（可能留下不完整的文件）'):
                return
            global _stop_flag, _batch_stop
            _stop_flag = True
            _batch_stop = True
            self.running = False
        close_browser()
        self.root.destroy()


# ========================================================================
# 5. CLI 入口
# ========================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='wnacg 漫画下载器 — 支持 GUI / CLI / 批量三种模式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  python wnacg.py                             启动 GUI
  python wnacg.py --cli                        交互式 CLI 单漫画模式
  python wnacg.py --cli --name "漫画名" --save-dir ./dl   免交互 CLI
  python wnacg.py --batch "X:/path/to/parent"  CLI 批量模式
''')
    parser.add_argument('--cli', action='store_true',
                        help='CLI 单漫画模式（不加此参数默认启动 GUI）')
    parser.add_argument('--name', type=str, default=None,
                        help='漫画名称（配合 --cli 使用，跳过交互输入）')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='保存目录（配合 --cli 使用）')
    parser.add_argument('--batch', type=str, default=None, metavar='PARENT_DIR',
                        help='CLI 批量模式：扫描指定文件夹下的子文件夹并批量下载')
    args = parser.parse_args()

    if args.batch:
        # CLI 批量模式
        run_batch(args.batch)
        close_browser()
    elif args.cli:
        # CLI 单漫画模式
        main(name=args.name, save_dir=args.save_dir)
        close_browser()
    else:
        # 默认：GUI 模式
        app = WnacgGUI()
        app.run()
