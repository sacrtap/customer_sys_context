"""
结算管理 API 测试

使用 TDD 方式开发，包含 8 个 API 端点的完整测试覆盖
"""

import pytest
import pytest_asyncio
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def sample_settlement(authenticated_client, sample_customer):
    """创建测试结算记录"""
    async with authenticated_client.app.ctx.db() as session:
        from app.models.customer import Settlement, SettlementStatus

        settlement = Settlement(
            customer_id=sample_customer.id,
            month=date(2025, 1, 1),
            amount=Decimal("1000.00"),
            status=SettlementStatus.UNSETTLED,
            remark="测试结算记录",
        )
        session.add(settlement)
        await session.commit()
        await session.refresh(settlement)

        yield settlement

        # 清理
        await session.delete(settlement)
        await session.commit()


@pytest_asyncio.fixture
async def settled_settlement(authenticated_client, sample_customer):
    """创建已结算的测试记录"""
    async with authenticated_client.app.ctx.db() as session:
        from app.models.customer import Settlement, SettlementStatus

        settlement = Settlement(
            customer_id=sample_customer.id,
            month=date(2025, 2, 1),
            amount=Decimal("2000.00"),
            status=SettlementStatus.SETTLED,
            paid_amount=Decimal("2000.00"),
            paid_at=date(2025, 2, 15),
            remark="已结算测试记录",
        )
        session.add(settlement)
        await session.commit()
        await session.refresh(settlement)

        yield settlement

        # 清理
        await session.delete(settlement)
        await session.commit()


