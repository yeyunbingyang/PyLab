"""全局异常处理器 — 捕获各层异常，返回统一响应格式"""
# 参考：[[05 AI掘金头条-用户模块]] 第六节

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class BusinessException(Exception):
    """业务异常 — 如"用户已存在"、"旧密码错误"等"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常 → 400/自定义状态码"""
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """数据约束异常 — 如唯一约束冲突、外键不存在"""
    return JSONResponse(
        status_code=409,
        content={"code": 409, "message": "数据约束冲突，请检查参数唯一性或关联数据", "data": None},
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常 — 连接失败、事务错误等"""
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "数据库异常，请联系管理员", "data": None},
    )


async def global_exception_handler(request: Request, exc: Exception):
    """兜底 — 捕获所有未预期的异常"""
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": f"服务器内部异常: {str(exc)}", "data": None},
    )
