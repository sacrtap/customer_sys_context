#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 SQLAlchemy 枚举类型查询"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.models.customer import Customer, CustomerStatus
from app.database import async_session_maker
import asyncio


async def test():
    async with async_session_maker() as session:
        # 测试 1: 直接使用字符串
        query1 = select(Customer).where(Customer.status == "active")
        print("Query 1 (string) SQL:", str(query1))

        # 测试 2: 使用枚举.value
        query2 = select(Customer).where(Customer.status == CustomerStatus.ACTIVE.value)
        print("Query 2 (.value) SQL:", str(query2))

        # 测试 3: 使用枚举对象
        query3 = select(Customer).where(Customer.status == CustomerStatus.ACTIVE)
        print("Query 3 (enum) SQL:", str(query3))

        # 测试 4: 实际执行查询 1
        try:
            result = await session.execute(query1)
            print("Query 1 执行成功:", len(result.scalars().all()))
        except Exception as e:
            print("Query 1 执行失败:", e)

        # 测试 5: 实际执行查询 2
        try:
            result = await session.execute(query2)
            print("Query 2 执行成功:", len(result.scalars().all()))
        except Exception as e:
            print("Query 2 执行失败:", e)

        # 测试 6: 实际执行查询 3
        try:
            result = await session.execute(query3)
            print("Query 3 执行成功:", len(result.scalars().all()))
        except Exception as e:
            print("Query 3 执行失败:", e)


if __name__ == "__main__":
    asyncio.run(test())
