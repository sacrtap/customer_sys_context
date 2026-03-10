"""
数据分析 Dashboard API
"""

from sanic import Blueprint, json, request
from sqlalchemy import select, func, extract, case
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional

from app.models.customer import (
    Customer,
    CustomerUsage,
    Industry,
    CustomerLevel,
    Settlement,
    SettlementStatus,
    CustomerStatus,
)
from app.models.user import User
from app.utils.deps import require_permission

bp = Blueprint("dashboard", url_prefix="/dashboard")


@bp.get("/usage-trend")
@require_permission("dashboard:read")
async def usage_trend(request):
    """
    获取用量趋势数据

    Query Parameters:
        - customer_ids: 客户 ID 列表（可选，逗号分隔）
        - start_date: 开始日期（YYYY-MM-DD）
        - end_date: 结束日期（YYYY-MM-DD）

    Returns:
        [{date, usageCount, amount}]
    """
    async with request.app.ctx.db() as session:
        # 解析参数
        customer_ids = request.args.get("customer_ids")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        # 默认最近 3 个月
        if not start_date_str:
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = (
                datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if end_date_str
                else date.today()
            )

        # 构建查询
        query = (
            select(
                extract("year", CustomerUsage.month).label("year"),
                extract("month", CustomerUsage.month).label("month"),
                func.sum(CustomerUsage.usage_count).label("total_usage"),
                func.sum(CustomerUsage.amount).label("total_amount"),
            )
            .where(
                CustomerUsage.month >= start_date,
                CustomerUsage.month <= end_date,
            )
            .group_by(
                extract("year", CustomerUsage.month),
                extract("month", CustomerUsage.month),
            )
            .order_by("year", "month")
        )

        # 如果指定了客户 ID，添加过滤
        if customer_ids:
            ids_list = [id.strip() for id in customer_ids.split(",")]
            query = query.where(CustomerUsage.customer_id.in_(ids_list))

        result = await session.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            # 构造日期字符串
            year = int(row.year) if row.year else 2026
            month = int(row.month) if row.month else 1
            date_str = f"{year}-{month:02d}-01"

            items.append(
                {
                    "date": date_str,
                    "usageCount": int(row.total_usage) if row.total_usage else 0,
                    "amount": float(row.total_amount) if row.total_amount else 0,
                }
            )

    return json({"items": items})


@bp.get("/revenue-forecast")
@require_permission("dashboard:read")
async def revenue_forecast(request):
    """
    获取收入预测数据

    Query Parameters:
        - months: 预测月数（默认 3）

    Returns:
        [{month, actual, forecast, lowerBound, upperBound}]
    """
    months = request.args.get("months", "3")
    try:
        forecast_months = int(months)
        if forecast_months <= 0:
            forecast_months = 3
    except ValueError:
        forecast_months = 3

    async with request.app.ctx.db() as session:
        # 获取历史收入数据（最近 6 个月）
        six_months_ago = date.today() - timedelta(days=180)

        query = (
            select(
                extract("year", CustomerUsage.month).label("year"),
                extract("month", CustomerUsage.month).label("month"),
                func.sum(CustomerUsage.amount).label("total_amount"),
            )
            .where(
                CustomerUsage.month >= six_months_ago,
            )
            .group_by(
                extract("year", CustomerUsage.month),
                extract("month", CustomerUsage.month),
            )
            .order_by("year", "month")
        )

        result = await session.execute(query)
        historical_data = result.all()

        # 计算历史平均值和标准差
        amounts = [
            float(row.total_amount) if row.total_amount else 0
            for row in historical_data
        ]

        if len(amounts) > 0:
            avg_amount = sum(amounts) / len(amounts)
            # 计算标准差
            variance = sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
            std_dev = variance**0.5
        else:
            avg_amount = 0
            std_dev = 0

        # 生成预测数据
        items = []
        current_date = date.today()

        # 添加历史数据
        for row in historical_data:
            year = int(row.year) if row.year else 2026
            month = int(row.month) if row.month else 1
            month_str = f"{year}-{month:02d}"
            actual_amount = float(row.total_amount) if row.total_amount else 0

            items.append(
                {
                    "month": month_str,
                    "actual": actual_amount,
                    "forecast": None,
                    "lowerBound": None,
                    "upperBound": None,
                }
            )

        # 添加预测数据
        for i in range(1, forecast_months + 1):
            # 计算下一个月
            if current_date.month + i > 12:
                next_year = current_date.year + (current_date.month + i - 1) // 12
                next_month = (current_date.month + i - 1) % 12 + 1
            else:
                next_year = current_date.year
                next_month = current_date.month + i

            month_str = f"{next_year}-{next_month:02d}"

            # 简单预测：使用历史平均值
            forecast_value = avg_amount
            lower_bound = max(0, forecast_value - 1.96 * std_dev)
            upper_bound = forecast_value + 1.96 * std_dev

            items.append(
                {
                    "month": month_str,
                    "actual": None,
                    "forecast": round(forecast_value, 2),
                    "lowerBound": round(lower_bound, 2),
                    "upperBound": round(upper_bound, 2),
                }
            )

    return json({"items": items})


