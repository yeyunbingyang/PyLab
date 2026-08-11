"""用户模块 Service 层 — 注册、登录、信息查询、信息修改、密码修改"""
# 参考：[[05 AI掘金头条-用户模块]]

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserToken
from app.core.security import hash_password, verify_password
from app.core.exceptions import BusinessException


async def register_user(db: AsyncSession, username: str, password: str) -> dict:
    """用户注册

    流程：
    1. 检查用户名是否已存在 → 存在则抛 BusinessException
    2. passlib bcrypt 加密密码
    3. add 创建用户
    4. 用 uuid.uuid4() 生成临时 Token
    5. 返回 Token + 用户信息
    """
    # 1. 检查是否已存在
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise BusinessException(message="用户名已存在")

    # 2. 创建用户
    user = User(
        username=username,
        password=hash_password(password),
        nickname=username,  # 默认昵称 = 用户名
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 3. 生成 Token
    token = str(uuid.uuid4())
    token_record = UserToken(token=token, user_id=user.id)
    db.add(token_record)
    await db.commit()

    return {"token": token, "user_info": user}


async def login_user(db: AsyncSession, username: str, password: str) -> dict:
    """用户登录

    流程：
    1. 按 username 查询用户
    2. passlib verify() 校验密码
    3. 生成新 Token
    4. 返回 Token + 用户信息
    """
    # 1. 查询用户
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise BusinessException(message="用户名或密码错误")

    # 2. 验证密码
    if not verify_password(password, user.password):
        raise BusinessException(message="用户名或密码错误")

    # 3. 生成 Token
    token = str(uuid.uuid4())
    token_record = UserToken(token=token, user_id=user.id)
    db.add(token_record)
    await db.commit()

    return {"token": token, "user_info": user}


async def get_user_info(db: AsyncSession, user: User) -> User:
    """获取当前登录用户信息 — 依赖 get_current_user 已查出 User"""
    return user


async def update_user_info(db: AsyncSession, user: User, update_data: dict) -> User:
    """修改用户信息 — 只更新传入的非 None 字段

    可修改字段：昵称、头像、性别、简介、手机号
    """
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(
    db: AsyncSession, user: User, old_password: str, new_password: str
) -> bool:
    """修改密码

    流程：
    1. verify 校验旧密码
    2. hash 加密新密码
    3. 更新 user.password
    """
    if not verify_password(old_password, user.password):
        raise BusinessException(message="旧密码错误")

    user.password = hash_password(new_password)
    await db.commit()
    return True
