"""
依赖注入和权限验证
"""

from functools import wraps
from sanic import json, request
from sqlalchemy import select
from jose import jwt, JWTError
from config import settings

from app.models.user import User


async def get_current_user(request) -> User:
    """获取当前登录用户"""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")

        if not user_id:
            return None

        async with request.app.ctx.db() as session:
            # SQLAlchemy 2.0: 使用 select(User) 而不是 User.select()
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar()

            if not user or not user.is_active:
                return None

            return user

    except JWTError:
        return None


def require_permission(permission_code: str):
    """权限验证装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            user = await get_current_user(request)

            if not user:
                return json(
                    {"error": "未授权访问"},
                    status=401,
                )

            if not user.is_active:
                return json(
                    {"error": "用户已被禁用"},
                    status=403,
                )

            # 超级管理员拥有所有权限
            if user.is_superuser:
                return await func(request, *args, **kwargs)

            # 检查权限
            if not user.has_permission(permission_code):
                return json(
                    {"error": "权限不足"},
                    status=403,
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def login_required():
    """登录验证装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            user = await get_current_user(request)

            if not user:
                return json(
                    {"error": "未授权访问"},
                    status=401,
                )

            if not user.is_active:
                return json(
                    {"error": "用户已被禁用"},
                    status=403,
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
