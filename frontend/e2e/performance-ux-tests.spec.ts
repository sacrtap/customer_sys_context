import { test, expect } from '@playwright/test'

/**
 * 性能和用户体验测试套件
 * 
 * 测试覆盖:
 * - 页面加载速度 (< 3 秒)
 * - 表单提交反馈
 * - 错误提示
 * - 加载状态
 * 
 * 总计：6 个用例
 */

test.describe('性能和用户体验', () => {
  // 简化的登录辅助函数
  async function login(page) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').fill('admin')
    await page.locator('input[placeholder="密码"]').fill('admin123')
    await page.locator('button[type="submit"], button:has-text("登录")').click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test('Dashboard 页面应该在 3 秒内加载完成', async ({ page }) => {
    await login(page)
    
    const startTime = Date.now()
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    const loadTime = Date.now() - startTime
    
    console.log(`Dashboard 加载时间：${loadTime}ms`)
    expect(loadTime).toBeLessThan(3000)
    await expect(page.getByText('工作台')).toBeVisible()
  })

  test('客户列表页面应该在 3 秒内加载完成', async ({ page }) => {
    await login(page)
    
    const startTime = Date.now()
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    const loadTime = Date.now() - startTime
    
    console.log(`客户列表加载时间：${loadTime}ms`)
    expect(loadTime).toBeLessThan(3000)
    await expect(page.getByText('客户管理')).toBeVisible()
  })

  test('表单验证失败时应该显示错误提示', async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForTimeout(1000)
    
    await page.getByText('新建客户').first().click()
    await page.waitForSelector('.ant-modal', { state: 'visible', timeout: 5000 })
    await page.waitForTimeout(500)
    
    // 提交空表单触发验证错误
    await page.locator('.ant-modal button[type="submit"]').click()
    await page.waitForTimeout(1000)
    
    const formItems = page.locator('.ant-form-item-has-error')
    const errorCount = await formItems.count()
    console.log(`表单验证错误数量：${errorCount}`)
    expect(errorCount).toBeGreaterThan(0)
  })

  test('表格数据加载完成后应该显示数据', async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForTimeout(2000)
    
    const table = page.locator('[data-testid="customer-table"]')
    await expect(table).toBeVisible()
    
    const rows = page.locator('.ant-table-tbody tr')
    const rowCount = await rows.count()
    console.log(`表格数据行数：${rowCount}`)
    expect(rowCount).toBeGreaterThan(0)
  })

  test('Dashboard 应该显示统计卡片', async ({ page }) => {
    await login(page)
    await page.goto('/dashboard')
    await page.waitForTimeout(2000)
    
    const statCards = page.locator('.ant-statistic')
    const cardCount = await statCards.count()
    console.log(`Dashboard 统计卡片数：${cardCount}`)
    expect(cardCount).toBeGreaterThan(0)
  })

  test('登录失败时应该阻止进入系统', async ({ browser }) => {
    const context = await browser.newContext()
    const page = await context.newPage()
    
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').fill('admin')
    await page.locator('input[placeholder="密码"]').fill('wrongpassword')
    await page.locator('button[type="submit"], button:has-text("登录")').click()
    await page.waitForTimeout(2000)
    
    // 验证仍然在登录页面
    const currentUrl = page.url()
    console.log(`登录失败后 URL: ${currentUrl}`)
    expect(currentUrl).toContain('/login')
    
    await context.close()
  })
})
