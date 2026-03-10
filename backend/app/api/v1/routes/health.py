"""
健康检查 API
"""

import time
from sanic import Blueprint, json
from datetime import datetime

bp = Blueprint("health", url_prefix="/health")

# 应用启动时间
START_TIME = time.time()


@bp.get("")
async def health_check(request):
    """
    健康检查接口

    返回系统健康状态，包括：
    - 数据库连接状态
    - API 版本信息
    - 运行时间统计

    该接口不需要认证
    """
    from app.database import database

    # 检查数据库连接
    db_status = "connected"
    try:
        # 尝试执行简单查询验证连接
        async with request.app.ctx.db() as session:
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "disconnected"

    # 计算运行时间
    uptime = time.time() - START_TIME

    return json(
        {
            "status": "healthy" if db_status == "connected" else "degraded",
            "database": {
                "status": db_status,
            },
            "version": {
                "api_version": "v1",
                "build_time": datetime.now().isoformat(),
            },
            "uptime": round(uptime, 2),
            "timestamp": datetime.now().isoformat(),
        }
    )
