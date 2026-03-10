from app.database import async_session_maker
from sqlalchemy import select
from app.models.role import Permission
import asyncio


async def check():
    async with async_session_maker() as session:
        result = await session.execute(select(Permission))
        perms = result.scalars().all()
        print("权限数据示例:")
        for p in perms[:10]:
            print(f"  {p.code} | {p.name} | {p.type}")
        print(f"\n总权限数：{len(perms)}")


asyncio.run(check())
