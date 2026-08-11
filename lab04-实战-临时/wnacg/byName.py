"""
依据漫画名称爬取下载链接 并下载
【韩漫】 https://www.wnacg.com/albums-favorite_ranking-type-week-cate-19.html
搜索页： https://www.wnacg.com/search/?q=<关键词>&f=_all&s=create_time_DESC&syn=yes

架构（两阶段 + 状态文件）：
  ① 抓取阶段（单线程，用真实浏览器过 Cloudflare）：
     搜索 → 翻页 → 进详情页/下载页 取真实 .zip 链接 → 写入 state.json（status=pending）
  ② 下载阶段（多线程 requests + 全局节流 + 429 长退避）：
     只下载 status=pending 且本地无有效文件的条目；
     下载完做大小校验 + zip 完整性校验；成功标 done、失败标 failed；
     一轮结束后打印失败清单，对 failed 再重试若干轮。
  state.json 既做断点续传，也做去重（有效已下载文件不重复抓/不重复下）。
"""
from urllib.parse import quote
import os
import re
import time
import json
import zipfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from DrissionPage import Chromium

BASE = 'https://www.wnacg.com'

# ===== 默认配置（GUI 调用时通过 main(name, save_dir) 覆盖） =====
DEFAULT_SAVE_DIR = './downloads'
SAVE_DIR = None            # 由 main() 设置
STATE_FILE = None          # 由 main() 设置
MAX_WORKERS = 2            # 下载并发数
MIN_REQUEST_INTERVAL = 3  # 全局节流：发起新下载请求的最小间隔（秒）
RETRY_ROUNDS = 2          # 一轮下载后，对失败项再重试的轮数

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0 Safari/537.36'),
    'Referer': 'https://www.wnacg.com/',
}

_state_lock = threading.Lock()    # 多线程读写 state 时加锁
_rate_lock = threading.Lock()     # 全局节流锁
_last_request = [0.0]             # 上一次发起下载请求的时间（monotonic）


# ==================== 状态文件 ====================
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


# ==================== 浏览器（过 Cloudflare 用） ====================
# 在 main() 中按需创建，避免 import 即连浏览器
browser = None
tab = None


# ==================== 工具函数 ====================
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


# ==================== 抓取阶段 ====================
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
    search_url = f'{BASE}/search/?q={quote(name)}&f=_all&s=create_time_DESC&syn=yes'
    tab.get(search_url)
    tab.wait.eles_loaded('xpath://li[contains(@class,"gallary_item")]', timeout=15)

    page_urls = get_page_urls(tab)
    all_pages = [search_url] + page_urls if page_urls else [search_url]
    print(f'共 {len(all_pages)} 页，开始抓取画廊列表...')

    seen, galleries = set(), []  #  去重
    for i, url in enumerate(all_pages, start=1):
        if i > 1:
            tab.get(url)
            tab.wait.eles_loaded('xpath://li[contains(@class,"gallary_item")]', timeout=15)  # 等待加载
            time.sleep(1)
        for title, gurl in parse_gallery_links(tab):
            if gurl not in seen:
                seen.add(gurl)
                galleries.append((title, gurl))
        print(f'  第 {i} 页：累计 {len(galleries)} 条')
    return galleries


# ==================== 下载阶段 ====================
def download_file(url, save_path, max_retries=3, max_429=6):
    """
    流式下载单个文件：
      - 发起前 _throttle() 全局节流
      - 429：读 Retry-After / 默认 20s 长退避，单独计数（max_429），不消耗普通重试
      - 下完做大小校验（Content-Length）+ zip 完整性校验
      - 失败删残文件，普通异常按 3s/6s/9s 退避重试
    """
    clean_url = url.split('?')[0]
    last_err = None
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
            # D：大小校验
            if expected:
                actual = os.path.getsize(save_path)
                if int(expected) != actual:
                    raise IOError(f'大小不符：预期 {expected} 实际 {actual}')
            # E：zip 完整性校验
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
    # 下载成功（download_file 内已做 testzip），回填完整性缓存，后续启动可跳过 testzip
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


# ==================== 主流程 ====================
def main(name=None, save_dir=None):
    """入口函数。
    Args:
        name:    漫画名称。None 则弹出 input() 交互输入。
        save_dir:保存目录。None 则弹出 input() 交互输入。
    """
    global SAVE_DIR, STATE_FILE, browser, tab
    name = (name or input('漫画名称（回车默认"獵艷管理員"）：').strip()) or '獵艷管理員'
    save_dir = save_dir or input('保存目录（回车默认 ./downloads）：').strip() or DEFAULT_SAVE_DIR
    SAVE_DIR = save_dir
    STATE_FILE = os.path.join(SAVE_DIR, 'state.json')
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 按需初始化浏览器
    if browser is None:
        browser = Chromium(9333)
        tab = browser.latest_tab

    state = load_state()
    done_cnt = sum(1 for v in state.values() if v.get('status') == 'done')
    print(f'\n已有状态：{len(state)} 条（其中 done {done_cnt} 条）')

    # ---- ① 抓取阶段：合并画廊列表，对未完成条目抓下载链接 ----
    galleries = scrape_galleries(tab, name)
    print(f'\n抓到 {len(galleries)} 个画廊，开始提取下载链接...')

    for idx, (title, gurl) in enumerate(galleries, start=1):
        rec = state.get(gurl)
        # 已完成且本地文件有效 → 跳过，不重复抓
        if rec and rec.get('status') == 'done' and file_is_valid(rec.get('save_path'), rec):
            continue
        # 其余（新条目 / pending / failed / done但文件损坏）→ (重新)抓下载链接
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

    # ---- ② 下载阶段：先校正状态，再多线程下载 + 失败重试 ----
    # 校正：本地有效文件→done；done 但文件损坏/丢失→pending 重下
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
        # 下一轮重试：置回 pending
        todo = [state[k] for k in failed_keys]
        for k in failed_keys:
            state[k]['status'] = 'pending'
        save_state(state)
        if round_i <= RETRY_ROUNDS:
            time.sleep(5)   # 轮间喘息

    # ---- 汇总 ----
    failed_items = [v for v in state.values() if v['status'] == 'failed']
    if failed_items:
        print(f'\n===== 最终失败清单（{len(failed_items)} 个）====')
        for v in failed_items:
            print(f'  ✗ {v["title"]}  ({v.get("error")})')
    counts = {}
    for v in state.values():
        counts[v['status']] = counts.get(v['status'], 0) + 1
    print(f'\n全部完成。状态统计：{counts}')


if __name__ == '__main__':
    main()
