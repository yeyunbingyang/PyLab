from DrissionPage import Chromium
import time
from datetime import datetime

# 连接浏览器
browser = Chromium(9333)
tab = browser.latest_tab

# 获取当天日期，格式: 2026/06/18
today = datetime.now().strftime('%Y/%m/%d')
# today = '2026/06/17'
print(f"目标日期: {today}")

results = []
page = 1

while True:
    # 构造列表页 URL
    if page == 1:
        list_url = 'https://supjav.com/ja/category/reducing-mosaic'
    else:
        list_url = f'https://supjav.com/ja/category/reducing-mosaic/page/{page}'

    print(f"\n{'='*60}")
    print(f"【第 {page} 页】{list_url}")

    tab.get(list_url)

    # 等待列表加载
    if not tab.wait.eles_loaded('xpath://div[@class="post"]', timeout=10):
        print("页面无数据或加载超时，结束")
        break

    posts = tab.eles('xpath://div[@class="post"]')
    if not posts:
        print("未找到帖子，结束")
        break

    stop_crawl = False   # 标记是否遇到非当天日期

    # 遍历本页帖子，边收集基础信息边进详情页
    for idx, post in enumerate(posts, 1):
        meta = post.ele('xpath:.//div[@class="meta"]', timeout=1)
        if not meta:
            continue

        # 提取日期（meta 文本第一行）
        date_str = meta.raw_text.split('\n')[0].strip()

        # 日期不是当天 → 结束整个抓取（列表按时间倒序）
        if date_str != today:
            print(f"遇到非当天日期: {date_str}，停止抓取")
            stop_crawl = True
            break  # 跳出 for

        # 是当天 → 提取基础字段
        href = post.ele('xpath:.//a[@class="img"]').attr('href')
        title = post.ele('xpath:.//a[@class="img"]').attr('title')
        img = post.ele('xpath:.//img').attr('data-original')
        views = post.ele('xpath:.//span[@class="date"]').text if post.ele('xpath:.//span[@class="date"]') else ''

        print(f"  [{idx}/{len(posts)}] {href}")

        # 在新标签页打开详情页（列表页不动，元素不失效）
        detail_tab = browser.new_tab(href)
        detail_tab.wait.eles_loaded('xpath://div[@class="cats"]', timeout=5)

        try:
            # Maker
            maker_ele = detail_tab.ele('xpath://div[@class="cats"]/p[span[contains(text(),"Maker")]]/a', timeout=2)
            maker = maker_ele.text if maker_ele else ''

            # Cast
            cast_ele = detail_tab.ele('xpath://div[@class="cats"]/p[span[contains(text(),"Cast")]]/a', timeout=2)
            cast = cast_ele.text if cast_ele else ''

            print(f"    日期: {date_str} | 浏览: {views}")
            print(f"    Maker: {maker} | Cast: {cast}")

            # 合并为完整记录
            results.append({
                'href': href,
                'title': title,
                'img': img,
                'date': date_str,
                'views': views,
                'maker': maker,
                'cast': cast,
            })

        except Exception as e:
            print(f"    解析详情失败: {e}")
            results.append({
                'href': href, 'title': title, 'img': img,
                'date': date_str, 'views': views,
                'maker': '', 'cast': ''
            })

        finally:
            # 关闭详情页标签，回到列表页
            detail_tab.close()

        time.sleep(1)  # 礼貌延时

    # 本页遇到非当天日期，结束外层循环
    if stop_crawl:
        break

    page += 1

# 最终结果输出
print(f"\n{'='*60}")
print(f"共抓取 {len(results)} 条 {today} 的数据")
print('='*60)

for r in results:
    print(f"\n日期: {r['date']} | 浏览: {r['views']}")
    print(f"Maker: {r['maker']} | Cast: {r['cast']}")
    print(f"链接: {r['href']}")
    print(f"标题: {r['title'][:50]}...")
    print(f"图片: {r['img']}")
    print("-" * 60)

# 保存到 JSON
import json
with open(f'results_{today.replace("/", "-")}.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n已保存到 results_{today.replace('/', '-')}.json")