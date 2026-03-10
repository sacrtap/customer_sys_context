"""
结算管理路由
"""

from datetime import datetime
from decimal import Decimal
from sanic import Blueprint, json, request, response
from sqlalchemy import select, func, extract
from io import BytesIO

from app.database import get_db
from app.models.customer import (
    Settlement,
    Customer,
    CustomerUsage,
    SettlementStatus,
)
from app.schemas.settlement import (
    SettlementCreate,
    SettlementUpdate,
    PaymentConfirmRequest,
    MonthlyBillGenerateRequest,
    ExportRequest,
)
from app.utils.deps import require_permission
from app.services.billing import BillingService

bp = Blueprint("settlements", url_prefix="/settlements")


def settlement_to_dict(settlement: Settlement) -> dict:
    """将结算记录转换为字典"""
    return {
        "id": str(settlement.id),
        "customer_id": str(settlement.customer_id),
        "customer_name": settlement.customer.customer_name
        if settlement.customer
        else None,
        "month": settlement.month.isoformat(),
        "amount": str(settlement.amount),
        "status": settlement.status.value,
        "settled_at": settlement.settled_at.isoformat()
        if settlement.settled_at
        else None,
        "remark": settlement.remark,
        "created_at": settlement.created_at.isoformat(),
        "updated_at": settlement.updated_at.isoformat(),
    }


@bp.get("")
@require_permission("settlements:read")
async def list_settlements(request):
    """结算记录列表"""
    async with request.app.ctx.db() as session:
        query = select(Settlement)

        # 筛选参数
        customer_id = request.args.get("customer_id")
        if customer_id:
            query = query.where(Settlement.customer_id == customer_id)

        status = request.args.get("status")
        if status:
            query = query.where(Settlement.status == status)

        month = request.args.get("month")
        if month:
            try:
                month_date = datetime.strptime(month, "%Y-%m").date()
                query = query.where(
                    (extract("year", Settlement.month) == month_date.year)
                    & (extract("month", Settlement.month) == month_date.month)
                )
            except ValueError:
                return json({"error": "月份格式错误，应为 YYYY-MM"}, status=400)

        # 分页
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        offset = (page - 1) * page_size

        # 总数
        count_query = select(func.count()).select_from(Settlement)
        if customer_id:
            count_query = count_query.where(Settlement.customer_id == customer_id)
        if status:
            count_query = count_query.where(Settlement.status == status)

        count_result = await session.execute(count_query)
        total = count_result.scalar()

        # 加载客户信息
        from sqlalchemy.orm import selectinload

        query = query.options(selectinload(Settlement.customer))
        query = query.offset(offset).limit(page_size)
        result = await session.execute(query)
        settlements = result.scalars().all()

    return json(
        {
            "items": [settlement_to_dict(s) for s in settlements],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@bp.get("/<settlement_id>")
@require_permission("settlements:read")
async def get_settlement(request, settlement_id):
    """获取结算记录详情"""
    from sqlalchemy.orm import selectinload
    import uuid

    try:
        settlement_uuid = uuid.UUID(settlement_id)
    except ValueError:
        return json({"error": "无效的结算记录 ID"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Settlement)
            .options(selectinload(Settlement.customer))
            .where(Settlement.id == settlement_uuid)
        )
        settlement = result.scalar()

        if not settlement:
            return json({"error": "结算记录不存在"}, status=404)

    return json(settlement_to_dict(settlement))


@bp.post("")
@require_permission("settlements:create")
async def create_settlement(request):
    """创建结算记录"""
    from sqlalchemy.orm import selectinload

    try:
        data = SettlementCreate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        # 验证客户是否存在
        result = await session.execute(
            select(Customer).where(Customer.id == data.customer_id)
        )
        customer = result.scalar()

        if not customer:
            return json({"error": "客户不存在"}, status=400)

        # 解析月份
        try:
            month_date = datetime.strptime(data.month, "%Y-%m").date()
        except ValueError:
            return json({"error": "月份格式错误，应为 YYYY-MM"}, status=400)

        # 检查是否已存在该月份的结算记录
        existing = await session.scalar(
            select(Settlement).where(
                Settlement.customer_id == data.customer_id,
                extract("year", Settlement.month) == month_date.year,
                extract("month", Settlement.month) == month_date.month,
            )
        )

        if existing:
            return json({"error": "该客户该月份的结算记录已存在"}, status=400)

        # 创建结算记录
        settlement = Settlement(
            customer_id=data.customer_id,
            month=month_date,
            amount=data.amount,
            status=SettlementStatus.UNSETTLED,
            remark=data.remark,
        )

        session.add(settlement)
        await session.flush()

    return json(
        {
            "id": str(settlement.id),
            "message": "结算记录创建成功",
        },
        status=201,
    )


@bp.put("/<settlement_id>")
@require_permission("settlements:update")
async def update_settlement(request, settlement_id):
    """更新结算记录"""
    import uuid

    try:
        settlement_uuid = uuid.UUID(settlement_id)
    except ValueError:
        return json({"error": "无效的结算记录 ID"}, status=400)

    try:
        data = SettlementUpdate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Settlement).where(Settlement.id == settlement_uuid)
        )
        settlement = result.scalar()

        if not settlement:
            return json({"error": "结算记录不存在"}, status=404)

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                if field == "status":
                    # 验证状态值
                    try:
                        setattr(settlement, field, SettlementStatus(value))
                    except ValueError:
                        return json({"error": "无效的结算状态"}, status=400)
                elif field == "amount":
                    if value <= 0:
                        return json({"error": "金额必须大于 0"}, status=400)
                    setattr(settlement, field, value)
                else:
                    setattr(settlement, field, value)

        await session.flush()

    return json({"message": "结算记录更新成功"})


