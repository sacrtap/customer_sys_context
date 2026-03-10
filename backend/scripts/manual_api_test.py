#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动 API 集成测试脚本
用于在 sanic-testing 兼容性问题下验证 API 功能

使用方法:
1. 启动后端服务：python main.py
2. 运行此脚本：python scripts/manual_api_test.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

BASE_URL = "http://127.0.0.1:8000"
TOKEN = None


class colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_result(test_name: str, passed: bool, message: str = ""):
    status = (
        f"{colors.GREEN}✓ PASS{colors.END}"
        if passed
        else f"{colors.RED}✗ FAIL{colors.END}"
    )
    print(f"{status} - {test_name}")
    if message and not passed:
        print(f"       {colors.RED}{message}{colors.END}")
    return passed


async def run_tests():
    """运行所有 API 测试"""
    global TOKEN

    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n{colors.BOLD}{colors.BLUE}{'=' * 60}{colors.END}")
        print(
            f"{colors.BOLD}{colors.BLUE}API 集成测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{colors.END}"
        )
        print(f"{colors.BOLD}{colors.BLUE}{'=' * 60}{colors.END}\n")

        # 1. 健康检查测试
        print(f"{colors.BOLD}1. 健康检查 API{colors.END}")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            passed = response.status_code == 200
            data = response.json() if passed else {}
            results.append(
                print_result(
                    "健康检查返回 200",
                    passed,
                    f"状态码：{response.status_code}" if not passed else "",
                )
            )
            if passed:
                print(
                    f"       状态：{data.get('status')}, 运行时间：{data.get('uptime', 'N/A')}s"
                )
        except Exception as e:
            results.append(print_result("健康检查 API", False, str(e)))

        # 2. 登录测试
        print(f"\n{colors.BOLD}2. 认证 API{colors.END}")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": "admin", "password": "admin123"},
            )
            passed = response.status_code == 200
            if passed:
                TOKEN = response.json().get("access_token")
                results.append(print_result("管理员登录成功", passed))
                print(f"       Token: {TOKEN[:30]}...")
            else:
                results.append(
                    print_result(
                        "管理员登录成功", passed, f"响应：{response.text[:100]}"
                    )
                )
        except Exception as e:
            results.append(print_result("管理员登录", False, str(e)))

        if not TOKEN:
            print(f"\n{colors.YELLOW}⚠ 登录失败，跳过需要认证的测试{colors.END}\n")
        else:
            headers = {"Authorization": f"Bearer {TOKEN}"}

            # 3. 用户 API 测试
            print(f"\n{colors.BOLD}3. 用户管理 API{colors.END}")

            # 获取当前用户信息
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/users/me", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取当前用户信息", passed))
                if passed:
                    data = response.json()
                    print(
                        f"       用户：{data.get('username')}, 角色数：{len(data.get('roles', []))}"
                    )
            except Exception as e:
                results.append(print_result("获取当前用户信息", False, str(e)))

            # 获取用户详情
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/users/1", headers=headers
                )
                passed = response.status_code in [200, 404]
                results.append(print_result("获取用户详情 (ID=1)", passed))
            except Exception as e:
                results.append(print_result("获取用户详情", False, str(e)))

            # 4. 角色 API 测试
            print(f"\n{colors.BOLD}4. 角色管理 API{colors.END}")

            # 获取角色列表
            try:
                response = await client.get(f"{BASE_URL}/api/v1/roles", headers=headers)
                passed = response.status_code == 200
                results.append(print_result("获取角色列表", passed))
                if passed:
                    data = response.json()
                    print(f"       角色数：{len(data.get('items', []))}")
            except Exception as e:
                results.append(print_result("获取角色列表", False, str(e)))

            # 获取权限列表
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/roles/permissions", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取权限列表", passed))
                if passed:
                    data = response.json()
                    print(f"       权限数：{data.get('total', 0)}")
            except Exception as e:
                results.append(print_result("获取权限列表", False, str(e)))

            # 5. 客户 API 测试
            print(f"\n{colors.BOLD}5. 客户管理 API{colors.END}")

            # 获取客户列表
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/customers", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取客户列表", passed))
                if passed:
                    data = response.json()
                    print(f"       客户数：{len(data.get('items', []))}")
            except Exception as e:
                results.append(print_result("获取客户列表", False, str(e)))

            # 获取行业列表
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/industries", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取行业列表", passed))
            except Exception as e:
                results.append(print_result("获取行业列表", False, str(e)))

            # 获取客户等级列表
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/customer-levels", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取客户等级列表", passed))
            except Exception as e:
                results.append(print_result("获取客户等级列表", False, str(e)))

            # 6. 结算 API 测试
            print(f"\n{colors.BOLD}6. 结算管理 API{colors.END}")

            # 获取结算列表
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/settlements", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取结算列表", passed))
                if passed:
                    data = response.json()
                    print(f"       结算记录数：{len(data.get('items', []))}")
            except Exception as e:
                results.append(print_result("获取结算列表", False, str(e)))

            # 7. Dashboard API 测试
            print(f"\n{colors.BOLD}7. Dashboard API{colors.END}")

            # 获取概览数据
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/dashboard/overview", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取 Dashboard 概览", passed))
                if passed:
                    data = response.json()
                    print(f"       总客户数：{data.get('total_customers', 'N/A')}")
            except Exception as e:
                results.append(print_result("获取 Dashboard 概览", False, str(e)))

            # 获取快速操作
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/dashboard/quick-actions", headers=headers
                )
                passed = response.status_code == 200
                results.append(print_result("获取快速操作", passed))
            except Exception as e:
                results.append(print_result("获取快速操作", False, str(e)))

        # 总结
        print(f"\n{colors.BOLD}{colors.BLUE}{'=' * 60}{colors.END}")
        passed_count = sum(results)
        total_count = len(results)
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0

        status_color = (
            colors.GREEN
            if success_rate >= 90
            else colors.YELLOW
            if success_rate >= 70
            else colors.RED
        )
        print(
            f"{colors.BOLD}测试结果：{status_color}{passed_count}/{total_count} 通过 ({success_rate:.1f}%){colors.END}"
        )
        print(f"{colors.BOLD}{colors.BLUE}{'=' * 60}{colors.END}\n")

        return passed_count == total_count


if __name__ == "__main__":
    print("\n开始 API 集成测试...\n")
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
