"""
数据库配置
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session 工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base 类
Base = declarative_base()


class Database:
    """数据库连接管理"""

    async def connect(self):
        """连接数据库"""
        await engine.connect()
        print(f"✓ 数据库连接成功：{settings.DATABASE_URL}")

    async def disconnect(self):
        """断开数据库连接"""
        await engine.dispose()
        print("✓ 数据库连接已关闭")

    async def session(self) -> AsyncSession:
        """获取数据库会话"""
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


database = Database()


async def get_db() -> AsyncSession:
    """获取数据库会话依赖"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
