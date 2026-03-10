"""
新 API 端点集成测试脚本
使用同步测试客户端，避免 Python 3.14 事件循环问题

sanic-testing 客户端返回 (request, response) 元组
"""

import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import create_app
from app.database import database, async_session_maker
import json


def test_health_api():
    """测试健康检查 API"""
    print("\n=== 测试健康检查 API ===")

    app = create_app()
    app.ctx.db = lambda: async_session_maker()

    client = app.test_client
    app.config.SINGLE_WORKER = True

    # 测试未认证访问 - 返回 (request, response) 元组
    request, response = client.get("/api/v1/health")
    print(f"GET /api/v1/health - 状态码：{response.status}")

    assert response.status == 200, f"期望 200，实际 {response.status}"

    data = response.json
    print(f"响应数据：{json.dumps(data, indent=2, ensure_ascii=False)}")

    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "version" in data
    assert "uptime" in data

    print("✓ 健康检查 API 测试通过")


def test_users_api():
    """测试用户 API 新增端点"""
    print("\n=== 测试用户 API ===")

    app = create_app()
    app.ctx.db = lambda: async_session_maker()

    client = app.test_client
    app.config.SINGLE_WORKER = True

    # 1. 登录获取 token
    print("1. 登录获取 token...")
    req, login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    print(f"   登录状态码：{login_response.status}")

    if login_response.status != 200:
        print("   ⚠ 登录失败，跳过后续测试")
        return

    token = login_response.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 测试获取当前用户信息
    print("2. 测试 GET /api/v1/users/me...")
    req, response = client.get("/api/v1/users/me", headers=headers)
    print(f"   状态码：{response.status}")

    if response.status == 200:
        data = response.json
        print(f"   当前用户：{data.get('username')}")
        assert "username" in data
        print("   ✓ 获取当前用户信息成功")
    else:
        print(f"   ✗ 失败：{response.json}")

    # 3. 测试获取用户详情
    print("3. 测试 GET /api/v1/users/{id}...")
    # 先获取用户列表找到 admin 的 ID
    req, users_response = client.get("/api/v1/users", headers=headers)
    if users_response.status == 200:
        users_data = users_response.json
        if users_data.get("items"):
            admin_id = users_data["items"][0]["id"]
            req, detail_response = client.get(
                f"/api/v1/users/{admin_id}", headers=headers
            )
            print(f"   状态码：{detail_response.status}")

            if detail_response.status == 200:
                print("   ✓ 获取用户详情成功")
            else:
                print(f"   ✗ 失败：{detail_response.json}")

    print("✓ 用户 API 测试完成")


def test_roles_api():
    """测试角色 API 新增端点"""
    print("\n=== 测试角色 API ===")

    app = create_app()
    app.ctx.db = lambda: async_session_maker()

    client = app.test_client
    app.config.SINGLE_WORKER = True

    # 登录
    req, login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    if login_response.status != 200:
        print("⚠ 登录失败，跳过测试")
        return

    token = login_response.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 获取角色列表
    print("1. 获取角色列表...")
    req, response = client.get("/api/v1/roles", headers=headers)
    print(f"   状态码：{response.status}")

    if response.status == 200:
        roles_data = response.json
        print(f"   角色数量：{len(roles_data.get('items', []))}")

        # 获取第一个角色的 ID
        if roles_data.get("items"):
            role_id = roles_data["items"][0]["id"]

            # 2. 测试获取角色下的用户列表
            print(f"2. 测试 GET /api/v1/roles/{role_id}/users...")
            req, users_response = client.get(
                f"/api/v1/roles/{role_id}/users", headers=headers
            )
            print(f"   状态码：{users_response.status}")

            if users_response.status == 200:
                users_data = users_response.json
                print(f"   用户数量：{users_data.get('total', 0)}")
                print("   ✓ 获取角色用户列表成功")

            # 3. 测试获取权限列表
            print("3. 测试 GET /api/v1/roles/permissions...")
            req, perms_response = client.get(
                "/api/v1/roles/permissions", headers=headers
            )
            print(f"   状态码：{perms_response.status}")

            if perms_response.status == 200:
                perms_data = perms_response.json
                print(f"   权限数量：{len(perms_data.get('items', []))}")
                print("   ✓ 获取权限列表成功")

    print("✓ 角色 API 测试完成")


def test_customers_api():
    """测试客户 API 新增端点"""
    print("\n=== 测试客户 API ===")

    app = create_app()
    app.ctx.db = lambda: async_session_maker()

    client = app.test_client
    app.config.SINGLE_WORKER = True

    # 登录
    req, login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    if login_response.status != 200:
        print("⚠ 登录失败，跳过测试")
        return

    token = login_response.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 获取客户列表
    print("1. 获取客户列表...")
    req, response = client.get("/api/v1/customers", headers=headers)
    print(f"   状态码：{response.status}")

    if response.status == 200:
        customers_data = response.json
        print(f"   客户数量：{customers_data.get('total', 0)}")

        if customers_data.get("items"):
            customer_id = customers_data["items"][0]["id"]

            # 2. 测试获取客户详情
            print(f"2. 测试 GET /api/v1/customers/{customer_id}...")
            req, detail_response = client.get(
                f"/api/v1/customers/{customer_id}", headers=headers
            )
            print(f"   状态码：{detail_response.status}")

            if detail_response.status == 200:
                detail_data = detail_response.json
                print(f"   客户名称：{detail_data.get('customer_name')}")
                print("   ✓ 获取客户详情成功")

            # 3. 测试获取客户用量历史
            print(f"3. 测试 GET /api/v1/customers/{customer_id}/usages...")
            req, usages_response = client.get(
                f"/api/v1/customers/{customer_id}/usages", headers=headers
            )
            print(f"   状态码：{usages_response.status}")

            if usages_response.status == 200:
                usages_data = usages_response.json
                print(f"   用量记录数：{usages_data.get('total', 0)}")
                print("   ✓ 获取用量历史成功")

            # 4. 测试获取客户结算记录
            print(f"4. 测试 GET /api/v1/customers/{customer_id}/settlements...")
            req, settlements_response = client.get(
                f"/api/v1/customers/{customer_id}/settlements", headers=headers
            )
            print(f"   状态码：{settlements_response.status}")

            if settlements_response.status == 200:
                settlements_data = settlements_response.json
                print(f"   结算记录数：{settlements_data.get('total', 0)}")
                print("   ✓ 获取结算记录成功")

    print("✓ 客户 API 测试完成")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("新 API 端点集成测试")
    print("=" * 60)

    try:
        test_health_api()
        test_users_api()
        test_roles_api()
        test_customers_api()

        print("\n" + "=" * 60)
        print("✓ 所有测试完成!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 测试失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错：{e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
