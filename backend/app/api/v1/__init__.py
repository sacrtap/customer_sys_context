"""
API v1 路由
"""

from sanic import Blueprint

from app.api.v1.routes import (
    auth,
    users,
    roles,
    customers,
    dashboard,
    settlements,
    health,
)

# 创建 v1 版本蓝图
api_v1_router = Blueprint.group(
    auth.bp,
    users.bp,
    roles.bp,
    customers.bp,
    dashboard.bp,
    settlements.bp,
    health.bp,
    url_prefix="/api/v1",
)
