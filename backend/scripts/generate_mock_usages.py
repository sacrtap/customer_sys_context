"""
生成模拟用量数据脚本

用于生成立史用量数据和结算数据，以便测试 Dashboard API
"""

import asyncio
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# 添加项目路径
sys.path.insert(0, ".")

from config import settings
from app.database import database, async_session_maker
from app.models.customer import (
    Customer,
    CustomerUsage,
    Settlement,
    SettlementStatus,
    Industry,
    CustomerLevel,
)


async def generate_mock_data():
    """生成模拟数据"""
    print("开始生成模拟数据...")

    async with async_session_maker() as session:
        # 获取所有客户
        result = await session.execute(select(Customer))
        customers = result.scalars().all()

        if not customers:
            print("警告：没有找到客户，请先创建客户数据")
            return

        print(f"找到 {len(customers)} 个客户")

        # 为每个客户生成用量数据
        for customer in customers:
            # 生成过去 12 个月的用量数据
            current_date = date.today()

            for i in range(12):
                # 计算月份
                month_offset = 11 - i
                month_date = current_date - timedelta(days=30 * month_offset)
                # 设置为月初
                month_date = date(month_date.year, month_date.month, 1)

                # 检查是否已存在该月的数据
                exists_query = select(CustomerUsage).where(
                    CustomerUsage.customer_id == customer.id,
                    CustomerUsage.month == month_date,
                )
                exists_result = await session.execute(exists_query)
                if exists_result.scalar():
                    continue

                # 生成随机用量
                usage_count = random.randint(50, 500)
                amount = Decimal(str(round(random.uniform(500, 5000), 2)))

                usage = CustomerUsage(
                    customer_id=customer.id,
                    month=month_date,
                    usage_count=usage_count,
                    amount=amount,
                )
                session.add(usage)

            # 生成结算数据
            for i in range(6):
                month_offset = 5 - i
                month_date = current_date - timedelta(days=30 * month_offset)
                month_date = date(month_date.year, month_date.month, 1)

                # 检查是否已存在
                exists_query = select(Settlement).where(
                    Settlement.customer_id == customer.id,
                    Settlement.month == month_date,
                )
                exists_result = await session.execute(exists_query)
                if exists_result.scalar():
                    continue

                # 生成结算记录（70% 已结算）
                amount = Decimal(str(round(random.uniform(500, 5000), 2)))
                is_settled = random.random() < 0.7

                settlement = Settlement(
                    customer_id=customer.id,
                    month=month_date,
                    amount=amount,
                    status=SettlementStatus.SETTLED
                    if is_settled
                    else SettlementStatus.UNSETTLED,
                    settled_at=datetime.now() if is_settled else None,
                )
                session.add(settlement)

        await session.commit()
        print("✓ 模拟数据生成完成")


async def main():
    """主函数"""
    await database.connect()

    try:
        await generate_mock_data()
    finally:
        await database.disconnect()


if __name__ == "__main__":
    from sqlalchemy import select

    asyncio.run(main())
