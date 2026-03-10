import pytest
import uuid

pytestmark = pytest.mark.asyncio


class TestCustomerValidation:
    """客户数据验证测试"""

    async def test_create_customer_missing_required_fields(self, authenticated_client):
        """测试缺少必填字段返回400"""
        # 缺少customer_code和customer_name
        invalid_data = {"contact_person": "张三", "contact_phone": "13800138000"}

        response = await authenticated_client.post(
            "/api/v1/customers", json=invalid_data
        )

        assert response.status == 400
        assert "error" in response.json
        assert "数据验证失败" in response.json["error"]

    async def test_create_customer_invalid_email(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试邮箱格式无效返回400"""
        invalid_data = {
            "customer_code": f"TEST_EMAIL_{uuid.uuid4().hex[:8].upper()}",
            "customer_name": "无效邮箱测试客户",
            "industry_id": str(sample_industry.id),
            "level_id": str(sample_customer_level.id),
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "contact_email": "invalid-email-format",  # 无效邮箱
        }

        response = await authenticated_client.post(
            "/api/v1/customers", json=invalid_data
        )

        assert response.status == 400
        assert "error" in response.json
        assert "数据验证失败" in response.json["error"]

    async def test_create_customer_invalid_phone(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试手机号格式无效返回400"""
        invalid_data = {
            "customer_code": f"TEST_PHONE_{uuid.uuid4().hex[:8].upper()}",
            "customer_name": "无效手机号测试客户",
            "industry_id": str(sample_industry.id),
            "level_id": str(sample_customer_level.id),
            "contact_person": "张三",
            "contact_phone": "123456",  # 无效手机号
            "contact_email": "test@example.com",
        }

        response = await authenticated_client.post(
            "/api/v1/customers", json=invalid_data
        )

        assert response.status == 400
        assert "error" in response.json
        assert "数据验证失败" in response.json["error"]

    async def test_create_customer_invalid_industry(
        self, authenticated_client, sample_customer_level
    ):
        """测试行业ID不存在返回400"""
        non_existent_industry_id = uuid.uuid4()
        invalid_data = {
            "customer_code": f"TEST_INDUSTRY_{uuid.uuid4().hex[:8].upper()}",
            "customer_name": "无效行业测试客户",
            "industry_id": str(non_existent_industry_id),  # 不存在的行业ID
            "level_id": str(sample_customer_level.id),
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "contact_email": "test@example.com",
        }

        response = await authenticated_client.post(
            "/api/v1/customers", json=invalid_data
        )

        # 目前API可能没有校验行业ID是否存在，所以这个测试会失败
        assert response.status == 400
        assert "error" in response.json
        assert (
            "行业不存在" in response.json["error"]
            or "数据验证失败" in response.json["error"]
        )

    async def test_create_customer_invalid_level(
        self, authenticated_client, sample_industry
    ):
        """测试客户等级ID不存在返回400"""
        non_existent_level_id = uuid.uuid4()
        invalid_data = {
            "customer_code": f"TEST_LEVEL_{uuid.uuid4().hex[:8].upper()}",
            "customer_name": "无效等级测试客户",
            "industry_id": str(sample_industry.id),
            "level_id": str(non_existent_level_id),  # 不存在的等级ID
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "contact_email": "test@example.com",
        }

        response = await authenticated_client.post(
            "/api/v1/customers", json=invalid_data
        )

        # 目前API可能没有校验等级ID是否存在，所以这个测试会失败
        assert response.status == 400
        assert "error" in response.json
        assert (
            "客户等级不存在" in response.json["error"]
            or "数据验证失败" in response.json["error"]
        )