@pytest_asyncio.fixture
async def multiple_settlements(authenticated_client, sample_customer):
    """创建多个结算记录（12个月）"""
    async with authenticated_client.app.ctx.db() as session:
        from app.models.customer import Settlement, SettlementStatus

        settlements = []
        for i in range(12):
            month_date = date(2025, i + 1, 1)
            settlement = Settlement(
                customer_id=sample_customer.id,
                month=month_date,
                amount=Decimal(f"{1000 * (i + 1)}.00"),
                status=SettlementStatus.SETTLED
                if i % 2 == 0
                else SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            settlements.append(settlement)

        await session.commit()
        for s in settlements:
            await session.refresh(s)

        yield settlements

        # 清理
        for s in settlements:
            await session.delete(s)
        await session.commit()


@pytest_asyncio.fixture
async def mock_usage_data(authenticated_client, mixed_customers):
    """创建测试用量数据用于生成账单"""
    async with authenticated_client.app.ctx.db() as session:
        from app.models.customer import CustomerUsage

        usages = []
        for customer in mixed_customers:
            for i in range(3):
                month_date = date(2025, 1 + i, 1)
                usage = CustomerUsage(
                    customer_id=customer.id,
                    month=month_date,
                    usage_count=100 * (i + 1),
                    amount=Decimal(str(1000 * (i + 1))),
                )
                session.add(usage)
                usages.append(usage)

        await session.commit()
        yield usages

        # 清理
        for u in usages:
            await session.delete(u)
        await session.commit()


class TestListSettlementsAPI:
    """结算记录列表 API 测试"""

    async def test_list_settlements_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试获取结算记录列表 - 认证成功"""
        # 先创建测试结算数据
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            for i in range(3):
                month_date = date(2026, 1 + i, 1)
                settlement = Settlement(
                    customer_id=sample_customer.id,
                    month=month_date,
                    amount=Decimal(str(5000 * (i + 1))),
                    status=SettlementStatus.UNSETTLED,
                )
                session.add(settlement)
            await session.flush()

        response = await authenticated_client.get(
            "/api/v1/settlements",
            params={"customer_id": str(sample_customer.id)},
        )

        assert response.status == 200
        data = response.json
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 3

    async def test_list_settlements_unauthenticated(self, app):
        """测试获取结算记录列表 - 认证失败"""
        async with app.test_client as client:
            response = await client.get("/api/v1/settlements")
            assert response.status == 401

    async def test_list_settlements_pagination(
        self, authenticated_client, sample_customer
    ):
        """测试结算记录列表 - 分页"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            for i in range(25):
                settlement = Settlement(
                    customer_id=sample_customer.id,
                    month=date(2026, 1, 1) + timedelta(days=i),
                    amount=Decimal("1000"),
                    status=SettlementStatus.UNSETTLED,
                )
                session.add(settlement)
            await session.flush()

        response = await authenticated_client.get(
            "/api/v1/settlements",
            params={"customer_id": str(sample_customer.id), "page": 1, "page_size": 10},
        )

        assert response.status == 200
        data = response.json
        assert len(data["items"]) == 10
        assert data["total"] == 25

    async def test_list_settlements_filter_by_status(
        self, authenticated_client, sample_customer
    ):
        """测试结算记录列表 - 按状态筛选"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            for i in range(3):
                settlement = Settlement(
                    customer_id=sample_customer.id,
                    month=date(2026, 1 + i, 1),
                    amount=Decimal("5000"),
                    status=SettlementStatus.SETTLED
                    if i % 2 == 0
                    else SettlementStatus.UNSETTLED,
                )
                session.add(settlement)
            await session.flush()

        response = await authenticated_client.get(
            "/api/v1/settlements",
            params={"customer_id": str(sample_customer.id), "status": "settled"},
        )

        assert response.status == 200
        data = response.json
        for item in data["items"]:
            assert item["status"] == "settled"

    async def test_list_settlements_empty_data(self, authenticated_client):
        """测试结算记录列表 - 空数据"""
        response = await authenticated_client.get("/api/v1/settlements")
        assert response.status == 200
        data = response.json
        assert len(data["items"]) == 0


class TestGetSettlementAPI:
    """获取结算记录详情 API 测试"""

    async def test_get_settlement_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试获取结算记录详情 - 认证成功"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 1, 1),
                amount=Decimal("5000"),
                status=SettlementStatus.UNSETTLED,
                remark="测试备注",
            )
            session.add(settlement)
            await session.flush()
            settlement_id = str(settlement.id)

        response = await authenticated_client.get(
            f"/api/v1/settlements/{settlement_id}"
        )
        assert response.status == 200
        data = response.json
        assert data["id"] == settlement_id
        assert data["amount"] == "5000.00"

    async def test_get_settlement_unauthenticated(self, app):
        """测试获取结算记录详情 - 认证失败"""
        async with app.test_client as client:
            response = await client.get(f"/api/v1/settlements/{uuid.uuid4()}")
            assert response.status == 401

    async def test_get_settlement_not_found(self, authenticated_client):
        """测试获取结算记录详情 - 记录不存在"""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.get(f"/api/v1/settlements/{fake_id}")
        assert response.status == 404

    async def test_get_settlement_invalid_uuid(self, authenticated_client):
        """测试获取结算记录详情 - 无效 UUID 格式"""
        response = await authenticated_client.get("/api/v1/settlements/invalid-uuid")
        assert response.status == 400


class TestCreateSettlementAPI:
    """创建结算记录 API 测试"""

    async def test_create_settlement_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试创建结算记录 - 认证成功"""
        data = {
            "customer_id": str(sample_customer.id),
            "month": "2026-03",
            "amount": 8000.00,
            "remark": "测试创建",
        }

        response = await authenticated_client.post("/api/v1/settlements", json=data)
        assert response.status == 201
        assert "id" in response.json

    async def test_create_settlement_unauthenticated(self, app, sample_customer):
        """测试创建结算记录 - 认证失败"""
        async with app.test_client as client:
            data = {
                "customer_id": str(sample_customer.id),
                "month": "2026-03",
                "amount": 8000.00,
            }
            response = await client.post("/api/v1/settlements", json=data)
            assert response.status == 401

    async def test_create_settlement_missing_required_fields(
        self, authenticated_client, sample_customer
    ):
        """测试创建结算记录 - 缺少必填字段"""
        data = {"customer_id": str(sample_customer.id), "month": "2026-03"}
        response = await authenticated_client.post("/api/v1/settlements", json=data)
        assert response.status == 400

    async def test_create_settlement_invalid_customer_id(self, authenticated_client):
        """测试创建结算记录 - 客户不存在"""
        data = {"customer_id": str(uuid.uuid4()), "month": "2026-03", "amount": 8000.00}
        response = await authenticated_client.post("/api/v1/settlements", json=data)
        assert response.status == 400

    async def test_create_settlement_invalid_month_format(
        self, authenticated_client, sample_customer
    ):
        """测试创建结算记录 - 月份格式错误"""
        data = {
            "customer_id": str(sample_customer.id),
            "month": "invalid",
            "amount": 8000.00,
        }
        response = await authenticated_client.post("/api/v1/settlements", json=data)
        assert response.status == 400

    async def test_create_settlement_invalid_amount(
        self, authenticated_client, sample_customer
    ):
        """测试创建结算记录 - 金额格式错误"""
        data = {
            "customer_id": str(sample_customer.id),
            "month": "2026-03",
            "amount": -100,
        }
        response = await authenticated_client.post("/api/v1/settlements", json=data)
        assert response.status == 400

    async def test_create_settlement_duplicate(
        self, authenticated_client, sample_customer
    ):
        """测试创建结算记录 - 重复记录"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 3, 1),
                amount=Decimal("5000"),
                status=SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            await session.flush()

        data = {
            "customer_id": str(sample_customer.id),
            "month": "2026-03",
            "amount": 8000.00,
        }
        response = await authenticated_client.post("/api/v1/settlements", json=data)
        assert response.status == 400


class TestUpdateSettlementAPI:
    """更新结算记录 API 测试"""

    async def test_update_settlement_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试更新结算记录 - 认证成功"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 1, 1),
                amount=Decimal("5000"),
                status=SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            await session.flush()
            settlement_id = str(settlement.id)

        response = await authenticated_client.put(
            f"/api/v1/settlements/{settlement_id}",
            json={"amount": 6000.00, "remark": "更新备注"},
        )
        assert response.status == 200

    async def test_update_settlement_unauthenticated(self, app):
        """测试更新结算记录 - 认证失败"""
        client = app.test_client
        response = await client.put(
            f"/api/v1/settlements/{uuid.uuid4()}", json={"amount": 6000}
        )
        assert response.status == 401

    async def test_update_settlement_not_found(self, authenticated_client):
        """测试更新结算记录 - 记录不存在"""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.put(
            f"/api/v1/settlements/{fake_id}", json={"amount": 6000}
        )
        assert response.status == 404

    async def test_update_settlement_status(
        self, authenticated_client, sample_customer
    ):
        """测试更新结算记录状态"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 1, 1),
                amount=Decimal("5000"),
                status=SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            await session.flush()
            settlement_id = str(settlement.id)

        response = await authenticated_client.put(
            f"/api/v1/settlements/{settlement_id}",
            json={"status": "settled"},
        )
        assert response.status == 200


class TestDeleteSettlementAPI:
    """删除结算记录 API 测试"""

    async def test_delete_settlement_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试删除结算记录 - 认证成功"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 1, 1),
                amount=Decimal("5000"),
                status=SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            await session.flush()
            settlement_id = str(settlement.id)

        response = await authenticated_client.delete(
            f"/api/v1/settlements/{settlement_id}"
        )
        assert response.status == 200

        # 验证已删除
        response = await authenticated_client.get(
            f"/api/v1/settlements/{settlement_id}"
        )
        assert response.status == 404

    async def test_delete_settlement_unauthenticated(self, app):
        """测试删除结算记录 - 认证失败"""
        client = app.test_client
        response = await client.delete(f"/api/v1/settlements/{uuid.uuid4()}")
        assert response.status == 401

    async def test_delete_settlement_not_found(self, authenticated_client):
        """测试删除结算记录 - 记录不存在"""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.delete(f"/api/v1/settlements/{fake_id}")
        assert response.status == 404


class TestConfirmPaymentAPI:
    """确认支付 API 测试"""

    async def test_confirm_payment_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试确认支付 - 认证成功"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 1, 1),
                amount=Decimal("5000"),
                status=SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            await session.flush()
            settlement_id = str(settlement.id)

        response = await authenticated_client.post(
            f"/api/v1/settlements/{settlement_id}/confirm-payment",
            json={"paid_amount": 5000.00, "paid_at": datetime.now().isoformat()},
        )
        assert response.status == 200

    async def test_confirm_payment_unauthenticated(self, app):
        """测试确认支付 - 认证失败"""
        client = app.test_client
        response = await client.post(
            f"/api/v1/settlements/{uuid.uuid4()}/confirm-payment",
            json={"paid_amount": 5000},
        )
        assert response.status == 401

    async def test_confirm_payment_not_found(self, authenticated_client):
        """测试确认支付 - 记录不存在"""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.post(
            f"/api/v1/settlements/{fake_id}/confirm-payment",
            json={"paid_amount": 5000},
        )
        assert response.status == 404


class TestGenerateMonthlyBillsAPI:
    """生成月度账单 API 测试"""

    async def test_generate_monthly_bills_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试生成月度账单 - 认证成功"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import CustomerUsage

            usage = CustomerUsage(
                customer_id=sample_customer.id,
                month=date(2026, 3, 1),
                usage_count=100,
                amount=Decimal("8000"),
            )
            session.add(usage)
            await session.flush()

        response = await authenticated_client.post(
            "/api/v1/settlements/generate-monthly",
            json={"year": 2026, "month": 3},
        )
        assert response.status == 200
        assert "generated_count" in response.json

    async def test_generate_monthly_bills_unauthenticated(self, app):
        """测试生成月度账单 - 认证失败"""
        client = app.test_client
        response = await client.post(
            "/api/v1/settlements/generate-monthly",
            json={"year": 2026, "month": 3},
        )
        assert response.status == 401

    async def test_generate_monthly_bills_skip_existing(
        self, authenticated_client, sample_customer
    ):
        """测试生成月度账单 - 跳过已存在的记录"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import CustomerUsage, Settlement, SettlementStatus

            usage = CustomerUsage(
                customer_id=sample_customer.id,
                month=date(2026, 3, 1),
                usage_count=100,
                amount=Decimal("8000"),
            )
            session.add(usage)

            settlement = Settlement(
                customer_id=sample_customer.id,
                month=date(2026, 3, 1),
                amount=Decimal("8000"),
                status=SettlementStatus.UNSETTLED,
            )
            session.add(settlement)
            await session.flush()

        response = await authenticated_client.post(
            "/api/v1/settlements/generate-monthly",
            json={"year": 2026, "month": 3},
        )
        assert response.status == 200
        assert response.json["skipped_count"] >= 1


class TestExportSettlementsAPI:
    """导出结算记录 API 测试"""

    async def test_export_settlements_authenticated(
        self, authenticated_client, sample_customer
    ):
        """测试导出结算记录 - 认证成功"""
        async with authenticated_client.app.ctx.db() as session:
            from app.models.customer import Settlement, SettlementStatus

            for i in range(3):
                settlement = Settlement(
                    customer_id=sample_customer.id,
                    month=date(2026, 1 + i, 1),
                    amount=Decimal("5000"),
                    status=SettlementStatus.UNSETTLED,
                )
                session.add(settlement)
            await session.flush()

        response = await authenticated_client.post(
            "/api/v1/settlements/export",
            json={
                "customer_ids": [str(sample_customer.id)],
                "date_range": {"start": "2026-01-01", "end": "2026-03-31"},
            },
        )
        assert response.status == 200

    async def test_export_settlements_unauthenticated(self, app):
        """测试导出结算记录 - 认证失败"""
        client = app.test_client
        response = await client.post(
            "/api/v1/settlements/export",
            json={"customer_ids": [], "date_range": {}},
        )
        assert response.status == 401
