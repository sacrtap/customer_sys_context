import { test, expect } from '@playwright/test'

test.describe('角色管理 - 权限列表诊断', () => {
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').first().fill('admin')
    await page.locator('input[placeholder="密码"]').first().fill('admin123')
    await page.locator('button[type="submit"]').first().click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test('诊断权限树显示问题', async ({ page }) => {
    await login(page)
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
    
    // 收集控制台日志
    const consoleLogs: string[] = []
    page.on('console', msg => {
      consoleLogs.push(`[${msg.type()}] ${msg.text()}`)
    })
    
    // 点击新建角色
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(3000)
    
    // 打印控制台日志
    console.log('\n=== 控制台日志 ===')
    consoleLogs.forEach(log => console.log(log))
    console.log('===  End ===\n')
    
    // 检查模态框
    const modal = page.locator('.ant-modal')
    await expect(modal.first()).toBeVisible()
    
    // 检查权限配置区域
    const permissionsSection = page.locator('[data-testid="permissions"]')
    await expect(permissionsSection.first()).toBeVisible()
    
    // 检查 tree 组件
    const tree = page.locator('.ant-tree')
    const treeCount = await tree.count()
    console.log('权限树数量:', treeCount)
    
    if (treeCount > 0) {
      await expect(tree.first()).toBeVisible()
      
      // 检查树节点
      const treeNodes = page.locator('.ant-tree-treenode')
      const nodeCount = await treeNodes.count()
      console.log('权限树节点数:', nodeCount)
      
      if (nodeCount > 0) {
        const firstNodeText = await treeNodes.first().textContent()
        console.log('第一个节点文本:', firstNodeText)
        
        // 期望显示"接口权限"
        expect(firstNodeText).toContain('接口权限')
      } else {
        console.log('警告：权限树节点数为 0')
        // 截图
        await page.screenshot({ path: 'test-results/role-form-empty-tree.png' })
        console.log('截图已保存')
      }
    } else {
      console.log('警告：权限树数量为 0')
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/role-form-debug.png' })
    console.log('调试截图已保存')
  })
})
