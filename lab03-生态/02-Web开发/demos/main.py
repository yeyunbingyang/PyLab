"""FastAPI 基础演示 — 笔记配套代码

运行: uvicorn main:app --reload
访问: http://127.0.0.1:8000/docs

包含笔记对应代码：
- [[01 FastAPI入门]]：同步/异步、参数（Path/Query/Field）
- [[02 FastAPI进阶]]：中间件、依赖注入、ORM CRUD
- [[03 ORM模板代码]]：SQLAlchemy 配置
"""

from fastapi import FastAPI

app = FastAPI(
    title="FastAPI 基础演示",
    description="[[01 FastAPI入门]] + [[02 FastAPI进阶]] 配套代码",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Hello World", "docs": "/docs"}


# ── 挂载 demos 路由 ──────────────────────
import code01_快速入门, code02_参数

app.include_router(code01_快速入门.router)
app.include_router(code02_参数.router)

# code03_ORM 使用独立引擎，解除注释即可挂载
import code03_ORM
app.include_router(code03_ORM.router)
