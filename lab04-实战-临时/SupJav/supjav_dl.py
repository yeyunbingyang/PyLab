"""
SupJav 视频下载器 — 单文件版
===============================
用 DrissionPage 接管 Chrome 标签页，自动完成：
  1. 定位FST元素 //a[text()="FST"] 点击 到播放页
  2.在 supjav 页面中定位 iframe#video 播放器
  2. 点击 JW Player 播放按钮 -> 触发 m3u8 网络请求
  3. 监听网络请求捕获 m3u8 URL
  4. 调用 yt-dlp 下载视频

使用前提:
  1. 启动带调试端口的 Chrome:
     chrome.exe --remote-debugging-port=9333
  2. 在 Chrome 中手动打开 supjav 视频页面（过 Cloudflare 验证）
  3. pip install DrissionPage yt-dlp

用法:
  python supjav_dl.py                          # 交互模式
  python supjav_dl.py --url https://supjav.com/ja/431839.html
  python supjav_dl.py --url https://supjav.com/ja/431839.html -o ./videos
"""

import re
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from DrissionPage import Chromium


# ═══════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════

CHROME_PORT = 9222          # Chrome 调试端口
M3U8_TIMEOUT = 30           # m3u8 监听超时（秒）
SAVE_DIR = "./downloads"    # 默认保存目录


# ═══════════════════════════════════════════════════
# M3U8 捕获
# ═══════════════════════════════════════════════════

def capture_m3u8(browser: Chromium, page_url: str) -> Dict[str, dict]:
    """
    从 supjav 页面捕获 m3u8 视频流 URL

    页面结构:
      <iframe id="video" src="https://lk1.supremejav.com/supjav.php?...">
        内部 -> JW Player -> 点击播放后产生 m3u8 请求

    流程:
      1. 接管已打开的 supjav 标签页
      2. 启动网络监听
      3. 点击 iframe#video 内的 JW Player 播放按钮
      4. 收集 m3u8 请求
      5. 备选: JS 从 DOM 提取
    """
    tab = browser.latest_tab
    print(f"[标签页] {tab.url}")

    # ── 导航到目标页（如果当前不在） ──
    if page_url and page_url not in tab.url:
        print(f"[导航] {page_url}")
        tab.get(page_url)
        time.sleep(3)

    print(f"[当前] {tab.url}")

    # ── 步骤1: 启动网络监听（必须在触发播放之前！） ──
    print("[监听] 启动 m3u8 监听...")
    tab.listen.start(
        targets=r'\.m3u8',
        is_regex=True,
        res_type=['Media', 'XHR', 'Fetch', 'Other'],
    )

    # 点击FST按钮 xpath  //a[text()="FST"]
    print("[监听] 触发播放按钮...")
    tab.ele('xpath://a[text()="FST"]').click()

    # ── 步骤2: 点击 iframe#video 元素 ──
    _click_play(tab)

    # ── 步骤3: 收集 m3u8 请求 ──
    print(f"[监听] 等待 m3u8 请求（最多 {M3U8_TIMEOUT} 秒）...")
    results = _collect_m3u8(tab, timeout=M3U8_TIMEOUT)

    try:
        tab.listen.stop()
    except Exception:
        pass

    # ── 步骤4: 备选 — JS 提取 ──
    if not results:
        print("[备选] JS 提取...")
        results = _js_extract_m3u8(tab)

    return results


# ═══════════════════════════════════════════════════
# 点击播放按钮
# ═══════════════════════════════════════════════════

def _click_play(tab):
    """
    点击 id="video"元素

    """
    print("[播放] 点击 video")

    # DrissionPage 定位: video
    try:
        tab.ele('id:video').click()
        print("[播放] 点击成功")

        return
    except Exception as e:
        print(f"  点击失败: {e}")



# ═══════════════════════════════════════════════════
# 网络监听收集 m3u8
# ═══════════════════════════════════════════════════

