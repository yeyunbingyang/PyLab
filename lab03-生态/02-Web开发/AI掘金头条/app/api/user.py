"""用户模块 API — /api/user"""
# 参考：[[05 AI掘金头条-用户模块]]

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserUpdateRequest, UserChangePwdRequest,
    UserInfoResponse, UserAuthResponse,
)
from app.services import user_service

router = APIRouter(prefix="/api/user", tags=["用户模块"])


# ── 用户注册 ──────────────────────────────
# 流程：检查用户名唯一 → bcrypt 加密密码 → add → uuid生成Token → 返回token+userInfo
@router.post("/register")
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await user_service.register_user(db, data.username, data.password)
    token = result["token"]
    user = result["user_info"]
    response = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )
    return success_response(message="注册成功", data=response)


# ── 用户登录 ──────────────────────────────
# 流程：查用户 → verify 密码 → 生成Token → 返回token+userInfo
@router.post("/login")
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await user_service.login_user(db, data.username, data.password)
    token = result["token"]
    user = result["user_info"]
    response = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )
    return success_response(message="登录成功", data=response)


# ── 获取用户信息 ──────────────────────────
# Header Authorization: Bearer <token> → 查token表 → 查user表 → 返回
@router.get("/info")
async def get_info(
    user: User = Depends(get_current_user),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    return success_response(data=UserInfoResponse.model_validate(user))


# ── 修改用户信息 ──────────────────────────
# 可修改：昵称、头像、性别、简介、手机号
@router.put("/update")
async def update_info(
    data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    updated = await user_service.update_user_info(db, user, data.model_dump(exclude_unset=True))
    return success_response(message="更新成功", data=UserInfoResponse.model_validate(updated))


# ── 修改密码 ──────────────────────────────
# 流程：验证旧密码 → hash新密码 → 更新
@router.put("/password")
async def change_password(
    data: UserChangePwdRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        from app.core.exceptions import BusinessException
        raise BusinessException(message="请先登录", code=401)
    await user_service.change_password(db, user, data.old_password, data.new_password)
    return success_response(message="密码修改成功")
