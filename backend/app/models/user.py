# -*- coding: utf-8 -*-
"""
系统用户模型
"""

import bcrypt
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class User(BaseModel):
    """系统用户"""

    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 关联
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    # 负责的客户
    owned_customers = relationship(
        "Customer",
        back_populates="owner",
        foreign_keys="Customer.owner_id",
    )

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """密码加密"""
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    def has_permission(self, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        if self.is_superuser:
            return True

        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False

    def get_permissions(self) -> list:
        """获取用户所有权限码"""
        if self.is_superuser:
            return ["*"]

        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.code)
        return list(permissions)
