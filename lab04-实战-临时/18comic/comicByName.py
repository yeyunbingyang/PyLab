"""
18comic.vip 漫画下载器 — 单线程浏览器自动化版

============================================================
业务核心逻辑（务必先读此注释，避免误改）
============================================================

一、下载流程
  搜索 → 获取章节 → 逐章处理
  每章：
  triggerpop 【点击获取验证码元素】【会有广告页标签】
  →
  关广告【记录下载页 关掉多余广告】
    →
  OCR验证码 【去除广告后就是下载页 直接进行元素获取处理即可】
  →
  提交
  【验证码正确浏览器会下载文件 进行接管事件 指定文件名 下载位置就行】
  【无事件 进行无限重试 直到有下载事件【验证码正确】】
  →
  等待文件 【对于接管的事件需要验证是否下载成功 修改状态JSON】

二、验证码机制
  1. 点击 <a class="triggerpop"> 弹出验证码弹窗（同时弹出广告页）
  2. 关闭广告标签，只保留下载页标签
  3. 验证码图片 <img src="/captcha">
  4. OCR 识别两个数字加法：a+b=？
  5. 填入 <input id="invite_verification">
  6. 点击 <button id="download_submit">

三、⭐ 下载事件（关键约束）
  - 只有验证码正确 、点击提交后 → 浏览器触发 download 事件
  有事件 验证码正确 进行接管处理下载即可
  无事件 验证码错误 重试【死循环一直等待 出现事件】

四、文件处理
  浏览器下载到 SAVE_DIR，文件名不确定（可能是 UUID 或无扩展名）
  监测目录中新文件：.zip → _zip_intact 校验 → 重命名为 {专辑}_{章节}.zip
  无扩展名大文件(>512KB) → 尝试加 .zip 后缀 → 校验

五、标签页管理
  - 进入下载页记录 dl_tid = page.tab_id
  - triggerpop 后可能有广告新标签
  - 规则：只保留 tid == dl_tid 的标签，其他全关
  - 不依赖 URL 匹配（URL 可能因 Cloudflare/广告跳转而变化）

六、超时重试
  - OCR失败：不刷新，直接下一轮（验证码还在）
  - 提交后无.crdownload：验证码错误 → refresh → 重新 triggerpop → OCR识别重新输入


七、OCR 策略
  v1: R+G+B<50 纯黑像素检测（→ 白字黑底）
  v2: 灰度反色 → 多阈值二值化
  v3: 灰度低阈值（数字是深色前景）
"""
from urllib.parse import quote
import os, re, time, json, zipfile, random
from DrissionPage import ChromiumPage

BASE = 'https://18comic.vip'
DEFAULT_SAVE_DIR = './downloads'
SAVE_DIR = None
STATE_FILE = None
DOWNLOAD_TIMEOUT = 120

page: ChromiumPage = None


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: print('⚠ 状态文件损坏，重新开始')
    return {}

def save_state(state):
    tmp = STATE_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)

def clean_title(s):
    s = re.sub(r'<[^>]+>', '', s or '').strip()
    if not s: return 'untitled'
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']: s = s.replace(ch, '_')
    return s

def _zip_intact(path):
    try:
        if not zipfile.is_zipfile(path): return False
        with zipfile.ZipFile(path) as zf: return zf.testzip() is None
    except: return False

def _safe_remove(path):
    try:
        if path and os.path.exists(path): os.remove(path)
    except: pass

def _thumbprint(path):
    try:
        st = os.stat(path); return (st.st_size, int(st.st_mtime))
    except: return None

def js_click(selector):
    try: page.run_js(f'document.querySelector({json.dumps(selector)})?.click()')
    except: pass

def dismiss_age():
    try:
        page.run_js('document.querySelector("button#chk_cover")?.click()')
        time.sleep(0.8)
        page.run_js('document.querySelector("button#chk_guide")?.click()')
        time.sleep(0.5)
    except: pass

