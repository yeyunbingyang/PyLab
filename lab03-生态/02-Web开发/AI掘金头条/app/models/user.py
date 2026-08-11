"""用户模型 — user 表 + user_token 表"""
# 参考：[[05 AI掘金头条-用户模块]]

from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码（bcrypt密文）")
    nickname: Mapped[str | None] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[str | None] = mapped_column(String(255), comment="头像URL")
    gender: Mapped[int | None] = mapped_column(Integer, default=0, comment="性别：0未知 1男 2女")
    bio: Mapped[str | None] = mapped_column(String(500), comment="个人简介")
    phone: Mapped[str | None] = mapped_column(String(20), comment="手机号")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")


class UserToken(Base):
    """Token 表 — 记录用户的登录凭证

    为什么需要独立表而非存于 user 表？
    - 一个用户可能有多个设备同时登录，每个设备一个 Token
    - 前端保存 Token，每次请求携带在 Authorization Header
    """
    __tablename__ = "user_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="UUID Token")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="关联用户ID")