def _collect_m3u8(tab, timeout: int = 30) -> Dict[str, dict]:
    """listen.steps() 逐包筛选 .m3u8 请求"""
    results = {}
    started = time.time()
    count = 0

    try:
        for packet in tab.listen.steps():
            count += 1
            if time.time() - started > timeout:
                print(f"  超时 ({timeout}s)，收到 {count} 个包")
                break

            url = packet.url
            if '.m3u8' not in url:
                continue

            key = _classify_m3u8(url)
            if key not in results:
                headers = {}
                try:
                    headers = dict(packet.request.headers)
                except Exception:
                    pass
                results[key] = {'url': url, 'headers': headers}
                print(f"  [OK] [{key}] {url[:120]}")

            if ('master' in results and len(results) >= 2) or len(results) >= 5:
                print("  已收集足够，提前结束")
                break
    except Exception as e:
        print(f"  异常: {e}")

    print(f"  共 {count} 包 -> {len(results)} 个 m3u8")
    return results


def _classify_m3u8(url: str) -> str:
    """根据 URL 判断画质"""
    u = url.lower()
    if 'master' in u:
        return 'master'
    for pat, label in [('-f4-', '4K'), ('-f3-', '1080p'), ('-f2-', '720p'), ('-f1-', '480p')]:
        if pat in u:
            return label
    m = re.search(r'[/_\-](\d{3,4})p?[/_\-\.]', u)
    if m:
        h = int(m.group(1))
        if h >= 2160: return '4K'
        if h >= 1440: return '2K'
        if h >= 1080: return '1080p'
        if h >= 720: return '720p'
        if h >= 480: return '480p'
    m2 = re.search(r'(\d{3,4})p\.m3u8', u)
    if m2:
        return f'{m2.group(1)}p'
    return f'stream_{abs(hash(url)) % 10000}'


# ═══════════════════════════════════════════════════
# JS 提取 m3u8（备选）
# ═══════════════════════════════════════════════════

def _js_extract_m3u8(tab) -> Dict[str, dict]:
    """从 DOM 中搜索 m3u8 URL"""
    results = {}

    # 1. <video>/<source> 标签
    try:
        url = tab.run_js("""
            (() => {
                const v = document.querySelector('video');
                if (v) {
                    if (v.src && v.src.includes('.m3u8')) return v.src;
                    if (v.currentSrc && v.currentSrc.includes('.m3u8')) return v.currentSrc;
                }
                for (const s of document.querySelectorAll('source')) {
                    if (s.src && s.src.includes('.m3u8')) return s.src;
                }
                return null;
            })()
        """)
        if url:
            results[_classify_m3u8(url)] = {'url': url, 'headers': {}}
            print(f"  JS(video): {url[:100]}")
    except Exception:
        pass

    # 2. <script> 标签
    try:
        urls_json = tab.run_js("""
            (() => {
                const found = [];
                for (const s of document.scripts) {
                    const t = s.textContent || s.innerHTML || '';
                    const m = t.match(/https?:\\/\\/[^"'\\s]+\\.m3u8[^"'\\s]*/g);
                    if (m) found.push(...m);
                }
                return JSON.stringify([...new Set(found)]);
            })()
        """)
        if urls_json:
            for url in json.loads(urls_json):
                key = _classify_m3u8(url)
                if key not in results:
                    results[key] = {'url': url, 'headers': {}}
                    print(f"  JS(script): {url[:100]}")
    except Exception:
        pass

    # 3. 整个 HTML 搜索
    if not results:
        try:
            url = tab.run_js("""
                (() => {
                    const m = document.documentElement.innerHTML.match(
                        /https?:\\/\\/[^"'\\s]+\\.m3u8[^"'\\s]*/
                    );
                    return m ? m[0] : null;
                })()
            """)
            if url:
                results[_classify_m3u8(url)] = {'url': url, 'headers': {}}
                print(f"  JS(html): {url[:100]}")
        except Exception:
            pass

    return results


