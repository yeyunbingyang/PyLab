"""
============================================================
 ????)?? — jsonpath + XPath + BeautifulSoup — OOP ????
============================================================
????: ????) / ??
????:
  httpbin.org/json  — JSON API (jsonpath ??)
  douban.com        — ???? (XPath ??)
  baidu.com         — ??? (BeautifulSoup ??)
============================================================
"""

import requests
from lxml import etree
from bs4 import BeautifulSoup


class BaseParser:
    """????: requests Session + headers ??"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        })


# ============================================================
# 1. JsonParser — JSON ???? (jsonpath)
# ============================================================
class JsonParser:
    """jsonpath ???? — ???? Ajax/XHR JSON ????"""

    def __init__(self, data):
        """
        :param data: ?? JSON ???? (dict)
        """
        self.data = data

    def extract(self, expr):
        """?? jsonpath ??"""
        try:
            from jsonpath import jsonpath
            return jsonpath(self.data, expr)
        except ImportError:
            raise ImportError("jsonpath ???? pip install jsonpath")

    def demo_httpbin(self):
        """httpbin.org JSON ?? ??"""
        print("=" * 50)
        print("[?? 1: jsonpath ????)")
        print("=" * 50)

        resp = requests.get("https://httpbin.org/json", timeout=10)
        self.data = resp.json()

        # json ????
        root_title = self.extract("$.slideshow.title")
        all_titles = self.extract("$..title")
        slide_titles = self.extract("$.slideshow.slides[*].title")

        print(f"?? title  : {root_title}")
        print(f"?? title   : {all_titles}")
        print(f"??slide??? : {slide_titles}")

        # ??: ???? json ????
        print()
        print("???? (??????):")
        slides = self.data["slideshow"]["slides"]
        for s in slides:
            print(f"  ??  : {s['title']}")

    def demo_lagou(self):
        """
        ???? jsonpath ??
        ??: ????? Ajax ????
        ???? ???? ???? ?? ip???, `pip install jsonpath` ??
        """
        print()
        print("=" * 50)
        print("[?? 2: ????jsonpath ?? — ????")
        print("=" * 50)
        print("(?????? Ajax ????, ??????)")


# ============================================================
# 2. XPathParser — HTML/XML ????
# ============================================================
class XPathParser(BaseParser):
    """XPath + lxml ???? — HTML ???? XPath ??????"""

    def __init__(self, html_str=None, url=None):
        super().__init__()
        self.tree = None
        if html_str:
            self.from_string(html_str)
        if url:
            self.from_url(url)

    def from_string(self, html_str):
        """?? HTML ??"""
        self.tree = etree.HTML(html_str)
        return self

    def from_url(self, url):
        """?? URL ??? HTML"""
        resp = self.session.get(url, timeout=10)
        self.tree = etree.HTML(resp.content)
        return self

    def xpath(self, expr):
        """?? XPath ??, ???? ??"""
        if self.tree is None:
            raise ValueError("????????????????? from_string() / from_url() ????????")
        return self.tree.xpath(expr)

    def demo_movie_list(self):
        """???? XPath ??"""
        html = """
        <html><body>
          <div class="movie-list">
            <div class="item">
              <h2><a href="/movie/1">????</a></h2>
              <span class="rating">9.7</span>
              <span class="year">1994</span>
            </div>
            <div class="item">
              <h2><a href="/movie/2">???</a></h2>
              <span class="rating">9.6</span>
              <span class="year">1993</span>
            </div>
            <div class="item">
              <h2><a href="/movie/3">???</a></h2>
              <span class="rating">9.5</span>
              <span class="year">1994</span>
            </div>
          </div>
        </body></html>
        """
        self.from_string(html)
        items = self.xpath("//div[@class='item']")
        print(f"?? {len(items)} ???: ")
        for item in items:
            name = item.xpath(".//h2/a/text()")[0]
            rating = item.xpath(".//span[@class='rating']/text()")[0]
            year = item.xpath(".//span[@class='year']/text()")[0]
            href = item.xpath(".//h2/a/@href")[0]
            print(f"  {name:10s} | {rating} ? | {year} | {href}")

    def demo_xpath_cheatsheet(self):
        """XPath ????"""
        print()
        print("=" * 50)
        print("[XPath ????]")
        print("=" * 50)
        print("  //div[@class='xxx']            — ????")
        print("  //h2/text()                    — ???")
        print("  //a/@href                      — ???")
        print("  //div[position()=2]            — ?2?")
        print("  //span[contains(@class,'rat')] — ???")
        print("  //*[contains(text(),'??')]    — ???")
        print("  //li | //a                     — ???")
        print("  .//h2/a/text()                 — ???? (???? .//)")
        print()

    def demo_tieba(self, kw, max_pages=3):
        """
        ???? OOP FAQ
        ?? XPath ?[next?]?→ while True ?→?????
        """
        print("=" * 50)
        print(f"[??: ???? — {kw}]")
        print("=" * 50)

        import time
        base_url = "https://tieba.baidu.com/f"
        current_url = f"{base_url}?kw={kw}&ie=utf-8&pn=0"
        all_posts = []
        page = 1

        while True:
            print(f"???? {page} ?: {current_url}")
            resp = self.session.get(current_url, timeout=10)
            tree = etree.HTML(resp.content)

            # ????
            items = tree.xpath('//li[contains(@class, "j_thread_list")]')
            for item in items:
                title_el = item.xpath('.//a[contains(@class, "j_th_tit")]')
                author_el = item.xpath('.//span[contains(@class, "tb_icon_author")]')
                reply_el = item.xpath('.//span[contains(@class, "threadlist_rep_num")]')

                if title_el:
                    all_posts.append({
                        "title": title_el[0].xpath("string()").strip() if title_el else "",
                        "author": author_el[0].xpath("string()").strip() if author_el else "",
                        "replies": reply_el[0].xpath("string()").strip() if reply_el else "0",
                    })

            print(f"  ?? {len(items)} ?, ?? {len(all_posts)} ?")

            if page >= max_pages:
                print(f"????? {max_pages} ?, ??")
                break

            # ?[next?]??
            next_link = tree.xpath('//a[contains(text(), "????")]/@href')
            if not next_link:
                print("?????, ??")
                break

            current_url = "https:" + next_link[0] if next_link[0].startswith("//") else next_link[0]
            page += 1
            time.sleep(1)

        # ??
        print()
        print(f"?? {len(all_posts)} ??:")
        for i, post in enumerate(all_posts[:10]):
            print(f"  {i+1}. {post['title'][:30]} | {post['author']} | {post['replies']}??")


# ============================================================
# 3. BeautifulSoupParser — HTML???? (CSS ?????)
# ============================================================
class BeautifulSoupParser(BaseParser):
    """BeautifulSoup ???? — CSS ??????????? HTML"""

    def __init__(self, html_str=None, url=None, parser="lxml"):
        super().__init__()
        self.soup = None
        if html_str:
            self.from_string(html_str, parser)
        if url:
            self.from_url(url, parser)

    def from_string(self, html_str, parser="lxml"):
        self.soup = BeautifulSoup(html_str, parser)
        return self

    def from_url(self, url, parser="lxml"):
        resp = self.session.get(url, timeout=10)
        self.soup = BeautifulSoup(resp.text, parser)
        return self

    def select(self, selector):
        """CSS ??"""
        return self.soup.select(selector)

    def select_one(self, selector):
        """CSS ??? (???1?)"""
        return self.soup.select_one(selector)

    def find_all(self, tag, **kwargs):
        """?????"""
        return self.soup.find_all(tag, **kwargs)

    def demo_baidu_hot(self):
        """???? — ???? CSS ????"""
        print("=" * 50)
        print("[??: BeautifulSoup — ????]")
        print("=" * 50)

        try:
            self.from_url("https://www.baidu.com/")

            # ??
            print(f"??: {self.soup.title.string}")

            # ????
            links = self.find_all("a")
            print(f"? {len(links)} ??")

            # ????
            hot_items = self.select(".hotsearch-item .title-content-title, "
                                   ".s-hotsearch-title, "
                                   ".title-content-title")
            print(f"?? {len(hot_items)} ?:")
            for i, item in enumerate(hot_items[:10]):
                title = item.get_text(strip=True)
                if title:
                    print(f"  {i+1}. {title}")

            # BeautifulSoup ????
            print()
            print("BeautifulSoup ????:")
            print("  soup.find('div', class_='xxx')   — ??1?")
            print("  soup.find_all('a')                 — ???")
            print("  soup.select('.class #id a')       — CSS ???? (??)")
            print("  tag.get_text(strip=True)           — ???")
            print("  tag.get('href') / tag['href']     — ???")

        except Exception as e:
            print(f"????: {e}")

    def demo_bs4_cheatsheet(self):
        """BeautifulSoup ???? (??)"""
        html = """
        <div class="article">
          <h2><a href="/post/1">Python????</a></h2>
          <p class="desc">????? Python ??, ??? requests / lxml / BS4</p>
          <span class="tag">??</span>
          <span class="tag">Python</span>
          <span class="date">2025-01-01</span>
        </div>
        """
        self.from_string(html)

        # find
        h2 = self.soup.find("h2")
        print(f"find h2: {h2.get_text()}")

        # find_all
        tags = self.soup.find_all("span", class_="tag")
        print(f"????: {[t.get_text() for t in tags]}")

        # CSS select
        desc = self.select_one(".desc")
        print(f"CSS ??: {desc.get_text() if desc else 'N/A'}")

        # ??
        link = self.select_one("h2 a")
        print(f"?????? href: {link['href'] if link else 'N/A'}")


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    # ?? 1: JsonParser
    print("\n=== ?? 1: JsonParser (jsonpath) ===\n")
    jp = JsonParser({})
    jp.demo_httpbin()
    jp.demo_lagou()

    # ?? 2: XPathParser (lxml + XPath)
    print("\n=== ?? 2: XPathParser (lxml + XPath) ===\n")
    xp = XPathParser()
    xp.demo_movie_list()
    xp.demo_xpath_cheatsheet()

    # ?? 3: BeautifulSoupParser (BS4)
    print("\n=== ?? 3: BeautifulSoupParser (BS4) ===\n")
    bsp = BeautifulSoupParser()
    bsp.demo_bs4_cheatsheet()
    bsp.demo_baidu_hot()

    print()
    print("=" * 50)
    print("??: ?????????")
    print("=" * 50)
    print("  jsonpath            -> JSON API ???? (Ajax/XHR)")
    print("  XPath + lxml        -> HTML ???? (??/??/??)")
    print("  BeautifulSoup       -> HTML ???? (CSS????/??)")
    print("  ????: JSON?jsonpath, HTML?BS4(??)?XPath(??)")
    print()
    print("????? XPathParser.demo_tieba('python', max_pages=2) ??while True??")