@bp.get("/customer-distribution")
@require_permission("dashboard:read")
async def customer_distribution(request):
    """
    获取客户分布数据

    Query Parameters:
        - dimension: 维度 (industry|level)

    Returns:
        [{name, value, percentage}]
    """
    dimension = request.args.get("dimension", "industry")

    async with request.app.ctx.db() as session:
        if dimension == "level":
            # 按客户等级分布
            query = (
                select(
                    CustomerLevel.name,
                    func.count(Customer.id).label("count"),
                )
                .outerjoin(Customer, Customer.level_id == CustomerLevel.id)
                .group_by(CustomerLevel.name)
            )
        else:
            # 默认按行业分布
            query = (
                select(
                    Industry.name,
                    func.count(Customer.id).label("count"),
                )
                .outerjoin(Customer, Customer.industry_id == Industry.id)
                .group_by(Industry.name)
            )

        result = await session.execute(query)
        rows = result.all()

        # 计算总数
        total = sum(row.count for row in rows)

        items = []
        for row in rows:
            name = row.name if row.name else "未分类"
            count = row.count if row.count else 0
            percentage = round((count / total * 100) if total > 0 else 0, 2)

            items.append(
                {
                    "name": name,
                    "value": count,
                    "percentage": percentage,
                }
            )

    return json({"items": items})


@bp.get("/settlement-status")
@require_permission("dashboard:read")
async def settlement_status(request):
    """
    获取结算状态数据

    Query Parameters:
        - year: 年份（默认当前年）

    Returns:
        [{month, settled, unsettled}]
    """
    year_str = request.args.get("year")

    try:
        year = int(year_str) if year_str else datetime.now().year
    except ValueError:
        year = datetime.now().year

    async with request.app.ctx.db() as session:
        # 查询该年每个月的结算状态
        query = (
            select(
                extract("month", Settlement.month).label("month"),
                func.sum(
                    case(
                        (Settlement.status == SettlementStatus.SETTLED.value, 1),
                        else_=0,
                    )
                ).label("settled"),
                func.sum(
                    case(
                        (Settlement.status == SettlementStatus.UNSETTLED.value, 1),
                        else_=0,
                    )
                ).label("unsettled"),
            )
            .where(
                extract("year", Settlement.month) == year,
            )
            .group_by(
                extract("month", Settlement.month),
            )
            .order_by("month")
        )

        result = await session.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            month = int(row.month) if row.month else 1
            month_str = f"{year}-{month:02d}-01"

            items.append(
                {
                    "month": month_str,
                    "settled": int(row.settled) if row.settled else 0,
                    "unsettled": int(row.unsettled) if row.unsettled else 0,
                }
            )

    return json({"items": items})


