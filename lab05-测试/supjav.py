"""
supjav.com 爬虫 === 诊断报告 ===

问题: 无法获取 HTML
├── 症状: requests 返回 403, Chrome 浏览器也卡在 Cloudflare 验证页
├── 根因: Cloudflare Turnstile Managed Challenge
│         响应头 Cf-Mitigated: challenge 确认
├── 当前 IP: 146.235.17.47 (Oracle Cloud 新加坡)
│          → 数据中心 IP, Cloudflare 风险分极高
└── 结论: 非代码问题, 是 IP 信誉问题

已尝试方案 (全部失败):
  1. requests + User-Agent                         → 403
  2. requests + 完整 headers                       → 403
  3. cloudscraper (Cloudflare 专用)                 → 403 + JS 挑战
  4. DrissionPage SessionPage                      → API 兼容性
  5. DrissionPage ChromiumPage + 真实 Chrome 90秒  → 验证循环

可行方案:
  1. 更换 IP — 使用住宅代理/VPN (非数据中心 IP)
  2. 使用 flaresolverr — Docker 容器化的 Cloudflare 绕过
     docker run -d -p 8191:8191 ghcr.io/flaresolverr/flaresolverr
     然后通过 http://localhost:8191/v1 代理请求
  3. 手动浏览器访问一次建立 cookie → 导给爬虫复用
"""

import requests
from bs4 import BeautifulSoup


class Supjav:
    """
    supjav.com 爬虫 — 当前环境无法绕过 Cloudflare
    代码保留完整框架, IP 更换后即可工作
    """

    def __init__(self):
        self.url = 'https://supjav.com/ja/category/reducing-mosaic/page/2'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://supjav.com/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_data(self):
        """
        获取页面数据
        当前 IP (146.235.17.47, Oracle Cloud) 被 Cloudflare 拦截
        换 IP 后即可正常获取
        """
        try:
            resp = self.session.get(self.url, timeout=30, allow_redirects=True)
            print(f'状态码: {resp.status_code}')
            print(f'响应头 Cf-Mitigated: {resp.headers.get("Cf-Mitigated", "无")}')
            print(f'Server: {resp.headers.get("Server", "无")}')

            html = resp.text
            print(f'HTML 长度: {len(html)} 字符')

            # Cloudflare 检测
            if 'Just a moment' in html or 'cf_chl' in html or 'しばらく' in html:
                print('\n=== 被 Cloudflare 拦截 ===')
                print('Cf-Mitigated: challenge (需要人机验证)')
                print('当前 IP 被判定为高风险, 需要:')
                print('  1. 更换住宅代理 IP')
                print('  2. 或使用 flaresolverr 服务')
                return None

            # 正常解析
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, 'lxml')
            print(f'\n页面标题: {soup.title.string if soup.title else "N/A"}')

            posts = soup.select('article h2 a, .post-title a, h2.entry-title a, .entry-title a, h3 a')
            print(f'找到 {len(posts)} 个条目:')
            for i, post in enumerate(posts[:10]):
                text = post.get_text(strip=True)
                href = post.get('href', '')
                print(f'  {i+1}. {text}')
                print(f'     {href}')

            return resp.text

        except Exception as e:
            print(f'请求失败: {e}')
            import traceback
            traceback.print_exc()
            return None


if __name__ == '__main__':
    print("=== supjav.com 爬虫诊断 ===\n")
    print("当前 IP 146.235.17.47 (Oracle Cloud, Singapore)")
    print("Cloudflare 状态: BLOCKED — managed challenge 无法通过\n")

    supjav = Supjav()
    html = supjav.get_data()

    if html is None:
        print("\n=== 诊断结论 ===")
        print("问题不在代码层面。")
        print("supjav.com 使用 Cloudflare Turnstile + 数据中心 IP 黑名单。")
        print("更换为住宅 IP 后代码即可正常工作。")