def search_album(keyword):
    url = f'{BASE}/search/photos?main_tag=0&search_query={quote(keyword)}'
    for retry in range(3):
        page.get(url); time.sleep(2); dismiss_age()
        try:
            page.wait.eles_loaded('xpath://div[contains(@class,"thumb-overlay")]', timeout=15)
        except:
            pass
        overlays = page.eles('xpath://div[contains(@class,"thumb-overlay")]')
        if not overlays:
            print(f'⚠ 搜索结果为空，第 {retry+1} 次重试...')
            time.sleep(2)
            continue
        for overlay in overlays[:5]:
            a = overlay.ele('xpath:.//a', timeout=1); img = overlay.ele('xpath:.//img', timeout=1)
            if not a: continue
            href = a.attr('href') or ''
            raw_title = (img.attr('title') or '') if img else ''
            if not raw_title: raw_title = a.attr('title') or a.text or ''
            title = raw_title.split('/')[0].strip() if '/' in raw_title else raw_title.strip()
            if not title: continue
            m = re.search(r'/album/(\d+)', href)
            if m: return (m.group(1), title, f'{BASE}/album/{m.group(1)}')
        print(f'⚠ 未能从搜索结果中解析出专辑信息，第 {retry+1} 次重试...')
        time.sleep(2)
    print('✗ 搜索失败，请确认关键词或检查网络')
    return None

def get_chapters(album_url):
    page.get(album_url); time.sleep(2); dismiss_age()
    try: page.wait.eles_loaded('xpath://div[contains(@class,"btn-group")]//ul[contains(@class,"dropdown-menu")]', timeout=10)
    except: print('⚠ 未找到章节下拉菜单'); return []
    links = page.eles('xpath://div[contains(@class,"btn-group")]//ul[contains(@class,"dropdown-menu")]//li//a[contains(@href,"album_download")]')
    chapters = []
    for a in links:
        href = a.attr('href') or ''; text = (a.text or '').strip()
        if href and text: chapters.append((text, href))
    seen = set(); unique = []
    for t, u in chapters:
        if u not in seen: seen.add(u); unique.append((t, u))
    return unique


def process_chapter(chapter_title, download_page_url, album_title):
    """
    处理单章：循环（triggerpop → 关广告 → OCR → 提交 → 监听下载事件）
    有 download 事件 → 验证码正确 → 接管下载 → 校验 ZIP
    无 download 事件 → 验证码错误 → 无限重试
    """
    file_name = f'{clean_title(album_title)}_{clean_title(chapter_title)}.zip'
    full_path = os.path.abspath(SAVE_DIR)
    target_path = os.path.join(full_path, file_name)

    page.get(download_page_url)
    time.sleep(1)
    dismiss_age()
    dl_tid = page.tab_id

    # ① triggerpop + 关广告（只做一次，OCR不刷新）
    print(f'        [1/4] 点击triggerpop...')
    js_click('a.triggerpop')
    time.sleep(1)
    print(f'        [2/4] 标签 {page.tabs_count}个，清理非下载页...')
    for tid in list(page.tab_ids):
        if tid != dl_tid:
            try: page.close_tabs(tid)
            except: pass
    page.activate_tab(dl_tid)

    ocr_fail_count = 0
    while True:
        # ③ OCR（验证码还在，不重新triggerpop）
        print(f'        [3/4] 获取验证码（连续失败{ocr_fail_count}次）...')
        captcha_img = None
        try:
            captcha_img = page.ele('xpath://img[contains(@src,"captcha")]', timeout=1)
        except: pass

        if not captcha_img:
            print(f'        → ⚠ 无验证码元素，refresh')
            page.refresh(); time.sleep(2); dismiss_age()
            js_click('a.triggerpop'); time.sleep(1)
            for tid in list(page.tab_ids):
                if tid != dl_tid:
                    try: page.close_tabs(tid)
                    except: pass
            page.activate_tab(dl_tid)
            ocr_fail_count = 0
            continue

        captcha_ans = _ocr_captcha(captcha_img)

        if not captcha_ans:
            ocr_fail_count += 1
            if ocr_fail_count >= 10:
                print(f'        → ⚠ OCR连续10次失败，可能验证码过期，refresh')
                page.refresh(); time.sleep(2); dismiss_age()
                js_click('a.triggerpop'); time.sleep(1)
                for tid in list(page.tab_ids):
                    if tid != dl_tid:
                        try: page.close_tabs(tid)
                        except: pass
                page.activate_tab(dl_tid)
                ocr_fail_count = 0
            continue

        # ④ 填验证码
        print(f'        [4/4] 提交...  答案: {captcha_ans}')
        el = page.ele('#invite_verification')
        if el: el.input(str(captcha_ans), clear=True)
        else: page.run_js(f'document.getElementById("invite_verification").value="{captcha_ans}"')

        page.set.download_path(full_path)
        page.set.when_download_file_exists('overwrite')
        before = set(os.listdir(full_path))

        page.run_js('document.getElementById("download_submit")?.click()')
        print(f'        → ✅ 提交')

        # ⑤ download_begin? → 验证码正确 → 等下载完成
        try:
            page.wait.download_begin(timeout=5)
            print(f'        📥 download_begin → 验证码正确')
            page.wait.all_downloads_done(timeout=60)
            print(f'        ✅ 所有下载完成')
        except:
            print(f'        → ⏭ 下载失败')
            page.refresh(); time.sleep(2); dismiss_age()
            js_click('a.triggerpop'); time.sleep(1)
            for tid in list(page.tab_ids):
                if tid != dl_tid:
                    try: page.close_tabs(tid)
                    except: pass
            page.activate_tab(dl_tid)
            continue

        # 找出最新的 zip 文件（刚下载的）
        newest = None
        for fname in os.listdir(full_path):
            if fname.endswith('.crdownload'): continue
            fp = os.path.join(full_path, fname)
            if fname.endswith('.zip') and _zip_intact(fp):
                mtime = os.path.getmtime(fp)
                if newest is None or mtime > newest[1]:
                    newest = (fp, mtime)

        if newest:
            src_path = newest[0]
            if os.path.basename(src_path) != file_name:
                if os.path.exists(target_path):
                    os.remove(target_path)
                try: os.rename(src_path, target_path)
                except:
                    import shutil
                    shutil.move(src_path, target_path)
            print(f'      ✅ {file_name}')
            return target_path

        print(f'        → 文件未找到，刷新重试')
        page.refresh(); time.sleep(2); dismiss_age()
        js_click('a.triggerpop'); time.sleep(1)
        for tid in list(page.tab_ids):
            if tid != dl_tid:
                try: page.close_tabs(tid)
                except: pass
        page.activate_tab(dl_tid)


