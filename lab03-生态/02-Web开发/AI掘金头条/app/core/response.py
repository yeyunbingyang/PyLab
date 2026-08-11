"""统一响应格式 — success_response"""
# 参考：[[05 AI掘金头条-用户模块]] 第五节

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(message: str = "success", data=None):
    """封装通用成功响应格式 {code:200, message:..., data:...}

    jsonable_encoder 的作用：
    把任何 FastAPI/Pydantic/ORM 对象转换成可被 JSON 安全序列化的数据
    例如：datetime → "2026-06-19T12:00:00"，ORM lazy-load 属性不会触发
    """
    content = {"code": 200, "message": message, "data": data}
    return JSONResponse(content=jsonable_encoder(content))
