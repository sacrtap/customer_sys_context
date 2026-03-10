import { test, expect } from '@playwright/test'

test.describe('角色管理 - 权限列表数据流验证', () => {
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').first().fill('admin')
    await page.locator('input[placeholder="密码"]').first().fill('admin123')
    await page.locator('button[type="submit"]').first().click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test('验证权限数据流', async ({ page }) => {
    await login(page)
    
    // 收集控制台日志
    const consoleLogs: string[] = []
    page.on('console', msg => {
      const text = msg.text()
      if (text.includes('[RoleList]') || text.includes('[RoleForm]')) {
        consoleLogs.push(text)
        console.log('CONSOLE:', text)
      }
    })
    
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(3000)
    
    // 点击新建角色
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(5000)
    
    // 打印所有相关日志
    console.log('\n=== 角色管理控制台日志 ===')
    consoleLogs.forEach(log => console.log(log))
    console.log('=== End ===\n')
    
    // 检查权限树是否存在（不要求可见）
    const tree = page.locator('.ant-tree')
    const treeCount = await tree.count()
    console.log('权限树 DOM 数量:', treeCount)
    
    if (treeCount > 0) {
      // 获取 tree 的 aria 属性
      const role = await tree.first().getAttribute('role')
      console.log('Tree role 属性:', role)
      
      // 检查树节点
      const treeNodes = page.locator('.ant-tree-treenode')
      const nodeCount = await treeNodes.count()
      console.log('权限树节点数:', nodeCount)
      
      // 截图
      await page.screenshot({ path: 'test-results/role-form-tree-state.png' })
      console.log('截图已保存：test-results/role-form-tree-state.png')
    }
  })
})
