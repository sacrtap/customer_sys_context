"""
角色表单 API 测试
"""

import pytest
import pytest_asyncio
from sqlalchemy import select
import uuid


class TestRoleFormAPI:
    """角色表单 API 测试"""

    async def test_update_role_permissions(self, authenticated_client):
        """测试批量更新角色权限"""
        # 先创建一个测试角色和一些权限
        async with authenticated_client.app.ctx.db() as session:
            from app.models.role import Role, Permission

            # 创建测试角色
            role = Role(name="测试角色", description="测试权限更新")
            session.add(role)
            await session.flush()
            role_id = str(role.id)

            # 创建一些测试权限
            perm1 = Permission(code="users:read", name="查看用户", type="api")
            perm2 = Permission(code="users:create", name="创建用户", type="api")
            session.add_all([perm1, perm2])
            await session.flush()

            perm_ids = [str(perm1.id), str(perm2.id)]

        # 批量更新角色权限
        response = await authenticated_client.post(
            f"/api/v1/roles/{role_id}/permissions", json={"permission_ids": perm_ids}
        )

        assert response.status == 200
        data = response.json
        assert "message" in data or "permissions" in data

        # 验证权限已更新
        get_response = await authenticated_client.get(f"/api/v1/roles/{role_id}")
        assert get_response.status == 200
        role_data = get_response.json
        assert len(role_data.get("permissions", [])) >= 2

    async def test_update_role_permissions_invalid_role(self, authenticated_client):
        """测试更新不存在角色的权限"""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.post(
            f"/api/v1/roles/{fake_id}/permissions",
            json={"permission_ids": ["fake-permission-id"]},
        )

        assert response.status == 404
        data = response.json
        assert "error" in data

    async def test_get_role_users(self, authenticated_client):
        """测试获取角色下的用户列表"""
        # 创建测试角色和用户
        async with authenticated_client.app.ctx.db() as session:
            from app.models.role import Role
            from app.models.user import User

            role = Role(name="测试角色", description="测试用户列表")
            session.add(role)
            await session.flush()
            role_id = str(role.id)

            # 创建关联用户
            user1 = User(
                username=f"roleuser1_{uuid.uuid4().hex[:8]}",
                email="roleuser1@example.com",
                password_hash=User.hash_password("password123"),
                is_active=True,
            )
            user1.roles = [role]
            session.add(user1)

            user2 = User(
                username=f"roleuser2_{uuid.uuid4().hex[:8]}",
                email="roleuser2@example.com",
                password_hash=User.hash_password("password123"),
                is_active=True,
            )
            user2.roles = [role]
            session.add(user2)

            await session.flush()

        # 获取角色下的用户列表
        response = await authenticated_client.get(f"/api/v1/roles/{role_id}/users")

        assert response.status == 200
        data = response.json

        # 验证返回用户列表
        assert "items" in data or "users" in data
        users_list = data.get("items", data.get("users", []))
        assert len(users_list) >= 2

        # 验证用户信息
        usernames = [u["username"] for u in users_list]
        assert any("roleuser1" in u for u in usernames)
        assert any("roleuser2" in u for u in usernames)

    async def test_get_role_users_empty(self, authenticated_client):
        """测试获取空角色下的用户列表"""
        # 创建没有用户的角色
        async with authenticated_client.app.ctx.db() as session:
            from app.models.role import Role

            role = Role(name="空角色", description="没有用户")
            session.add(role)
            await session.flush()
            role_id = str(role.id)

        # 获取用户列表
        response = await authenticated_client.get(f"/api/v1/roles/{role_id}/users")

        assert response.status == 200
        data = response.json

        # 验证返回空列表
        users_list = data.get("items", data.get("users", []))
        assert len(users_list) == 0
        assert data.get("total", 0) == 0

    async def test_update_role_permissions_partial(self, authenticated_client):
        """测试部分更新角色权限"""
        # 创建角色和权限
        async with authenticated_client.app.ctx.db() as session:
            from app.models.role import Role, Permission

            role = Role(name="部分更新角色", description="测试部分更新")
            session.add(role)
            await session.flush()
            role_id = str(role.id)

            # 创建 3 个权限
            perms = []
            for i in range(3):
                perm = Permission(code=f"test:perm{i}", name=f"测试权限{i}", type="api")
                session.add(perm)
                perms.append(perm)

            await session.flush()

            # 先分配所有权限
            role.permissions = perms
            await session.flush()

        # 只保留前两个权限
        response = await authenticated_client.post(
            f"/api/v1/roles/{role_id}/permissions",
            json={"permission_ids": [str(perms[0].id), str(perms[1].id)]},
        )

        assert response.status == 200

        # 验证权限数量
        get_response = await authenticated_client.get(f"/api/v1/roles/{role_id}")
        role_data = get_response.json
        assert len(role_data.get("permissions", [])) == 2
