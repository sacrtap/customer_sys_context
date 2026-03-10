# -*- coding: utf-8 -*-
"""
结算管理 API 手动测试脚本
"""

import asyncio
from datetime import date
from decimal import Decimal

async def test_settlements():
    """测试结算管理 API"""
    from main import create_app
    from app.database import async_session_maker
    from app.models.customer import Settlement, SettlementStatus, Customer, Industry, CustomerLevel
    from app.models.user import User
    from sqlalchemy import select
    
    app = create_app()
    app.ctx.db = lambda: async_session_maker()
    
    print("✓ 应用创建成功")
    
    # 测试数据库连接
    async with app.ctx.db() as session:
        # 检查是否有用户
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"✓ 数据库连接成功，用户数：{len(users)}")
        
        # 检查 Settlement 模型
        result = await session.execute(select(Settlement))
        settlements = result.scalars().all()
        print(f"✓ Settlement 模型正常，结算记录数：{len(settlements)}")
    
    print("\n✓ 所有基础测试通过")

if __name__ == "__main__":
    asyncio.run(test_settlements())
