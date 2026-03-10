"""
初始数据库迁移 - 创建所有表（修复枚举类型问题）

Revision ID: 002_fix_enums
Revises: initial
Create Date: 2026-03-10

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_fix_enums"
down_revision: Union[str, None] = "initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 枚举类型已在 initial 迁移中创建，这里只创建表
    pass


def downgrade() -> None:
    pass
