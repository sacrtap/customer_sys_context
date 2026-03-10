import pytest
import uuid
from datetime import date, datetime, timedelta
from io import BytesIO
import pandas as pd
from decimal import Decimal

from app.models.customer import CustomerStatus, SettlementStatus
from app.models.user import User

pytestmark = pytest.mark.asyncio


class TestAuthIntegration:
    """认证集成测试"""

    async def test_login_and_access_protected_resource(self, test_client):
        """测试登录并访问受保护资源"""
        # 未登录访问受保护资源，应该返回401
        response = await test_client.get("/api/v1/customers")
        assert response.status == 401

        # 登录获取token
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_response.status == 200
        token = login_response.json["access_token"]
        refresh_token = login_response.json["refresh_token"]
        assert token is not None
        assert refresh_token is not None

        # 使用token访问受保护资源
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        response = await test_client.get("/api/v1/customers")
        assert response.status == 200
        assert "items" in response.json

    async def test_invalid_credentials(self, test_client):
        """测试无效凭证登录"""
        # 错误密码
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong_password"},
        )
        assert response.status == 401

        # 不存在的用户
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password"},
        )
        assert response.status == 401

        # 空凭证
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "", "password": ""},
        )
        assert response.status == 400

    async def test_invalid_token(self, test_client):
        """测试无效Token访问"""
        # 无效Token
        test_client.headers.update({"Authorization": "Bearer invalid_token"})
        response = await test_client.get("/api/v1/customers")
        assert response.status == 401

        # 过期Token模拟
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        test_client.headers.update({"Authorization": f"Bearer {expired_token}"})
        response = await test_client.get("/api/v1/customers")
        assert response.status == 401

        # 无Token
        if "Authorization" in test_client.headers:
            del test_client.headers["Authorization"]
        response = await test_client.get("/api/v1/customers")
        assert response.status == 401

    async def test_refresh_token_flow(self, test_client):
        """测试刷新Token流程"""
        # 登录获取refresh token
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_response.status == 200
        refresh_token = login_response.json["refresh_token"]

        # 使用refresh token获取新的access token
        refresh_response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status == 200
        new_access_token = refresh_response.json["access_token"]
        assert new_access_token is not None
        assert new_access_token != login_response.json["access_token"]

        # 使用新token访问资源
        test_client.headers.update({"Authorization": f"Bearer {new_access_token}"})
        response = await test_client.get("/api/v1/customers")
        assert response.status == 200

    async def test_logout_functionality(self, test_client):
        """测试登出功能"""
        # 登录
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_response.status == 200
        token = login_response.json["access_token"]
        refresh_token = login_response.json["refresh_token"]

        # 登出
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        logout_response = await test_client.post("/api/v1/auth/logout")
        assert logout_response.status == 200

        # 登出后token应该失效
        response = await test_client.get("/api/v1/customers")
        assert response.status == 401

        # refresh token也应该失效
        refresh_response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status == 401


