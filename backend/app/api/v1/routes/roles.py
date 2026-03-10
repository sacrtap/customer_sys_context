"""
角色管理路由
"""

from sanic import Blueprint, json
from sqlalchemy import select, func
from uuid import UUID

from app.models.role import Role, Permission
from app.utils.deps import require_permission

bp = Blueprint("roles", url_prefix="/roles")


@bp.get("")
@require_permission("roles:read")
async def list_roles(request):
    """角色列表"""
    async with request.app.ctx.db() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()

    return json(
        {
            "items": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "description": r.description,
                    "is_default": r.is_default,
                    "permissions": [
                        {"id": str(p.id), "code": p.code, "name": p.name}
                        for p in r.permissions
                    ],
                    "created_at": r.created_at.isoformat(),
                }
                for r in roles
            ],
            "total": len(roles),
        }
    )


@bp.post("")
@require_permission("roles:create")
async def create_role(request):
    """创建角色"""
    from app.schemas.role import RoleCreate

    try:
        data = RoleCreate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        # 检查角色名是否已存在
        exists = await session.scalar(select(Role).where(Role.name == data.name))
        if exists:
            return json({"error": "角色名已存在"}, status=400)

        # 创建角色
        role = Role(
            name=data.name,
            description=data.description,
            is_default=data.is_default or False,
        )

        # 分配权限
        if data.permission_ids:
            permissions = await session.execute(
                select(Permission).where(Permission.id.in_(data.permission_ids))
            )
            role.permissions = list(permissions.scalars().all())

        session.add(role)
        await session.commit()

    return json(
        {
            "id": str(role.id),
            "name": role.name,
            "message": "角色创建成功",
        },
        status=201,
    )


@bp.put("/<role_id>")
@require_permission("roles:update")
async def update_role(request, role_id):
    """更新角色"""
    from app.schemas.role import RoleUpdate

    # 验证并转换 UUID 格式
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        return json({"error": "无效的角色 ID 格式"}, status=400)

    try:
        data = RoleUpdate(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(Role).where(Role.id == role_uuid))
        role = result.scalar()

        if not role:
            return json({"error": "角色不存在"}, status=404)

        # 更新字段
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.is_default is not None:
            role.is_default = data.is_default

        # 更新权限
        if data.permission_ids is not None:
            permissions = await session.execute(
                select(Permission).where(Permission.id.in_(data.permission_ids))
            )
            role.permissions = list(permissions.scalars().all())

        await session.commit()

    return json({"message": "角色更新成功"})


@bp.delete("/<role_id>")
@require_permission("roles:delete")
async def delete_role(request, role_id):
    """删除角色"""
    # 验证并转换 UUID 格式
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        return json({"error": "无效的角色 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(Role).where(Role.id == role_uuid))
        role = result.scalar()

        if not role:
            return json({"error": "角色不存在"}, status=404)

        # 不能删除默认角色
        if role.is_default:
            return json(
                {"error": "不能删除默认角色"},
                status=400,
            )

        await session.delete(role)
        await session.commit()

    return json({"message": "角色删除成功"})


@bp.get("/<role_id>/permissions")
@require_permission("roles:read")
async def get_role_permissions(request, role_id):
    """获取角色权限"""
    # 验证并转换 UUID 格式
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        return json({"error": "无效的角色 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(Role).where(Role.id == role_uuid))
        role = result.scalar()

        if not role:
            return json({"error": "角色不存在"}, status=404)

    return json(
        {
            "role_id": str(role.id),
            "permissions": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "type": p.type,
                }
                for p in role.permissions
            ],
        }
    )


@bp.get("/permissions")
@require_permission("roles:read")
async def list_permissions(request):
    """权限列表"""
    async with request.app.ctx.db() as session:
        result = await session.execute(select(Permission))
        permissions = result.scalars().all()

    return json(
        {
            "items": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                }
                for p in permissions
            ],
            "total": len(permissions),
        }
    )


@bp.post("/<role_id>/permissions")
@require_permission("roles:update")
async def update_role_permissions(request, role_id):
    """批量更新角色权限"""
    from pydantic import BaseModel, Field

    # 验证并转换 UUID 格式
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        return json({"error": "无效的角色 ID 格式"}, status=400)

    class PermissionUpdateRequest(BaseModel):
        permission_ids: list[str] = Field(default_factory=list)

    try:
        data = PermissionUpdateRequest(**request.json)
    except Exception as e:
        return json({"error": f"数据验证失败：{str(e)}"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(Role).where(Role.id == role_uuid))
        role = result.scalar()

        if not role:
            return json({"error": "角色不存在"}, status=404)

        # 更新权限
        if data.permission_ids:
            permissions = await session.execute(
                select(Permission).where(Permission.id.in_(data.permission_ids))
            )
            role.permissions = list(permissions.scalars().all())
        else:
            # 清空权限
            role.permissions = []

        await session.commit()

    return json(
        {
            "message": "权限更新成功",
            "permissions": [
                {"id": str(p.id), "code": p.code, "name": p.name}
                for p in role.permissions
            ],
        }
    )


@bp.get("/<role_id>/users")
@require_permission("roles:read")
async def get_role_users(request, role_id):
    """获取角色下的用户列表"""
    from app.models.user import User

    # 验证并转换 UUID 格式
    try:
        role_uuid = UUID(role_id)
    except ValueError:
        return json({"error": "无效的角色 ID 格式"}, status=400)

    async with request.app.ctx.db() as session:
        result = await session.execute(select(Role).where(Role.id == role_uuid))
        role = result.scalar()

        if not role:
            return json({"error": "角色不存在"}, status=404)

        # 查询该角色下的所有用户
        users_result = await session.execute(
            select(User).where(User.roles.contains(role))
        )
        users = users_result.scalars().all()

    return json(
        {
            "items": [
                {
                    "id": str(u.id),
                    "username": u.username,
                    "email": u.email,
                    "full_name": u.full_name,
                    "is_active": u.is_active,
                }
                for u in users
            ],
            "total": len(users),
        }
    )
