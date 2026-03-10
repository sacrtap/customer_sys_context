import { test, expect } from '@playwright/test'

test.describe('角色管理页面修复', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/dashboard/)
  })

  test('角色列表应该正常加载', async ({ page }) => {
    // 导航到角色列表
    await page.click('.ant-menu-item:has-text("角色权限")')
    
    // 等待表格加载
    await page.waitForSelector('[data-testid="role-table"]', { timeout: 5000 })
    
    // 验证表格显示
    const table = page.getByTestId('role-table')
    await expect(table).toBeVisible()
  })
  
  test('角色列表应该有数据', async ({ page }) => {
    // 导航到角色列表
    await page.click('.ant-menu-item:has-text("角色权限")')
    await page.waitForSelector('[data-testid="role-table"]', { timeout: 5000 })
    
    // 验证表格有数据行
    const rows = page.getByTestId('role-table').locator('tbody tr')
    await expect(rows).not.toHaveCount(0)
  })
  
  test('角色列表页面不应该显示错误', async ({ page }) => {
    await page.click('.ant-menu-item:has-text("角色权限")')
    
    // 等待一段时间确保数据加载完成
    await page.waitForTimeout(2000)
    
    // 检查是否有错误提示
    const errorElements = page.locator('.ant-alert-error, .ant-message-error')
    await expect(errorElements).toHaveCount(0)
  })
  
  test('新建角色按钮应该可见', async ({ page }) => {
    await page.click('.ant-menu-item:has-text("角色权限")')
    await page.waitForSelector('[data-testid="role-table"]', { timeout: 5000 })
    
    // 验证新建按钮存在
    const addButton = page.locator('button:has-text("新建角色")')
    await expect(addButton).toBeVisible()
  })
  
  test('角色列表应该显示角色名称和权限列', async ({ page }) => {
    await page.click('.ant-menu-item:has-text("角色权限")')
    await page.waitForSelector('[data-testid="role-table"]', { timeout: 5000 })
    
    // 验证表头
    const headers = page.locator('[data-testid="role-table"] thead th')
    await expect(headers.first()).toContainText('角色名称')
  })
})