class TestCustomerIntegration:
    """客户管理集成测试"""

    async def test_customer_full_lifecycle(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试客户完整生命周期：创建 -> 查看列表 -> 更新 -> 查看详情 -> 删除"""
        # 1. 创建客户
        customer_code = f"TEST_INT_{uuid.uuid4().hex[:8].upper()}"
        create_data = {
            "customer_code": customer_code,
            "customer_name": "集成测试客户",
            "industry_id": str(sample_industry.id),
            "level_id": str(sample_customer_level.id),
            "contact_person": "集成测试联系人",
            "contact_phone": "13900139000",
            "contact_email": "integration@example.com",
            "status": CustomerStatus.ACTIVE.value,
        }

        create_response = await authenticated_client.post(
            "/api/v1/customers",
            json=create_data,
        )
        assert create_response.status == 201
        customer_id = create_response.json["id"]
        assert customer_id is not None

        # 2. 查看客户列表，确认客户存在
        list_response = await authenticated_client.get("/api/v1/customers")
        assert list_response.status == 200
        customers = list_response.json["items"]
        assert any(c["id"] == customer_id for c in customers)

        # 3. 更新客户信息
        update_data = {
            "customer_name": "集成测试客户_更新",
            "contact_person": "更新后的联系人",
            "contact_phone": "13900139001",
        }
        update_response = await authenticated_client.put(
            f"/api/v1/customers/{customer_id}",
            json=update_data,
        )
        assert update_response.status == 200
        assert update_response.json["customer_name"] == update_data["customer_name"]
        assert update_response.json["contact_person"] == update_data["contact_person"]

        # 4. 查看客户详情，确认更新生效
        detail_response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}"
        )
        assert detail_response.status == 200
        assert detail_response.json["customer_name"] == update_data["customer_name"]
        assert detail_response.json["contact_person"] == update_data["contact_person"]
        assert detail_response.json["contact_phone"] == update_data["contact_phone"]

        # 5. 删除客户
        delete_response = await authenticated_client.delete(
            f"/api/v1/customers/{customer_id}"
        )
        assert delete_response.status == 204

        # 6. 确认客户已删除
        detail_response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}"
        )
        assert detail_response.status == 404

    async def test_customer_import_workflow(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试Excel导入客户流程"""
        # 1. 创建测试Excel文件
        df = pd.DataFrame(
            [
                {
                    "客户编码": f"IMPORT_{i}_{uuid.uuid4().hex[:6].upper()}",
                    "客户名称": f"导入客户{i}",
                    "行业ID": str(sample_industry.id),
                    "客户等级ID": str(sample_customer_level.id),
                    "联系人": f"导入联系人{i}",
                    "联系电话": f"1370013700{i}",
                    "状态": "active",
                }
                for i in range(3)
            ]
        )

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # 2. 上传Excel文件导入客户
        response = await authenticated_client.post(
            "/api/v1/customers/import",
            files={
                "file": (
                    "customers.xlsx",
                    output.read(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert response.status == 200
        assert response.json["imported"] == 3
        assert response.json["skipped"] == 0

        # 3. 验证导入的客户存在
        list_response = await authenticated_client.get(
            "/api/v1/customers?page_size=100"
        )
        assert list_response.status == 200
        imported_codes = [f"IMPORT_{i}" for i in range(3)]
        imported_count = sum(
            1
            for c in list_response.json["items"]
            if any(code in c["customer_code"] for code in imported_codes)
        )
        assert imported_count == 3

    async def test_customer_filtering_workflow(
        self, authenticated_client, mixed_customers
    ):
        """测试客户筛选功能"""
        # 按状态筛选
        response = await authenticated_client.get(
            f"/api/v1/customers?status={CustomerStatus.ACTIVE.value}"
        )
        assert response.status == 200
        assert response.json["total"] >= len(mixed_customers)

        # 按行业筛选
        industry_id = mixed_customers[0].industry_id
        response = await authenticated_client.get(
            f"/api/v1/customers?industry_id={industry_id}"
        )
        assert response.status == 200
        assert all(c["industry_id"] == str(industry_id) for c in response.json["items"])

        # 按等级筛选
        level_id = mixed_customers[0].level_id
        response = await authenticated_client.get(
            f"/api/v1/customers?level_id={level_id}"
        )
        assert response.status == 200
        assert all(c["level_id"] == str(level_id) for c in response.json["items"])

        # 搜索功能
        search_keyword = mixed_customers[0].customer_name[:2]
        response = await authenticated_client.get(
            f"/api/v1/customers?search={search_keyword}"
        )
        assert response.status == 200
        assert any(search_keyword in c["customer_name"] for c in response.json["items"])

    async def test_customer_status_change_workflow(
        self, authenticated_client, sample_customer
    ):
        """测试客户状态变更流程"""
        # 改为停用状态
        response = await authenticated_client.patch(
            f"/api/v1/customers/{sample_customer.id}/status",
            json={"status": CustomerStatus.INACTIVE.value},
        )
        assert response.status == 200
        assert response.json["status"] == CustomerStatus.INACTIVE.value

        # 验证状态已更新
        detail_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert detail_response.status == 200
        assert detail_response.json["status"] == CustomerStatus.INACTIVE.value

        # 改为活跃状态
        response = await authenticated_client.patch(
            f"/api/v1/customers/{sample_customer.id}/status",
            json={"status": CustomerStatus.ACTIVE.value},
        )
        assert response.status == 200
        assert response.json["status"] == CustomerStatus.ACTIVE.value

    async def test_customer_validation_rules(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试客户数据验证规则"""
        # 测试重复客户编码
        customer_code = f"TEST_DUPLICATE_{uuid.uuid4().hex[:6].upper()}"
        create_data = {
            "customer_code": customer_code,
            "customer_name": "重复编码测试",
            "industry_id": str(sample_industry.id),
            "level_id": str(sample_customer_level.id),
            "contact_person": "测试",
            "contact_phone": "13800138000",
            "status": CustomerStatus.ACTIVE.value,
        }

        # 第一次创建成功
        response1 = await authenticated_client.post(
            "/api/v1/customers", json=create_data
        )
        assert response1.status == 201

        # 第二次创建相同编码应该失败
        response2 = await authenticated_client.post(
            "/api/v1/customers", json=create_data
        )
        assert response2.status == 400
        assert "客户编码已存在" in response2.json["error"]

        # 测试手机号格式验证
        invalid_data = create_data.copy()
        invalid_data["customer_code"] = f"TEST_INVALID_{uuid.uuid4().hex[:6].upper()}"
        invalid_data["contact_phone"] = "123456"  # 无效手机号
        response = await authenticated_client.post(
            "/api/v1/customers", json=invalid_data
        )
        assert response.status == 400
        assert "手机号格式不正确" in response.json["error"]

    async def test_customer_owner_assignment(
        self, authenticated_client, sample_customer
    ):
        """测试客户负责人分配"""
        # 获取当前用户信息
        user_response = await authenticated_client.get("/api/v1/auth/me")
        assert user_response.status == 200
        current_user_id = user_response.json["id"]

        # 分配负责人
        response = await authenticated_client.patch(
            f"/api/v1/customers/{sample_customer.id}/assign",
            json={"owner_id": current_user_id},
        )
        assert response.status == 200
        assert response.json["owner_id"] == current_user_id

        # 验证分配成功
        detail_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert detail_response.status == 200
        assert detail_response.json["owner_id"] == current_user_id

    async def test_customer_bulk_export(self, authenticated_client, mixed_customers):
        """测试客户批量导出"""
        response = await authenticated_client.post("/api/v1/customers/export")
        assert response.status == 200
        assert (
            response.headers["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "customers.xlsx" in response.headers["Content-Disposition"]


class TestSettlementIntegration:
    """结算管理集成测试"""

    async def test_settlement_full_workflow(
        self, authenticated_client, sample_customer
    ):
        """测试结算完整流程：生成月度账单 -> 查看结算列表 -> 确认支付 -> 导出报表"""
        current_month = date.today().replace(day=1)
        month_str = current_month.strftime("%Y-%m")

        # 1. 先为客户创建用量数据
        # 创建3个月的用量数据
        async with authenticated_client.app.ctx.db() as session:
            for i in range(3):
                usage_month = current_month - timedelta(days=30 * i)
                await session.execute(
                    """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                    VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": usage_month,
                        "usage_count": 100 + i * 10,
                        "amount": Decimal(f"{1000 + i * 100}.00"),
                    },
                )
            await session.commit()

        # 2. 生成月度账单
        generate_response = await authenticated_client.post(
            "/api/v1/settlements/generate-monthly",
            json={"year": current_month.year, "month": current_month.month},
        )
        assert generate_response.status == 200
        assert generate_response.json["generated"] >= 1

        # 3. 查看结算列表，确认账单生成
        list_response = await authenticated_client.get(
            f"/api/v1/settlements?month={month_str}"
        )
        assert list_response.status == 200
        settlements = list_response.json["items"]
        customer_settlement = next(
            (s for s in settlements if s["customer_id"] == str(sample_customer.id)),
            None,
        )
        assert customer_settlement is not None
        assert customer_settlement["status"] == SettlementStatus.UNSETTLED.value
        assert Decimal(customer_settlement["amount"]) > 0

        settlement_id = customer_settlement["id"]

        # 4. 确认支付
        confirm_response = await authenticated_client.patch(
            f"/api/v1/settlements/{settlement_id}/confirm",
            json={"payment_date": date.today().isoformat()},
        )
        assert confirm_response.status == 200
        assert confirm_response.json["status"] == SettlementStatus.SETTLED.value

        # 5. 验证结算状态已更新
        detail_response = await authenticated_client.get(
            f"/api/v1/settlements/{settlement_id}"
        )
        assert detail_response.status == 200
        assert detail_response.json["status"] == SettlementStatus.SETTLED.value

        # 6. 导出结算报表
        export_response = await authenticated_client.post(
            "/api/v1/settlements/export",
            json={"year": current_month.year, "month": current_month.month},
        )
        assert export_response.status == 200
        assert (
            export_response.headers["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "settlements.xlsx" in export_response.headers["Content-Disposition"]

    async def test_settlement_filtering(self, authenticated_client, sample_customer):
        """测试结算筛选功能"""
        current_month = date.today().replace(day=1)

        # 创建测试结算数据
        async with authenticated_client.app.ctx.db() as session:
            # 已结算
            await session.execute(
                """INSERT INTO settlements (customer_id, month, amount, status, created_at, updated_at)
                VALUES (:customer_id, :month, :amount, :status, NOW(), NOW())
                ON CONFLICT DO NOTHING""",
                {
                    "customer_id": sample_customer.id,
                    "month": current_month,
                    "amount": Decimal("1000.00"),
                    "status": SettlementStatus.SETTLED.value,
                },
            )
            # 未结算
            await session.execute(
                """INSERT INTO settlements (customer_id, month, amount, status, created_at, updated_at)
                VALUES (:customer_id, :month, :amount, :status, NOW(), NOW())
                ON CONFLICT DO NOTHING""",
                {
                    "customer_id": sample_customer.id,
                    "month": current_month - timedelta(days=30),
                    "amount": Decimal("1500.00"),
                    "status": SettlementStatus.UNSETTLED.value,
                },
            )
            await session.commit()

        # 按状态筛选已结算
        response = await authenticated_client.get(
            f"/api/v1/settlements?status={SettlementStatus.SETTLED.value}"
        )
        assert response.status == 200
        assert all(
            s["status"] == SettlementStatus.SETTLED.value
            for s in response.json["items"]
        )

        # 按状态筛选未结算
        response = await authenticated_client.get(
            f"/api/v1/settlements?status={SettlementStatus.UNSETTLED.value}"
        )
        assert response.status == 200
        assert all(
            s["status"] == SettlementStatus.UNSETTLED.value
            for s in response.json["items"]
        )

        # 按客户筛选
        response = await authenticated_client.get(
            f"/api/v1/settlements?customer_id={sample_customer.id}"
        )
        assert response.status == 200
        assert len(response.json["items"]) >= 2

    async def test_settlement_duplicate_prevention(
        self, authenticated_client, sample_customer
    ):
        """测试重复生成账单防护机制"""
        current_month = date.today().replace(day=1)

        # 创建用量数据
        async with authenticated_client.app.ctx.db() as session:
            await session.execute(
                """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                ON CONFLICT DO NOTHING""",
                {
                    "customer_id": sample_customer.id,
                    "month": current_month,
                    "usage_count": 100,
                    "amount": Decimal("1000.00"),
                },
            )
            await session.commit()

        # 第一次生成账单
        response1 = await authenticated_client.post(
            "/api/v1/settlements/generate-monthly",
            json={"year": current_month.year, "month": current_month.month},
        )
        assert response1.status == 200
        generated1 = response1.json["generated"]

        # 第二次生成同一月份的账单，应该不会重复生成
        response2 = await authenticated_client.post(
            "/api/v1/settlements/generate-monthly",
            json={"year": current_month.year, "month": current_month.month},
        )
        assert response2.status == 200
        generated2 = response2.json["generated"]

        # 第二次生成的数量应该比第一次少或者为0
        assert generated2 <= generated1
        assert response2.json["skipped"] >= 1


class TestDashboardIntegration:
    """Dashboard集成测试"""

    async def test_dashboard_data_accuracy(self, authenticated_client, mixed_customers):
        """测试Dashboard数据准确性"""
        # 1. 创建测试数据：结算记录、用量数据
        current_month = date.today().replace(day=1)
        async with authenticated_client.app.ctx.db() as session:
            # 为每个客户创建用量数据
            for idx, customer in enumerate(mixed_customers):
                # 近3个月用量
                for i in range(3):
                    usage_month = current_month - timedelta(days=30 * i)
                    await session.execute(
                        """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                        VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                        ON CONFLICT DO NOTHING""",
                        {
                            "customer_id": customer.id,
                            "month": usage_month,
                            "usage_count": 100 + i * 10 + idx * 5,
                            "amount": Decimal(f"{1000 + i * 100 + idx * 50}.00"),
                        },
                    )

            # 创建结算记录
            for idx, customer in enumerate(mixed_customers):
                status = (
                    SettlementStatus.SETTLED
                    if idx % 2 == 0
                    else SettlementStatus.UNSETTLED
                )
                await session.execute(
                    """INSERT INTO settlements (customer_id, month, amount, status, created_at, updated_at)
                    VALUES (:customer_id, :month, :amount, :status, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": customer.id,
                        "month": current_month,
                        "amount": Decimal(f"{1000 + idx * 100}.00"),
                        "status": status.value,
                    },
                )

            await session.commit()

        # 2. 获取Dashboard概览数据
        overview_response = await authenticated_client.get("/api/v1/dashboard/overview")
        assert overview_response.status == 200
        overview_data = overview_response.json

        # 3. 验证数据完整性
        assert "total_customers" in overview_data
        assert "active_customers" in overview_data
        assert "total_revenue" in overview_data
        assert "settled_revenue" in overview_data
        assert "unsettled_count" in overview_data
        assert "health_stats" in overview_data

        # 4. 验证数据合理性
        assert overview_data["total_customers"] >= len(mixed_customers)
        assert overview_data["active_customers"] >= len(mixed_customers)
        assert overview_data["total_revenue"] > 0
        assert overview_data["settled_revenue"] > 0
        assert overview_data["unsettled_count"] >= 1

    async def test_dashboard_quick_actions(self, authenticated_client, mixed_customers):
        """测试Dashboard快捷操作数据"""
        response = await authenticated_client.get("/api/v1/dashboard/quick-actions")
        assert response.status == 200
        data = response.json

        assert "pending_settlements" in data
        assert "expiring_customers" in data
        assert "health_alerts" in data
        assert "recent_activities_count" in data

        assert isinstance(data["pending_settlements"], int)
        assert isinstance(data["expiring_customers"], int)
        assert isinstance(data["health_alerts"], int)

    async def test_dashboard_recent_activities(
        self, authenticated_client, mixed_customers
    ):
        """测试Dashboard最近活动"""
        # 测试默认limit
        response = await authenticated_client.get("/api/v1/dashboard/recent-activities")
        assert response.status == 200
        activities = response.json
        assert isinstance(activities, list)
        assert len(activities) <= 10  # 默认limit是10

        # 测试自定义limit
        response = await authenticated_client.get(
            "/api/v1/dashboard/recent-activities?limit=5"
        )
        assert response.status == 200
        activities = response.json
        assert len(activities) <= 5

        # 测试活动格式
        if activities:
            activity = activities[0]
            assert "type" in activity
            assert "description" in activity
            assert "created_at" in activity
            assert "user" in activity


class TestHealthIntegration:
    """健康度评分集成测试"""

    async def test_health_score_workflow(self, authenticated_client, sample_customer):
        """测试健康度评分完整流程"""
        current_month = date.today().replace(day=1)

        # 1. 创建测试数据：用量数据和结算记录
        async with authenticated_client.app.ctx.db() as session:
            # 创建近6个月的用量数据（稳定增长）
            for i in range(6):
                usage_month = current_month - timedelta(days=30 * i)
                # 用量逐渐增长
                usage_count = 100 + i * 20
                await session.execute(
                    """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                    VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": usage_month,
                        "usage_count": usage_count,
                        "amount": Decimal(f"{usage_count * 10}.00"),
                    },
                )

            # 创建已结算记录（全部按时结算）
            for i in range(3):
                settlement_month = current_month - timedelta(days=30 * i)
                await session.execute(
                    """INSERT INTO settlements (customer_id, month, amount, status, payment_date, created_at, updated_at)
                    VALUES (:customer_id, :month, :amount, :status, :payment_date, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": settlement_month,
                        "amount": Decimal(f"{1000 + i * 200}.00"),
                        "status": SettlementStatus.SETTLED.value,
                        "payment_date": settlement_month + timedelta(days=10),
                    },
                )

            await session.commit()

        # 2. 获取客户详情，包含健康度评分
        customer_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert customer_response.status == 200
        customer_data = customer_response.json

        # 3. 验证健康度数据存在
        assert "health_score" in customer_data
        assert "health_level" in customer_data

        # 4. 验证评分合理（用量增长 + 按时结算，应该是健康客户）
        assert isinstance(customer_data["health_score"], (int, float))
        assert 0 <= customer_data["health_score"] <= 100
        assert customer_data["health_level"] in ["healthy", "warning", "critical"]
        # 我们的测试数据应该是健康的
        assert customer_data["health_level"] == "healthy"
        assert customer_data["health_score"] >= 80

    async def test_health_score_warning_level(
        self, authenticated_client, sample_customer
    ):
        """测试健康度警告等级（有少量逾期结算，用量下降）"""
        current_month = date.today().replace(day=1)

        async with authenticated_client.app.ctx.db() as session:
            # 创建用量数据（持续下降）
            for i in range(6):
                usage_month = current_month - timedelta(days=30 * i)
                usage_count = 200 - i * 20  # 用量逐渐下降
                await session.execute(
                    """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                    VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": usage_month,
                        "usage_count": usage_count,
                        "amount": Decimal(f"{usage_count * 10}.00"),
                    },
                )

            # 有1次逾期结算
            for i in range(3):
                settlement_month = current_month - timedelta(days=30 * i)
                status = (
                    SettlementStatus.UNSETTLED if i == 0 else SettlementStatus.SETTLED
                )
                await session.execute(
                    """INSERT INTO settlements (customer_id, month, amount, status, created_at, updated_at)
                    VALUES (:customer_id, :month, :amount, :status, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": settlement_month,
                        "amount": Decimal(f"{1000 + i * 200}.00"),
                        "status": status.value,
                    },
                )

            await session.commit()

        # 获取健康度评分
        customer_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert customer_response.status == 200
        customer_data = customer_response.json

        # 应该是警告等级
        assert customer_data["health_level"] in ["warning", "critical"]
        assert customer_data["health_score"] < 80

    async def test_health_score_refresh_after_data_change(
        self, authenticated_client, sample_customer
    ):
        """测试健康度评分在数据变更后自动刷新"""
        current_month = date.today().replace(day=1)

        # 1. 初始状态：健康客户
        async with authenticated_client.app.ctx.db() as session:
            for i in range(6):
                usage_month = current_month - timedelta(days=30 * i)
                await session.execute(
                    """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                    VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": usage_month,
                        "usage_count": 100 + i * 10,
                        "amount": Decimal("1000.00"),
                    },
                )
            await session.commit()

        # 获取初始评分
        response1 = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        initial_score = response1.json["health_score"]
        initial_level = response1.json["health_level"]

        # 2. 添加逾期结算记录，健康度应该下降
        async with authenticated_client.app.ctx.db() as session:
            for i in range(3):
                settlement_month = current_month - timedelta(days=30 * i)
                await session.execute(
                    """INSERT INTO settlements (customer_id, month, amount, status, created_at, updated_at)
                    VALUES (:customer_id, :month, :amount, :status, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": settlement_month,
                        "amount": Decimal("1000.00"),
                        "status": SettlementStatus.UNSETTLED.value,
                    },
                )
            await session.commit()

        # 获取更新后的评分
        response2 = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        updated_score = response2.json["health_score"]
        updated_level = response2.json["health_level"]

        # 评分应该下降
        assert updated_score < initial_score
        assert updated_level != initial_level or updated_level == "warning"


class TestDashboardIntegration:
    """Dashboard集成测试"""

    async def test_dashboard_data_accuracy(self, authenticated_client, mixed_customers):
        """测试Dashboard数据准确性"""
        # 1. 创建测试数据：结算记录、用量数据
        current_month = date.today().replace(day=1)
        async with authenticated_client.app.ctx.db() as session:
            # 为每个客户创建用量数据
            for idx, customer in enumerate(mixed_customers):
                # 近3个月用量
                for i in range(3):
                    usage_month = current_month - timedelta(days=30 * i)
                    await session.execute(
                        """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                        VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                        ON CONFLICT DO NOTHING""",
                        {
                            "customer_id": customer.id,
                            "month": usage_month,
                            "usage_count": 100 + i * 10 + idx * 5,
                            "amount": Decimal(f"{1000 + i * 100 + idx * 50}.00"),
                        },
                    )

            # 创建结算记录
            for idx, customer in enumerate(mixed_customers):
                status = (
                    SettlementStatus.SETTLED
                    if idx % 2 == 0
                    else SettlementStatus.UNSETTLED
                )
                await session.execute(
                    """INSERT INTO settlements (customer_id, month, amount, status, created_at, updated_at)
                    VALUES (:customer_id, :month, :amount, :status, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": customer.id,
                        "month": current_month,
                        "amount": Decimal(f"{1000 + idx * 100}.00"),
                        "status": status.value,
                    },
                )

            await session.commit()

        # 2. 获取Dashboard概览数据
        overview_response = await authenticated_client.get("/api/v1/dashboard/overview")
        assert overview_response.status == 200
        overview_data = overview_response.json

        # 3. 验证数据完整性
        assert "total_customers" in overview_data
        assert "active_customers" in overview_data
        assert "total_revenue" in overview_data
        assert "settled_revenue" in overview_data
        assert "unsettled_count" in overview_data
        assert "health_stats" in overview_data

        # 4. 验证数据合理性
        assert overview_data["total_customers"] >= len(mixed_customers)
        assert overview_data["active_customers"] >= len(mixed_customers)
        assert overview_data["total_revenue"] > 0
        assert overview_data["settled_revenue"] > 0
        assert overview_data["unsettled_count"] >= 1

        # 5. 获取快捷操作数据
        quick_actions_response = await authenticated_client.get(
            "/api/v1/dashboard/quick-actions"
        )
        assert quick_actions_response.status == 200
        quick_actions_data = quick_actions_response.json
        assert "pending_settlements" in quick_actions_data
        assert "expiring_customers" in quick_actions_data
        assert "health_alerts" in quick_actions_data

        # 6. 获取最近活动
        recent_activities_response = await authenticated_client.get(
            "/api/v1/dashboard/recent-activities?limit=10"
        )
        assert recent_activities_response.status == 200
        activities = recent_activities_response.json
        assert isinstance(activities, list)
        assert len(activities) <= 10


class TestHealthIntegration:
    """健康度评分集成测试"""

    async def test_health_score_workflow(self, authenticated_client, sample_customer):
        """测试健康度评分完整流程"""
        current_month = date.today().replace(day=1)

        # 1. 创建测试数据：用量数据和结算记录
        async with authenticated_client.app.ctx.db() as session:
            # 创建近6个月的用量数据（稳定增长）
            for i in range(6):
                usage_month = current_month - timedelta(days=30 * i)
                # 用量逐渐增长
                usage_count = 100 + i * 20
                await session.execute(
                    """INSERT INTO customer_usage (customer_id, month, usage_count, amount, created_at, updated_at)
                    VALUES (:customer_id, :month, :usage_count, :amount, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": usage_month,
                        "usage_count": usage_count,
                        "amount": Decimal(f"{usage_count * 10}.00"),
                    },
                )

            # 创建已结算记录（全部按时结算）
            for i in range(3):
                settlement_month = current_month - timedelta(days=30 * i)
                await session.execute(
                    """INSERT INTO settlements (customer_id, month, amount, status, payment_date, created_at, updated_at)
                    VALUES (:customer_id, :month, :amount, :status, :payment_date, NOW(), NOW())
                    ON CONFLICT DO NOTHING""",
                    {
                        "customer_id": sample_customer.id,
                        "month": settlement_month,
                        "amount": Decimal(f"{1000 + i * 200}.00"),
                        "status": SettlementStatus.SETTLED.value,
                        "payment_date": settlement_month + timedelta(days=10),
                    },
                )

            await session.commit()

        # 2. 获取客户详情，包含健康度评分
        customer_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert customer_response.status == 200
        customer_data = customer_response.json

        # 3. 验证健康度数据存在
        assert "health_score" in customer_data
        assert "health_level" in customer_data

        # 4. 验证评分合理（用量增长 + 按时结算，应该是健康客户）
        assert isinstance(customer_data["health_score"], (int, float))
        assert 0 <= customer_data["health_score"] <= 100
        assert customer_data["health_level"] in ["healthy", "warning", "critical"]
        # 我们的测试数据应该是健康的
        assert customer_data["health_level"] == "healthy"
        assert customer_data["health_score"] >= 80

        # 5. 验证Dashboard健康统计包含此客户
        overview_response = await authenticated_client.get("/api/v1/dashboard/overview")
        assert overview_response.status == 200
        health_stats = overview_response.json["health_stats"]
        assert health_stats["healthy"] >= 1
