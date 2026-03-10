#!/usr/bin/env python3
"""
数据库初始化脚本

用法:
    python scripts/init_database.py

功能:
    1. 创建数据库表
    2. 创建枚举类型
    3. 创建初始管理员用户
    4. 创建默认角色和权限
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.database import Base
from app.models.user import User
from app.models.role import Role, Permission
from app.models.customer import Industry, CustomerLevel
from config import settings
import uuid


async def init_database():
    """初始化数据库"""
    print(f"🔧 开始初始化数据库...")
    print(
        f"数据库：{settings.DATABASE_URL.replace('postgresql+asyncpg://', '***@').split('/')[-1]}"
    )

    # 创建引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # 1. 创建枚举类型
            print("\n📋 创建枚举类型...")
            await conn.execute(
                text("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customerstatus') THEN
                        CREATE TYPE customerstatus AS ENUM ('active', 'inactive', 'test');
                    END IF;
                END $$
            """)
            )
            await conn.execute(
                text("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'settlementstatus') THEN
                        CREATE TYPE settlementstatus AS ENUM ('settled', 'unsettled');
                    END IF;
                END $$
            """)
            )
            print("✅ 枚举类型创建成功")

            # 2. 创建所有表
            print("\n📊 创建数据库表...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ 数据库表创建成功")

        # 3. 创建初始数据
        async with async_sessionmaker(engine)() as session:
            # 3.1 创建管理员用户
            print("\n👤 创建管理员用户...")
            result = await session.execute(
                text("SELECT id FROM users WHERE username = 'admin'")
            )
            if result.first():
                print("⚠️  管理员用户已存在")
            else:
                admin = User(
                    id=uuid.uuid4(),
                    username="admin",
                    email="admin@example.com",
                    password_hash=User.hash_password("admin123"),
                    full_name="系统管理员",
                    is_active=True,
                    is_superuser=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                session.add(admin)
                await session.commit()
                print("✅ 管理员用户创建成功 (admin/admin123)")

            # 3.2 创建默认角色
            print("\n🎭 创建默认角色...")
            roles_to_create = [
                ("admin", "系统管理员", "拥有所有权限"),
                ("operator", "操作员", "日常运营操作权限"),
                ("viewer", "观察员", "只读权限"),
            ]

            for code, name, desc in roles_to_create:
                result = await session.execute(
                    text("SELECT id FROM roles WHERE name = :name"), {"name": name}
                )
                if not result.first():
                    role = Role(
                        id=uuid.uuid4(),
                        name=name,
                        code=code,
                        description=desc,
                        is_default=(code == "viewer"),
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    session.add(role)

            await session.commit()
            print("✅ 默认角色创建成功")

            # 3.3 创建默认权限
            print("\n🔐 创建默认权限...")
            permissions_to_create = [
                # 用户管理
                ("user:read", "查看用户", "system"),
                ("user:create", "创建用户", "system"),
                ("user:update", "更新用户", "system"),
                ("user:delete", "删除用户", "system"),
                # 角色管理
                ("role:read", "查看角色", "system"),
                ("role:create", "创建角色", "system"),
                ("role:update", "更新角色", "system"),
                ("role:delete", "删除角色", "system"),
                # 客户管理
                ("customer:read", "查看客户", "business"),
                ("customer:create", "创建客户", "business"),
                ("customer:update", "更新客户", "business"),
                ("customer:delete", "删除客户", "business"),
                # 结算管理
                ("settlement:read", "查看结算", "business"),
                ("settlement:create", "创建结算", "business"),
                ("settlement:update", "更新结算", "business"),
                ("settlement:delete", "删除结算", "business"),
                # Dashboard
                ("dashboard:read", "查看工作台", "business"),
            ]

            for code, name, type_ in permissions_to_create:
                result = await session.execute(
                    text("SELECT id FROM permissions WHERE code = :code"),
                    {"code": code},
                )
                if not result.first():
                    permission = Permission(
                        id=uuid.uuid4(),
                        code=code,
                        name=name,
                        type=type_,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    session.add(permission)

            await session.commit()
            print("✅ 默认权限创建成功")

            # 3.4 创建示例行业
            print("\n🏭 创建示例行业...")
            industries = [
                ("房地产", "realestate", 1),
                ("制造业", "manufacturing", 2),
                ("互联网", "internet", 3),
                ("金融", "finance", 4),
                ("零售", "retail", 5),
            ]

            for name, code, level in industries:
                result = await session.execute(
                    text("SELECT id FROM industries WHERE code = :code"), {"code": code}
                )
                if not result.first():
                    industry = Industry(
                        id=uuid.uuid4(),
                        name=name,
                        code=code,
                        level=level,
                        sort_order=level,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    session.add(industry)

            await session.commit()
            print("✅ 示例行业创建成功")

            # 3.5 创建示例客户等级
            print("\n📈 创建示例客户等级...")
            levels = [
                ("vip", "VIP 客户", 1, "重要客户"),
                ("standard", "普通客户", 2, "普通客户"),
                ("trial", "试用客户", 3, "试用客户"),
            ]

            for code, name, priority, desc in levels:
                result = await session.execute(
                    text("SELECT id FROM customer_levels WHERE code = :code"),
                    {"code": code},
                )
                if not result.first():
                    level = CustomerLevel(
                        id=uuid.uuid4(),
                        code=code,
                        name=name,
                        priority=priority,
                        description=desc,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    session.add(level)

            await session.commit()
            print("✅ 示例客户等级创建成功")

        print("\n" + "=" * 50)
        print("🎉 数据库初始化完成!")
        print("=" * 50)
        print("\n默认管理员账号:")
        print("  用户名：admin")
        print("  密码：admin123")
        print("\n请登录后立即修改密码!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 初始化失败：{e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