@bp.get("/customer-health")
@require_permission("dashboard:read")
async def customer_health(request):
    """
    获取客户健康度数据

    Returns:
        {
            summary: {healthy: count, warning: count, critical: count},
            list: [{customer_id, customer_name, score, level, factors}]
        }
    """
    async with request.app.ctx.db() as session:
        # 获取所有活跃客户
        query = select(Customer).where(Customer.status == "active")
        result = await session.execute(query)
        customers = result.scalars().all()

        health_list = []
        summary = {"healthy": 0, "warning": 0, "critical": 0}

        for customer in customers:
            # 计算健康度评分
            health_data = await calculate_health_score(session, customer)

            health_list.append(
                {
                    "customer_id": str(customer.id),
                    "customer_name": customer.customer_name,
                    "score": health_data["score"],
                    "level": health_data["level"],
                    "factors": health_data["factors"],
                }
            )

            # 更新汇总
            summary[health_data["level"]] += 1

    return json(
        {
            "summary": summary,
            "list": health_list,
        }
    )


async def calculate_health_score(session, customer: Customer) -> dict:
    """
    计算客户健康度评分

    评分维度:
    1. 用量活跃度 (40%) - 近 3 个月平均用量 vs 历史平均
    2. 结算及时性 (30%) - 是否按时结算
    3. 用量趋势 (30%) - 用量增长/下降趋势

    Returns:
        {score: 0-100, level: 'healthy'|'warning'|'critical', factors: [...]}
    """
    factors = []
    score = 0

    # 1. 用量活跃度 (40 分)
    activity_score = await calculate_activity_score(session, customer)
    score += activity_score * 0.4
    factors.append(
        {
            "name": "用量活跃度",
            "score": activity_score,
            "weight": 0.4,
        }
    )

    # 2. 结算及时性 (30 分)
    settlement_score = await calculate_settlement_score(session, customer)
    score += settlement_score * 0.3
    factors.append(
        {
            "name": "结算及时性",
            "score": settlement_score,
            "weight": 0.3,
        }
    )

    # 3. 用量趋势 (30 分)
    trend_score = await calculate_trend_score(session, customer)
    score += trend_score * 0.3
    factors.append(
        {
            "name": "用量趋势",
            "score": trend_score,
            "weight": 0.3,
        }
    )

    # 计算最终得分（0-100）
    final_score = round(score, 2)

    # 确定健康等级
    if final_score >= 80:
        level = "healthy"
    elif final_score >= 60:
        level = "warning"
    else:
        level = "critical"

    return {
        "score": final_score,
        "level": level,
        "factors": factors,
    }


async def calculate_activity_score(session, customer: Customer) -> float:
    """计算用量活跃度得分 (0-100)"""
    # 获取近 3 个月用量
    three_months_ago = date.today() - timedelta(days=90)

    query = select(func.avg(CustomerUsage.usage_count)).where(
        CustomerUsage.customer_id == customer.id,
        CustomerUsage.month >= three_months_ago,
    )
    result = await session.execute(query)
    recent_avg = result.scalar() or 0

    # 获取历史平均用量
    query = select(func.avg(CustomerUsage.usage_count)).where(
        CustomerUsage.customer_id == customer.id,
    )
    result = await session.execute(query)
    historical_avg = result.scalar() or 0

    # 如果历史平均为 0，给基础分
    if historical_avg == 0:
        return 50 if recent_avg > 0 else 0

    # 计算比率
    ratio = recent_avg / historical_avg if historical_avg > 0 else 0

    # 比率越高分数越高
    if ratio >= 1.0:
        return 100
    elif ratio >= 0.8:
        return 80
    elif ratio >= 0.5:
        return 60
    elif ratio >= 0.3:
        return 40
    else:
        return 20


