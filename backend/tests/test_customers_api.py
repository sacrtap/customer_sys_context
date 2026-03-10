import pytest
import uuid

pytestmark = pytest.mark.asyncio


class TestCustomersCRUD:
    """客户CRUD操作测试"""

    async def test_list_customers(self, authenticated_client, sample_customer):
        """测试获取客户列表"""
        response = await authenticated_client.get("/api/v1/customers")

        assert response.status == 200
        data = response.json
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

        # 检查返回的客户信息是否正确
        customer_found = False
        for item in data["items"]:
            if item["id"] == str(sample_customer.id):
                customer_found = True
                assert item["customer_code"] == sample_customer.customer_code
                assert item["customer_name"] == sample_customer.customer_name
                assert item["contact_person"] == sample_customer.contact_person
                break
        assert customer_found, "测试客户未在列表中找到"

    async def test_get_customer(self, authenticated_client, sample_customer):
        """测试获取单个客户详情"""
        response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )

        assert response.status == 200
        data = response.json
        assert data["id"] == str(sample_customer.id)
        assert data["customer_code"] == sample_customer.customer_code
        assert data["customer_name"] == sample_customer.customer_name
        assert data["contact_person"] == sample_customer.contact_person
        assert data["contact_phone"] == sample_customer.contact_phone
        assert data["contact_email"] == sample_customer.contact_email
        assert data["address"] == sample_customer.address
        assert data["remark"] == sample_customer.remark

    async def test_get_customer_not_found(self, authenticated_client):
        """测试获取不存在的客户返回404"""
        non_existent_id = uuid.uuid4()
        response = await authenticated_client.get(
            f"/api/v1/customers/{non_existent_id}"
        )

        assert response.status == 404
        assert "error" in response.json
        assert response.json["error"] == "客户不存在"

    async def test_create_customer(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试创建新客户"""
        customer_data = {
            "customer_code": f"TEST_NEW_{uuid.uuid4().hex[:8].upper()}",
            "customer_name": "新建测试客户",
            "industry_id": str(sample_industry.id),
            "level_id": str(sample_customer_level.id),
            "contact_person": "李四",
            "contact_phone": "13900139000",
            "contact_email": "new_test@example.com",
            "address": "新测试地址",
            "remark": "新建测试备注",
        }

        response = await authenticated_client.post(
            "/api/v1/customers", json=customer_data
        )

        assert response.status == 201
        data = response.json
        assert "id" in data
        assert data["customer_code"] == customer_data["customer_code"]
        assert data["message"] == "客户创建成功"

        # 验证客户是否真的创建成功
        customer_id = data["id"]
        get_response = await authenticated_client.get(
            f"/api/v1/customers/{customer_id}"
        )
        assert get_response.status == 200
        assert get_response.json["customer_name"] == customer_data["customer_name"]

    async def test_create_customer_duplicate_code(
        self, authenticated_client, sample_customer
    ):
        """测试客户编码重复返回400"""
        customer_data = {
            "customer_code": sample_customer.customer_code,  # 使用已存在的编码
            "customer_name": "重复编码测试客户",
            "industry_id": str(sample_customer.industry_id),
            "level_id": str(sample_customer.level_id),
            "contact_person": "王五",
            "contact_phone": "13700137000",
        }

        response = await authenticated_client.post(
            "/api/v1/customers", json=customer_data
        )

        # 这里应该返回400，因为编码重复，但目前API可能没有做唯一校验，所以会失败
        assert response.status == 400
        assert "error" in response.json

    async def test_update_customer(self, authenticated_client, sample_customer):
        """测试更新客户信息"""
        update_data = {
            "customer_name": "更新后的客户名称",
            "contact_person": "更新后的联系人",
            "contact_phone": "13600136000",
            "remark": "更新后的备注",
        }

        response = await authenticated_client.put(
            f"/api/v1/customers/{sample_customer.id}", json=update_data
        )

        assert response.status == 200
        assert response.json["message"] == "客户更新成功"

        # 验证更新是否生效
        get_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert get_response.status == 200
        assert get_response.json["customer_name"] == update_data["customer_name"]
        assert get_response.json["contact_person"] == update_data["contact_person"]
        assert get_response.json["contact_phone"] == update_data["contact_phone"]
        assert get_response.json["remark"] == update_data["remark"]

    async def test_update_customer_not_found(self, authenticated_client):
        """测试更新不存在的客户返回404"""
        non_existent_id = uuid.uuid4()
        update_data = {"customer_name": "不存在的客户"}

        response = await authenticated_client.put(
            f"/api/v1/customers/{non_existent_id}", json=update_data
        )

        assert response.status == 404
        assert "error" in response.json
        assert response.json["error"] == "客户不存在"

    async def test_delete_customer(self, authenticated_client, sample_customer):
        """测试删除客户"""
        response = await authenticated_client.delete(
            f"/api/v1/customers/{sample_customer.id}"
        )

        assert response.status == 200
        assert response.json["message"] == "客户删除成功"

        # 验证客户是否真的被删除
        get_response = await authenticated_client.get(
            f"/api/v1/customers/{sample_customer.id}"
        )
        assert get_response.status == 404

    async def test_delete_customer_not_found(self, authenticated_client):
        """测试删除不存在的客户返回404"""
        non_existent_id = uuid.uuid4()
        response = await authenticated_client.delete(
            f"/api/v1/customers/{non_existent_id}"
        )

        assert response.status == 404
        assert "error" in response.json
        assert response.json["error"] == "客户不存在"
