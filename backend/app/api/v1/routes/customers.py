"""
客户管理路由
"""

from sanic import Blueprint, json, request
from sqlalchemy import select, func
from io import BytesIO
from uuid import UUID

from app.models.customer import (
    Customer,
    CustomerUsage,
    Industry,
    CustomerLevel,
    CustomerStatus,
    SettlementStatus,
)
from app.utils.deps import require_permission

bp = Blueprint("customers", url_prefix="/customers")


@bp.get("")
@require_permission("customers:read")
async def list_customers(request):
    """客户列表"""
    async with request.app.ctx.db() as session:
        query = select(Customer)

        # 搜索
        search = request.args.get("search")
        if search:
            query = query.where(
                (Customer.customer_name.contains(search))
                | (Customer.customer_code.contains(search))
                | (Customer.contact_person.contains(search))
            )

        # 状态筛选
        status = request.args.get("status")
        if status:
            # 尝试将输入转换为枚举值（支持 "ACTIVE" 或 "active" 输入）
            try:
                status_enum = CustomerStatus[status.upper()]
                query = query.where(Customer.status == status_enum.value)
            except KeyError:
                return json({"error": f"无效的客户状态：{status}"}, status=400)

        # 结算状态筛选
        settlement_status = request.args.get("settlement_status")
        if settlement_status:
            # 尝试将输入转换为枚举值（支持 "UNSETTLED" 或 "unsettled" 输入）
            try:
                status_enum = SettlementStatus[settlement_status.upper()]
                query = query.where(Customer.settlement_status == status_enum.value)
            except KeyError:
                return json(
                    {"error": f"无效的结算状态：{settlement_status}"}, status=400
                )

        # 行业筛选
        industry_id = request.args.get("industry_id")
        if industry_id:
            query = query.where(Customer.industry_id == industry_id)

        # 客户等级筛选
        level_id = request.args.get("level_id")
        if level_id:
            query = query.where(Customer.level_id == level_id)

        # 负责人筛选
        owner_id = request.args.get("owner_id")
        if owner_id:
            query = query.where(Customer.owner_id == owner_id)

        # 合同到期日期筛选
        expiry_status = request.args.get("expiry_status")
        if expiry_status == "expiring":
            # 即将到期（最近 30 天内）
            from datetime import date, timedelta

            thirty_days_later = date.today() + timedelta(days=30)
            query = query.where(
                Customer.contract_expiry_date != None,
                Customer.contract_expiry_date <= thirty_days_later,
                Customer.contract_expiry_date >= date.today(),
            )
        elif expiry_status == "expired":
            # 已到期
            from datetime import date

            query = query.where(
                Customer.contract_expiry_date != None,
                Customer.contract_expiry_date < date.today(),
            )

        # 分页
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        offset = (page - 1) * page_size

        # 总数
        count_query = select(func.count()).select_from(Customer)
        count_result = await session.execute(count_query)
        total = count_result.scalar()

        # 查询
        query = query.offset(offset).limit(page_size)
        result = await session.execute(query)
        customers = result.scalars().all()

    return json(
        {
            "items": [
                {
                    "id": str(c.id),
                    "customer_code": c.customer_code,
                    "customer_name": c.customer_name,
                    "industry": {
                        "id": str(c.industry.id),
                        "name": c.industry.name,
                    }
                    if c.industry
                    else None,
                    "level": {
                        "id": str(c.level.id),
                        "code": c.level.code,
                        "name": c.level.name,
                    }
                    if c.level
                    else None,
                    "status": c.status.value,
                    "contact_person": c.contact_person,
                    "contact_phone": c.contact_phone,
                    "settlement_status": c.settlement_status.value,
                    "owner": {
                        "id": str(c.owner.id),
                        "username": c.owner.username,
                        "full_name": c.owner.full_name,
                    }
                    if c.owner
                    else None,
                    "created_at": c.created_at.isoformat(),
                }
                for c in customers
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@bp.post("")
@require_permission("customers:create")
async def create_customer(request):
    """创建客户"""
    from app.schemas.customer import CustomerCreate

    try:
        data = CustomerCreate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        # 验证客户编码唯一性
        existing = await session.scalar(
            select(Customer).where(Customer.customer_code == data.customer_code)
        )
        if existing:
            return json({"error": "客户编码已存在"}, status=400)

        # 验证行业 ID
        if data.industry_id:
            industry = await session.scalar(
                select(Industry).where(Industry.id == data.industry_id)
            )
            if not industry:
                return json({"error": "行业不存在"}, status=400)

        # 验证客户等级 ID
        if data.level_id:
            level = await session.scalar(
                select(CustomerLevel).where(CustomerLevel.id == data.level_id)
            )
            if not level:
                return json({"error": "客户等级不存在"}, status=400)

        # 验证负责人 ID
        if data.owner_id:
            from app.models.user import User

            owner = await session.scalar(select(User).where(User.id == data.owner_id))
            if not owner:
                return json({"error": "负责人不存在"}, status=400)

        customer = Customer(
            customer_code=data.customer_code,
            customer_name=data.customer_name,
            industry_id=data.industry_id,
            level_id=data.level_id,
            status=data.status or CustomerStatus.ACTIVE,
            contact_person=data.contact_person,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            address=data.address,
            settlement_status=data.settlement_status or SettlementStatus.UNSETTLED,
            owner_id=data.owner_id,
            remark=data.remark,
        )

        session.add(customer)
        await session.commit()

        return json(
            {
                "id": str(customer.id),
                "customer_code": customer.customer_code,
                "message": "客户创建成功",
            },
            status=201,
        )


@bp.get("/<customer_id>")
@require_permission("customers:read")
async def get_customer(request, customer_id):
    """获取客户详情"""
    # 验证并转换 UUID 格式
    try:
        customer_uuid = UUID(customer_id)
    except ValueError:
        return json({"error": "无效的客户 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Customer).where(Customer.id == customer_uuid)
        )
        customer = result.scalar()

        if not customer:
            return json({"error": "客户不存在"}, status=404)

    return json(
        {
            "id": str(customer.id),
            "customer_code": customer.customer_code,
            "customer_name": customer.customer_name,
            "industry": {
                "id": str(customer.industry.id),
                "name": customer.industry.name,
            }
            if customer.industry
            else None,
            "level": {
                "id": str(customer.level.id),
                "code": customer.level.code,
                "name": customer.level.name,
            }
            if customer.level
            else None,
            "status": customer.status.value,
            "contact_person": customer.contact_person,
            "contact_phone": customer.contact_phone,
            "contact_email": customer.contact_email,
            "address": customer.address,
            "settlement_status": customer.settlement_status.value,
            "owner": {
                "id": str(customer.owner.id),
                "username": customer.owner.username,
                "full_name": customer.owner.full_name,
            }
            if customer.owner
            else None,
            "remark": customer.remark,
            "created_at": customer.created_at.isoformat(),
            "updated_at": customer.updated_at.isoformat(),
        }
    )


@bp.put("/<customer_id>")
@require_permission("customers:update")
async def update_customer(request, customer_id):
    """更新客户"""
    from app.schemas.customer import CustomerUpdate

    # 验证并转换 UUID 格式
    try:
        customer_uuid = UUID(customer_id)
    except ValueError:
        return json({"error": "无效的客户 ID 格式"}, status=400)

    try:
        data = CustomerUpdate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Customer).where(Customer.id == customer_uuid)
        )
        customer = result.scalar()

        if not customer:
            return json({"error": "客户不存在"}, status=404)

        # 验证客户编码唯一性（如果更新编码）
        if data.customer_code and data.customer_code != customer.customer_code:
            existing = await session.scalar(
                select(Customer).where(
                    Customer.customer_code == data.customer_code,
                    Customer.id != customer_id,
                )
            )
            if existing:
                return json({"error": "客户编码已存在"}, status=400)

        # 验证行业 ID
        if data.industry_id is not None and data.industry_id != str(
            customer.industry_id
        ):
            industry = await session.scalar(
                select(Industry).where(Industry.id == data.industry_id)
            )
            if not industry:
                return json({"error": "行业不存在"}, status=400)

        # 验证客户等级 ID
        if data.level_id is not None and data.level_id != str(customer.level_id):
            level = await session.scalar(
                select(CustomerLevel).where(CustomerLevel.id == data.level_id)
            )
            if not level:
                return json({"error": "客户等级不存在"}, status=400)

        # 验证负责人 ID
        if data.owner_id is not None and data.owner_id != str(customer.owner_id):
            from app.models.user import User

            owner = await session.scalar(select(User).where(User.id == data.owner_id))
            if not owner:
                return json({"error": "负责人不存在"}, status=400)

        # 更新字段
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(customer, field, value)

        await session.commit()

        return json({"message": "客户更新成功"})


@bp.delete("/<customer_id>")
@require_permission("customers:delete")
async def delete_customer(request, customer_id):
    """删除客户"""
    # 验证并转换 UUID 格式
    try:
        customer_uuid = UUID(customer_id)
    except ValueError:
        return json({"error": "无效的客户 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(Customer).where(Customer.id == customer_uuid)
        )
        customer = result.scalar()

        if not customer:
            return json({"error": "客户不存在"}, status=404)

        await session.delete(customer)
        await session.commit()

        return json({"message": "客户删除成功"})


@bp.get("/industries")
async def list_industries(request):
    """行业列表"""
    async with request.app.ctx.db() as session:
        result = await session.execute(select(Industry).order_by(Industry.sort_order))
        industries = result.scalars().all()

    return json(
        {
            "items": [
                {
                    "id": str(i.id),
                    "name": i.name,
                    "code": i.code,
                    "parent_id": str(i.parent_id) if i.parent_id else None,
                    "level": i.level,
                }
                for i in industries
            ]
        }
    )


@bp.get("/levels")
async def list_levels(request):
    """客户等级列表"""
    async with request.app.ctx.db() as session:
        result = await session.execute(
            select(CustomerLevel).order_by(CustomerLevel.priority)
        )
        levels = result.scalars().all()

    return json(
        {
            "items": [
                {
                    "id": str(l.id),
                    "code": l.code,
                    "name": l.name,
                    "priority": l.priority,
                    "description": l.description,
                }
                for l in levels
            ]
        }
    )


@bp.post("/import")
@require_permission("customers:create")
async def import_customers(request):
    """Excel 导入客户"""
    from app.utils.excel_import import CustomerExcelImporter, ExcelImportError

    # 检查文件
    if not request.files:
        return json({"error": "未上传文件"}, status=400)

    file = request.files.get("file")
    if not file:
        return json({"error": "未找到上传文件"}, status=400)

    try:
        # 解析 Excel
        importer = CustomerExcelImporter(file.body)
        data, errors = importer.parse()

        if errors:
            return json(
                {
                    "success": False,
                    "message": f"数据验证失败，共 {len(errors)} 条错误",
                    "errors": errors,
                    "summary": importer.get_summary(),
                },
                status=400,
            )

        # 导入数据
        async with request.app.ctx.db() as session:
            # 预加载行业和等级
            industry_map = {}
            level_map = {}
            owner_map = {}

            # 获取所有行业名称映射
            from app.models.customer import Industry

            result = await session.execute(select(Industry))
            for ind in result.scalars().all():
                industry_map[ind.name] = ind.id
                if ind.code:
                    industry_map[ind.code] = ind.id

            # 获取所有等级映射
            result = await session.execute(select(CustomerLevel))
            for lvl in result.scalars().all():
                level_map[lvl.code] = lvl.id

            # 获取所有用户映射
            from app.models.user import User

            result = await session.execute(select(User))
            for user in result.scalars().all():
                owner_map[user.username] = user.id
                owner_map[user.email] = user.id

            # 批量创建客户
            created_count = 0
            for item in data:
                customer = Customer(
                    customer_code=item["customer_code"],
                    customer_name=item["customer_name"],
                    contact_person=item.get("contact_person"),
                    contact_phone=item.get("contact_phone"),
                    contact_email=item.get("contact_email"),
                    address=item.get("address"),
                    remark=item.get("remark"),
                    status=item.get("status", CustomerStatus.ACTIVE),
                    settlement_status=item.get(
                        "settlement_status", SettlementStatus.UNSETTLED
                    ),
                )

                # 关联行业
                if "industry_name" in item:
                    customer.industry_id = industry_map.get(item["industry_name"])

                # 关联等级
                if "level_code" in item:
                    customer.level_id = level_map.get(item["level_code"])

                # 关联负责人
                if "owner_username" in item:
                    customer.owner_id = owner_map.get(item["owner_username"])

                session.add(customer)
                created_count += 1

            await session.commit()

        return json(
            {
                "success": True,
                "message": f"成功导入 {created_count} 条客户数据",
                "summary": importer.get_summary(),
            }
        )

    except ExcelImportError as e:
        return json(
            {"error": str(e.message), "row": e.row, "column": e.column},
            status=400,
        )
    except Exception as e:
        return json(
            {"error": f"导入失败：{str(e)}"},
            status=500,
        )


@bp.get("/<customer_id>/usages")
@require_permission("customers:read")
async def get_customer_usages(request, customer_id):
    """获取客户用量历史（分页）"""
    from sqlalchemy import select

    async with request.app.ctx.db() as session:
        # 验证客户存在
        customer = await session.get(Customer, customer_id)
        if not customer:
            return json({"error": "客户不存在"}, status=404)

        # 分页参数
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        offset = (page - 1) * page_size

        # 查询用量历史
        query = (
            select(CustomerUsage)
            .where(CustomerUsage.customer_id == customer_id)
            .order_by(CustomerUsage.month.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(query)
        usages = result.scalars().all()

        # 总数
        count_query = (
            select(func.count())
            .select_from(CustomerUsage)
            .where(CustomerUsage.customer_id == customer_id)
        )
        count_result = await session.execute(count_query)
        total = count_result.scalar()

    return json(
        {
            "items": [
                {
                    "id": str(u.id),
                    "month": u.month.isoformat(),
                    "usage_count": u.usage_count,
                    "amount": float(u.amount),
                }
                for u in usages
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@bp.get("/<customer_id>/settlements")
@require_permission("customers:read")
async def get_customer_settlements(request, customer_id):
    """获取客户结算记录（分页）"""
    from sqlalchemy import select
    from app.models.customer import Settlement

    async with request.app.ctx.db() as session:
        # 验证客户存在
        customer = await session.get(Customer, customer_id)
        if not customer:
            return json({"error": "客户不存在"}, status=404)

        # 分页参数
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
        offset = (page - 1) * page_size

        # 查询结算记录
        query = (
            select(Settlement)
            .where(Settlement.customer_id == customer_id)
            .order_by(Settlement.month.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(query)
        settlements = result.scalars().all()

        # 总数
        count_query = (
            select(func.count())
            .select_from(Settlement)
            .where(Settlement.customer_id == customer_id)
        )
        count_result = await session.execute(count_query)
        total = count_result.scalar()

    return json(
        {
            "items": [
                {
                    "id": str(s.id),
                    "month": s.month.isoformat(),
                    "amount": float(s.amount),
                    "status": s.status.value,
                    "settled_at": s.settled_at.isoformat() if s.settled_at else None,
                    "remark": s.remark,
                }
                for s in settlements
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )
