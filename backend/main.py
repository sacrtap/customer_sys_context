"""
客户运营中台 API 服务
"""

from sanic import Sanic
from sanic_cors import CORS
from sanic_ext import Extend

from config import settings
from app.api.v1 import api_v1_router
from app.database import database, async_session_maker


def create_app() -> Sanic:
    """创建 Sanic 应用实例"""

    app = Sanic(__name__)

    # 配置
    app.config.update(
        {
            "DEBUG": settings.DEBUG,
            "RESPONSE_TIMEOUT": 60,
            "REQUEST_TIMEOUT": 60,
            "KEEP_ALIVE_TIMEOUT": 30,
            "REQUEST_MAX_SIZE": settings.MAX_UPLOAD_SIZE,
        }
    )

    # CORS
    CORS(app, origins=settings.CORS_ORIGINS)

    # Sanic Ext
    Extend(app)

    # 数据库连接
    @app.before_server_start
    async def init_db(app, loop):
        await database.connect()
        # 注册 db 上下文
        app.ctx.db = lambda: async_session_maker()

    @app.after_server_stop
    async def close_db(app, loop):
        await database.disconnect()

    # 注册蓝图（api_v1_router 已经包含 /api/v1 前缀）
    app.blueprint(api_v1_router)

    # 根路径
    @app.get("/")
    async def root(request):
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }

    return app


# 全局 app 实例（用于测试导入）
app = create_app()


# 仅在直接运行时创建实例
if __name__ == "__main__":
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
        auto_reload=settings.DEBUG,
    )
