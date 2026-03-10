# -*- coding: utf-8 -*-
import asyncio
import httpx
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5173"
API_URL = "http://127.0.0.1:8000/api/v1"


async def diagnose():
    print("=" * 60)
    print("角色管理 - 权限列表显示问题诊断")
    print("=" * 60)

    # 1. 获取 Token
    print("\n1. 获取 Token...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_URL}/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = response.json()["access_token"]
        print(f"   ✅ Token 获取成功")

        # 2. 获取权限数据
        print("\n2. 获取权限列表 API 数据...")
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"{API_URL}/roles/permissions", headers=headers)
        data = response.json()
        print(f"   - 权限总数：{data.get('total', 0)}")
        print(f"   - 数据类型：{type(data.get('items'))}")
        if data.get("items"):
            print(f"   - 第一个权限：{data['items'][0]}")
            print(f"   - 字段：{list(data['items'][0].keys())}")

    # 3. 浏览器测试
    print("\n3. 浏览器测试...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 设置 localStorage token
        await page.add_init_script(f"""
            localStorage.setItem('access_token', '{token}')
        """)

        # 导航到角色页面
        print("   - 打开角色管理页面...")
        await page.goto(f"{BASE_URL}/roles")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # 点击新建角色
        print("   - 点击新建角色按钮...")
        await page.click('[data-testid="add-role-btn"]')
        await page.wait_for_timeout(2000)

        # 检查模态框
        modal = page.locator(".ant-modal")
        modal_count = await modal.count()
        print(f"   - 模态框数量：{modal_count}")

        if modal_count > 0:
            # 检查权限配置区域
            permissions_section = page.locator('[data-testid="permissions"]')
            section_count = await permissions_section.count()
            print(f"   - 权限配置区域数量：{section_count}")

            # 检查 tree 组件
            tree = page.locator(".ant-tree")
            tree_count = await tree.count()
            print(f"   - 权限树数量：{tree_count}")

            if tree_count > 0:
                tree_nodes = page.locator(".ant-tree-treenode")
                node_count = await tree_nodes.count()
                print(f"   - 权限树节点数：{node_count}")

                if node_count > 0:
                    first_node = await tree_nodes.first().text_content()
                    print(f"   - 第一个节点文本：{first_node}")

                # 截图
                await page.screenshot(path="role-form-debug.png")
                print(f"   - 截图已保存：role-form-debug.png")

            # 获取控制台日志
            print("\n4. 控制台日志:")
            console_logs = []
            page.on(
                "console",
                lambda msg: console_logs.append(f"   [{msg.type}] {msg.text}"),
            )

            # 重新触发一次
            await page.click('[data-testid="add-role-btn"]')
            await page.wait_for_timeout(1000)

            for log in console_logs[-10:]:
                print(log)

        await browser.close()

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(diagnose())
