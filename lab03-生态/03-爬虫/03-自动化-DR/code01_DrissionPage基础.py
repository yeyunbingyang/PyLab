"""
============================================================
 DrissionPage — SessionPage + ChromiumPage OOP ????
============================================================
????: DrissionPage ????
  — BaseDrissionSpider : ???? (?? + UA)
  — SessionSpider     : ???? requests ????TLS??
  — ChromiumSpider    : ????????, ?? webdriver

????:
  httpbin.org  — SessionSpider ???????
  baidu.com    — ChromiumSpider ?? + ??
============================================================
"""

from DrissionPage import SessionPage, ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup


class BaseDrissionSpider:
    """DrissionPage ??: ?? session + headers"""

    def __init__(self):
        self.session = SessionPage()
        self.session.set.headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        })


# ============================================================
# ?? 1: SessionSpider — ?????? (?????)
# ============================================================
class SessionSpider(BaseDrissionSpider):
    """
    SessionPage ????
    ?? requests ???, ???? TLS ??, ??????????
    """

    def demo_get(self):
        """GET ?? + params"""
        print("=" * 50)
        print("[1.1 GET ?? — params / headers]")
        print("=" * 50)

        resp = self.session.get("https://httpbin.org/get",
                                params={"q": "python", "page": 1})
        print(f"???: {resp.status_code}")
        data = resp.json()
        print(f"origin: {data['origin']}")
        print(f"args  : {data['args']}")

        # ??
        self.session.set.headers({"Referer": "https://www.baidu.com/"})
        resp = self.session.get("https://httpbin.org/headers")
        data = resp.json()
        print(f"?? Referer: {data['headers'].get('Referer', 'N/A')}")

    def demo_post(self):
        """POST ?? — form / json"""
        print()
        print("=" * 50)
        print("[1.2 POST ?? — form / json]")
        print("=" * 50)

        # form ??
        resp = self.session.post("https://httpbin.org/post",
                                 data={"username": "admin", "password": "123456"})
        print(f"form POST: {resp.json()['form']}")

        # JSON body
        resp = self.session.post("https://httpbin.org/post",
                                 json={"name": "??", "skills": ["Python", "??"]})
        print(f"json POST: {resp.json()['json']}")

    def demo_cookie(self):
        """Session ??"""
        print()
        print("=" * 50)
        print("[1.3 Cookie — Session ????")
        print("=" * 50)

        self.session.get("https://httpbin.org/cookies/set/username/alice")
        self.session.get("https://httpbin.org/cookies/set/token/abc123")
        resp = self.session.get("https://httpbin.org/cookies")
        print(f"Session ???: {resp.json()['cookies']}")

    def demo_proxy(self):
        """?? proxies"""
        print()
        print("=" * 50)
        print("[1.4 proxies ??]")
        print("=" * 50)
        print("HTTP ??:  proxies={'http': 'http://127.0.0.1:7890'}")
        print("SOCKS5:    proxies={'http': 'socks5://127.0.0.1:1080'}")

        try:
            test_proxy = {"http": "http://httpbin.org:80"}
            resp = self.session.get("https://httpbin.org/ip",
                                    proxies=test_proxy, timeout=5)
            print(f"???? IP: {resp.json()['origin']}")
        except Exception as e:
            print(f"??????: {e}")

    def demo_baidu_hot(self):
        """SessionPage + BS4 ????"""
        print()
        print("=" * 50)
        print("[1.5 SessionPage ?? — ????")
        print("=" * 50)

        try:
            resp = self.session.get("https://www.baidu.com/", timeout=10)
            soup = BeautifulSoup(resp.text, "lxml")
            hot_items = soup.select(".hotsearch-item .title-content-title, "
                                   ".s-hotsearch-title")
            print(f"?? {len(hot_items)} ?:")
            for i, item in enumerate(hot_items[:10]):
                title = item.get_text(strip=True)
                if title:
                    print(f"  {i+1}. {title}")
        except Exception as e:
            print(f"????: {e}")

    def run_all(self):
        """??????"""
        self.demo_get()
        self.demo_post()
        self.demo_cookie()
        self.demo_proxy()
        self.demo_baidu_hot()
        print()
        print("SessionSpider ????")
        print("  Session ?  requests ??: ")
        print("  TLS ?? ?????????")