def _ocr_captcha(captcha_img_el):
    """
    验证码识别：JS canvas 截图 → 多策略 Tesseract → 正则提取 a+b
    """
    try:
        from PIL import Image, ImageOps, ImageFilter
        import pytesseract
        import re, io, base64

        tess_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tess_cmd): pytesseract.pytesseract.tesseract_cmd = tess_cmd

        # —— ① JS canvas 截图 ——
        b64 = page.run_js('''
            var c = document.createElement("canvas");
            var img = document.querySelector("img[src*='captcha']");
            if (!img) return "";
            c.width = img.naturalWidth;
            c.height = img.naturalHeight;
            var ctx = c.getContext("2d");
            ctx.drawImage(img, 0, 0);
            return c.toDataURL("image/png").split(",")[1];
        ''')
        if not b64:
            captcha_img_el.get_screenshot('captcha_image.png')
            orig = Image.open('captcha_image.png')
        else:
            raw = base64.b64decode(b64)
            orig = Image.open(io.BytesIO(raw))

        # 统一灰度
        gray = orig.convert('L')

        # 尝试多阈值组合
        recipes = []

        # 反色 + 二值化（白字黑底）
        inv = ImageOps.invert(gray)
        for thr in (50, 80, 100, 120, 140):
            img = inv.point(lambda x: 0 if x < (255 - thr) else 255)
            recipes.append((f'inv{thr}', img))

        # 灰度低阈值（深色前景）
        for thr in (30, 50, 80, 100, 120):
            img = gray.point(lambda x: 255 if x < thr else 0)
            recipes.append((f'gray{thr}', img))

        # 纯黑检测
        if orig.mode == 'RGB':
            binary = Image.new('L', (orig.width, orig.height))
            for y in range(orig.height):
                for x in range(orig.width):
                    rv, gv, bv = orig.getpixel((x, y))
                    binary.putpixel((x, y), 255 if rv + gv + bv < 50 else 0)
            recipes.append(('rgb', binary))

        # 先用中值滤波去噪再处理
        denoised = gray.filter(ImageFilter.MedianFilter(3))
        for thr in (80, 100, 120):
            img = ImageOps.invert(denoised).point(lambda x: 0 if x < (255 - thr) else 255)
            recipes.append((f'denoised{thr}', img))

        # 放大后 OCR（统一5倍）
        def ocr_img(img):
            img = img.resize((img.width * 5, img.height * 5), Image.LANCZOS)
            for cfg in [
                '--psm 7 -c tessedit_char_whitelist=0123456789+=',
                '--psm 8 -c tessedit_char_whitelist=0123456789+=',
                '--psm 6 -c tessedit_char_whitelist=0123456789+=',
            ]:
                text = pytesseract.image_to_string(img, config=cfg).strip()
                text = text.replace(' ', '').replace('\n', '').replace('\x0c', '')
                # 直接匹配加法表达式 a+b
                m = re.search(r'(\d{1,2})\s*\+\s*(\d{1,2})', text)
                if m:
                    a, b = int(m.group(1)), int(m.group(2))
                    return a, b
                # 兜底：找两个数字
                nums = re.findall(r'\d+', text)
                if len(nums) >= 2:
                    a, b = int(nums[-2]), int(nums[-1])
                    if a < 100 and b < 100:
                        return a, b
            return None, None

        for name, v in recipes:
            a, b = ocr_img(v)
            if a is not None:
                print(f'    ✅ OCR[{name}]: {a}+{b}={a+b}')
                return str(a + b)

        # 最终兜底：放大后宽松模式
        for name, v in recipes:
            img = v.resize((v.width * 5, v.height * 5), Image.LANCZOS)
            text = pytesseract.image_to_string(img, config='--psm 7').strip()
            nums = re.findall(r'\d+', text.replace(' ', ''))
            if len(nums) >= 2:
                a, b = int(nums[-2]), int(nums[-1])
                print(f'    ✅ OCR宽松[{name}]: {a}+{b}={a+b}')
                return str(a + b)

        return None
    except Exception as e:
        print(f'    ✗ OCR异常: {e}')
        return None


