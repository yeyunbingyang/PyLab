"""收藏 & 浏览历史模块 API — /api/favorite /api/history"""
# 参考：[[06 AI掘金头条-收藏和浏览历史]]

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.behavior import FavoriteAddRequest, HistoryAddRequest
from app.services import behavior_service

# ── 收藏路由 ──────────────────────────────
favorite_router = APIRouter(prefix="/api/favorite", tags=["收藏模块"])

# ── 浏览历史路由 ──────────────────────────
history_router = APIRouter(prefix="/api/history", tags=["浏览历史"])

# ═══ 收藏 ═══════════════════════════════════

@favorite_router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId", ge=1),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        return success_response(data={"is_favorite": False})
    is_fav = await behavior_service.check_favorite(db, user.id, news_id)
    return success_response(data={"is_favorite": is_fav})


@favorite_router.post("/add")
async def add_favorite(
    data: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    fav = await behavior_service.add_favorite(db, user.id, data.news_id)
    return success_response(message="收藏成功", data=fav)


@favorite_router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId", ge=1),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    await behavior_service.remove_favorite(db, user.id, news_id)
    return success_response(message="取消收藏成功")


@favorite_router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    result = await behavior_service.get_favorite_list(db, user.id, page, page_size)
    return success_response(data=result)


@favorite_router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    count = await behavior_service.clear_favorite(db, user.id)
    return success_response(message=f"已清空 {count} 条收藏记录")


# ═══ 浏览历史 ═══════════════════════════════

@history_router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    hist = await behavior_service.add_history(db, user.id, data.news_id)
    return success_response(message="添加成功", data=hist)


@history_router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    result = await behavior_service.get_history_list(db, user.id, page, page_size)
    return success_response(data=result)


@history_router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    await behavior_service.delete_history(db, user.id, history_id)
    return success_response(message="删除成功")


@history_router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    count = await behavior_service.clear_history(db, user.id)
    return success_response(message=f"已清空 {count} 条浏览记录")
