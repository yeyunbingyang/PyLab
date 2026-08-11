"""SQLAlchemy 声明式基类 — 包含通用时间字段"""
# 参考：[[02 FastAPI进阶]] 3.2 节、[[03 ORM模板代码]] 第三节

from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """所有 ORM 模型类的基类

    自动为每张表添加：
    - create_time → 创建时间，写入时自动填充
    - update_time → 更新时间，写入和修改时自动填充
    """
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now(),
        default=datetime.now,
        comment="创建时间",
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now(),
        onupdate=func.now(),
        default=datetime.now,
        comment="修改时间",
    )
