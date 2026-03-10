import { test, expect } from '@playwright/test'

test.describe('角色管理 - 简单调试', () => {
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').first().fill('admin')
    await page.locator('input[placeholder="密码"]').first().fill('admin123')
    await page.locator('button[type="submit"]').first().click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test('测试新建角色表单', async ({ page }) => {
    await login(page)
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(3000)
    
    // 点击新建角色
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(5000)
    
    // 检查模态框
    const modal = page.locator('.ant-modal')
    const modalCount = await modal.count()
    console.log('模态框数量:', modalCount)
    
    if (modalCount > 0) {
      await expect(modal.first()).toBeVisible()
      
      // 检查模态框标题
      const title = await page.locator('.ant-modal-title').first().textContent()
      console.log('模态框标题:', title)
      
      // 检查表单字段
      const roleNameInput = page.locator('[data-testid="role-name"] input')
      const roleNameCount = await roleNameInput.count()
      console.log('角色名称输入框数量:', roleNameCount)
      
      // 检查权限配置区域
      const permissionsSection = page.locator('[data-testid="permissions"]')
      const permissionsCount = await permissionsSection.count()
      console.log('权限配置区域数量:', permissionsCount)
      
      if (permissionsCount > 0) {
        // 检查树
        const tree = page.locator('.ant-tree')
        const treeCount = await tree.count()
        console.log('权限树数量:', treeCount)
        
        if (treeCount > 0) {
          // 获取树的所有节点
          const treeNodes = page.locator('.ant-tree-treenode')
          const nodeCount = await treeNodes.count()
          console.log('权限树节点数:', nodeCount)
          
          for (let i = 0; i < nodeCount; i++) {
            const nodeText = await treeNodes.nth(i).textContent()
            console.log(`  节点 ${i}: "${nodeText}"`)
          }
        }
      }
      
      // 截图
      await page.screenshot({ path: 'test-results/role-form-simple.png' })
      console.log('截图已保存')
    }
  })
})
