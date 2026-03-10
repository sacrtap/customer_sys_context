"""
初始数据库迁移 - 创建所有表

Revision ID: initial
Revises:
Create Date: 2026-03-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 使用 PL/pgSQL 检查枚举类型是否存在，不存在则创建
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customerstatus') THEN
                CREATE TYPE customerstatus AS ENUM ('active', 'inactive', 'test');
            END IF;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'settlementstatus') THEN
                CREATE TYPE settlementstatus AS ENUM ('settled', 'unsettled');
            END IF;
        END $$
    """)

    # 1. 用户表
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)

    # 2. 角色表
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)
    op.create_index(op.f("ix_roles_created_at"), "roles", ["created_at"], unique=False)

    # 3. 权限表
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissions_code"), "permissions", ["code"], unique=True)
    op.create_index(
        op.f("ix_permissions_created_at"), "permissions", ["created_at"], unique=False
    )

    # 4. 用户角色关联表
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    # 5. 角色权限关联表
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permissions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # 6. 行业分类表
    op.create_table(
        "industries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False, default=1),
        sa.Column("sort_order", sa.Integer(), nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["industries.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_industries_name"), "industries", ["name"], unique=False)
    op.create_index(
        op.f("ix_industries_created_at"), "industries", ["created_at"], unique=False
    )

    # 7. 客户等级表
    op.create_table(
        "customer_levels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, default=0),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_customer_levels_code"), "customer_levels", ["code"], unique=True
    )
    op.create_index(
        op.f("ix_customer_levels_created_at"),
        "customer_levels",
        ["created_at"],
        unique=False,
    )

    # 8. 客户表
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_code", sa.String(length=50), nullable=False),
        sa.Column("customer_name", sa.String(length=200), nullable=False),
        sa.Column("industry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("level_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active", "inactive", "test", name="customerstatus", create_type=False
            ),
            nullable=False,
            default="active",
        ),
        sa.Column("contact_person", sa.String(length=50), nullable=True),
        sa.Column("contact_phone", sa.String(length=20), nullable=True),
        sa.Column("contact_email", sa.String(length=100), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column(
            "settlement_status",
            sa.Enum("settled", "unsettled", name="settlementstatus", create_type=False),
            nullable=False,
            default="unsettled",
        ),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("remark", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["industry_id"], ["industries.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["level_id"], ["customer_levels.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_customers_customer_code"), "customers", ["customer_code"], unique=True
    )
    op.create_index(
        op.f("ix_customers_customer_name"), "customers", ["customer_name"], unique=False
    )
    op.create_index(op.f("ix_customers_status"), "customers", ["status"], unique=False)
    op.create_index(
        op.f("ix_customers_settlement_status"),
        "customers",
        ["settlement_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customers_owner_id"), "customers", ["owner_id"], unique=False
    )
    op.create_index(
        op.f("ix_customers_created_at"), "customers", ["created_at"], unique=False
    )

    # 9. 客户用量表
    op.create_table(
        "customer_usages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "amount", sa.Numeric(precision=10, scale=2), nullable=False, default=0
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_customer_usages_customer_id"),
        "customer_usages",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_usages_month"), "customer_usages", ["month"], unique=False
    )
    op.create_index(
        op.f("ix_customer_usages_created_at"),
        "customer_usages",
        ["created_at"],
        unique=False,
    )

    # 10. 结算记录表
    op.create_table(
        "settlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("settled", "unsettled", name="settlementstatus", create_type=False),
            nullable=False,
            default="unsettled",
        ),
        sa.Column("settled_at", sa.DateTime(), nullable=True),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_settlements_customer_id"), "settlements", ["customer_id"], unique=False
    )
    op.create_index(
        op.f("ix_settlements_month"), "settlements", ["month"], unique=False
    )
    op.create_index(
        op.f("ix_settlements_status"), "settlements", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_settlements_created_at"), "settlements", ["created_at"], unique=False
    )


def downgrade() -> None:
    # 删除所有表（顺序相反）
    op.drop_table("settlements")
    op.drop_table("customer_usages")
    op.drop_table("customers")
    op.drop_table("customer_levels")
    op.drop_table("industries")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS customerstatus")
    op.execute("DROP TYPE IF EXISTS settlementstatus")
