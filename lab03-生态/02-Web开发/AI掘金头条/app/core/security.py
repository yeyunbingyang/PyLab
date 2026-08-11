"""密码加密与校验 — passlib + bcrypt"""
# 参考：[[05 AI掘金头条-用户模块]] 第三节

from passlib.context import CryptContext

# 创建加密上下文 — schemes=["bcrypt"] 使用 bcrypt 哈希算法
# deprecated="auto" → passlib 自动处理算法升级迁移
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """明文密码 → bcrypt 密文"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """明文 vs 密文 → 是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)
