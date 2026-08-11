"""Pydantic 请求/响应 Schema — 用户模块"""
# 参考：[[05 AI掘金头条-用户模块]]

from pydantic import BaseModel, Field, ConfigDict


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdateRequest(BaseModel):
    """修改用户信息请求 — 全部可选，传什么改什么"""
    nickname: str | None = Field(None, max_length=50, description="昵称")
    avatar: str | None = Field(None, max_length=255, description="头像URL")
    gender: int | None = Field(None, ge=0, le=2, description="性别：0未知 1男 2女")
    bio: str | None = Field(None, max_length=500, description="个人简介")
    phone: str | None = Field(None, max_length=20, description="手机号")


class UserChangePwdRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=128, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = None
    bio: str | None = None
    phone: str | None = None
    model_config = ConfigDict(from_attributes=True)


class UserAuthResponse(BaseModel):
    """认证响应（注册/登录成功后返回 Token + 用户信息）"""
    token: str
    user_info: UserInfoResponse
    model_config = ConfigDict(from_attributes=True)
