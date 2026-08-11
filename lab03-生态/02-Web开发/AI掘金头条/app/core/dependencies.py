"""认证依赖项 — 从 HTTP Header 提取 Token 并验证用户身份"""
# 参考：[[05 AI掘金头条-用户模块]] 第四节、第八节

from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserToken


async def get_token(authorization: str = Header(...)):
    """从请求头提取 Bearer Token

    HTTP 请求头格式：
    Authorization: Bearer <token>

    - Authorization → 专门放身份信息的请求头
    - Bearer → 表示"持有者令牌"的认证方案
    - <token>  → 真正的身份凭证
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None
    return token


async def get_current_user(
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    """验证 Token 并返回当前登录用户 — 若无效则返回 None

    流程：
    1. 从 Authorization Header 提取 token
    2. 查 user_token 表确认 token 存在
    3. 查 user 表返回关联的用户对象
    """
    if not token:
        return None

    from sqlalchemy import select

    # 查找 token 记录
    result = await db.execute(
        select(UserToken).where(UserToken.token == token)
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        return None

    # 查找对应用户
    user = await db.get(User, token_record.user_id)
    return user
