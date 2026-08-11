"""新闻分类模型 — news_category 表"""
# 参考：[[04 AI掘金头条-新闻模块]] 第五节

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Category(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类名称")
    description: Mapped[str | None] = mapped_column(String(255), comment="分类描述")
    icon: Mapped[str | None] = mapped_column(String(255), comment="分类图标URL")
