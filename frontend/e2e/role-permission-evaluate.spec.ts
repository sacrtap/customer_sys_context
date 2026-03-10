import { test, expect } from '@playwright/test'

test.describe('角色管理 - 权限树评估', () => {
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').first().fill('admin')
    await page.locator('input[placeholder="密码"]').first().fill('admin123')
    await page.locator('button[type="submit"]').first().click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test('评估权限树数据', async ({ page }) => {
    await login(page)
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(3000)
    
    // 点击新建角色
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(3000)
    
    // 评估页面中的 Vue 组件状态
    const permissionTreeData = await page.evaluate(() => {
      // 尝试获取 Vue 组件实例
      const modal = document.querySelector('.ant-modal')
      if (modal) {
        // 查找 a-tree 组件
        const tree = modal.querySelector('.ant-tree')
        if (tree) {
          return {
            treeExists: true,
            treeClass: tree.className,
            childNodes: tree.childNodes.length,
            innerHTML: tree.innerHTML.substring(0, 500)
          }
        }
        return { modalExists: true, modalHasTree: false }
      }
      return { modalExists: false }
    })
    
    console.log('权限树评估结果:', JSON.stringify(permissionTreeData, null, 2))
    
    // 检查树节点的文本内容
    const firstTreeNode = page.locator('.ant-tree-treenode').first()
    const firstNodeText = await firstTreeNode.textContent()
    console.log('第一个树节点文本:', firstNodeText)
    
    // 检查是否有子节点
    const childNodes = page.locator('.ant-tree-treenode')
    const count = await childNodes.count()
    console.log('树节点总数:', count)
    
    // 列出所有节点文本
    console.log('\n所有树节点:')
    for (let i = 0; i < count; i++) {
      const text = await childNodes.nth(i).textContent()
      console.log(`  ${i}: ${text}`)
    }
    
    expect(count).toBeGreaterThan(0)
  })
})
