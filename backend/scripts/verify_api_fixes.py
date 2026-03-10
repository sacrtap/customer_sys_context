#!/usr/bin/env python
"""
后端 API 修复验证脚本

用于验证 Dashboard、Users、Roles、Customers API 的修复是否成功

使用方法:
    cd backend
    source venv/bin/activate
    python scripts/verify_api_fixes.py
"""

import sys
import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000"
TOKEN = None


class Colors:
    """终端颜色"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


async def get_token(client: httpx.AsyncClient):
    """获取管理员 Token"""
    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            return None
    except Exception as e:
        print_error(f"获取 Token 失败：{e}")
        return None


async def test_health_check(client: httpx.AsyncClient):
    """测试健康检查 API"""
    print_header("健康检查 API")

    try:
        response = await client.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"健康检查通过 - 状态：{data.get('status', 'unknown')}")
            print(f"  数据库：{data.get('database', {}).get('status', 'unknown')}")
            print(
                f"  API 版本：{data.get('version', {}).get('api_version', 'unknown')}"
            )
            return True
        else:
            print_error(f"健康检查失败 - 状态码：{response.status_code}")
            return False
    except Exception as e:
        print_error(f"健康检查异常：{e}")
        return False


async def test_dashboard_api(client: httpx.AsyncClient):
    """测试 Dashboard API"""
    print_header("Dashboard API 测试")

    headers = {"Authorization": f"Bearer {TOKEN}"}
    tests = [
        ("概览数据", "/api/v1/dashboard/overview"),
        ("快捷入口", "/api/v1/dashboard/quick-actions"),
        ("最新动态", "/api/v1/dashboard/recent-activities"),
        ("客户健康度", "/api/v1/dashboard/customer-health"),
    ]

    results = []
    for name, endpoint in tests:
        try:
            response = await client.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                print_success(f"{name} - 状态码：{response.status_code}")
                results.append(True)
            elif response.status_code == 500:
                print_error(f"{name} - 服务器错误 (500) - 可能是枚举类型问题未修复")
                results.append(False)
            else:
                print_warning(f"{name} - 状态码：{response.status_code}")
                results.append(False)
        except Exception as e:
            print_error(f"{name} - 异常：{e}")
            results.append(False)

    return all(results)


async def test_user_api(client: httpx.AsyncClient):
    """测试用户 API"""
    print_header("用户管理 API 测试")

    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. 获取用户列表
    try:
        response = await client.get(f"{BASE_URL}/api/v1/users", headers=headers)
        if response.status_code == 200:
            users = response.json().get("items", [])
            print_success(f"获取用户列表 - 共 {len(users)} 个用户")

            if users:
                # 测试获取用户详情
                user_id = users[0]["id"]
                response = await client.get(
                    f"{BASE_URL}/api/v1/users/{user_id}", headers=headers
                )
                if response.status_code == 200:
                    print_success(f"获取用户详情 - 用户：{users[0]['username']}")
                elif response.status_code == 500:
                    print_error(
                        f"获取用户详情 - 服务器错误 (500) - 可能是 UUID 转换问题"
                    )
                    return False
                else:
                    print_warning(f"获取用户详情 - 状态码：{response.status_code}")
        else:
            print_error(f"获取用户列表失败 - 状态码：{response.status_code}")
            return False
    except Exception as e:
        print_error(f"用户 API 测试异常：{e}")
        return False

    # 2. 测试无效 UUID 格式
    response = await client.get(
        f"{BASE_URL}/api/v1/users/invalid-uuid", headers=headers
    )
    if response.status_code == 400:
        print_success(f"无效 UUID 验证 - 返回 400 错误")
    else:
        print_warning(f"无效 UUID 验证 - 状态码：{response.status_code} (期望 400)")

    return True


async def test_role_api(client: httpx.AsyncClient):
    """测试角色 API"""
    print_header("角色管理 API 测试")

    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. 获取角色列表
    try:
        response = await client.get(f"{BASE_URL}/api/v1/roles", headers=headers)
        if response.status_code == 200:
            roles = response.json().get("items", [])
            print_success(f"获取角色列表 - 共 {len(roles)} 个角色")

            if roles:
                role_id = roles[0]["id"]

                # 测试获取角色权限
                response = await client.get(
                    f"{BASE_URL}/api/v1/roles/{role_id}/permissions", headers=headers
                )
                if response.status_code == 200:
                    print_success(f"获取角色权限 - 角色：{roles[0]['name']}")
                elif response.status_code == 500:
                    print_error(
                        f"获取角色权限 - 服务器错误 (500) - 可能是 UUID 转换问题"
                    )
                    return False

                # 测试获取角色用户
                response = await client.get(
                    f"{BASE_URL}/api/v1/roles/{role_id}/users", headers=headers
                )
                if response.status_code == 200:
                    print_success(f"获取角色用户 - 角色：{roles[0]['name']}")
                elif response.status_code == 500:
                    print_error(
                        f"获取角色用户 - 服务器错误 (500) - 可能是 UUID 转换问题"
                    )
                    return False
        else:
            print_error(f"获取角色列表失败 - 状态码：{response.status_code}")
            return False
    except Exception as e:
        print_error(f"角色 API 测试异常：{e}")
        return False

    return True


async def test_customer_api(client: httpx.AsyncClient):
    """测试客户 API"""
    print_header("客户管理 API 测试")

    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 1. 获取行业列表
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/customers/industries", headers=headers
        )
        if response.status_code == 200:
            industries = response.json().get("items", [])
            print_success(f"获取行业列表 - 共 {len(industries)} 个行业")
        else:
            print_error(f"获取行业列表失败 - 状态码：{response.status_code}")
    except Exception as e:
        print_error(f"行业 API 测试异常：{e}")

    # 2. 获取客户等级列表
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/customers/levels", headers=headers
        )
        if response.status_code == 200:
            levels = response.json().get("items", [])
            print_success(f"获取客户等级列表 - 共 {len(levels)} 个等级")
        else:
            print_error(f"获取客户等级列表失败 - 状态码：{response.status_code}")
    except Exception as e:
        print_error(f"客户等级 API 测试异常：{e}")

    # 3. 获取客户列表
    try:
        response = await client.get(f"{BASE_URL}/api/v1/customers", headers=headers)
        if response.status_code == 200:
            customers = response.json().get("items", [])
            print_success(f"获取客户列表 - 共 {len(customers)} 个客户")

            if customers:
                customer_id = customers[0]["id"]

                # 测试获取客户详情
                response = await client.get(
                    f"{BASE_URL}/api/v1/customers/{customer_id}", headers=headers
                )
                if response.status_code == 200:
                    print_success(
                        f"获取客户详情 - 客户：{customers[0]['customer_name']}"
                    )
                elif response.status_code == 500:
                    print_error(
                        f"获取客户详情 - 服务器错误 (500) - 可能是 UUID 转换问题"
                    )
                    return False
        else:
            print_error(f"获取客户列表失败 - 状态码：{response.status_code}")
            return False
    except Exception as e:
        print_error(f"客户 API 测试异常：{e}")
        return False

    return True


async def main():
    """主函数"""
    print_header("后端 API 修复验证")
    print(f"目标服务器：{BASE_URL}")
    print(f"测试时间：{asyncio.get_event_loop().time():.2f}s\n")

    # 检查服务是否运行
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            await client.get(f"{BASE_URL}/api/v1/health")
        except httpx.ConnectError:
            print_error(f"无法连接到 {BASE_URL}")
            print_warning(
                "请确保后端服务正在运行：cd backend && source venv/bin/activate && python main.py"
            )
            sys.exit(1)

        # 1. 健康检查
        health_ok = await test_health_check(client)

        # 2. 获取 Token
        print_header("获取认证 Token")
        token = await get_token(client)
        if token:
            global TOKEN
            TOKEN = token
            print_success(f"获取 Token 成功：{token[:50]}...")
        else:
            print_error("获取 Token 失败，跳过需要认证的测试")
            return

        # 3. Dashboard API 测试
        dashboard_ok = await test_dashboard_api(client)

        # 4. 用户 API 测试
        user_ok = await test_user_api(client)

        # 5. 角色 API 测试
        role_ok = await test_role_api(client)

        # 6. 客户 API 测试
        customer_ok = await test_customer_api(client)

        # 汇总结果
        print_header("测试结果汇总")

        results = [
            ("健康检查", health_ok),
            ("Dashboard API", dashboard_ok),
            ("用户管理 API", user_ok),
            ("角色管理 API", role_ok),
            ("客户管理 API", customer_ok),
        ]

        passed = sum(1 for _, ok in results if ok)
        total = len(results)

        for name, ok in results:
            if ok:
                print_success(f"{name}: 通过")
            else:
                print_error(f"{name}: 失败")

        print(f"\n总计：{passed}/{total} 通过")

        if passed == total:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！API 修复成功！{Colors.END}\n"
            )
            sys.exit(0)
        else:
            print(
                f"\n{Colors.YELLOW}{Colors.BOLD}⚠ 部分测试失败，请检查修复情况{Colors.END}\n"
            )
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
