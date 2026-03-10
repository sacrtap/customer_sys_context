"""
角色相关 Schema
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """权限基础 Schema"""

    code: str
    name: str
    type: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    """创建权限请求"""

    pass


class PermissionResponse(PermissionBase):
    """权限响应"""

    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """角色基础 Schema"""

    name: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    is_default: bool = False


class RoleCreate(RoleBase):
    """创建角色请求"""

    permission_ids: list[str] | None = None


class RoleUpdate(BaseModel):
    """更新角色请求"""

    name: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = None
    is_default: bool | None = None
    permission_ids: list[str] | None = None


class RoleResponse(RoleBase):
    """角色响应"""

    id: str
    permissions: list[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
