"""
认证相关 Schema
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """登录请求"""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户响应"""

    id: str
    username: str
    email: str
    full_name: str | None = None
    phone: str | None = None
    is_active: bool
    roles: list[dict] = []
    permissions: list[str] = []
