"""
账单服务
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession


class BillingService:
    """账单服务类"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_monthly_bills(
        self,
        year: int,
        month: int,
        customer_ids: Optional[List[str]] = None,
    ) -> tuple[int, int]:
        """
        生成月度账单

        Args:
            year: 年份
            month: 月份
            customer_ids: 客户 ID 列表（可选）

        Returns:
            (generated_count, skipped_count): 生成数量和跳过数量
        """
        from app.models.customer import CustomerUsage, Settlement, SettlementStatus

        # 查询该月份的用量汇总
        usage_query = select(
            CustomerUsage.customer_id,
            func.sum(CustomerUsage.usage_count).label("total_usage"),
            func.sum(CustomerUsage.amount).label("total_amount"),
        ).where(
            extract("year", CustomerUsage.month) == year,
            extract("month", CustomerUsage.month) == month,
        )

        if customer_ids:
            usage_query = usage_query.where(CustomerUsage.customer_id.in_(customer_ids))

        usage_query = usage_query.group_by(CustomerUsage.customer_id)
        result = await self.session.execute(usage_query)
        usage_data = result.all()

        # 创建结算记录
        generated = 0
        skipped = 0

        for row in usage_data:
            # 检查是否已存在结算记录
            exists = await self.session.scalar(
                select(Settlement).where(
                    Settlement.customer_id == row.customer_id,
                    extract("year", Settlement.month) == year,
                    extract("month", Settlement.month) == month,
                )
            )

            if exists:
                skipped += 1
                continue

            # 创建结算记录
            settlement = Settlement(
                customer_id=row.customer_id,
                month=date(year, month, 1),
                amount=row.total_amount or Decimal("0"),
                status=SettlementStatus.UNSETTLED,
            )
            self.session.add(settlement)
            generated += 1

        await self.session.commit()
        return generated, skipped

    async def export_settlements(
        self,
        customer_ids: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[dict]:
        """
        导出结算记录

        Args:
            customer_ids: 客户 ID 列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            结算记录列表
        """
        from app.models.customer import Settlement, Customer
        from sqlalchemy.orm import selectinload

        query = select(Settlement).options(
            selectinload(Settlement.customer).selectinload(Customer.owner)
        )

        if customer_ids:
            query = query.where(Settlement.customer_id.in_(customer_ids))

        if start_date:
            query = query.where(Settlement.month >= start_date)

        if end_date:
            query = query.where(Settlement.month <= end_date)

        query = query.order_by(Settlement.month.desc())
        result = await self.session.execute(query)
        settlements = result.scalars().all()

        return [
            {
                "id": str(s.id),
                "customer_id": str(s.customer_id),
                "customer_name": s.customer.customer_name if s.customer else None,
                "month": s.month.isoformat(),
                "amount": str(s.amount),
                "status": s.status.value,
                "settled_at": s.settled_at.isoformat() if s.settled_at else None,
                "remark": s.remark,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in settlements
        ]
