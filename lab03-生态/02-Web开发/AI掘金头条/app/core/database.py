"""数据库引擎配置 — create_async_engine + 异步会话工厂 + get_db 依赖项"""
# 参考：[[02 FastAPI进阶]] 3.1~3.4 节、[[03 ORM模板代码]] 第二节

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库连接 URL — mysql+aiomysql 异步驱动
# 格式：mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
ASYNC_DATABASE_URL = "mysql+aiomysql://root:1234@localhost:3306/pymysql?charset=utf8mb4"

# 创建异步引擎 — FastAPI 推荐全局单例
# echo=True      → 控制台输出每句 SQL，开发期调试用
# pool_size=10   → 连接池常驻连接数
# max_overflow=20 → 连接池允许临时多开的连接数（满载上限 10+20=30）
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

# 创建异步会话工厂 — 每次请求调用 get_db 时从中取一个会话
# expire_on_commit=False → commit 后 ORM 对象不会过期，可在返回到 Pydantic 时继续读取
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """数据库会话依赖项 — 通过 Depends(get_db) 注入到路由处理函数中

    设计模式：yield + try/except/finally
    - yield 之前：建立会话
    - yield 中间：路由处理函数使用会话
    - finally：无论成功或异常，确保会话关闭，连接归还连接池
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()   # 无异常则提交
        except Exception:
            await session.rollback()  # 有异常则回滚
            raise
        finally:
            await session.close()     # 关闭会话，归还连接池