async def calculate_settlement_score(session, customer: Customer) -> float:
    """计算结算及时性得分 (0-100)"""
    # 查询最近 6 个月的结算记录
    six_months_ago = date.today() - timedelta(days=180)

    query = select(Settlement).where(
        Settlement.customer_id == customer.id,
        Settlement.month >= six_months_ago,
    )
    result = await session.execute(query)
    settlements = result.scalars().all()

    if not settlements:
        return 50  # 无结算记录，给中等分数

    # 计算已结算比例
    settled_count = sum(
        1 for s in settlements if s.status == SettlementStatus.SETTLED.value
    )
    ratio = settled_count / len(settlements)

    return ratio * 100


async def calculate_trend_score(session, customer: Customer) -> float:
    """计算用量趋势得分 (0-100)"""
    # 获取最近 3 个月和之前 3 个月的用量
    today = date.today()
    three_months_ago = today - timedelta(days=90)
    six_months_ago = today - timedelta(days=180)

    # 最近 3 个月总用量
    query = select(func.sum(CustomerUsage.usage_count)).where(
        CustomerUsage.customer_id == customer.id,
        CustomerUsage.month >= three_months_ago,
        CustomerUsage.month < today,
    )
    result = await session.execute(query)
    recent_total = result.scalar() or 0

    # 前 3 个月总用量
    query = select(func.sum(CustomerUsage.usage_count)).where(
        CustomerUsage.customer_id == customer.id,
        CustomerUsage.month >= six_months_ago,
        CustomerUsage.month < three_months_ago,
    )
    result = await session.execute(query)
    previous_total = result.scalar() or 0

    # 计算增长率
    if previous_total == 0:
        return 100 if recent_total > 0 else 50

    growth_rate = (recent_total - previous_total) / previous_total

    # 增长率越高分数越高
    if growth_rate >= 0.2:
        return 100
    elif growth_rate >= 0.1:
        return 80
    elif growth_rate >= 0:
        return 60
    elif growth_rate >= -0.2:
        return 40
    else:
        return 20


# ==================== 工作台概览 API ====================


@bp.get("/overview")
@require_permission("dashboard:read")
async def overview(request):
    """
    工作台概览数据

    Returns:
        {
            total_customers: number,      # 客户总数
            active_customers: number,     # 活跃客户数
            total_revenue: number,        # 总收入（本月）
            settled_revenue: number,      # 已结算收入
            unsettled_count: number,      # 未结算记录数
            health_stats: {               # 健康度统计
                healthy: number,
                warning: number,
                critical: number
            }
        }
    """
    async with request.app.ctx.db() as session:
        # 客户统计
        total_customers = await session.scalar(
            select(func.count()).select_from(Customer)
        )

        active_customers = await session.scalar(
            select(func.count())
            .select_from(Customer)
            .where(Customer.status == CustomerStatus.ACTIVE.value)
        )

        # 收入统计（本月）
        current_month = date.today().replace(day=1)
        next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)

        # 本月总收入
        total_revenue_result = await session.execute(
            select(func.sum(CustomerUsage.amount)).where(
                CustomerUsage.month >= current_month,
                CustomerUsage.month < next_month,
            )
        )
        total_revenue = float(total_revenue_result.scalar() or 0)

        # 已结算收入
        settled_revenue_result = await session.execute(
            select(func.sum(Settlement.amount)).where(
                Settlement.status == SettlementStatus.SETTLED.value,
                Settlement.month >= current_month,
                Settlement.month < next_month,
            )
        )
        settled_revenue = float(settled_revenue_result.scalar() or 0)

        # 未结算记录数
        unsettled_count = await session.scalar(
            select(func.count())
            .select_from(Settlement)
            .where(Settlement.status == SettlementStatus.UNSETTLED.value)
        )

        # 健康度统计
        health_stats = await get_health_stats(session)

        return json(
            {
                "total_customers": total_customers or 0,
                "active_customers": active_customers or 0,
                "total_revenue": round(total_revenue, 2),
                "settled_revenue": round(settled_revenue, 2),
                "unsettled_count": unsettled_count or 0,
                "health_stats": health_stats,
            }
        )


