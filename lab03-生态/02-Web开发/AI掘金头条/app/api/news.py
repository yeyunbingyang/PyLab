"""新闻模块 API — /api/news"""
# 参考：[[04 AI掘金头条-新闻模块]] 第三~七节

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.news import NewsCreate
from app.services import news_service

router = APIRouter(prefix="/api/news", tags=["新闻模块"])


# ── 获取新闻分类列表 ──────────────────────
# 缓存策略：Cache-Aside → 先查 Redis，未命中再查 MySQL
# 过期时间：7200s（分类变更频率低）
@router.get("/categories")
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    categories = await news_service.get_category_list(db, skip, limit)
    return success_response(data=categories)


# ── 获取新闻列表（分页+按分类过滤）─────────
# 缓存 Key: "news:list:{category_id}:{page}:{page_size}"
# 过期时间：600s
@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId", ge=1, description="分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    result = await news_service.get_news_list(db, category_id, page, page_size)
    return success_response(data=result)


# ── 获取新闻详情 ──────────────────────────
# 附带浏览量+1 + 相关新闻5条
@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id", ge=1),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException
    news = await news_service.get_news_detail(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 构造响应
    related = getattr(news, "_related_news", [])
    return success_response(data={
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "description": news.description,
        "image": news.image,
        "author": news.author,
        "category_id": news.category_id,
        "views": news.views,
        "publish_time": news.publish_time.isoformat() if news.publish_time else None,
        "related_news": [
            {"id": n.id, "title": n.title, "image": n.image, "views": n.views}
            for n in related
        ],
    })


# ── 新增新闻 ──────────────────────────────
@router.post("/create")
async def create_news(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
):
    news = await news_service.create_news(db, data.model_dump())
    return success_response(message="新闻创建成功", data=news)
