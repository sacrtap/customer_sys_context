# -*- coding: utf-8 -*-
"""
客户相关模型
"""

from decimal import Decimal
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    Date,
    Numeric,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.models.base import BaseModel


class CustomerStatus(str, enum.Enum):
    """客户状态"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TEST = "test"

    @classmethod
    def get_values(cls):
        """获取枚举值列表用于 SQLEnum"""
        return [e.value for e in cls]


class SettlementStatus(str, enum.Enum):
    """结算状态"""

    SETTLED = "settled"
    UNSETTLED = "unsettled"

    @classmethod
    def get_values(cls):
        """获取枚举值列表用于 SQLEnum"""
        return [e.value for e in cls]


class Industry(BaseModel):
    """行业分类"""

    __tablename__ = "industries"

    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=True)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("industries.id", ondelete="SET NULL"),
        nullable=True,
    )
    level = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    # 关联
    parent = relationship(
        "Industry",
        remote_side="Industry.id",
        backref="children",
    )
    customers = relationship("Customer", back_populates="industry")

    def __repr__(self):
        return f"<Industry {self.name}>"


class CustomerLevel(BaseModel):
    """客户等级"""

    __tablename__ = "customer_levels"

    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    description = Column(String(255), nullable=True)

    # 关联
    customers = relationship("Customer", back_populates="level")

    def __repr__(self):
        return f"<CustomerLevel {self.code}>"


class Customer(BaseModel):
    """客户"""

    __tablename__ = "customers"

    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(200), nullable=False, index=True)
    industry_id = Column(
        UUID(as_uuid=True),
        ForeignKey("industries.id", ondelete="SET NULL"),
        nullable=True,
    )
    level_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customer_levels.id", ondelete="SET NULL"),
        nullable=True,
    )
    status = Column(
        SQLEnum(
            CustomerStatus,
            name="customerstatus",
            values_callable=lambda x: CustomerStatus.get_values(),
        ),
        default=CustomerStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    contact_person = Column(String(50), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)

    # 结算状态
    settlement_status = Column(
        SQLEnum(
            SettlementStatus,
            name="settlementstatus",
            values_callable=lambda x: SettlementStatus.get_values(),
        ),
        default=SettlementStatus.UNSETTLED,
        nullable=False,
        index=True,
    )

    # 负责人
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # 备注
    remark = Column(String(1000), nullable=True)

    # 关联
    industry = relationship("Industry", back_populates="customers")
    level = relationship("CustomerLevel", back_populates="customers")
    owner = relationship("User", back_populates="owned_customers")

    usages = relationship(
        "CustomerUsage",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    settlements = relationship(
        "Settlement",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Customer {self.customer_name}>"


class CustomerUsage(BaseModel):
    """客户用量记录"""

    __tablename__ = "customer_usages"

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month = Column(Date, nullable=False, index=True)
    usage_count = Column(Integer, default=0, nullable=False)
    amount = Column(Numeric(10, 2), default=0, nullable=False)

    # 关联
    customer = relationship("Customer", back_populates="usages")

    def __repr__(self):
        return f"<CustomerUsage {self.customer_id} {self.month}>"


class Settlement(BaseModel):
    """结算记录"""

    __tablename__ = "settlements"

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SQLEnum(
            SettlementStatus,
            name="settlementstatus",
            values_callable=lambda x: SettlementStatus.get_values(),
        ),
        default=SettlementStatus.UNSETTLED,
        nullable=False,
        index=True,
    )
    settled_at = Column(DateTime, nullable=True)
    remark = Column(String(500), nullable=True)

    # 关联
    customer = relationship("Customer", back_populates="settlements")

    def __repr__(self):
        return f"<Settlement {self.customer_id} {self.month}>"
