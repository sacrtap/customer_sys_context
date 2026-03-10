"""
健康检查 API 测试
"""

import pytest
from datetime import datetime


class TestHealthAPI:
    """健康检查 API 测试"""

    async def test_health_check_authenticated(self, authenticated_client):
        """测试健康检查接口 - 已认证用户"""
        response = await authenticated_client.get("/api/v1/health")

        assert response.status == 200
        data = response.json

        # 验证返回字段
        assert "status" in data
        assert "database" in data
        assert "version" in data
        assert "uptime" in data

        # 验证状态
        assert data["status"] == "healthy"
        assert data["database"]["status"] == "connected"

        # 验证版本信息
        assert "api_version" in data["version"]
        assert data["version"]["api_version"] == "v1"

    async def test_health_check_unauthenticated(self, app):
        """测试健康检查接口 - 未认证用户（允许访问）"""
        client = app.test_client
        client.app.config.SINGLE_WORKER = True

        response = await client.get("/api/v1/health")

        assert response.status == 200
        data = response.json

        # 健康检查接口应该允许未认证访问
        assert data["status"] == "healthy"
        assert data["database"]["status"] == "connected"

    async def test_health_check_version_info(self, authenticated_client):
        """测试版本信息完整性"""
        response = await authenticated_client.get("/api/v1/health")

        assert response.status == 200
        data = response.json

        version = data["version"]

        # 验证版本字段
        assert "api_version" in version
        assert "build_time" in version or "timestamp" in version

        # uptime 应该是正数
        assert data["uptime"] >= 0
