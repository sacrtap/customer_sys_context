import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"


async def test_permissions_api():
    """测试权限列表 API 并模拟前端数据结构"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 登录获取 Token
        print("1. 登录获取 Token...")
        response = await client.post(
            f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"}
        )
        TOKEN = response.json()["access_token"]
        print(f"   ✅ Token: {TOKEN[:50]}...")

        # 2. 获取权限列表
        print("\n2. 获取权限列表...")
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = await client.get(f"{BASE_URL}/roles/permissions", headers=headers)
        data = response.json()

        # 3. 模拟前端 Permission 接口
        print("\n3. 模拟前端数据结构转换...")
        permissions = data.get("items", [])

        # 检查每个权限是否有 type 字段
        has_type = all("type" in p for p in permissions)
        has_module = any("module" in p for p in permissions)

        print(f"   - 权限总数：{len(permissions)}")
        print(f"   - 所有权限都有 'type' 字段：{has_type} ✅")
        print(f"   - 有 'module' 字段：{has_module} ❌")

        # 4. 模拟前端 permissionTree 计算逻辑
        print("\n4. 模拟前端 permissionTree 计算...")
        typeMap = {}
        typeNames = {
            "api": "接口权限",
            "menu": "菜单权限",
            "button": "按钮权限",
        }

        for perm in permissions:
            type_name = typeNames.get(perm["type"], perm["type"])
            if type_name not in typeMap:
                typeMap[type_name] = {
                    "id": f"type_{perm['type']}",
                    "name": type_name,
                    "children": [],
                }
            typeMap[type_name]["children"].append(
                {"id": perm["id"], "name": f"{perm['name']} ({perm['code']})"}
            )

        tree_data = list(typeMap.values())
        print(f"   - 生成的权限树节点数：{len(tree_data)}")
        for node in tree_data:
            print(f"     * {node['name']}: {len(node['children'])} 个权限")

        # 5. 打印完整的树结构
        print("\n5. 完整的权限树结构:")
        import json

        print(json.dumps(tree_data, indent=2, ensure_ascii=False)[:1000])


if __name__ == "__main__":
    print("=" * 60)
    print("权限列表 API 测试 - 模拟前端数据处理")
    print("=" * 60)
    asyncio.run(test_permissions_api())
