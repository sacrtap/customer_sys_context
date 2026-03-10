"""
认证路由
"""

from datetime import datetime, timedelta
from sanic import Blueprint, json, request
from sanic_jwt import exceptions
from jose import jwt
from sqlalchemy import select
from config import settings

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.deps import get_current_user

bp = Blueprint("auth", url_prefix="/auth")


@bp.post("/login")
async def login(request):
    """用户登录"""
    from app.schemas.auth import LoginRequest

    data = request.json
    if not data:
        return json(
            {"error": "请求数据不能为空"},
            status=400,
        )

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return json(
            {"error": "用户名和密码不能为空"},
            status=400,
        )

    async with request.app.ctx.db() as session:
        # SQLAlchemy 2.0 用法：使用 select(User) 而不是 User.select()
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar()

        if not user or not user.verify_password(password):
            return json(
                {"error": "用户名或密码错误"},
                status=401,
            )

        if not user.is_active:
            return json(
                {"error": "用户已被禁用"},
                status=403,
            )

    # 生成 JWT Token
    expire = datetime.utcnow() + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "sub": str(user.id),
        "username": user.username,
        "exp": expire,
    }
    token = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return json(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
            },
        }
    )


@bp.get("/me")
async def get_me(request):
    """获取当前用户信息"""
    user = await get_current_user(request)

    return json(
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "roles": [{"id": str(r.id), "name": r.name} for r in user.roles],
            "permissions": user.get_permissions(),
        }
    )


@bp.post("/logout")
async def logout(request):
    """用户登出"""
    return json({"message": "登出成功"})
