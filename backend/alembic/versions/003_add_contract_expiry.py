"""
添加客户合同到期日期字段

Revision ID: 003_add_contract_expiry
Revises: 002_fix_enums
Create Date: 2026-03-10

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_contract_expiry"
down_revision: Union[str, None] = "002_fix_enums"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加合同到期日期字段
    op.add_column(
        "customers", sa.Column("contract_expiry_date", sa.Date(), nullable=True)
    )

    # 创建索引以提高查询性能
    op.create_index(
        "ix_customers_contract_expiry_date", "customers", ["contract_expiry_date"]
    )


def downgrade() -> None:
    # 删除索引
    op.drop_index("ix_customers_contract_expiry_date", "customers")

    # 删除字段
    op.drop_column("customers", "contract_expiry_date")
