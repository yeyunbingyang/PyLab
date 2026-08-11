"""code03 — ORM 数据库操作：CRUD 完整示例

学习笔记：
- [[02 FastAPI进阶]] 第三节 ORM、第四节 数据库 CRUD
- [[03 ORM模板代码]] SQLAlchemy 配置 + News 模型

涵盖知识点：
- create_async_engine + 异步会话工厂
- 模型类继承 DeclarativeBase
- 依赖注入 get_database
- 查询 select() / 新增 add() / 更新 重新赋值 / 删除 delete()
- 条件查询 where()：比较、模糊 like()、与非 &|~、包含 in_()
- 聚合查询 func.count/avg/max/min/sum
- 分页查询 offset().limit()
- 全局异常处理 HTTPException
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, select, func, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


# ── ORM 引擎配置（code03 独立引擎，不依赖 main.py） ──
# 参考：[[03 ORM模板代码]] 第二节

ASYNC_DATABASE_URL = "mysql+aiomysql://root:1234@localhost:3306/pymysql?charset=utf8mb4"

# 异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── 数据库会话依赖项 ──────────────────────────
# 参考：[[02 FastAPI进阶]] → 三、ORM → 3.4 数据库会话依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── 模型基类 & Book 模型 ──────────────────
# 参考：[[02 FastAPI进阶]] → 三、ORM → 3.2 定义模型类

class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now(), default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now(), onupdate=func.now(), default=datetime.now, comment="修改时间")


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bookname: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column()

    def __repr__(self):
        return f"<Book(id={self.id}, name='{self.bookname}', price={self.price})>"

# CREATE TABLE `pymysql`.`book`  (
#     `id` int NOT NULL AUTO_INCREMENT,
# `bookname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
# `author` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
# `price` decimal(10, 2) NULL DEFAULT NULL,
# `create_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
# `update_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
# PRIMARY KEY (`id`) USING BTREE
# ) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;


# ── 路由前缀 ──────────────────────────────
router = APIRouter(prefix="/orm/book", tags=["03-ORM"])


# ── 建表事件（启动时执行） ──────────────────
# 参考：[[02 FastAPI进阶]] → 三、ORM → 3.3 创建数据库表
# async def create_tables():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# ── 查询所有 ──────────────────────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.1 查询
# scalars().all() → 获取所有数据

@router.get("/list")
async def list_books(db: AsyncSession = Depends(get_database)):
    """GET /orm/book/list — 查询所有图书"""
    result = await db.execute(select(Book))
    return result.scalars().all()


# ── 按 ID 查询 ────────────────────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.1 查询
# db.get(模型, 主键值) 或 scalars().first()

@router.get("/{book_id}")
async def get_book(book_id: int, db: AsyncSession = Depends(get_database)):
    """GET /orm/book/1 — 按主键查询，不存在返回 404"""
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"图书 {book_id} 不存在")
    return book


# ── 条件查询 —— 模糊 like() ──────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.2 查询条件 → 模糊查询
# % → 零个或多个字符，_ → 一个单个字符

@router.get("/search/{author}")
async def search_by_author(author: str, db: AsyncSession = Depends(get_database)):
    """GET /orm/book/search/曹雪芹 — 按作者模糊查询"""
    result = await db.execute(select(Book).where(Book.author.like(f"%{author}%")))
    return result.scalars().all()


# ── 聚合查询 ──────────────────────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.3 聚合查询
# func.count / func.avg / func.max / func.min / func.sum

@router.get("/stats/count")
async def count_books(db: AsyncSession = Depends(get_database)):
    """GET /orm/book/stats/count — 统计总数 + 均价"""
    total = (await db.execute(select(func.count(Book.id)))).scalar()
    avg_price = (await db.execute(select(func.avg(Book.price)))).scalar()
    return {"total": total, "avg_price": round(float(avg_price or 0), 2)}


# ── Pydantic 请求模型 ────────────────────
# 参考：[[01 FastAPI入门]] → 四、参数 → 4.3 请求体参数 → Field

class BookCreate(BaseModel):
    bookname: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)


class BookUpdate(BaseModel):
    bookname: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=255)
    price: float | None = Field(None, gt=0)


# ── 新增数据 ──────────────────────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.5 新增数据
# 步骤：创建 ORM 对象 → add() → commit() → refresh()

@router.post("/add")
async def add_book(data: BookCreate, db: AsyncSession = Depends(get_database)):
    """POST /orm/book/add — 新增一本图书"""
    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return {"message": "添加成功", "book": book}


# ── 更新数据（重新赋值） ──────────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.6 更新数据
# 步骤：get 查询 → 属性重新赋值 → commit

@router.put("/update/{book_id}")
async def update_book(book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_database)):
    """PUT /orm/book/update/1 — 部分更新（只改传来的字段）"""
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"图书 {book_id} 不存在")
    update_data = data.model_dump(exclude_unset=True)  # 获取非空字段
    for field, value in update_data.items():  # 逐个字段赋值
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return {"message": "更新成功", "book": book}


# ── update() 语句更新 ────────────────────
# 参考：[[04 AI掘金头条-新闻模块]] → 七、新闻详情 → update().where().values()

from sqlalchemy import update

@router.put("/price/{book_id}")
async def update_price(book_id: int, price: float, db: AsyncSession = Depends(get_database)):
    """PUT /orm/book/price/1?price=99.9 — 直接用 update 语句改价"""
    stmt = update(Book).where(Book.id == book_id).values(price=price)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"图书 {book_id} 不存在")
    return {"message": f"价格已更新为 {price}", "affected_rows": result.rowcount}


# ── 删除数据 ──────────────────────────────
# 参考：[[02 FastAPI进阶]] → 四、数据库操作 → 4.7 删除数据
# 步骤：get 查询 → delete() → commit

@router.delete("/delete/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_database)):
    """DELETE /orm/book/delete/1 — 删除一本图书"""
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"图书 {book_id} 不存在")
    await db.delete(book)
    await db.commit()
    return {"message": f"图书 {book_id} 已删除"}
