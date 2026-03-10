"""
Dashboard 相关 Schema
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class UsageTrendItem(BaseModel):
    """用量趋势数据项"""

    date: str
    usageCount: int
    amount: float


class UsageTrendResponse(BaseModel):
    """用量趋势响应"""

    items: List[UsageTrendItem]


class RevenueForecastItem(BaseModel):
    """收入预测数据项"""

    month: str
    actual: Optional[float] = None
    forecast: Optional[float] = None
    lowerBound: Optional[float] = None
    upperBound: Optional[float] = None


class RevenueForecastResponse(BaseModel):
    """收入预测响应"""

    items: List[RevenueForecastItem]


class DistributionItem(BaseModel):
    """分布数据项"""

    name: str
    value: int
    percentage: float


class DistributionResponse(BaseModel):
    """分布响应"""

    items: List[DistributionItem]


class SettlementStatusItem(BaseModel):
    """结算状态数据项"""

    month: str
    settled: int
    unsettled: int


class SettlementStatusResponse(BaseModel):
    """结算状态响应"""

    items: List[SettlementStatusItem]


class HealthFactor(BaseModel):
    """健康度因素"""

    name: str
    score: float
    weight: float


class CustomerHealthItem(BaseModel):
    """客户健康度数据项"""

    customer_id: str
    customer_name: str
    score: float
    level: str
    factors: List[HealthFactor]


class HealthSummary(BaseModel):
    """健康度汇总"""

    healthy: int
    warning: int
    critical: int


class CustomerHealthResponse(BaseModel):
    """客户健康度响应"""

    summary: HealthSummary
    list: List[CustomerHealthItem]
