"""
数据库初始化脚本 - 创建默认数据和初始权限
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.user import User
from app.models.role import Role, Permission, user_roles, role_permissions
from app.models.customer import Industry, CustomerLevel


async def init_data():
    """初始化基础数据"""

    # 数据库连接
    from config import settings

    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. 创建默认权限
        permissions_data = [
            # 用户管理
            {"code": "users:read", "name": "查看用户", "type": "api"},
            {"code": "users:create", "name": "创建用户", "type": "api"},
            {"code": "users:update", "name": "更新用户", "type": "api"},
            {"code": "users:delete", "name": "删除用户", "type": "api"},
            # 角色管理
            {"code": "roles:read", "name": "查看角色", "type": "api"},
            {"code": "roles:create", "name": "创建角色", "type": "api"},
            {"code": "roles:update", "name": "更新角色", "type": "api"},
            {"code": "roles:delete", "name": "删除角色", "type": "api"},
            # 客户管理
            {"code": "customers:read", "name": "查看客户", "type": "api"},
            {"code": "customers:create", "name": "创建客户", "type": "api"},
            {"code": "customers:update", "name": "更新客户", "type": "api"},
            {"code": "customers:delete", "name": "删除客户", "type": "api"},
        ]

        created_permissions = {}
        for perm_data in permissions_data:
            # 检查是否已存在
            result = await session.execute(
                select(Permission).where(Permission.code == perm_data["code"])
            )
            perm = result.scalar()

            if not perm:
                perm = Permission(**perm_data)
                session.add(perm)
                await session.flush()
                print(f"✓ 创建权限：{perm_data['code']}")
            else:
                print(f"  权限已存在：{perm_data['code']}")

            created_permissions[perm_data["code"]] = perm

        # 2. 创建默认角色
        roles_data = [
            {
                "name": "管理员",
                "description": "系统管理员，拥有所有权限",
                "is_default": False,
                "permissions": list(created_permissions.values()),
            },
            {
                "name": "运营人员",
                "description": "运营人员，拥有客户管理权限",
                "is_default": True,
                "permissions": [
                    created_permissions["customers:read"],
                    created_permissions["customers:create"],
                    created_permissions["customers:update"],
                ],
            },
            {
                "name": "销售人员",
                "description": "销售人员，只能查看和更新自己的客户",
                "is_default": True,
                "permissions": [
                    created_permissions["customers:read"],
                    created_permissions["customers:update"],
                ],
            },
        ]

        for role_data in roles_data:
            result = await session.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            role = result.scalar()

            if not role:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    is_default=role_data["is_default"],
                )
                role.permissions = role_data["permissions"]
                session.add(role)
                await session.flush()
                print(f"✓ 创建角色：{role_data['name']}")
            else:
                print(f"  角色已存在：{role_data['name']}")

        # 3. 创建默认管理员用户
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar()

        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=User.hash_password("admin123"),
                full_name="系统管理员",
                is_active=True,
                is_superuser=True,
            )
            # 分配管理员角色
            admin_role = await session.scalar(select(Role).where(Role.name == "管理员"))
            if admin_role:
                admin.roles.append(admin_role)
            session.add(admin)
            await session.flush()
            print("✓ 创建管理员用户：admin (密码：admin123)")
        else:
            print("  管理员用户已存在")

        # 4. 创建默认行业分类
        industries_data = [
            {"code": "project", "name": "项目", "level": 1},
            {"code": "broker", "name": "房产经纪", "level": 1},
            {"code": "erp", "name": "房产 ERP", "level": 1},
            {"code": "developer", "name": "开发商", "level": 1},
            {"code": "agency", "name": "中介机构", "level": 1},
            {"code": "other", "name": "其他", "level": 1},
        ]

        for ind_data in industries_data:
            result = await session.execute(
                select(Industry).where(Industry.code == ind_data["code"])
            )
            industry = result.scalar()

            if not industry:
                industry = Industry(**ind_data)
                session.add(industry)
                await session.flush()
                print(f"✓ 创建行业：{ind_data['name']}")
            else:
                print(f"  行业已存在：{ind_data['name']}")

        # 5. 创建客户等级
        levels_data = [
            {"code": "S", "name": "S 级客户", "priority": 5},
            {"code": "A", "name": "A 级客户", "priority": 4},
            {"code": "B", "name": "B 级客户", "priority": 3},
            {"code": "C", "name": "C 级客户", "priority": 2},
            {"code": "D", "name": "D 级客户", "priority": 1},
        ]

        for lvl_data in levels_data:
            result = await session.execute(
                select(CustomerLevel).where(CustomerLevel.code == lvl_data["code"])
            )
            level = result.scalar()

            if not level:
                level = CustomerLevel(**lvl_data)
                session.add(level)
                await session.flush()
                print(f"✓ 创建客户等级：{lvl_data['name']}")
            else:
                print(f"  客户等级已存在：{lvl_data['name']}")

        await session.commit()
        print("\n✓ 数据库初始化完成!")


if __name__ == "__main__":
    asyncio.run(init_data())