# ============================================================
# ?? 2: ChromiumSpider — ???????
# ============================================================
class ChromiumSpider:
    """
    ChromiumPage ???? — ?????
    ?? webdriver, ???? Chrome ???????
    """

    def __init__(self, headless=False):
        """
        :param headless: True=??????, False=??????
        """
        co = ChromiumOptions()
        if headless:
            co.headless(True)
        self.page = ChromiumPage(co)

    def demo_baidu_search(self, keyword="Python DrissionPage"):
        """?????"""
        print("=" * 50)
        print(f"[ChromiumSpider] ???? — {keyword}")
        print("=" * 50)

        try:
            # 1. ??
            self.page.get("https://www.baidu.com/")

            # 2. ???????
            self.page.ele("#kw").input(keyword)

            # 3. ??????
            self.page.ele("#su").click()

            # 4. ?????
            self.page.wait.ele_displayed("#content_left", timeout=10)

            # 5. ?????
            results = self.page.eles(".result")
            print(f"?? {len(results)} ???: ")
            for i, item in enumerate(results[:5]):
                try:
                    title = item.ele("h3").text if item.ele("h3") else "???"
                    link = item.ele("a").attr("href") if item.ele("a") else ""
                    print(f"  {i+1}. {title}")
                    if link:
                        print(f"     {link}")
                except Exception:
                    pass

            # 6. ??
            self.page.get_screenshot("baidu_search_drission.png")
            print()
            print("????: baidu_search_drission.png")

        except Exception as e:
            print(f"???: {e}")
            print("(?? Chrome ?????????)")

    def demo_element_locate(self):
        """4???? (????)"""
        print()
        print("=" * 50)
        print("[?????? — 4????")
        print("=" * 50)
        print("  page.ele('#kw')                    — CSS id")
        print("  page.ele('.s_ipt')                 — CSS class")
        print("  page.ele('@name=wd')               — ????")
        print("  page.ele('text:????')             — ????")
        print("")
        print("?????:")
        print("  page.eles('.result')               — ?????????")
        print("  page.ele('tag:div@class=item')     — ?? + ??")
        print("")
        print("iframe ??:")
        print("  iframe = page.get_frame('#iframe_id')")
        print("  iframe.ele('body').text")

    def demo_actions(self):
        """????? (????)"""
        print()
        print("=" * 50)
        print("[?????? — ? / ??]")
        print("=" * 50)
        print("  page.ele('#kw').input('hello')       — ??")
        print("  page.ele('#su').click()               — ??")
        print("  page.run_js('window.scrollTo(0,500)') — ?? JS")
        print("  page.get_screenshot('s.png')          — ??")
        print("  page.wait.load_start()                 — ?????")
        print("  page.wait.ele_displayed('#result')     — ?????????")

    def demo_stealth(self):
        """?????"""
        print()
        print("=" * 50)
        print("[?????? — ????")
        print("=" * 50)
        print("DrissionPage ???? navigator.webdriver ???")
        print("??? Selenium ???? JS ???")
        print()
        print("?? + ??:")
        print("  co = ChromiumOptions()")
        print("  co.set_argument('--disable-blink-features=AutomationControlled')")
        print("  page = ChromiumPage(co)")

    def close(self):
        """?????"""
        self.page.quit()

    def run_all(self):
        """??????"""
        try:
            self.demo_baidu_search()
        except Exception:
            print("Chromium ?????, ???? API ??...")
        self.demo_element_locate()
        self.demo_actions()
        self.demo_stealth()
        print()
        print("ChromiumSpider ??")


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    print("=== ?? 1: SessionSpider (????) ===\n")
    session_spider = SessionSpider()
    session_spider.run_all()

    print("\n\n=== ?? 2: ChromiumSpider (????) ===\n")
    print("(???: Chromium ?????, ????)")
    print()
    chromium_spider = ChromiumSpider()
    chromium_spider.run_all()

    print()
    print("=" * 50)
    print("??:")
    print("=" * 50)
    print("  SessionSpider  -> ????  ?????????")
    print("  ChromiumSpider -> ????  ?JS??/????????")
    print("  ????: ????SessionSpider, ??/JS????ChromiumSpider")
