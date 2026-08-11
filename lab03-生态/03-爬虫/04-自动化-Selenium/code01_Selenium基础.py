"""
============================================================
 Selenium — ?????? OOP ????
============================================================
????: Selenium ????
  — SeleniumSpider : ? WebDriver ??
  — ?????? 8 ???? / ?? / ?? / iframe / Cookie
  — ???? + ??

????:
  baidu.com — ?? + ????, ?????
============================================================

??:
  pip install selenium webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================
# ?? 1: SeleniumSpider — ??????? (OOP)
# ============================================================
class SeleniumSpider:
    """
    Selenium ?????
    ? WebDriver ?????, ????/??/iframe/????
    """

    def __init__(self, headless=False, stealth=True):
        """
        :param headless: True=??????, False=??????
        :param stealth: True=????? (?? webdriver ??)
        """
        self.options = Options()

        if headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--window-size=1920,1080")

        if stealth:
            # ???? Selenium ??
            self.options.add_argument("--disable-blink-features=AutomationControlled")
            self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # ?????? webdriver-manager
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        # ????
        self.id_ = self.driver   # ???? driver ?????

    # ---- ???? ---- #
    def open(self, url):
        """??????"""
        self.driver.get(url)
        return self

    def close(self):
        """?????"""
        self.driver.quit()

    # ----????—8??法---- #
    def find(self, by, selector):
        """定位元素"""
        return self.driver.find_element(by, selector)

    def find_all(self, by, selector):
        return self.driver.find_elements(by, selector)

    def by_id(self, selector):
        return self.find(By.ID, selector)

    def by_name(self, selector):
        return self.find(By.NAME, selector)

    def by_class(self, selector):
        return self.find(By.CLASS_NAME, selector)

    def by_xpath(self, selector):
        return self.find(By.XPATH, selector)

    def by_css(self, selector):
        """CSS选择器 (推荐)"""
        return self.find(By.CSS_SELECTOR, selector)

    def by_link_text(self, text):
        return self.find(By.LINK_TEXT, text)

    def by_partial_link_text(self, text):
        return self.find(By.PARTIAL_LINK_TEXT, text)

    def by_tag(self, tag):
        return self.find(By.TAG_NAME, tag)

    # ---- ?? ---- #
    def input(self, by, selector, text, clear_first=True):
        """输入文本"""
        el = self.find(by, selector)
        if clear_first:
            el.clear()
        el.send_keys(text)

    def click(self, by, selector):
        """点击"""
        self.find(by, selector).click()

    def submit(self, by, selector, keys=Keys.ENTER):
        """提交 (回车)"""
        self.find(by, selector).send_keys(keys)

    # ---- ?? ---- #
    def wait_element(self, by, selector, timeout=10):
        """显式等待 — 直到元素出现"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )

    def wait_elements(self, by, selector, timeout=10):
        """显式等待 — 直到所有元素出现"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, selector))
        )

    def wait_visible(self, by, selector, timeout=10):
        """显式等待 — 直到元素可见"""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )

    def set_implicit_wait(self, seconds=10):
        """隐式等待 (全局, 整个 driver 生命周期)"""
        self.driver.implicitly_wait(seconds)

    # ---- 提取 ---- #
    def extract_text(self, by, selector):
        """提取文本"""
        return self.find(by, selector).text

    def extract_attr(self, by, selector, attr):
        """提取属性"""
        return self.find(by, selector).get_attribute(attr)

    # ---- JS ???? ---- #
    def run_js(self, script):
        """执行 JS"""
        return self.driver.execute_script(script)

    def scroll_to(self, x=0, y=500):
        """滚动页面"""
        self.run_js(f"window.scrollTo({x}, {y})")

    def scroll_bottom(self):
        """滚动到底部"""
        self.run_js("window.scrollTo(0, document.body.scrollHeight)")

    # ---- ???? ---- #
    def screenshot(self, filename="screenshot.png"):
        """截图"""
        self.driver.save_screenshot(filename)
        print(f"???: {filename}")

    # ---- iframe / ??? ---- #
    def switch_to_iframe(self, ref):
        """切换 iframe (id / name / element)"""
        self.driver.switch_to.frame(ref)

    def switch_to_default(self):
        """切回主页"""
        self.driver.switch_to.default_content()

    def switch_to_last_window(self):
        """切换到最后一个窗口"""
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_first_window(self):
        """切换到第一个窗口"""
        self.driver.switch_to.window(self.driver.window_handles[0])

    # ---- Cookie ---- #
    def get_cookies(self):
        """获取所有 cookie"""
        return self.driver.get_cookies()

    def add_cookie(self, cookie_dict):
        """添加 cookie"""
        self.driver.add_cookie(cookie_dict)

    # ---- ???? ---- #
    def get_page_source(self):
        """获取页面源码 (传给 lxml/BS4 ??)"""
        return self.driver.page_source

    def get_current_url(self):
        """获取当前 URL"""
        return self.driver.current_url

    def get_title(self):
        """获取页面标题"""
        return self.driver.title

    # ---- ???? ---- #
    def inject_stealth_js(self):
        """注入隐藏 webdriver 属性的 JS"""
        self.run_js(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )


# ============================================================
# ?? 2: ElementLocator — 8??????
# ============================================================
class ElementLocator:
    """8????? + ????"""

    @staticmethod
    def demo():
        print("=" * 50)
        print("[??: Selenium 8????")
        print("=" * 50)
        print("""
