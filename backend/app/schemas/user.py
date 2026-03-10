"""
用户相关 Schema
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础 Schema"""

    email: EmailStr
    full_name: str | None = None
    phone: str | None = None


class UserCreate(UserBase):
    """创建用户请求"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    is_active: bool = True
    role_ids: list[str] | None = None


class UserUpdate(BaseModel):
    """更新用户请求"""

    email: EmailStr | None = None
    full_name: str | None = None
    phone: str | None = None
    password: str | None = Field(None, min_length=6)
    is_active: bool | None = None
    role_ids: list[str] | None = None


class UserResponse(UserBase):
    """用户响应"""

    id: str
    username: str
    is_active: bool
    is_superuser: bool
    roles: list[dict] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
