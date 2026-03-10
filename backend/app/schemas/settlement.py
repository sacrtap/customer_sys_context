"""
结算管理相关 Schema
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class SettlementCreate(BaseModel):
    """创建结算记录请求"""

    customer_id: str = Field(..., description="客户 ID")
    month: str = Field(..., description="结算月份，格式：YYYY-MM")
    amount: Decimal = Field(..., gt=0, description="结算金额")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class SettlementUpdate(BaseModel):
    """更新结算记录请求"""

    amount: Optional[Decimal] = Field(None, gt=0, description="结算金额")
    status: Optional[str] = Field(None, description="结算状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class PaymentConfirmRequest(BaseModel):
    """支付确认请求"""

    paid_amount: Decimal = Field(..., gt=0, description="支付金额")
    paid_at: str = Field(..., description="支付时间，ISO 格式")


class MonthlyBillGenerateRequest(BaseModel):
    """月度账单生成请求"""

    year: int = Field(..., gt=2000, lt=2100, description="年份")
    month: int = Field(..., gt=0, le=12, description="月份")
    customer_ids: Optional[List[str]] = Field(None, description="客户 ID 列表（可选）")


class ExportRequest(BaseModel):
    """导出请求"""

    customer_ids: Optional[List[str]] = Field(None, description="客户 ID 列表")
    date_range: dict = Field(..., description="日期范围")


class SettlementResponse(BaseModel):
    """结算记录响应"""

    id: str
    customer_id: str
    customer_name: Optional[str] = None
    month: str
    amount: str
    status: str
    settled_at: Optional[str] = None
    remark: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SettlementListResponse(BaseModel):
    """结算记录列表响应"""

    items: List[SettlementResponse]
    total: int
    page: int
    page_size: int


class GenerateBillResponse(BaseModel):
    """账单生成响应"""

    generated_count: int
    skipped_count: int
