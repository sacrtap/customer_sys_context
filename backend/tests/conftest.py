import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import create_app
from app.database import database, async_session_maker
from app.models.customer import (
    Customer,
    Industry,
    CustomerLevel,
    CustomerStatus,
    SettlementStatus,
)
from app.models.user import User

# 默认测试管理员账号
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="session")
def app():
    """创建测试应用"""
    app = create_app()
    # 配置为单 worker 模式，避免 Python 3.14 事件循环问题
    app.config.TESTING = True
    return app


@pytest_asyncio.fixture
async def test_client(app):
    """获取测试客户端"""
    # 手动初始化数据库上下文
    app.ctx.db = lambda: async_session_maker()

    # 使用 test_client 而不启动完整服务器
    client = app.test_client
    # 配置单 worker 模式
    client.app.config.SINGLE_WORKER = True

    yield client


@pytest_asyncio.fixture
async def authenticated_client(test_client, app):
    """获取已认证的客户端，使用默认管理员账号"""
    # 使用 sanic-testing 的同步方式登录，避免事件循环嵌套问题
    # 设置单 worker 模式
    app.config.SINGLE_WORKER = True

    # 使用同步方式调用 (req, response) 元组返回
    req, response = test_client.post(
        "/api/v1/auth/login",
        json={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
    )

    assert response.status == 200, f"登录失败：{response.text}"
    token = response.json["access_token"]

    # 设置 Authorization header
    test_client.headers.update({"Authorization": f"Bearer {token}"})

    yield test_client


@pytest_asyncio.fixture
async def sample_industry():
    """创建测试行业"""
    async with database.session() as session:
        industry = Industry(
            name="测试行业", code="test_industry", level=1, sort_order=1
        )
        session.add(industry)
        await session.flush()

        yield industry

        # 清理
        await session.delete(industry)
        await session.flush()


@pytest_asyncio.fixture
async def sample_customer_level():
    """创建测试客户等级"""
    async with database.session() as session:
        level = CustomerLevel(
            name="VIP客户", code="vip", priority=1, description="重要客户"
        )
        session.add(level)
        await session.flush()

        yield level

        # 清理
        await session.delete(level)
        await session.flush()


@pytest_asyncio.fixture
async def sample_customer(sample_industry, sample_customer_level):
    """创建测试客户"""
    async with database.session() as session:
        # 获取默认管理员用户
        admin = await session.scalar(
            User.select().where(User.username == TEST_ADMIN_USERNAME)
        )

        customer = Customer(
            customer_code=f"TEST_{uuid.uuid4().hex[:8].upper()}",
            customer_name="测试客户",
            industry_id=sample_industry.id,
            level_id=sample_customer_level.id,
            status=CustomerStatus.ACTIVE,
            contact_person="张三",
            contact_phone="13800138000",
            contact_email="test@example.com",
            address="测试地址",
            settlement_status=SettlementStatus.UNSETTLED,
            owner_id=admin.id,
            remark="测试备注",
        )
        session.add(customer)
        await session.flush()

        yield customer

        # 清理
        await session.delete(customer)
        await session.flush()


@pytest_asyncio.fixture
async def mixed_customers(sample_industry, sample_customer_level):
    """创建多个测试客户用于统计测试"""
    async with database.session() as session:
        # 获取默认管理员用户
        admin = await session.scalar(
            User.select().where(User.username == TEST_ADMIN_USERNAME)
        )

        customers = []
        for i in range(3):
            customer = Customer(
                customer_code=f"TEST_MIX_{i}_{uuid.uuid4().hex[:6].upper()}",
                customer_name=f"测试客户{i}",
                industry_id=sample_industry.id,
                level_id=sample_customer_level.id,
                status=CustomerStatus.ACTIVE,
                contact_person=f"联系人{i}",
                contact_phone=f"1380013800{i}",
                owner_id=admin.id,
            )
            session.add(customer)
            customers.append(customer)

        await session.flush()

        yield customers

        # 清理
        for customer in customers:
            await session.delete(customer)
        await session.flush()
