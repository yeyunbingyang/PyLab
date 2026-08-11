"""
M3U8 捕获服务 — DrissionPage 实现
从 supjav 页面自动跳转到 fc2stream 并捕获 m3u8 视频流

核心流程:
  1. 接管 Chrome 标签页 → 导航到 supjav 页面
  2. 定位并点击播放源按钮（优先 FST/fc2stream）
  3. 播放页中点击 JW Player 播放按钮 → 触发 m3u8 网络请求
  4. 通过 listen.steps() 捕获 m3u8 URL
  5. 备选方案: JS 从 DOM/script 提取 m3u8
"""

import re
import time
from typing import Dict, List, Optional, Callable

from DrissionPage import Chromium


class M3U8CaptureService:
    """M3U8 流捕获服务 — 支持 supjav + fc2stream"""

    def __init__(self, browser_port: int = 9333):
        self.browser_port = browser_port
        self.browser: Optional[Chromium] = None
        self.tab = None
        self.captured: Dict[str, dict] = {}
        self.page_url: str = ""
        self.referer: str = ""
        self._log_cb: Optional[Callable] = None

    # ══════════════════════════════════════════════
    # 公开 API
    # ══════════════════════════════════════════════

    def set_log_callback(self, cb: Callable[[str], None]):
        self._log_cb = cb

    def _log(self, msg: str):
        if self._log_cb:
            self._log_cb(msg)
        else:
            print(f"  [{msg}]")

    def capture(self, page_url: str, use_current_tab: bool = True) -> Dict[str, dict]:
        """
        主流程:
          接管标签页 → 点击播放源 → 切到播放页 → 监听 m3u8 → JS提取(备选)
        """
        self.page_url = page_url
        self.captured = {}

        self._log("正在连接浏览器...")
        self.browser = Chromium(self.browser_port)

        if use_current_tab:
            self.tab = self.browser.latest_tab
            self._log(f"接管当前标签页: {self.tab.url}")
            if page_url and page_url not in self.tab.url:
                self._log(f"导航到目标页: {page_url}")
                self.tab.get(page_url)
                time.sleep(3)
        else:
            self.tab = self.browser.new_tab()
            self.tab.set.window.size(1920, 1080)
            self._log(f"打开页面: {page_url}")
            self.tab.get(page_url)
            time.sleep(3)

        # 1. supjav 页面 → 尝试点击播放源按钮
        if 'supjav' in self.tab.url.lower():
            self._click_fst_button()
            time.sleep(2)
        elif 'fc2stream' in self.tab.url.lower():
            self._log("已在 fc2stream 页面")
        else:
            self._log(f"当前页面: {self.tab.url}，尝试直接处理")

        # 2. 切到播放页标签（如果打开了新标签页）
        self._switch_to_media_tab()
        time.sleep(1)

        current_url = self.tab.url
        self._log(f"当前页面: {current_url}")
        self.referer = current_url

        # 3. 启动网络监听
        self._log("启动网络监听...")
        self.tab.listen.start(
            targets=r'\.m3u8',
            is_regex=True,
            res_type=['Media', 'XHR', 'Fetch', 'Other'],
        )

        # 4. 点击 iframe#video 中的 JW Player 播放按钮
        self._trigger_playback()

        # 5. 收集 m3u8
        self._log("等待 m3u8 请求（最多30秒）...")
        collected = self._collect_m3u8_requests(timeout=30)
        self._log(f"方案A（网络监听）: 收集到 {len(collected)} 个 m3u8")

        # 6. 备选方案: JS 提取
        if not collected:
            self._log("方案A未捕获到，尝试方案B（JS提取）...")
            collected = self._js_extract_m3u8()
            self._log(f"方案B（JS提取）: 收集到 {len(collected)} 个 m3u8")

        self.captured = collected
        return collected

    def get_available_formats(self) -> List[dict]:
        """从已捕获的 m3u8 列表生成画质选项"""
        formats = []
        priority = ['1080p', '720p', '480p', 'master']
        labels = {
            '1080p': '1080p (全高清)',
            '720p': '720p (高清)',
            '480p': '480p (标清)',
            'master': 'master (多路流)',
        }
        for key in priority:
            if key in self.captured:
                formats.append({
                    'quality': key,
                    'url': self.captured[key]['url'],
                    'label': labels.get(key, key),
                    'headers': self.captured[key].get('headers', {}),
                })
        for key, info in self.captured.items():
            if key not in priority:
                formats.append({
                    'quality': key,
                    'url': info['url'],
                    'label': f'{key} (其他)',
                    'headers': info.get('headers', {}),
                })
        if len(formats) > 1:
            formats.insert(0, {
                'quality': 'best',
                'url': formats[0]['url'],
                'label': '最佳画质 (自动)',
                'headers': formats[0].get('headers', {}),
            })
        return formats

    def get_best_url(self) -> Optional[str]:
        """获取最佳画质的 m3u8 URL"""
        for key in ['1080p', '720p', '480p', 'master']:
            if key in self.captured:
                return self.captured[key]['url']
        if self.captured:
            return list(self.captured.values())[0]['url']
        return None

    def cleanup(self):
        self._log("已断开浏览器连接")

    # ══════════════════════════════════════════════
    # 播放源按钮点击 & 触发播放
    # ══════════════════════════════════════════════

    def _click_fst_button(self):
        """
        supjav 页面 → 定位并点击播放源按钮
        优先 fc2stream/FST，其次其他外部链接
        """
        self._log("查找播放源按钮...")

        # 优先级: fc2stream > turboviplay > voe > 其他
        for kw in ['fc2stream', 'fc2', 'turboviplay', 'turbovid', 'voe.sx', 'streamtape', 'dood']:
            try:
                el = self.tab.ele(f'css:a[href*="{kw}"]', timeout=1)
                if el:
                    self._log(f"✓ 找到: {(el.text or '').strip()} → {(el.attr('href') or '')[:100]}")
                    el.click()
                    time.sleep(3)
                    self._switch_to_media_tab()
                    return
            except Exception:
                continue

        # 兜底: target="_blank" 的外部链接
        try:
            for a in (self.tab.eles('css:a[target="_blank"]') or []):
                href = (a.attr('href') or '').lower()
                if href and 'supjav' not in href:
                    self._log(f"兜底点击: {(a.text or '').strip()} → {href[:100]}")
                    a.click()
                    time.sleep(3)
                    self._switch_to_media_tab()
                    return
        except Exception:
            pass

        self._log("未找到播放源按钮，跳过（可能页面已有内嵌播放器）")

    def _switch_to_media_tab(self):
        """切换到播放页标签页"""
        try:
            for t in self.browser.get_tabs():
                url = (t.url or '').lower()
                if any(k in url for k in ['fc2stream', 'turboviplay', 'player', 'embed']):
                    if t.tab_id != self.tab.tab_id:
                        self._log(f"切换到: {t.url[:80]}")
                        self.tab = t
                        time.sleep(2)
                        return
        except Exception:
            pass

    def _trigger_playback(self):
        """
        触发视频播放 → 产生 m3u8 网络请求
        1. 在 iframe#video 中点击 JW Player 播放按钮
        2. 兜底: JS video.play()
        """
        self._log("触发播放...")

        # 在 iframe 中点击 JW Player 播放按钮
        try:
            iframe = self.tab.get_frame('css:#video')
            btn = iframe.ele('css:div.jw-icon-display', timeout=2)
            btn.click()
            self._log("✓ 点击播放按钮 (iframe#video .jw-icon-display)")
            return
        except Exception as e:
            self._log(f"iframe 内点击失败: {e}")

        # 兜底: 页面级查找
        try:
            btn = self.tab.ele('css:div.jw-icon-display', timeout=2)
            if btn:
                btn.click()
                self._log("✓ 点击播放按钮 (页面级 .jw-icon-display)")
                return
        except Exception:
            pass

        # 最后: JS video.play()
        try:
            self.tab.run_js('document.querySelector("video")?.play()')
            self._log("✓ JS video.play()")
        except Exception:
            self._log("未找到播放按钮，等待页面自动触发...")

    # ══════════════════════════════════════════════
    # M3U8 收集 — 方案A: 网络监听
    # ══════════════════════════════════════════════

    def _collect_m3u8_requests(self, timeout: int = 30) -> Dict[str, dict]:
        """使用 listen.steps() 迭代器收集 m3u8 请求"""
        results = {}
        start_time = time.time()
        packet_count = 0
        non_m3u8_logged = set()

        try:
            for packet in self.tab.listen.steps():
                packet_count += 1
                if time.time() - start_time > timeout:
                    self._log(f"监听超时 ({timeout}s)，共收到 {packet_count} 个数据包")
                    break

                url = packet.url
                if '.m3u8' not in url:
                    domain = url.split('/')[2] if '/' in url else url[:50]
                    if domain and domain not in non_m3u8_logged and len(non_m3u8_logged) < 10:
                        non_m3u8_logged.add(domain)
                        self._log(f"  [调试] 非m3u8: {domain}")
                    continue

                key = self._classify_m3u8(url)
                if key not in results:
                    headers = {}
                    try:
                        headers = dict(packet.request.headers)
                    except Exception:
                        pass
                    results[key] = {'url': url, 'headers': headers}
                    self._log(f"  捕获: [{key}] {url[:100]}")

                if 'master' in results and len(results) >= 2:
                    self._log("已捕获足够流，提前结束监听")
                    break
                if len(results) >= 5:
                    break

        except Exception as e:
            self._log(f"监听异常: {e}")
            import traceback
            self._log(f"  {traceback.format_exc()}")

        try:
            self.tab.listen.stop()
        except Exception:
            pass

        self._log(f"监听结束: 共 {packet_count} 个请求包，捕获 {len(results)} 个 m3u8")
        return results

    # ══════════════════════════════════════════════
    # M3U8 收集 — 方案B: JS 提取
    # ══════════════════════════════════════════════

    def _js_extract_m3u8(self) -> Dict[str, dict]:
        """备选方案: 通过 JS 从 DOM 中提取 m3u8 URL"""
        results = {}

        # 1. video/source 标签
        try:
            url = self.tab.run_js("""
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
                key = self._classify_m3u8(url)
                results[key] = {'url': url, 'headers': {}}
                self._log(f"  JS(video): {url[:100]}")
        except Exception as e:
            self._log(f"  JS(video) 失败: {e}")

        # 2. script 标签文本
        try:
            import json
            urls_json = self.tab.run_js("""
                (() => {
                    const found = [];
                    for (const s of document.scripts) {
                        const text = s.textContent || s.innerHTML || '';
                        const matches = text.match(/https?:\\/\\/[^"'\\s]+\\.m3u8[^"'\\s]*/g);
                        if (matches) found.push(...matches);
                    }
                    return JSON.stringify([...new Set(found)]);
                })()
            """)
            if urls_json:
                for url in json.loads(urls_json):
                    key = self._classify_m3u8(url)
                    if key not in results:
                        results[key] = {'url': url, 'headers': {}}
                        self._log(f"  JS(script): {url[:100]}")
        except Exception as e:
            self._log(f"  JS(script) 失败: {e}")

        # 3. 整个 HTML
        if not results:
            try:
                url = self.tab.run_js("""
                    (() => {
                        const m = document.documentElement.innerHTML.match(
                            /https?:\\/\\/[^"'\\s]+\\.m3u8[^"'\\s]*/
                        );
                        return m ? m[0] : null;
                    })()
                """)
                if url:
                    key = self._classify_m3u8(url)
                    results[key] = {'url': url, 'headers': {}}
                    self._log(f"  JS(html): {url[:100]}")
            except Exception as e:
                self._log(f"  JS(html) 失败: {e}")

        # 4. iframe 内
        if not results:
            try:
                for frame in self.tab.frames:
                    try:
                        url = frame.run_js("""
                            (() => {
                                const v = document.querySelector('video');
                                if (v && v.src) return v.src;
                                const m = document.documentElement.innerHTML.match(
                                    /https?:\\/\\/[^"'\\s]+\\.m3u8[^"'\\s]*/
                                );
                                return m ? m[0] : null;
                            })()
                        """)
                        if url:
                            key = self._classify_m3u8(url)
                            results[key] = {'url': url, 'headers': {}}
                            self._log(f"  JS(iframe): {url[:100]}")
                            break
                    except Exception:
                        continue
            except Exception as e:
                self._log(f"  JS(iframe) 失败: {e}")

        return results

    # ══════════════════════════════════════════════
    # 工具
    # ══════════════════════════════════════════════

    def _classify_m3u8(self, url: str) -> str:
        """根据 URL 特征分类 m3u8 流"""
        url_lower = url.lower()

        if 'master' in url_lower:
            return 'master'

        # f-number 分辨率 (fc2stream 命名规则)
        f_map = {'-f4-': '4K', '-f3-': '1080p', '-f2-': '720p', '-f1-': '480p'}
        for pat, label in f_map.items():
            if pat in url_lower:
                return label

        # 路径中的分辨率数字
        m = re.search(r'[/_\-](\d{3,4})p?[/_\-\.]', url_lower)
        if m:
            h = int(m.group(1))
            if h >= 2160: return '4K'
            if h >= 1440: return '2K'
            if h >= 1080: return '1080p'
            if h >= 720: return '720p'
            if h >= 480: return '480p'

        # 结尾 _480p.m3u8
        m2 = re.search(r'(\d{3,4})p\.m3u8', url_lower)
        if m2:
            return f'{m2.group(1)}p'

        return f'stream_{abs(hash(url)) % 10000}'
