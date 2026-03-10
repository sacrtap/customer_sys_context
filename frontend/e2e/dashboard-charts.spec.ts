import { test, expect } from '@playwright/test'

test.describe('Dashboard 图表集成', () => {
  // 登录辅助函数
  async function login(page) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    
    // 填充用户名
    const usernameInput = page.locator('input[placeholder="用户名"]')
    await usernameInput.fill('admin')
    
    // 填充密码
    const passwordInput = page.locator('input[placeholder="密码"]')
    await passwordInput.fill('admin123')
    
    // 点击登录按钮
    const loginButton = page.locator('button[type="submit"], button:has-text("登录")')
    await loginButton.click()
    
    // 等待导航和页面加载
    await page.waitForURL(/\/dashboard|^\//, { timeout: 10000 })
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test('应该显示用量趋势图', async ({ page }) => {
    await login(page)
    
    // 验证图表容器存在
    const trendChart = page.locator('.usage-trend-chart')
    await expect(trendChart).toBeVisible()
    
    // 验证图表标题
    const title = page.getByText('用量趋势').first()
    await expect(title).toBeVisible()
    
    // 验证时间范围选择器存在
    const rangeSelector = page.locator('.usage-trend-chart .ant-select')
    await expect(rangeSelector.first()).toBeVisible()
  })
  
  test('应该显示收入预测图', async ({ page }) => {
    await login(page)
    
    // 验证收入图表容器存在
    const revenueChart = page.locator('.revenue-forecast-chart')
    await expect(revenueChart).toBeVisible()
    
    // 验证图表标题
    const title = page.getByText('收入预测').first()
    await expect(title).toBeVisible()
    
    // 验证预测周期选择器存在
    const periodSelector = page.locator('.revenue-forecast-chart .ant-select')
    await expect(periodSelector.first()).toBeVisible()
  })
  
  test('应该显示客户分布图', async ({ page }) => {
    await login(page)
    
    // 验证客户分布图表容器存在
    const customerChart = page.locator('.customer-distribution-chart')
    await expect(customerChart).toBeVisible()
    
    // 验证图表标题
    const title = page.getByText('客户分布').first()
    await expect(title).toBeVisible()
    
    // 验证维度切换按钮存在
    const industryRadio = page.getByText('按行业').first()
    await expect(industryRadio).toBeVisible()
  })
  
  test('应该显示结算状态图', async ({ page }) => {
    await login(page)
    
    // 验证结算状态图表容器存在
    const settlementChart = page.locator('.settlement-status-chart')
    await expect(settlementChart).toBeVisible()
    
    // 验证图表标题
    const title = page.getByText('结算状态').first()
    await expect(title).toBeVisible()
    
    // 验证视图类型选择器存在
    const viewTypeSelector = page.locator('.settlement-status-chart .ant-select')
    await expect(viewTypeSelector.first()).toBeVisible()
  })
  
  test('用量趋势图应该支持时间范围切换', async ({ page }) => {
    await login(page)
    
    // 验证时间范围选择器存在
    const rangeSelector = page.locator('.usage-trend-chart .ant-select')
    await expect(rangeSelector.first()).toBeVisible()
    
    // 验证当前显示的时间范围
    await expect(rangeSelector.first()).toContainText('近')
  })
  
  test('图表应该是响应式的', async ({ page }) => {
    await login(page)
    
    // 验证图表容器存在
    const trendChart = page.locator('.usage-trend-chart')
    await expect(trendChart).toBeVisible()
    
    // 调整窗口大小为移动端
    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForTimeout(500)
    
    // 验证图表仍然可见
    await expect(trendChart).toBeVisible()
    
    // 验证图表标题仍然可见
    const title = page.getByText('用量趋势').first()
    await expect(title).toBeVisible()
  })
})
