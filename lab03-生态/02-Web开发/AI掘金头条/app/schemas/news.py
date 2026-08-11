"""Pydantic 请求/响应 Schema — 新闻模块"""
# 参考：[[01 FastAPI入门]] 第六节 response_model、[[04 AI掘金头条-新闻模块]]

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ── 分类 ──

class CategoryInfo(BaseModel):
    """新闻分类响应"""
    id: int
    name: str
    description: str | None = None
    icon: str | None = None
    model_config = ConfigDict(from_attributes=True)


# ── 新闻 ──

class NewsBrief(BaseModel):
    """新闻摘要（列表用）"""
    id: int
    title: str
    description: str | None = None
    image: str | None = None
    author: str | None = None
    category_id: int
    views: int
    publish_time: datetime
    model_config = ConfigDict(from_attributes=True)


class NewsDetail(BaseModel):
    """新闻详情（含正文 + 相关新闻）"""
    id: int
    title: str
    content: str
    description: str | None = None
    image: str | None = None
    author: str | None = None
    category_id: int
    views: int
    publish_time: datetime
    related_news: list["NewsBrief"] = []
    model_config = ConfigDict(from_attributes=True)


class NewsListResult(BaseModel):
    """新闻列表分页结果"""
    list: list[NewsBrief]
    total: int
    page: int
    page_size: int
    has_more: bool


class NewsCreate(BaseModel):
    """新增新闻请求"""
    title: str = Field(..., min_length=2, max_length=255, description="新闻标题")
    content: str = Field(..., min_length=1, description="新闻内容")
    description: str | None = Field(None, max_length=500)
    image: str | None = Field(None, max_length=255)
    author: str | None = Field(None, max_length=50)
    category_id: int = Field(..., gt=0, description="分类ID")
