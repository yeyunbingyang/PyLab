"""code02 — 路径参数、查询参数、请求体 Field 校验

学习笔记：[[01 FastAPI入门]] 第四、五节
- 路径参数 + Path 类型注解（ge/le/min_length/max_length）
- 查询参数 + Query 类型注解（default/ge/le/min_length/max_length）
- 请求体参数 + Field 类型注解（必填/默认值/长度/范围）
- 响应类型：response_model

练习场景：图书查询系统
"""

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/book", tags=["02-参数"])


# ── 路径参数 ──────────────────────────────
# 参考：[[01 FastAPI入门]] → 四、参数 → 4.1 路径参数
# Path 参数说明：
#   ... → 必填
#   ge/gt → 大于等于/大于
#   le/lt → 小于等于/小于
#   min_length/max_length → 字符串长度限制

@router.get("/{id}")
async def get_book(
    id: int = Path(..., ge=1, description="图书 ID"),
):
    """路径参数 — /book/{id}，要求 id >= 1"""
    return {"id": id, "title": f"这是第{id}本书"}


# ── 查询参数 ──────────────────────────────
# 参考：[[01 FastAPI入门]] → 四、参数 → 4.2 查询参数
# 声明的参数不是路径参数时，自动解释为查询参数

@router.get("/")
async def search_book(
    category: str = Query(default="Python开发", min_length=2, max_length=255, description="图书分类"),
    price: float = Query(default=0, ge=0, le=999, description="价格上限"),
    skip: int = Query(default=0, ge=0, description="跳过条数"),
    limit: int = Query(default=10, ge=1, le=100, description="每页条数"),
):
    """查询参数 — /book/?category=Python开发&price=50&skip=0&limit=10"""
    return {
        "category": category,
        "price": price,
        "skip": skip,
        "limit": limit,
    }


# ── 请求体参数 + Field 注解 ──────────────
# 参考：[[01 FastAPI入门]] → 四、参数 → 4.3 请求体参数 → Field 注解
# Field 参数说明：
#   ... → 必填
#   default → 默认值
#   gt/ge → 大于/大于等于
#   min_length/max_length → 长度限制

class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=20, description="书名")
    author: str = Field(min_length=2, max_length=10, description="作者")
    publisher: str = Field(default="黑马出版社", description="出版社")
    price: float = Field(..., gt=0, description="售价")


@router.post("/add")
async def add_book(book: BookCreate):
    """POST /book/add — 新增图书（请求体 + Field 校验）"""
    return book
