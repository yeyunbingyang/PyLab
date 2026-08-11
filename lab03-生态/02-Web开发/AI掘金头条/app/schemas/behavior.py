"""Pydantic 请求 Schema — 收藏与浏览历史模块"""
# 参考：[[06 AI掘金头条-收藏和浏览历史]]

from pydantic import BaseModel, Field


class FavoriteAddRequest(BaseModel):
    """添加收藏请求"""
    news_id: int = Field(..., alias="newsId", description="新闻ID")


class HistoryAddRequest(BaseModel):
    """添加浏览记录请求"""
    news_id: int = Field(..., alias="newsId", description="新闻ID")
