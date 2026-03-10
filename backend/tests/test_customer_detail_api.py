"""
客户详情 API 测试
"""

import pytest
import pytest_asyncio
from datetime import date, timedelta
from decimal import Decimal
import uuid


class TestCustomerDetailAPI:
    """客户详情 API 测试"""

    async def test_get_customer_detail_with_relations(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试获取客户详情（含关联数据）"""
        # 创建测试客户
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Customer, CustomerStatus
            from app.models.user import User

            admin = await session.scalar(User.select().where(User.username == "admin"))

            customer = Customer(
                customer_code=f"DETAIL_TEST_{uuid.uuid4().hex[:8].upper()}",
                customer_name="详情测试客户",
                industry_id=sample_industry.id,
                level_id=sample_customer_level.id,
                status=CustomerStatus.ACTIVE,
                contact_person="李四",
                contact_phone="13900139000",
                owner_id=admin.id,
            )
            session.add(customer)
            await session.flush()
            customer_id = str(customer.id)

        # 获取客户详情
        response = await authenticated_client.get(f"/api/v1/customers/{customer_id}")

        assert response.status == 200
        data = response.json

        # 验证基本信息
        assert data["customer_name"] == "详情测试客户"
        assert data["contact_person"] == "李四"

        # 验证关联数据
        assert "industry" in data
        assert data["industry"] is not None
        assert data["industry"]["name"] == "测试行业"

        assert "level" in data
        assert data["level"] is not None
        assert data["level"]["name"] == "VIP 客户"

        assert "owner" in data
        assert data["owner"] is not None

    async def test_get_customer_usages(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试获取客户用量历史"""
        # 创建客户和用量数据
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Customer, CustomerUsage, CustomerStatus
            from app.models.user import User

            admin = await session.scalar(User.select().where(User.username == "admin"))

            customer = Customer(
                customer_code=f"USAGE_TEST_{uuid.uuid4().hex[:8].upper()}",
                customer_name="用量测试客户",
                industry_id=sample_industry.id,
                level_id=sample_customer_level.id,
                status=CustomerStatus.ACTIVE,
                owner_id=admin.id,
            )
            session.add(customer)
            await session.flush()

            # 创建 3 个月的用量数据
            for i in range(3):
                month_date = date.today() - timedelta(days=30 * i)
                usage = CustomerUsage(
                    customer_id=customer.id,
                    month=month_date,
                    usage_count=100 * (i + 1),
                    amount=Decimal("1000.00") * (i + 1),
                )
                session.add(usage)

            await session.flush()
            customer_id = str(customer.id)

        # 获取用量历史
        response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}/usages"
        )

        assert response.status == 200
        data = response.json

        # 验证返回数据
        assert "items" in data
        assert len(data["items"]) >= 3

        # 验证用量数据字段
        usage = data["items"][0]
        assert "month" in usage
        assert "usage_count" in usage
        assert "amount" in usage

    async def test_get_customer_settlements(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试获取客户结算记录"""
        # 创建客户和结算数据
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import (
                Customer,
                Settlement,
                CustomerStatus,
                SettlementStatus,
            )
            from app.models.user import User

            admin = await session.scalar(User.select().where(User.username == "admin"))

            customer = Customer(
                customer_code=f"SETTLE_TEST_{uuid.uuid4().hex[:8].upper()}",
                customer_name="结算测试客户",
                industry_id=sample_industry.id,
                level_id=sample_customer_level.id,
                status=CustomerStatus.ACTIVE,
                owner_id=admin.id,
            )
            session.add(customer)
            await session.flush()

            # 创建 2 条结算记录
            for i in range(2):
                month_date = date.today() - timedelta(days=30 * i)
                settlement = Settlement(
                    customer_id=customer.id,
                    month=month_date,
                    amount=Decimal("5000.00") * (i + 1),
                    status=SettlementStatus.SETTLED
                    if i == 0
                    else SettlementStatus.UNSETTLED,
                )
                session.add(settlement)

            await session.flush()
            customer_id = str(customer.id)

        # 获取结算记录
        response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}/settlements"
        )

        assert response.status == 200
        data = response.json

        # 验证返回数据
        assert "items" in data
        assert len(data["items"]) >= 2

        # 验证结算数据字段
        settlement = data["items"][0]
        assert "month" in settlement
        assert "amount" in settlement
        assert "status" in settlement

    async def test_get_customer_not_found(self, authenticated_client):
        """测试获取不存在的客户"""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.get(f"/api/v1/customers/{fake_id}")

        assert response.status == 404
        data = response.json
        assert "error" in data
        assert "不存在" in data["error"]

    async def test_get_customer_usages_pagination(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试客户用量历史分页"""
        # 创建客户和大量用量数据
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Customer, CustomerUsage, CustomerStatus
            from app.models.user import User

            admin = await session.scalar(User.select().where(User.username == "admin"))

            customer = Customer(
                customer_code=f"PAGINATION_TEST_{uuid.uuid4().hex[:8].upper()}",
                customer_name="分页测试客户",
                industry_id=sample_industry.id,
                level_id=sample_customer_level.id,
                status=CustomerStatus.ACTIVE,
                owner_id=admin.id,
            )
            session.add(customer)
            await session.flush()

            # 创建 10 个月的用量数据
            for i in range(10):
                month_date = date.today() - timedelta(days=30 * i)
                usage = CustomerUsage(
                    customer_id=customer.id,
                    month=month_date,
                    usage_count=100,
                    amount=Decimal("1000.00"),
                )
                session.add(usage)

            await session.flush()
            customer_id = str(customer.id)

        # 测试分页参数
        response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}/usages?page=1&page_size=5"
        )

        assert response.status == 200
        data = response.json

        # 验证分页数据
        assert "items" in data
        assert len(data["items"]) <= 5
        assert data.get("page") == 1
        assert data.get("page_size") == 5
        assert data.get("total", 0) >= 10

    async def test_get_customer_settlements_pagination(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试客户结算记录分页"""
        # 创建客户和大量结算数据
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import (
                Customer,
                Settlement,
                CustomerStatus,
                SettlementStatus,
            )
            from app.models.user import User

            admin = await session.scalar(User.select().where(User.username == "admin"))

            customer = Customer(
                customer_code=f"SETTLE_PAGINATION_TEST_{uuid.uuid4().hex[:8].upper()}",
                customer_name="结算分页测试客户",
                industry_id=sample_industry.id,
                level_id=sample_customer_level.id,
                status=CustomerStatus.ACTIVE,
                owner_id=admin.id,
            )
            session.add(customer)
            await session.flush()

            # 创建 8 条结算记录
            for i in range(8):
                month_date = date.today() - timedelta(days=30 * i)
                settlement = Settlement(
                    customer_id=customer.id,
                    month=month_date,
                    amount=Decimal("5000.00"),
                    status=SettlementStatus.UNSETTLED,
                )
                session.add(settlement)

            await session.flush()
            customer_id = str(customer.id)

        # 测试分页参数
        response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}/settlements?page=1&page_size=3"
        )

        assert response.status == 200
        data = response.json

        # 验证分页数据
        assert "items" in data
        assert len(data["items"]) <= 3
        assert data.get("page") == 1
        assert data.get("page_size") == 3
        assert data.get("total", 0) >= 8
