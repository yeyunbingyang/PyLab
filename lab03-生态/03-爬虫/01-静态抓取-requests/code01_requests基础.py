# -*- coding: utf-8 -*-
"""
============================================================
 requests 静态抓取 — 面向对象实战
============================================================
对照笔记: 01 核心请求与响应 / 02 POST请求 / 03 Cookie与Session

类设计:
  ApiTestSpider  — JSONPlaceholder API (全功能演示 GET/POST/PUT/DELETE)
  BaiduSpider    — 百度首页 (编码/搜索/SSL)
  BiliSpider     — B站 API 搜索 + JSON响应解析
  CookieDemo     — Cookie/Session 知识点演示

原因: httpbin.org 在国内网络不可达, 改用 jsonplaceholder.typicode.com
============================================================
"""

import requests
import re
from urllib.parse import urlparse, parse_qs


class BaseSpider:
    """爬虫基类: session + headers 初始化 + 通用请求方法"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        }
        self.session.headers.update(self.headers)

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", 15)
        try:
            return self.session.get(url, **kwargs)
        except requests.Timeout:
            print(f"[请求超时] {url}")
            raise
        except requests.ConnectionError as e:
            print(f"[连接失败] {url} — {e}")
            raise

    def post(self, url, **kwargs):
        kwargs.setdefault("timeout", 15)
        return self.session.post(url, **kwargs)

    def put(self, url, **kwargs):
        kwargs.setdefault("timeout", 15)
        return self.session.put(url, **kwargs)

    def patch(self, url, **kwargs):
        kwargs.setdefault("timeout", 15)
        return self.session.patch(url, **kwargs)


# ============================================================
# 示例 1: ApiTestSpider — JSONPlaceholder REST API 全功能演示
# ============================================================
class ApiTestSpider(BaseSpider):
    """
    用 JSONPlaceholder 免费 REST API (https://jsonplaceholder.typicode.com)
    演示: GET / POST / PUT / PATCH / DELETE / headers / params / timeout / json
    """

    BASE = "https://jsonplaceholder.typicode.com"

    # ---- 1.1 GET 请求 — params + headers 伪装 ----
    def demo_get(self):
        """GET 请求 + params 参数 + headers 伪装"""
        print("=" * 55)
        print("[1.1 GET 请求 — params / headers 伪装]")
        print("=" * 55)

        # 带 params 的 GET — 获取前3条帖子
        resp = self.get(f"{self.BASE}/posts", params={"_limit": 3})
        print(f"状态码: {resp.status_code}")
        print(f"完整 URL: {resp.url}")
        print(f"返回 {len(resp.json())} 条数据:")
        # print(resp.json())
        # print(resp.content.decode('utf-8'))

        for post in resp.json():
            print(f"  [{post['id']}] {post['title'][:35]}...")

        # 验证 User-Agent 伪装
        print(f"\n请求的 User-Agent: {resp.request.headers['User-Agent'][:50]}...")

        # 添加 Referer 伪装
        self.session.headers.update({"Referer": "https://www.baidu.com/"})
        resp2 = self.get(f"{self.BASE}/posts/1")
        print(f"伪装 Referer 后: {resp2.request.headers.get('Referer', 'N/A')}")

        print("\n提示: params={'_limit': 3} 自动拼接为 ?_limit=3")

    # ---- 1.2 POST 请求 — form / json ----
    def demo_post(self):
        """POST 请求 + 五种数据来源示例"""
        print("\n" + "=" * 55)
        print("[1.2 POST 请求 — form / json]")
        print("=" * 55)

        # POST JSON 创建新帖子
        new_post = {
            "title": "Python爬虫学习笔记",
            "body": "POST请求的data字典, 值从五种来源获取",
            "userId": 1,
        }
        resp = self.post(f"{self.BASE}/posts", json=new_post)
        data = resp.json()
        print(f"状态码: {resp.status_code} (201 = 创建成功)")
        print(f"返回 id: {data['id']}")  # JSONPlaceholder 固定返回 101
        print(f"标题: {data['title']}")

        print("\nPOST data= (表单) vs json= (JSON):")
        print("  data={'k':'v'}  → Content-Type: application/x-www-form-urlencoded")
        print("  json={'k':'v'}  → Content-Type: application/json")
        print("  爬虫多数情况用 data= 发表单数据")

    # ---- 1.3 PUT / PATCH 更新 ----
    def demo_put_patch(self):
        """PUT 完全替换 vs PATCH 部分更新"""
        print("\n" + "=" * 55)
        print("[1.3 PUT / PATCH — 更新资源]")
        print("=" * 55)

        # PUT 完全替换
        resp = self.put(f"{self.BASE}/posts/1", json={
            "id": 1, "title": "PUT完全替换", "body": "...", "userId": 1
        })
        print(f"PUT 结果: {resp.status_code} | {resp.json()['title']}")

        # PATCH 部分更新
        resp = self.patch(f"{self.BASE}/posts/1", json={"title": "PATCH部分更新"})
        print(f"PATCH结果: {resp.status_code} | {resp.json()['title']}")

        print("\nPUT vs PATCH:")
        print("  PUT:   完全替换整个资源 (全部字段都要传)")
        print("  PATCH: 部分更新 (只传要改的字段)")

    # ---- 1.4 timeout 超时控制 ----
    def demo_timeout(self):
        """timeout 超时 + try/except 处理"""
        print("\n" + "=" * 55)
        print("[1.4 timeout 超时控制]")
        print("=" * 55)

        print("演示: requests.get(url, timeout=3)")
        print("  → 3秒未建立连接则抛出 Timeout 异常")
        try:
            # 模拟超时: 用不可达地址测试 timeout 捕获
            self.get("https://10.255.255.1", timeout=1)
        except requests.Timeout:
            print("  timeout=1: 请求超时被正确捕获")
        except requests.ConnectionError:
            print("  timeout=1: 连接失败被正确捕获")

        # 正常请求对比
        resp = self.get(f"{self.BASE}/posts/1", timeout=5)
        print(f"  正常请求 (timeout=5): {resp.status_code} OK")

        print("\n建议: 所有爬虫代码都应设置 timeout, 配合 try/except")

    # ---- 1.5 SSL 证书 — verify 参数 ----
    def demo_ssl(self):
        """SSL证书 verify 参数"""
        print("\n" + "=" * 55)
        print("[1.5 SSL / verify 证书处理]")
        print("=" * 55)

        # 正常 HTTPS
        resp = self.get(f"{self.BASE}/posts/1")
        print(f"正常 HTTPS (verify=True): {resp.status_code}")

        print("\n遇到 SSLError: certificate verify failed 时:")
        print("  1. verify=False  — 关闭证书验证")
        print("  2. urllib3.disable_warnings()  — 消除警告")
        print("\n适用场景: 自签名证书或非正规CA证书的HTTPS网站")

    # ---- 1.6 代理 proxies ----
    def demo_proxy(self):
        """代理 proxies (概念 + 用法)"""
        print("\n" + "=" * 55)
        print("[1.6 proxies 代理]")
        print("=" * 55)

        print("代理分类 (按匿名度):")
        print("  透明代理 — 服务器能发现真实IP")
        print("  匿名代理 — 服务器知道是代理请求")
        print("  高匿代理 — 服务器完全不知道是代理 (爬虫首选)")

        print("\n用法:")
        print("  proxies = {'http': 'http://IP:端口', 'https': 'https://IP:端口'}")
        print("  requests.get(url, headers=headers, proxies=proxies)")

    # ---- 1.7 Response 对象完全解析 ----
    def demo_response(self):
        """Response 对象属性 + encoding 处理"""
        print("\n" + "=" * 55)
        print("[1.7 Response 响应对象]")
        print("=" * 55)

        resp = self.get(f"{self.BASE}/posts/1")
        data = resp.json()

        print(f"status_code  : {resp.status_code}")
        print(f"url          : {resp.url}")
        print(f"encoding     : {resp.encoding}")
        print(f"Content-Type : {resp.headers.get('Content-Type')}")
        print(f"text (str)   : {resp.text[:50]}...")
        print(f"content (bytes): {len(resp.content)} bytes")
        print(f"json() (dict) : userId={data['userId']}, id={data['id']}")

        print("\nResponse 速查:")
        print("  resp.text         → str (自动解码, 可能乱码)")
        print("  resp.content      → bytes (推荐: .decode('utf-8') 精准控制)")
        print("  resp.json()       → dict (仅 JSON 响应)")
        print("  resp.status_code  → HTTP 状态码")
        print("  resp.url          → 最终请求 URL")
        print("  resp.headers      → 响应头")
        print("  resp.cookies      → CookieJar 对象")
        print("  resp.request.headers → 实际发出的请求头 (调试用)")

    def run_all(self):
        """运行全部演示"""
        self.demo_get()
        self.demo_post()
        self.demo_put_patch()
        self.demo_timeout()
        self.demo_ssl()
        self.demo_proxy()
        self.demo_response()
        print("\n" + "=" * 55)
        print("ApiTestSpider 演示完毕!")
        print("=" * 55)


# ============================================================
# 示例 2: BaiduSpider — 百度搜索实战
# ============================================================
class BaiduSpider(BaseSpider):
    """百度搜索: encoding / params / 标题提取"""

    URL = "https://www.baidu.com/"

    def fetch_homepage(self):
        """获取百度首页, 演示 encoding 处理"""
        print("=" * 55)
        print("[BaiduSpider — 百度首页]")
        print("=" * 55)

        resp = self.get(self.URL)
        print(f"状态码: {resp.status_code}")
        print(f"推测编码: {resp.apparent_encoding}")
        print(f"实际编码: {resp.encoding}")

        # 提取标题
        match = re.search(r"<title>(.+?)</title>", resp.text)
        if match:
            print(f"标题: {match.group(1)}")
        return resp.text

    def search(self, keyword="Python"):
        """百度搜索 — params 参数演示"""
        print("\n" + "=" * 55)
        print(f"[百度搜索 — {keyword}]")
        print("=" * 55)

        resp = self.get("https://www.baidu.com/s",
                        params={"wd": keyword})
        print(f"状态码: {resp.status_code}")
        print(f"最终 URL: {resp.url}")
        print(f"内容长度: {len(resp.content)} bytes")

        if keyword in resp.content.decode("utf-8", errors="ignore"):
            print("验证: 搜索结果中包含关键词 ✓")
        else:
            print("提示: 可能需要添加更多 headers 或 cookie")


# ============================================================
# 示例 3: BiliSpider — B站 API JSON 响应
# ============================================================
class BiliSpider(BaseSpider):
    """
    B站搜索 API — 演示 JSON API 请求与响应解析
    对应笔记知识点: response.json() / headers伪装 / 接口分析
    """

    def search(self, keyword="Python爬虫"):
        """B站搜索 — JSON API"""
        print("=" * 55)
        print(f"[BiliSpider — B站搜索 {keyword}]")
        print("=" * 55)

        api = "https://api.bilibili.com/x/web-interface/search/all/v2"
        self.session.headers.update({"Referer": "https://www.bilibili.com/"})

        resp = self.get(api, params={"keyword": keyword, "page": 1})
        data = resp.json()

        if data["code"] != 0:
            print(f"API 错误: {data['message']}")
            return

        # 从混合结果中提取视频
        for item in data["data"].get("result", []):
            if item.get("result_type") == "video":
                videos = item.get("data", [])
                print(f"\n找到 {len(videos)} 个视频:")
                for i, v in enumerate(videos[:5]):
                    title = re.sub(r"<.*?>", "", v.get("title", ""))
                    play = v.get("play", 0)
                    author = v.get("author", "")
                    print(f"  {i+1}. {title[:30]}")
                    print(f"     作者: {author} | 播放: {play}")
                break

    def demo_json_api(self):
        """演示 JSON API 解析要点"""
        print("\n" + "=" * 55)
        print("[JSON API 解析要点]")
        print("=" * 55)

        resp = self.get("https://api.bilibili.com/x/web-interface/search/all/v2",
                        params={"keyword": "python", "page": 1})
        data = resp.json()

        print(f"状态码: {resp.status_code}")
        print(f"API code: {data['code']}")
        print(f"消息: {data.get('message', 'N/A')}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")

        print("\n识别 JSON API 三步走:")
        print("  1. F12 → Network → XHR 过滤")
        print("  2. 找到返回 JSON 的请求")
        print("  3. 查看 Preview 确认数据结构")
        print("\n提取工具: jsonpath / 手动 data['key']['subkey']")


# ============================================================
# 示例 4: CookieDemo — Cookie 与 Session 知识点演示
# ============================================================
class CookieDemo(BaseSpider):
    """Cookie 三种携带方式 + Session 自动保持"""

    def demo_three_ways(self):
        """演示 Cookie 三种携带方式"""
        print("=" * 55)
        print("[Cookie — 三种携带方式]")
        print("=" * 55)

        print("""
方式1 — headers 携带 (最快, 测试用):
    headers = {"Cookie": "sessionid=abc; csrftoken=xyz"}
    requests.get(url, headers=headers)

方式2 — cookies 参数 (推荐, 更清晰):
    cookies = {"sessionid": "abc"}
    requests.get(url, headers=headers, cookies=cookies)

方式3 — Session 自动管理 (最省心, 生产用):
    session = requests.Session()
    session.post(login_url, data=login_data)  # 登录
    session.get(page_url)                      # 自动带Cookie
    # 整个过程不用写一行Cookie代码!
        """)

        print("Cookie 字符串转字典:")
        print('  cookie_str = "key1=val1; key2=val2"')
        print("  cookies = {k.strip(): v.strip() for k,v in")
        print("      [item.split('=',1) for item in cookie_str.split(';') if '=' in item]}")

    def demo_five_sources(self):
        """POST data 五种来源"""
        print("\n" + "=" * 55)
        print("[POST data 五种来源]")
        print("=" * 55)

        print("""
每一种来源的判定方法:
  来源1 固定值  — 多次抓包值不变 (如 f、t、commit)
  来源2 输入值  — 随用户输入同步变化 (如 w、keyword)
  来源3 HTML提取 — F5刷新后值变化, 但HTML源码中能搜到 (如 token)
  来源4 其他响应 — 在某前置请求的响应体中 (如 ticket)
  来源5 JS生成  — 以上都找不到, 字段像密文 (如 sign、hash)

判定流程: 1→2→3→4→5 逐级排查
        """)

    def demo_session_keep(self):
        """Session 自动 Cookie 保持 — 百度验证"""
        print("=" * 55)
        print("[Session Cookie 自动保持]")
        print("=" * 55)

        resp1 = self.get("https://www.baidu.com/")
        print(f"请求1: status={resp1.status_code}, cookies数量={len(self.session.cookies)}")

        resp2 = self.get("https://www.baidu.com/")
        print(f"请求2: status={resp2.status_code}, cookies数量={len(self.session.cookies)}")

        print("\n核心理解:")
        print("  Session 内部维护 CookieJar")
        print("  每次收到 Set-Cookie → 自动存储")
        print("  每次发出请求 → 自动带上")


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  requests 爬虫 OOP 演示")
    print("=" * 55)

    # 示例 1: API 全功能
    print("\n=== 示例1: ApiTestSpider (JSONPlaceholder) ===\n")
    api = ApiTestSpider()
    api.run_all()

    # 示例 2: 百度
    print("\n\n=== 示例2: BaiduSpider ===\n")
    baidu = BaiduSpider()
    try:
        baidu.fetch_homepage()
        baidu.search("Python")
    except Exception as e:
        print(f"百度访问失败: {e}")

    # 示例 3: B站 API
    print("\n\n=== 示例3: BiliSpider ===\n")
    bili = BiliSpider()
    try:
        bili.search("Python爬虫")
        bili.demo_json_api()
    except Exception as e:
        print(f"B站API失败: {e}")

    # 示例 4: Cookie / Session
    print("\n\n=== 示例4: CookieDemo ===\n")
    cookie = CookieDemo()
    cookie.demo_three_ways()
    cookie.demo_five_sources()
    cookie.demo_session_keep()

    print("\n" + "=" * 55)
    print("  全部演示完成!")
    print("=" * 55)
