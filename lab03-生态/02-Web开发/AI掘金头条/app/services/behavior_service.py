"""收藏 & 浏览历史模块 Service 层"""
# 参考：[[06 AI掘金头条-收藏和浏览历史]]

from datetime import datetime
from sqlalchemy import select, func, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.models.history import History
from app.models.news import News
from app.core.exceptions import BusinessException


# ═══ 收藏 ═══════════════════════════════════════

async def check_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """检查当前用户是否已收藏指定新闻"""
    result = await db.execute(
        select(Favorite).where(
            and_(Favorite.user_id == user_id, Favorite.news_id == news_id)
        )
    )
    return result.scalar_one_or_none() is not None


async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> Favorite:
    """添加收藏"""
    # 1. 检查新闻是否存在
    news = await db.get(News, news_id)
    if not news:
        raise BusinessException(message="新闻不存在", code=404)

    # 2. 检查是否已收藏（UniqueConstraint 会兜底）
    existing = await db.execute(
        select(Favorite).where(
            and_(Favorite.user_id == user_id, Favorite.news_id == news_id)
        )
    )
    if existing.scalar_one_or_none():
        raise BusinessException(message="已收藏，请勿重复操作")

    fav = Favorite(user_id=user_id, news_id=news_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int):
    """取消收藏"""
    result = await db.execute(
        delete(Favorite).where(
            and_(Favorite.user_id == user_id, Favorite.news_id == news_id)
        )
    )
    await db.commit()
    if result.rowcount == 0:
        raise BusinessException(message="未收藏该新闻", code=404)


async def get_favorite_list(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10
) -> dict:
    """获取收藏列表 — 联表查询（Favorite JOIN News）

    ORM 联表查询写法：
    select(主模型, 关联字段.label("别名")).join(关联模型, join条件)
    """
    skip = (page - 1) * page_size

    # 联表查询
    stmt = (
        select(
            News,
            Favorite.created_at.label("favorite_time"),
            Favorite.id.label("favorite_id"),
        )
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(skip)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # 统计总量
    count_stmt = (
        select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    )
    total = (await db.execute(count_stmt)).scalar()

    has_more = (skip + len(rows)) < total

    return {
        "list": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
    }


async def clear_favorite(db: AsyncSession, user_id: int) -> int:
    """清空收藏列表 — 返回删除条数"""
    result = await db.execute(delete(Favorite).where(Favorite.user_id == user_id))
    await db.commit()
    return result.rowcount


# ═══ 浏览历史 ═════════════════════════════════

async def add_history(db: AsyncSession, user_id: int, news_id: int):
    """添加浏览记录 — 若已浏览则更新时间，否则新增"""
    # 检查是否已浏览过
    result = await db.execute(
        select(History).where(
            and_(History.user_id == user_id, History.news_id == news_id)
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        # 已浏览 → 更新浏览时间
        existing.viewed_at = datetime.now()
        await db.commit()
        return existing

    # 未浏览 → 新增
    hist = History(user_id=user_id, news_id=news_id)
    db.add(hist)
    await db.commit()
    await db.refresh(hist)
    return hist


async def get_history_list(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10
) -> dict:
    """获取浏览历史列表 — 联表查询（History JOIN News）"""
    skip = (page - 1) * page_size

    stmt = (
        select(
            News,
            History.viewed_at.label("viewed_at"),
            History.id.label("history_id"),
        )
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.viewed_at.desc())
        .offset(skip)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.all()

    total = (await db.execute(
        select(func.count(History.id)).where(History.user_id == user_id)
    )).scalar()

    has_more = (skip + len(rows)) < total

    return {
        "list": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
    }


async def delete_history(db: AsyncSession, user_id: int, history_id: int):
    """删除单条浏览记录"""
    result = await db.execute(
        delete(History).where(
            and_(History.id == history_id, History.user_id == user_id)
        )
    )
    await db.commit()
    if result.rowcount == 0:
        raise BusinessException(message="记录不存在或无权操作", code=404)


async def clear_history(db: AsyncSession, user_id: int) -> int:
    """清空浏览历史 — 返回删除条数"""
    result = await db.execute(delete(History).where(History.user_id == user_id))
    await db.commit()
    return result.rowcount
