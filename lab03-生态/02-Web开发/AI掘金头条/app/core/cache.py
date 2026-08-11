"""Redis 缓存操作封装 — setex / get / delete / exists"""
# 参考：[[07 AI掘金头条-缓存和调用模型]] 第二、三节

import redis.asyncio as aioredis

# Redis 客户端（懒初始化）
_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 客户端单例

    配置说明：
    - host: Redis 服务器地址（本地默认 localhost）
    - port: 6379 是 Redis 默认端口
    - db: 0 是第一个逻辑数据库（Redis 有 0~15 共 16 个数据库）
    - decode_responses=True → 返回数据自动从 bytes 解码为 str
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
        )
    return _redis_client


# ── 缓存操作方法 ──

async def cache_set(key: str, value: str, expire: int = 600):
    """设置缓存并指定过期时间（秒）
    常见 TTL：
    - 分类/配置 → 7200s（2小时）
    - 列表数据  → 600s（10分钟）
    - 详情数据  → 1800s（30分钟）
    """
    r = await get_redis()
    await r.setex(key, expire, value)


async def cache_get(key: str) -> str | None:
    """获取缓存值，不存在返回 None"""
    r = await get_redis()
    return await r.get(key)


async def cache_delete(key: str):
    """删除指定缓存键"""
    r = await get_redis()
    await r.delete(key)


async def cache_exists(key: str) -> bool:
    """检查缓存键是否存在"""
    r = await get_redis()
    return await r.exists(key) > 0
