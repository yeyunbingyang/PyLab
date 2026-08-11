"""FastAPI 主入口 — AI掘金头条 新闻项目
=== 参考笔记 ===
- [[01 FastAPI入门]]：路由、参数、响应类型、response_model、异常处理
- [[02 FastAPI进阶]]：中间件、依赖注入、ORM 数据库操作
- [[03 ORM模板代码]]：SQLAlchemy 配置模板
- [[04 AI掘金头条-新闻模块]]：模块化路由 + CORS
- [[05 AI掘金头条-用户模块]]：passlib 密码加密 + Token 认证 + 通用响应 + 异常处理器
- [[06 AI掘金头条-收藏和浏览历史]]：收藏/浏览历史 CRUD + 联表查询 + 唯一约束
- [[07 AI掘金头条-缓存和调用模型]]：Redis 缓存 + Cache-Aside 策略

=== 运行 ===
uvicorn main:app --reload
访问 http://127.0.0.1:8000/docs 查看交互式 API 文档
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.database import async_engine
from app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    integrity_exception_handler,
    sqlalchemy_exception_handler,
    global_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：
    startup  → 创建所有数据库表（Base.metadata.create_all）
    shutdown → 释放数据库连接池
    """
    from app.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


app = FastAPI(
    title="AI掘金头条 API",
    description="FastAPI 全栈实战项目 — 新闻模块 + 用户模块 + 收藏/历史 + Redis缓存",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS 中间件 — 允许前端跨域调用 ──────────────────
# 前端 Vue (http://localhost:5173) → 后端 FastAPI (http://127.0.0.1:8000)
# 协议相同(http)，但域名/端口不同 → 跨域。CORS 中间件让后端主动声明"允许访问"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许的源（生产环境建议限制具体域名）
    allow_credentials=True,    # 允许携带 Cookie
    allow_methods=["*"],       # 允许所有 HTTP 方法
    allow_headers=["*"],       # 允许所有请求头
)

# ── 全局异常处理器 — 注册顺序：具体异常在前，兜底在后 ──
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# ── 根路由 ───────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "AI掘金头条 API 服务运行中", "docs": "/docs"}


# ── 挂载模块路由 — include_router 实现模块化 ──────
from app.api.news import router as news_router
from app.api.user import router as user_router
from app.api.behavior import favorite_router, history_router

app.include_router(news_router)
app.include_router(user_router)
app.include_router(favorite_router)
app.include_router(history_router)
