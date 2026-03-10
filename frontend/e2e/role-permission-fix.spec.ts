import { test, expect } from '@playwright/test'

test.describe('角色管理 - 权限列表显示', () => {
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').first().fill('admin')
    await page.locator('input[placeholder="密码"]').first().fill('admin123')
    await page.locator('button[type="submit"]').first().click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  })

  test('点击新建角色应该显示权限树', async ({ page }) => {
    // 点击新建角色按钮
    await page.locator('[data-testid="add-role-btn"]').first().click()
    
    // 等待权限数据加载完成（通过检查权限树出现）
    await page.waitForTimeout(3000)
    
    // 等待模态框出现（使用更通用的选择器）
    const modal = page.locator('.ant-modal')
    await expect(modal.first()).toBeVisible()
    
    // 等待权限树出现
    const tree = page.locator('.ant-tree')
    await expect(tree.first()).toBeVisible({ timeout: 5000 })
    
    // 验证有权限节点
    const treeNodes = page.locator('.ant-tree-treenode')
    const count = await treeNodes.count()
    expect(count).toBeGreaterThan(0)
    
    // 打印所有节点的文本用于调试
    console.log('权限树节点数:', count)
    for (let i = 0; i < count; i++) {
      const nodeText = await treeNodes.nth(i).textContent()
      console.log(`  节点 ${i}: "${nodeText}"`)
    }
    
    // 验证至少有一个权限类型组（跳过第一个空节点）
    const firstRealNode = treeNodes.nth(1)
    const firstNodeText = await firstRealNode.textContent()
    console.log('第一个有效节点文本:', firstNodeText)
    
    expect(firstNodeText).toMatch(/(接口权限|菜单权限|按钮权限)/)
  })
})
