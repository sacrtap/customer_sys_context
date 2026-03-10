"""
用户管理路由
"""

from sanic import Blueprint, json, request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.user import User
from app.models.role import Role
from app.utils.deps import get_current_user, require_permission
from app.utils.pagination import paginate

bp = Blueprint("users", url_prefix="/users")


@bp.get("")
@require_permission("users:read")
async def list_users(request):
    """用户列表"""
    async with request.app.ctx.db() as session:
        # 构建查询
        query = select(User)

        # 搜索
        search = request.args.get("search")
        if search:
            query = query.where(
                (User.username.contains(search))
                | (User.email.contains(search))
                | (User.full_name.contains(search))
            )

        # 状态筛选
        status = request.args.get("status")
        if status:
            query = query.where(User.is_active == (status == "active"))

        # 分页
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))

        result = await session.execute(query)
        users = result.scalars().all()

        # 总数
        count_query = select(func.count()).select_from(User)
        count_result = await session.execute(count_query)
        total = count_result.scalar()

    return json(
        {
            "items": [
                {
                    "id": str(u.id),
                    "username": u.username,
                    "email": u.email,
                    "full_name": u.full_name,
                    "phone": u.phone,
                    "is_active": u.is_active,
                    "roles": [{"id": str(r.id), "name": r.name} for r in u.roles],
                    "created_at": u.created_at.isoformat(),
                }
                for u in users
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@bp.post("")
@require_permission("users:create")
async def create_user(request):
    """创建用户"""
    from app.schemas.user import UserCreate

    try:
        data = UserCreate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        # 检查用户名是否已存在
        exists = await session.scalar(
            select(User).where(User.username == data.username)
        )
        if exists:
            return json({"error": "用户名已存在"}, status=400)

        # 创建用户
        user = User(
            username=data.username,
            email=data.email,
            password_hash=User.hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            is_active=data.is_active,
        )

        # 分配角色
        if data.role_ids:
            roles = await session.execute(
                select(Role).where(Role.id.in_(data.role_ids))
            )
            user.roles = list(roles.scalars().all())

        session.add(user)
        await session.commit()

        return json(
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "message": "用户创建成功",
            },
            status=201,
        )


@bp.get("/<user_id>")
@require_permission("users:read")
async def get_user(request, user_id):
    """获取用户详情"""
    # 验证并转换 UUID 格式
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return json({"error": "无效的用户 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar()

        if not user:
            return json({"error": "用户不存在"}, status=404)

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
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    )


@bp.put("/<user_id>")
@require_permission("users:update")
async def update_user(request, user_id):
    """更新用户"""
    from app.schemas.user import UserUpdate

    # 验证并转换 UUID 格式
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return json({"error": "无效的用户 ID 格式"}, status=400)

    try:
        data = UserUpdate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar()

        if not user:
            return json({"error": "用户不存在"}, status=404)

        # 更新字段
        if data.email is not None:
            user.email = data.email
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone
        if data.is_active is not None:
            user.is_active = data.is_active

        session.add(user)
        await session.commit()

        return json({"message": "用户更新成功"})


@bp.delete("/<user_id>")
@require_permission("users:delete")
async def delete_user(request, user_id):
    """删除用户"""
    # 验证并转换 UUID 格式
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return json({"error": "无效的用户 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar()

        if not user:
            return json({"error": "用户不存在"}, status=404)

        # 检查是否是自己的账户
        current_user = await get_current_user(request)
        if current_user and user.id == current_user.id:
            return json(
                {"error": "不能删除自己的账户"},
                status=400,
            )

        await session.delete(user)
        await session.commit()

    return json({"message": "用户删除成功"})


@bp.get("/me")
async def get_current_user_info(request):
    """获取当前登录用户信息"""
    from app.utils.deps import get_current_user

    user = await get_current_user(request)

    if not user:
        return json({"error": "未授权访问"}, status=401)

    async with request.app.ctx.db() as session:
        # 重新查询以获取完整的角色和权限信息
        result = await session.execute(select(User).where(User.id == user.id))
        user = result.scalar()

        # 获取权限列表
        permissions = []
        for role in user.roles:
            for perm in role.permissions:
                if perm.code not in permissions:
                    permissions.append(perm.code)

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
            "permissions": permissions,
        }
    )


@bp.put("/<user_id>/password")
async def update_user_password(request, user_id):
    """修改用户密码"""
    from app.utils.deps import get_current_user
    from pydantic import BaseModel, Field

    # 验证并转换 UUID 格式
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return json({"error": "无效的用户 ID 格式"}, status=400)

    class PasswordChangeRequest(BaseModel):
        old_password: str = Field(..., min_length=1)
        new_password: str = Field(..., min_length=6)

    # 验证请求数据
    try:
        data = PasswordChangeRequest(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar()

        if not user:
            return json({"error": "用户不存在"}, status=404)

        # 验证旧密码
        if not user.verify_password(data.old_password):
            return json({"error": "原密码错误"}, status=400)

        # 更新密码
        user.password_hash = User.hash_password(data.new_password)
        await session.commit()

    return json({"message": "密码修改成功"})