def main(name=None, save_dir=None):
    global SAVE_DIR, STATE_FILE, page

    print('=' * 50)
    print('18comic.vip 漫画下载器')
    print('=' * 50)

    name = (name or input('漫画名称（回车默认"继母的朋友们"）：').strip()) or '继母的朋友们'
    save_dir = save_dir or input('保存目录（回车默认 ./downloads）：').strip() or DEFAULT_SAVE_DIR
    SAVE_DIR = save_dir
    STATE_FILE = os.path.join(SAVE_DIR, 'state.json')
    os.makedirs(SAVE_DIR, exist_ok=True)

    if page is None:
        print('\n🔄 连接浏览器...')
        page = ChromiumPage(9333)
        print('✅ 连接成功')

    state = load_state()
    # 启动时校验：done 但文件不存在的 → 改回 pending 重新下载
    for k, v in state.items():
        if v.get('status') == 'done':
            sp = v.get('save_path', '')
            if not sp or not os.path.exists(sp):
                v['status'] = 'pending'
                v['error'] = '文件不存在，重新下载'
    done_cnt = sum(1 for v in state.values() if v.get('status') == 'done')
    print(f'\n已下载: {len(state)} 条（其中 done {done_cnt} 条）')

    # 搜索
    print(f'\n🔍 搜索: {name}')
    album = search_album(name)
    if not album: print('✗ 未找到专辑'); return
    album_id, album_title, album_url = album
    print(f'✅ {album_title} (ID: {album_id})')

    # 章节
    print(f'\n📖 获取章节...')
    chapters = get_chapters(album_url)
    if not chapters: print('✗ 未找到章节'); return
    print(f'✅ 共 {len(chapters)} 章')

    # 逐章处理
    print(f'\n⬇️  逐章处理：OCR验证码 → 监听下载事件...')
    for idx, (ch_title, ch_url) in enumerate(chapters, start=1):
        key = ch_url
        rec = state.get(key, {})
        save_path = rec.get('save_path', '')

        if rec.get('status') == 'done' and save_path and os.path.exists(save_path):
            if _zip_intact(save_path):
                print(f'  [{idx}/{len(chapters)}] {ch_title} ✓')
                continue
            rec['status'] = 'pending'

        print(f'  [{idx}/{len(chapters)}] {ch_title} ...')
        save_path = process_chapter(ch_title, ch_url, album_title)

        status = 'done' if save_path else 'failed'
        state[key] = {
            'chapter_title': ch_title, 'chapter_url': ch_url,
            'save_path': save_path or '', 'status': status,
            'error': None if save_path else '下载失败',
        }
        if save_path:
            tp = _thumbprint(save_path)
            if tp: state[key]['verified_size'], state[key]['verified_mtime'] = tp
        print(f'    → {"✅" if save_path else "✗"}')
        save_state(state)

    # 汇总
    failed = [v for v in state.values() if v['status'] == 'failed']
    if failed:
        print(f'\n===== 失败 {len(failed)} 个 =====')
        for v in failed: print(f'  ✗ {v.get("chapter_title","?")}  ({v.get("error","")})')
    counts = {}
    for v in state.values(): counts[v['status']] = counts.get(v['status'], 0) + 1
    print(f'\n完成: {counts}')


if __name__ == '__main__':
    main()
