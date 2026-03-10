import pytest
import uuid
from app.models.customer import CustomerStatus, SettlementStatus

pytestmark = pytest.mark.asyncio


class TestCustomerFilters:
    """客户筛选和搜索测试"""

    async def test_filter_by_industry(
        self, authenticated_client, sample_industry, sample_customer
    ):
        """测试按行业筛选"""
        response = await authenticated_client.get(
            "/api/v1/customers", params={"industry_id": str(sample_industry.id)}
        )

        assert response.status == 200
        data = response.json
        assert data["total"] >= 1

        # 验证返回的客户都属于该行业
        for item in data["items"]:
            assert item["industry"] is not None
            assert item["industry"]["id"] == str(sample_industry.id)

    async def test_filter_by_level(
        self, authenticated_client, sample_customer_level, sample_customer
    ):
        """测试按客户等级筛选"""
        response = await authenticated_client.get(
            "/api/v1/customers", params={"level_id": str(sample_customer_level.id)}
        )

        assert response.status == 200
        data = response.json
        assert data["total"] >= 1

        # 验证返回的客户都属于该等级
        for item in data["items"]:
            assert item["level"] is not None
            assert item["level"]["id"] == str(sample_customer_level.id)

    async def test_filter_by_status(self, authenticated_client, sample_customer):
        """测试按状态筛选"""
        # 先更新客户状态为停用
        await authenticated_client.put(
            f"/api/v1/customers/{sample_customer.id}",
            json={"status": CustomerStatus.INACTIVE.value},
        )

        # 筛选停用状态
        response = await authenticated_client.get(
            "/api/v1/customers", params={"status": CustomerStatus.INACTIVE.value}
        )

        assert response.status == 200
        data = response.json

        # 验证返回的客户状态正确
        customer_found = False
        for item in data["items"]:
            if item["id"] == str(sample_customer.id):
                customer_found = True
                assert item["status"] == CustomerStatus.INACTIVE.value
                break
        assert customer_found

    async def test_filter_by_settlement_status(
        self, authenticated_client, sample_customer
    ):
        """测试按结算状态筛选"""
        # 先更新客户结算状态为已结算
        await authenticated_client.put(
            f"/api/v1/customers/{sample_customer.id}",
            json={"settlement_status": SettlementStatus.SETTLED.value},
        )

        # 筛选已结算状态
        response = await authenticated_client.get(
            "/api/v1/customers",
            params={"settlement_status": SettlementStatus.SETTLED.value},
        )

        assert response.status == 200
        data = response.json

        # 验证返回的客户结算状态正确
        customer_found = False
        for item in data["items"]:
            if item["id"] == str(sample_customer.id):
                customer_found = True
                assert item["settlement_status"] == SettlementStatus.SETTLED.value
                break
        assert customer_found

    async def test_filter_by_owner(self, authenticated_client, sample_customer):
        """测试按负责人筛选"""
        # 获取当前用户ID
        me_response = await authenticated_client.get("/api/v1/auth/me")
        current_user_id = me_response.json["id"]

        response = await authenticated_client.get(
            "/api/v1/customers", params={"owner_id": current_user_id}
        )

        assert response.status == 200
        data = response.json
        assert data["total"] >= 1

        # 验证返回的客户负责人正确
        for item in data["items"]:
            assert item["owner"] is not None
            assert item["owner"]["id"] == current_user_id

    async def test_filter_combined(
        self,
        authenticated_client,
        sample_industry,
        sample_customer_level,
        sample_customer,
    ):
        """测试组合多个筛选条件"""
        # 先更新客户状态
        await authenticated_client.put(
            f"/api/v1/customers/{sample_customer.id}",
            json={"status": CustomerStatus.ACTIVE.value},
        )

        # 组合筛选：行业 + 等级 + 状态
        response = await authenticated_client.get(
            "/api/v1/customers",
            params={
                "industry_id": str(sample_industry.id),
                "level_id": str(sample_customer_level.id),
                "status": CustomerStatus.ACTIVE.value,
            },
        )

        assert response.status == 200
        data = response.json
        assert data["total"] >= 1

        # 验证所有筛选条件都满足
        for item in data["items"]:
            assert item["industry"]["id"] == str(sample_industry.id)
            assert item["level"]["id"] == str(sample_customer_level.id)
            assert item["status"] == CustomerStatus.ACTIVE.value

    async def test_search_by_name(self, authenticated_client, sample_customer):
        """测试按客户名称搜索"""
        # 搜索客户名称的一部分
        search_keyword = sample_customer.customer_name[:2]
        response = await authenticated_client.get(
            "/api/v1/customers", params={"search": search_keyword}
        )

        assert response.status == 200
        data = response.json
        assert data["total"] >= 1

        # 验证搜索结果包含关键词
        customer_found = False
        for item in data["items"]:
            if (
                search_keyword in item["customer_name"]
                or search_keyword in item["customer_code"]
                or search_keyword in item["contact_person"]
            ):
                customer_found = True
                break
        assert customer_found, "搜索结果不包含匹配的客户"
