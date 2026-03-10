import pytest
import uuid
from io import BytesIO
import pandas as pd

pytestmark = pytest.mark.asyncio


class TestCustomerImport:
    """客户Excel导入测试"""

    def _generate_test_excel(self, data: list) -> BytesIO:
        """生成测试用Excel文件"""
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        return output

    async def test_import_excel_success(
        self, authenticated_client, sample_industry, sample_customer_level
    ):
        """测试成功导入Excel数据"""
        # 准备测试数据
        test_data = [
            {
                "客户编码": f"IMP_{uuid.uuid4().hex[:8].upper()}",
                "客户名称": "导入测试客户1",
                "行业": sample_industry.name,
                "客户等级": sample_customer_level.code,
                "联系人": "导入测试人1",
                "联系电话": "13800138001",
                "联系邮箱": "import1@example.com",
                "地址": "导入测试地址1",
                "状态": "启用",
                "结算状态": "未结算",
                "负责人": "admin",
                "备注": "导入测试备注1",
            },
            {
                "客户编码": f"IMP_{uuid.uuid4().hex[:8].upper()}",
                "客户名称": "导入测试客户2",
                "联系人": "导入测试人2",
                "联系电话": "13800138002",
                "备注": "导入测试备注2",
            },
        ]

        # 生成Excel文件
        excel_file = self._generate_test_excel(test_data)

        # 上传导入
        response = await authenticated_client.post(
            "/api/v1/customers/import",
            files={
                "file": (
                    "test_customers.xlsx",
                    excel_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        assert response.status == 200
        data = response.json
        assert data["success"] is True
        assert "成功导入 2 条客户数据" in data["message"]
        assert data["summary"]["success_count"] == 2
        assert data["summary"]["error_count"] == 0
        assert data["summary"]["total_count"] == 2

    async def test_import_excel_partial_failure(self, authenticated_client):
        """测试部分记录导入失败"""
        # 准备测试数据，包含错误记录
        test_data = [
            {
                "客户编码": f"IMP_{uuid.uuid4().hex[:8].upper()}",
                "客户名称": "有效客户",
                "联系人": "有效联系人",
                "联系电话": "13800138003",
            },
            {
                # 缺少必填字段客户名称
                "客户编码": f"IMP_{uuid.uuid4().hex[:8].upper()}",
                "联系人": "无效客户",
                "联系电话": "13800138004",
            },
            {
                # 缺少必填字段客户编码
                "客户名称": "无效客户2",
                "联系人": "无效联系人2",
                "联系电话": "13800138005",
            },
        ]

        # 生成Excel文件
        excel_file = self._generate_test_excel(test_data)

        # 上传导入
        response = await authenticated_client.post(
            "/api/v1/customers/import",
            files={
                "file": (
                    "test_customers_partial.xlsx",
                    excel_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        assert response.status == 400
        data = response.json
        assert data["success"] is False
        assert "数据验证失败，共 2 条错误" in data["message"]
        assert data["summary"]["success_count"] == 1
        assert data["summary"]["error_count"] == 2
        assert data["summary"]["total_count"] == 3
        assert len(data["errors"]) == 2

    async def test_import_excel_invalid_format(self, authenticated_client):
        """测试Excel格式无效返回400"""
        # 上传非Excel文件
        invalid_file = BytesIO(b"this is not an excel file")

        response = await authenticated_client.post(
            "/api/v1/customers/import",
            files={"file": ("test.txt", invalid_file, "text/plain")},
        )

        assert response.status == 400
        assert "error" in response.json
        assert "文件解析失败" in response.json["error"]

    async def test_import_excel_empty_file(self, authenticated_client):
        """测试空文件返回错误"""
        # 空的Excel文件
        empty_data = []
        excel_file = self._generate_test_excel(empty_data)

        response = await authenticated_client.post(
            "/api/v1/customers/import",
            files={
                "file": (
                    "empty.xlsx",
                    excel_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        assert response.status == 400 or response.status == 500
        assert "error" in response.json

    async def test_import_result_format(self, authenticated_client, sample_industry):
        """验证导入结果格式"""
        test_data = [
            {
                "客户编码": f"IMP_{uuid.uuid4().hex[:8].upper()}",
                "客户名称": "格式测试客户",
                "行业": sample_industry.name,
                "联系人": "格式测试人",
                "联系电话": "13800138006",
            }
        ]

        excel_file = self._generate_test_excel(test_data)

        response = await authenticated_client.post(
            "/api/v1/customers/import",
            files={
                "file": (
                    "test_format.xlsx",
                    excel_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        assert response.status == 200
        data = response.json

        # 验证返回格式
        assert "success" in data
        assert "message" in data
        assert "summary" in data
        assert "success_count" in data["summary"]
        assert "error_count" in data["summary"]
        assert "total_count" in data["summary"]