?? HTML:
  <input type="text" id="kw" name="wd" class="s_ipt" placeholder="请输入关键词">
  <input type="submit" id="su" value="百度一下">
  <a href="https://news.baidu.com" class="nav-link">新闻</a>
  <a href="https://tieba.baidu.com" class="nav-link">贴吧</a>

8??法:
  1. By.ID              → driver.find_element(By.ID, 'kw')
  2. By.NAME            → driver.find_element(By.NAME, 'wd')
  3. By.CLASS_NAME      → driver.find_element(By.CLASS_NAME, 's_ipt')
  4. By.TAG_NAME        → driver.find_element(By.TAG_NAME, 'input')
  5. By.LINK_TEXT       → driver.find_element(By.LINK_TEXT, '贴吧')
  6. By.PARTIAL_LINK_TEXT → driver.find_element(By.PARTIAL_LINK_TEXT, '贴')
  7. By.XPATH           → driver.find_element(By.XPATH, '//input[@id="kw"]')
  8. By.CSS_SELECTOR    → driver.find_element(By.CSS_SELECTOR, '#kw')

推荐 (?????):
  By.XPATH       → ? ???90%, XPath Helper ????
  By.CSS_SELECTOR → ? ???, find_element??
        """)


# ============================================================
# ?? 3: ?????
# ============================================================
class BaiduSeleniumSpider(SeleniumSpider):
    """????? OOP ?? Selenium"""

    def search(self, keyword="Python Selenium"):
        """搜索关键词并提取结果"""
        print("=" * 50)
        print(f"[??: Selenium ???? — {keyword}]")
        print("=" * 50)

        try:
            # 1. 打开百度
            self.open("https://www.baidu.com/")

            # 2. 等待搜索框加载
            self.wait_element(By.ID, "kw")

            # 3. 输入关键词 + 回车
            self.input(By.ID, "kw", keyword)
            self.submit(By.ID, "kw")

            # 4. 等待结果加载
            self.wait_elements(By.CSS_SELECTOR, ".result", timeout=10)

            # 5. 提取结果
            results = self.find_all(By.CSS_SELECTOR, ".result")
            print(f"找到 {len(results)} 条结果:")
            for i, item in enumerate(results[:5]):
                try:
                    title = item.find_element(By.CSS_SELECTOR, "h3").text
                    link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    print(f"  {i+1}. {title}")
                    print(f"     {link}")
                except Exception:
                    pass

            # 6. 截图
            self.screenshot("baidu_selenium_search.png")

        except Exception as e:
            print(f"失败: {e}")
            print("(检查 chromedriver 版本是否匹配 Chrome 浏览器)")

    def demo_interaction(self):
        """交互演示 (文档说明)"""
        print()
        print("=" * 50)
        print("[交互动作 — send_keys / click / ActionChains]")
        print("=" * 50)
        print("""
基本交互:
  driver.find_element(By.ID, 'kw').send_keys('Python')
  driver.find_element(By.ID, 'su').click()
  driver.find_element(By.ID, 'kw').send_keys(Keys.ENTER)

ActionChains (动作链):
  from selenium.webdriver import ActionChains
  el = driver.find_element(By.CSS_SELECTOR, '#su')

  ActionChains(driver).move_to_element(el).click().perform()     # 鼠标悬停+点击
  ActionChains(driver).double_click(el).perform()                # 双击
  ActionChains(driver).context_click(el).perform()               # 右键
  ActionChains(driver).drag_and_drop(el1, el2).perform()         # 拖拽
        """)


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    # 静态演示 (不需要真实浏览器)
    ElementLocator.demo()

    # 浏览器实战
    print()
    print("=== 启动 Chrome 浏览器 === (首次自动下载 chromedriver)")
    print()

    spider = BaiduSeleniumSpider(headless=False, stealth=True)

    try:
        spider.search("Python Selenium 爬虫")
        spider.demo_interaction()
    except Exception as e:
        print(f"浏览器启动失败: {e}")
        print("提示:")
        print("  1. 检查 Chrome 是否安装")
        print("  2. 'pip install webdriver-manager selenium'")
        print("  3. 或手动下载 chromedriver (匹配 Chrome 版本)")
    finally:
        spider.close()

    print()
    print("=" * 50)
    print("总结: Selenium OOP 核心工作流")
    print("=" * 50)
    print("  1. 启动: SeleniumSpider()         — 自动管理 chromedriver")
    print("  2. 访问: spider.open(url)")
    print("  3. 等待: spider.wait_element(...)")
    print("  4. 定位: spider.by_css('#kw')     — 8种方式推荐CSS/XPath")
    print("  5. 操作: spider.input(...) / click(...)")
    print("  6. 提取: spider.extract_text(...) / extract_attr(...)")
    print("  7. 截图: spider.screenshot(...)")
    print("  8. 关闭: spider.close()")
