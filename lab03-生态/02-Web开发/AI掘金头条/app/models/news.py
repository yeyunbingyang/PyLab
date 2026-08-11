"""新闻模型 — news 表，含索引、外键"""
# 参考：[[03 ORM模板代码]] 第三节、[[04 AI掘金头条-新闻模块]]

from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class News(Base):
    __tablename__ = "news"

    # 创建索引 — 提升查询速度
    # fk_news_category_idx  → 按分类 ID 查询新闻的索引
    # idx_publish_time      → 按发布时间排序/筛选的索引
    __table_args__ = (
        Index("fk_news_category_idx", "category_id"),
        Index("idx_publish_time", "publish_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[str | None] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[str | None] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[str | None] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("news_category.id"), nullable=False, comment="分类ID"
    )
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="发布时间"
    )

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"