async def get_health_stats(session) -> dict:
    """获取健康度统计"""
    # 获取所有活跃客户
    query = select(Customer).where(Customer.status == CustomerStatus.ACTIVE.value)
    result = await session.execute(query)
    customers = result.scalars().all()

    health_stats = {"healthy": 0, "warning": 0, "critical": 0}

    for customer in customers:
        health_data = await calculate_health_score(session, customer)
        health_stats[health_data["level"]] += 1

    return health_stats


@bp.get("/quick-actions")
@require_permission("dashboard:read")
async def quick_actions(request):
    """
    快捷入口数据

    Returns:
        {
            pending_settlements: number,  # 待结算记录数
            expiring_customers: number,   # 即将到期客户数
            low_health_customers: number  # 健康度预警客户数
        }
    """
    async with request.app.ctx.db() as session:
        # 待结算记录数
        pending_settlements = await session.scalar(
            select(func.count())
            .select_from(Settlement)
            .where(Settlement.status == SettlementStatus.UNSETTLED.value)
        )

        # 即将到期客户数（这里简化为最近 30 天到期的客户）
        # 实际业务中可能有合同到期字段
        thirty_days_later = date.today() + timedelta(days=30)
        expiring_customers = await session.scalar(
            select(func.count())
            .select_from(Customer)
            .where(
                Customer.status == CustomerStatus.ACTIVE.value,
                Customer.updated_at <= thirty_days_later,  # 示例逻辑
            )
        )

        # 健康度预警客户数（warning + critical）
        query = select(Customer).where(Customer.status == CustomerStatus.ACTIVE.value)
        result = await session.execute(query)
        customers = result.scalars().all()

        low_health_customers = 0
        for customer in customers:
            health_data = await calculate_health_score(session, customer)
            if health_data["level"] in ["warning", "critical"]:
                low_health_customers += 1

        return json(
            {
                "pending_settlements": pending_settlements or 0,
                "expiring_customers": expiring_customers or 0,
                "low_health_customers": low_health_customers,
            }
        )


@bp.get("/recent-activities")
@require_permission("dashboard:read")
async def recent_activities(request):
    """
    最新动态

    Query Parameters:
        - limit: 返回数量（默认 10）

    Returns:
        [{type, description, created_at, user}]
    """
    limit = request.args.get("limit", "10")
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
        elif limit > 100:
            limit = 100
    except ValueError:
        limit = 10

    async with request.app.ctx.db() as session:
        activities = []

        # 获取最近的结算记录活动
        settlement_query = (
            select(Settlement).order_by(Settlement.created_at.desc()).limit(limit)
        )
        settlement_result = await session.execute(settlement_query)
        settlements = settlement_result.scalars().all()

        for settlement in settlements:
            # 获取客户信息
            customer = await session.get(Customer, settlement.customer_id)
            customer_name = customer.customer_name if customer else "未知客户"

            # 获取创建用户信息
            creator = (
                await session.get(User, settlement.created_by)
                if settlement.created_by
                else None
            )
            user_name = creator.username if creator else "系统"

            # 确定活动类型和描述
            if settlement.status == SettlementStatus.SETTLED.value:
                activity_type = "payment_confirmed"
                description = f"确认收款：{customer_name} - {settlement.month}"
            else:
                activity_type = "settlement_created"
                description = f"创建结算单：{customer_name} - {settlement.month}"

            activities.append(
                {
                    "type": activity_type,
                    "description": description,
                    "created_at": settlement.created_at.isoformat()
                    if settlement.created_at
                    else None,
                    "user": user_name,
                }
            )

        # 按时间排序并限制数量
        activities.sort(key=lambda x: x["created_at"] or "", reverse=True)

        return json(activities[:limit])
