import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = None


async def test_permissions_api():
    """测试权限列表 API"""
    global TOKEN

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 登录获取 Token
        print("1. 登录获取 Token...")
        response = await client.post(
            f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"}
        )
        if response.status_code != 200:
            print(f"   ❌ 登录失败：{response.status_code}")
            return
        TOKEN = response.json()["access_token"]
        print(f"   ✅ 登录成功")

        # 2. 测试权限列表 API
        print("\n2. 测试 GET /api/v1/roles/permissions...")
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = await client.get(f"{BASE_URL}/roles/permissions", headers=headers)

        if response.status_code != 200:
            print(f"   ❌ 请求失败：{response.status_code}")
            print(f"   响应：{response.text}")
            return

        data = response.json()
        print(f"   ✅ 请求成功")
        print(f"   权限总数：{data.get('total', 0)}")
        print(f"   返回数据结构:")

        items = data.get("items", [])
        for item in items[:5]:
            print(
                f"     - {item.get('code')} | {item.get('name')} | type={item.get('type')}"
            )

        # 检查是否有 module 字段
        if items:
            first_item = items[0]
            has_module = "module" in first_item
            has_type = "type" in first_item
            print(f"\n   字段检查:")
            print(f"     - 有 'type' 字段：{has_type} ✅")
            print(
                f"     - 有 'module' 字段：{has_module} {'❌ (预期)' if not has_module else '✅'}"
            )
            print(f"     - 所有字段：{list(first_item.keys())}")


if __name__ == "__main__":
    print("=" * 60)
    print("权限列表 API 测试")
    print("=" * 60)
    asyncio.run(test_permissions_api())
