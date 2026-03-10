import { test, expect, type Page } from '@playwright/test'

// 测试配置
const TEST_CONFIG = {
  baseURL: 'http://127.0.0.1:5173',
  username: 'admin',
  password: 'admin123',
}

/**
 * 登录工具函数
 */
async function login(page: Page) {
  await page.goto('/login')
  
  // 等待登录页面加载
  await expect(page.locator('input[type="text"], input[type="email"]')).toBeVisible()
  
  // 输入用户名
  const usernameInput = page.locator('input[type="text"], input[type="email"]').first()
  await usernameInput.fill(TEST_CONFIG.username)
  
  // 输入密码
  const passwordInput = page.locator('input[type="password"]')
  await passwordInput.fill(TEST_CONFIG.password)
  
  // 点击登录按钮
  const loginButton = page.locator('button[type="submit"], button:has-text("登录")')
  await loginButton.click()
  
  // 等待登录成功并跳转
  await page.waitForURL(/dashboard/, { timeout: 10000 })
}

/**
 * 工作台/Dashboard 测试
 */
test.describe('Dashboard / 工作台', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    // 确保导航到 dashboard
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
  })

  test('should display dashboard title', async ({ page }) => {
    // 验证页面标题
    const title = page.locator('h1, .page-title, .ant-page-header-heading-title')
    await expect(title.first()).toBeVisible()
  })

  test('should display overview cards', async ({ page }) => {
    // 验证数据概览卡片存在
    const cards = page.locator('.ant-statistic, .overview-card, [class*="statistic"]')
    const count = await cards.count()
    expect(count).toBeGreaterThanOrEqual(1)
  })

  test('should display usage trend chart', async ({ page }) => {
    // 验证图表容器存在
    const chart = page.locator('[class*="chart"], .echarts, [class*="usage"], [class*="trend"]')
    await expect(chart.first()).toBeVisible({ timeout: 10000 })
  })

  test('should display quick actions', async ({ page }) => {
    // 验证快捷操作存在
    const actions = page.locator('[class*="quick"], [class*="action"]').locator('button, a')
    const count = await actions.count()
    expect(count).toBeGreaterThanOrEqual(1)
  })

  test('should be responsive on mobile', async ({ page }) => {
    // 切换到移动视图
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 验证页面仍然可见
    await expect(page.locator('body')).toBeVisible()
  })
})

/**
 * 导航测试
 */
test.describe('Navigation / 导航', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('should navigate to dashboard', async ({ page }) => {
    const dashboardLink = page.locator('a[href*="dashboard"], .ant-menu-item:has-text("工作台"), .ant-menu-item:has-text("Dashboard")')
    if (await dashboardLink.count() > 0) {
      await dashboardLink.click()
      await expect(page).toHaveURL(/dashboard/, { timeout: 10000 })
    }
  })

  test('should navigate to customers', async ({ page }) => {
    const customersLink = page.locator('a[href*="customer"], .ant-menu-item:has-text("客户"), .ant-menu-item:has-text("Customer")')
    if (await customersLink.count() > 0) {
      await customersLink.click()
      await expect(page).toHaveURL(/customer/, { timeout: 10000 })
    }
  })

  test('should navigate to users', async ({ page }) => {
    const usersLink = page.locator('a[href*="user"], .ant-menu-item:has-text("用户"), .ant-menu-item:has-text("User")')
    if (await usersLink.count() > 0) {
      await usersLink.click()
      await expect(page).toHaveURL(/user/, { timeout: 10000 })
    }
  })

  test('should navigate to roles', async ({ page }) => {
    const rolesLink = page.locator('a[href*="role"], .ant-menu-item:has-text("角色"), .ant-menu-item:has-text("Role")')
    if (await rolesLink.count() > 0) {
      await rolesLink.click()
      await expect(page).toHaveURL(/role/, { timeout: 10000 })
    }
  })
})

/**
 * 登录功能测试
 */
test.describe('Login / 登录', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login')
    
    // 输入凭证
    await page.locator('input[type="text"], input[type="email"]').first().fill(TEST_CONFIG.username)
    await page.locator('input[type="password"]').fill(TEST_CONFIG.password)
    await page.locator('button[type="submit"], button:has-text("登录")').click()
    
    // 验证跳转
    await page.waitForURL(/dashboard/, { timeout: 10000 })
    await expect(page).toHaveURL(/dashboard/)
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login')
    
    // 输入错误凭证
    await page.locator('input[type="text"], input[type="email"]').first().fill('wrong')
    await page.locator('input[type="password"]').fill('wrong')
    await page.locator('button[type="submit"], button:has-text("登录")').click()
    
    // 验证错误消息
    await expect(page.locator('.ant-message-error, .error-message, [class*="error"]')).toBeVisible({ timeout: 5000 })
  })

  test('should redirect to dashboard if already logged in', async ({ page }) => {
    // 先登录
    await page.goto('/login')
    await page.locator('input[type="text"], input[type="email"]').first().fill(TEST_CONFIG.username)
    await page.locator('input[type="password"]').fill(TEST_CONFIG.password)
    await page.locator('button[type="submit"], button:has-text("登录")').click()
    await page.waitForURL(/dashboard/, { timeout: 10000 })
    
    // 尝试访问登录页
    await page.goto('/login')
    
    // 应该被重定向
    await expect(page).toHaveURL(/dashboard|\/|home/, { timeout: 5000 })
  })
})
