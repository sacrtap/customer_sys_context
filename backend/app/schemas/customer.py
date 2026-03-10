"""
客户相关 Schema
"""

import re
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from app.models.customer import CustomerStatus, SettlementStatus


def validate_phone(value: str | None) -> str | None:
    """验证手机号格式"""
    if value is None:
        return None
    # 中国手机号格式：1 开头，第二位 3-9，后面 9 位数字
    pattern = r"^1[3-9]\d{9}$"
    if value and not re.match(pattern, value):
        raise ValueError("手机号格式不正确")
    return value


class CustomerBase(BaseModel):
    """客户基础 Schema"""

    customer_code: str = Field(..., min_length=1, max_length=50)
    customer_name: str = Field(..., min_length=1, max_length=200)
    contact_person: str | None = None
    contact_phone: str | None = None
    contact_email: EmailStr | None = None
    address: str | None = None
    remark: str | None = None
    contract_expiry_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")

    _validate_phone = field_validator("contact_phone")(validate_phone)


class CustomerCreate(CustomerBase):
    """创建客户请求"""

    industry_id: str | None = None
    level_id: str | None = None
    status: CustomerStatus | None = None
    settlement_status: SettlementStatus | None = None
    owner_id: str | None = None


class CustomerUpdate(BaseModel):
    """更新客户请求"""

    customer_code: str | None = Field(None, min_length=1, max_length=50)
    customer_name: str | None = Field(None, min_length=1, max_length=200)
    industry_id: str | None = None
    level_id: str | None = None
    status: CustomerStatus | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    contact_email: EmailStr | None = None
    address: str | None = None
    settlement_status: SettlementStatus | None = None
    owner_id: str | None = None
    remark: str | None = None
    contract_expiry_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class IndustryResponse(BaseModel):
    """行业响应"""

    id: str
    name: str
    code: str | None
    parent_id: str | None = None
    level: int = 1

    class Config:
        from_attributes = True


class CustomerLevelResponse(BaseModel):
    """客户等级响应"""

    id: str
    code: str
    name: str
    priority: int
    description: str | None = None

    class Config:
        from_attributes = True


class CustomerResponse(CustomerBase):
    """客户响应"""

    id: str
    industry: IndustryResponse | None = None
    level: CustomerLevelResponse | None = None
    status: CustomerStatus
    settlement_status: SettlementStatus
    owner: dict | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """客户列表响应"""

    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
