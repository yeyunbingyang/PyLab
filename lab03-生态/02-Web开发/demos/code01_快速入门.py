"""code01 — 快速入门：同步 vs 异步、Pydantic 请求体

学习笔记：[[01 FastAPI入门]] 第一、四节
- 同步 vs 异步：并发处理 vs 逐个阻塞
- Pydantic 类型提示与验证
- 请求体参数
"""

import time
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/start", tags=["01-快速入门"])


# ── 同步 vs 异步对比 ──────────────────────
# 参考：[[01 FastAPI入门]] → 核心特性 → 同步与异步
# 同步：逐个 sleep(1) × 10，总耗时 ≈ 10s
# 异步：gather 并发 sleep(1) × 10，总耗时 ≈ 1s

@router.get("/sync")
def func_sync():
    """同步接口 — 阻塞执行，每个 I/O 等上一个完成"""
    start = time.time()
    for i in range(10):
        time.sleep(1)
    end = time.time()
    return {"mode": "sync", "time": f"{end - start:.2f}s"}


@router.get("/async")
async def func_async():
    """异步接口 — await 期间可处理其他请求"""
    start = time.time()
    tasks = [asyncio.sleep(1) for _ in range(10)]
    await asyncio.gather(*tasks)
    end = time.time()
    return {"mode": "async", "time": f"{end - start:.2f}s"}


# ── 请求体参数 — Pydantic 验证 ────────────
# 参考：[[01 FastAPI入门]] → 四、参数 → 4.3 请求体参数
# Field → 类型注解，... 表示必填

class User(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(user: User):
    """POST 注册 — Pydantic 自动校验请求体"""
    return {"message": "注册成功", "username": user.username}
