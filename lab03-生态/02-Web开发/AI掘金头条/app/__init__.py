# app — AI掘金头条 项目主包
# 各子模块按层划分：
#   models   → ORM 模型
#   schemas  → Pydantic 请求/响应
#   services → 业务逻辑
#   api      → 路由
#   core     → 基础设施（数据库、安全、缓存、异常、认证依赖）

from . import models, schemas, services, api, core