# ═══════════════════════════════════════════════════
# yt-dlp 下载
# ═══════════════════════════════════════════════════

def download_video(m3u8_url: str, save_dir: str, referer: str = "",
                   quality: str = "best", headers: dict = None) -> bool:
    """用 yt-dlp 下载 m3u8 视频流"""
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = str(Path(save_dir) / f'video_{timestamp}.%(ext)s')

    cmd = [
        'yt-dlp', '--newline', '--no-check-certificates',
        '--merge-output-format', 'mp4',
        '-o', output_path,
    ]

    if referer:
        cmd += ['--referer', referer]

    # 基础 User-Agent
    cmd += ['--add-header',
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36']

    # 额外请求头（只添加安全的键，过滤掉可能损坏的 header）
    SAFE_HEADER_KEYS = {'origin', 'referer', 'accept', 'accept-language', 'cookie', 'x-requested-with'}
    if headers:
        for k, v in headers.items():
            if k.lower() in SAFE_HEADER_KEYS and v and isinstance(v, str):
                cmd += ['--add-header', f'{k}:{v}']

    if quality and quality != 'best':
        cmd += ['-f', quality]

    cmd += ['--', m3u8_url]

    print(f"\n[下载] yt-dlp {' '.join(cmd[1:6])}...")
    print(f"       输出: {output_path}")
    print(f"       Referer: {referer}")

    result = subprocess.run(cmd, timeout=3600)
    return result.returncode == 0


# ═══════════════════════════════════════════════════
# 工具
# ═══════════════════════════════════════════════════

def get_best_m3u8(captured: Dict[str, dict]) -> Optional[dict]:
    """返回最佳画质的 m3u8"""
    for key in ['1080p', '720p', '480p', 'master']:
        if key in captured:
            return captured[key]
    if captured:
        return list(captured.values())[0]
    return None


# ═══════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='SupJav 视频下载器')
    parser.add_argument('--url', '-u', type=str, help='supjav 视频页面 URL')
    parser.add_argument('--output', '-o', type=str, default=SAVE_DIR, help=f'保存目录（默认: {SAVE_DIR}）')
    parser.add_argument('--quality', '-q', type=str, default='best', help='画质：best / 1080p / 720p / 480p')
    parser.add_argument('--port', '-p', type=int, default=CHROME_PORT, help=f'Chrome 调试端口（默认: {CHROME_PORT}）')
    args = parser.parse_args()

    url = args.url
    if not url:
        url = input("请输入 supjav 视频页面 URL: ").strip()
    if not url:
        print("错误: 未提供 URL")
        sys.exit(1)

    print("=" * 60)
    print("  SupJav 视频下载器")
    print("=" * 60)
    print(f"  目标: {url}")
    print(f"  保存: {args.output}")
    print(f"  画质: {args.quality}")
    print()

    # ── 1. 连接 Chrome ──
    print("[连接] Chrome ...")
    browser = Chromium(args.port)
    print(f"  已连接 - {browser.tabs_count} 个标签页")

    # ── 2. 捕获 m3u8 ──
    captured = capture_m3u8(browser, url)

    if not captured:
        print("\n[失败] 未捕获到 m3u8 流。")
        print("  提示: 确保 Chrome 中页面已正常加载（非 Cloudflare 验证页）")
        sys.exit(1)

    print(f"\n[结果] 捕获到 {len(captured)} 个流:")
    for key, info in captured.items():
        print(f"  [{key}] {info['url'][:100]}")

    # ── 3. 下载 ──
    best = get_best_m3u8(captured)
    if not best:
        print("无法确定最佳画质")
        sys.exit(1)

    referer = browser.latest_tab.url
    success = download_video(
        m3u8_url=best['url'],
        save_dir=args.output,
        referer=referer,
        quality=args.quality,
        headers=best.get('headers', {}),
    )

    if success:
        print(f"\n[OK] 下载完成 -> {args.output}")
    else:
        print(f"\n[FAIL] 下载失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
