"""浏览历史模型 — history 表"""
# 参考：[[06 AI掘金头条-收藏和浏览历史]] 第三节

from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class History(Base):
    __tablename__ = "history"

    __table_args__ = (
        Index("idx_history_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="浏览时间"
    )
