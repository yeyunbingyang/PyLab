"""新闻模块 Service 层 — 封装数据库操作及缓存逻辑"""
# 参考：[[04 AI掘金头条-新闻模块]]、[[07 AI掘金头条-缓存和调用模型]] 第四节

import json
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News
from app.core.cache import cache_get, cache_set, cache_delete


# ── 分类 ──────────────────────────────────

async def get_category_list(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list:
    """查询新闻分类列表 — 带缓存

    缓存策略（Cache-Aside / 旁路缓存）：
    1. 先查 Redis 缓存
    2. 命中 → 直接返回
    3. 未命中 → 查数据库 → 写入缓存 → 返回

    缓存 Key: "categories"
    过期时间: 7200s（分类变更频率低）
    """
    cache_key = "categories"

    # 1. 尝试从缓存获取
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 查数据库
    from app.models.category import Category
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # 3. 写入缓存
    if categories:
        # 转为可 JSON 序列化的结构
        data = [{"id": c.id, "name": c.name, "description": c.description, "icon": c.icon} for c in categories]
        await cache_set(cache_key, json.dumps(data, ensure_ascii=False), expire=7200)

    return categories


async def invalidate_category_cache():
    """当分类数据变更时清除缓存"""
    await cache_delete("categories")


# ── 新闻列表（分页 + 按分类过滤）──────────

async def get_news_list(
    db: AsyncSession,
    category_id: int,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """分页查询新闻列表 — 带缓存

    - offset = (page - 1) * page_size
    - has_more = (offset + 当前条数) < 总量

    缓存 Key: "news:list:{category_id}:{page}:{page_size}"
    过期时间: 600s（列表数据更新频率中等）
    """
    cache_key = f"news:list:{category_id}:{page}:{page_size}"

    # 1. 尝试缓存
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 查数据库
    skip = (page - 1) * page_size
    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc())
        .offset(skip)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 统计总量
    count_stmt = select(func.count(News.id)).where(News.category_id == category_id)
    total = (await db.execute(count_stmt)).scalar()

    # 计算是否有更多
    has_more = (skip + len(news_list)) < total

    data = {
        "list": news_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
    }

    # 3. 写入缓存
    await cache_set(cache_key, json.dumps(data, ensure_ascii=False, default=str), expire=600)

    return data


async def invalidate_news_list_cache(category_id: int):
    """新增/修改新闻后清除相关列表缓存"""
    await cache_delete(f"news:list:{category_id}:*")


# ── 新闻详情 ──────────────────────────────

async def get_news_detail(db: AsyncSession, news_id: int) -> News | None:
    """查询新闻详情 + 浏览量 +1 + 返回相关新闻

    缓存 Key: "news:detail:{news_id}"
    过期时间: 1800s
    """
    # 1. 查新闻
    news = await db.get(News, news_id)
    if not news:
        return None

    # 2. 浏览量 +1（update 语句，不走 ORM 对象，避免竞态条件）
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    await db.execute(stmt)
    await db.commit()

    # 3. 查询相关新闻（同分类，排除当前，按浏览量降序取前5）
    related_stmt = (
        select(News)
        .where(News.category_id == news.category_id, News.id != news_id)
        .order_by(News.views.desc())
        .limit(5)
    )
    related_result = await db.execute(related_stmt)
    related_news = related_result.scalars().all()

    # 手动附上相关新闻（不在 ORM 字段里）
    news._related_news = related_news
    return news


# ── 新闻新增 ────────────────────────────────

async def create_news(db: AsyncSession, data: dict) -> News:
    """新增新闻"""
    news = News(**data)
    db.add(news)
    await db.commit()
    await db.refresh(news)
    # 清除相关缓存
    await invalidate_category_cache()
    return news
