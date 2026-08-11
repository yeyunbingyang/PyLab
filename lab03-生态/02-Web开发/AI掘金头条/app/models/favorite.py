"""收藏模型 — favorite 表，含唯一约束"""
# 参考：[[06 AI掘金头条-收藏和浏览历史]] 第一节

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Favorite(Base):
    __tablename__ = "favorite"

    # UniqueConstraint → 同一用户不能重复收藏同一新闻
    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_user_news_favorite"),
        Index("idx_favorite_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