@bp.delete("/<settlement_id>")
@require_permission("settlements:delete")
async def delete_settlement(request, settlement_id):
    """删除结算记录"""
    import uuid

    try:
        settlement_uuid = uuid.UUID(settlement_id)
    except ValueError:
        return json({"error": "无效的结算记录 ID"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Settlement).where(Settlement.id == settlement_uuid)
        )
        settlement = result.scalar()

        if not settlement:
            return json({"error": "结算记录不存在"}, status=404)

        await session.delete(settlement)
        await session.flush()

    return json({"message": "结算记录删除成功"})


@bp.post("/<settlement_id>/confirm-payment")
@require_permission("settlements:update")
async def confirm_payment(request, settlement_id):
    """确认支付"""
    import uuid

    try:
        settlement_uuid = uuid.UUID(settlement_id)
    except ValueError:
        return json({"error": "无效的结算记录 ID"}, status=400)

    try:
        data = PaymentConfirmRequest(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Settlement).where(Settlement.id == settlement_uuid)
        )
        settlement = result.scalar()

        if not settlement:
            return json({"error": "结算记录不存在"}, status=404)

        # 解析支付时间
        try:
            paid_at = datetime.fromisoformat(data.paid_at.replace("Z", "+00:00"))
        except ValueError:
            return json({"error": "支付时间格式错误"}, status=400)

        # 更新结算记录
        settlement.status = SettlementStatus.SETTLED
        settlement.settled_at = paid_at
        settlement.remark = f"已支付 {data.paid_amount}" + (
            f" - {settlement.remark}" if settlement.remark else ""
        )

        await session.flush()

    return json({"message": "支付确认成功"})


@bp.post("/generate-monthly")
@require_permission("settlements:create")
async def generate_monthly(request):
    """生成月度账单"""
    try:
        data = MonthlyBillGenerateRequest(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        service = BillingService(session)
        generated, skipped = await service.generate_monthly_bills(
            year=data.year,
            month=data.month,
            customer_ids=data.customer_ids,
        )

    return json(
        {
            "generated_count": generated,
            "skipped_count": skipped,
        }
    )


@bp.post("/export")
@require_permission("settlements:read")
async def export_settlements(request):
    """导出结算记录为 Excel"""
    try:
        data = ExportRequest(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        service = BillingService(session)

        # 解析日期范围
        start_date = None
        end_date = None
        if data.date_range.get("start"):
            try:
                start_date = datetime.strptime(
                    data.date_range["start"], "%Y-%m-%d"
                ).date()
            except ValueError:
                return json({"error": "开始日期格式错误"}, status=400)

        if data.date_range.get("end"):
            try:
                end_date = datetime.strptime(data.date_range["end"], "%Y-%m-%d").date()
            except ValueError:
                return json({"error": "结束日期格式错误"}, status=400)

        settlements = await service.export_settlements(
            customer_ids=data.customer_ids,
            start_date=start_date,
            end_date=end_date,
        )

    # 生成 Excel
    try:
        import pandas as pd

        df = pd.DataFrame(settlements)
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="结算记录")

        output.seek(0)

        return response(
            output.read(),
            headers={
                "Content-Disposition": 'attachment; filename="settlements.xlsx"',
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        )
    except Exception as e:
        return json({"error": f"导出失败：{str(e)}"}, status=500)
