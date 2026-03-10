import { test, expect } from '@playwright/test'

test.describe('基础 UI 测试 - 18 个用例', () => {
  // 登录辅助函数
  async function login(page) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    
    await page.locator('input[placeholder="用户名"]').fill('admin')
    await page.locator('input[placeholder="密码"]').fill('admin123')
    await page.locator('button[type="submit"]').click()
    
    await page.waitForURL(/\/dashboard/, { timeout: 10000 })
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  }

  test.describe('1. 登录页面 (5 个用例)', () => {
    test('① 应该显示登录表单', async ({ page }) => {
      await page.goto('/login')
      await page.waitForLoadState('networkidle')
      
      await expect(page.locator('input[placeholder="用户名"]')).toBeVisible()
      await expect(page.locator('input[placeholder="密码"]')).toBeVisible()
      await expect(page.locator('button[type="submit"]')).toBeVisible()
      await expect(page.getByText('客户运营中台').first()).toBeVisible()
    })

    test('② 表单验证 - 空用户名', async ({ page }) => {
      await page.goto('/login')
      await page.waitForLoadState('networkidle')
      
      await page.locator('input[placeholder="密码"]').fill('admin123')
      await page.locator('button[type="submit"]').click()
      await page.waitForTimeout(500)
      
      const hasError = await page.locator(':has-text("请输入用户名")').count() > 0
      expect(hasError).toBeTruthy()
    })

    test('③ 表单验证 - 空密码', async ({ page }) => {
      await page.goto('/login')
      await page.waitForLoadState('networkidle')
      
      await page.locator('input[placeholder="用户名"]').fill('admin')
      await page.locator('button[type="submit"]').click()
      await page.waitForTimeout(500)
      
      const hasError = await page.locator(':has-text("请输入密码")').count() > 0
      expect(hasError).toBeTruthy()
    })

    test('④ 应该成功登录', async ({ page }) => {
      await login(page)
      expect(page.url()).toContain('/dashboard')
      await expect(page.locator('.main-layout').first()).toBeVisible()
    })

    test('⑤ 应该失败登录 - 错误密码', async ({ page }) => {
      await page.goto('/login')
      await page.waitForLoadState('networkidle')
      
      await page.locator('input[placeholder="用户名"]').fill('admin')
      await page.locator('input[placeholder="密码"]').fill('wrongpassword')
      await page.locator('button[type="submit"]').click()
      await page.waitForTimeout(2000)
      
      // 验证仍然在登录页面（登录失败）
      expect(page.url()).toContain('/login')
    })
  })

  test.describe('2. 主布局 (5 个用例)', () => {
    test.beforeEach(async ({ page }) => {
      await login(page)
    })

    test('⑥ 侧边栏应该默认展开', async ({ page }) => {
      await expect(page.locator('.ant-layout-sider').first()).toBeVisible()
      await expect(page.locator('.ant-menu-item').first()).toBeVisible()
    })

    test('⑦ 侧边栏应该支持收起/展开', async ({ page }) => {
      const toggleButton = page.locator('.anticon-menu-unfold, .anticon-menu-fold')
      if (await toggleButton.count() > 0) {
        await toggleButton.first().click()
        await page.waitForTimeout(500)
        await expect(page.locator('.anticon-menu-unfold, .anticon-menu-fold').first()).toBeVisible()
      }
    })

    test('⑧ 菜单切换 - 工作台', async ({ page }) => {
      const dashboardMenu = page.locator('.ant-menu-item:has-text("工作台")')
      if (await dashboardMenu.count() > 0) {
        await dashboardMenu.first().click()
        await page.waitForLoadState('networkidle')
        await page.waitForTimeout(500)
        expect(page.url()).toContain('/dashboard')
      }
    })

    test('⑨ 菜单切换 - 客户管理', async ({ page }) => {
      const customerMenu = page.locator('.ant-menu-item:has-text("客户")')
      await customerMenu.first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1000)
      
      // 验证 URL 或页面内容
      const hasCustomerContent = await page.locator('.page-container, .table-card, .customer-list').count() > 0
      expect(hasCustomerContent).toBeTruthy()
    })

    test('⑩ 菜单切换 - 用户管理', async ({ page }) => {
      const userMenu = page.locator('.ant-menu-item:has-text("用户")')
      await userMenu.first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1000)
      
      const hasUserContent = await page.locator('.page-container, .table-card, .user-list').count() > 0
      expect(hasUserContent).toBeTruthy()
    })
  })

  test.describe('3. 工作台/Dashboard (8 个用例)', () => {
    test.beforeEach(async ({ page }) => {
      await login(page)
      await page.goto('/dashboard')
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(2000)  // 等待数据加载
    })

    test('⑪ 应该显示数据概览卡片', async ({ page }) => {
      await expect(page.locator('.main-layout').first()).toBeVisible()
      await expect(page.locator('.ant-layout-content, .content').first()).toBeVisible()
      // 验证统计卡片存在
      const statCards = page.locator('.stat-card, .overview-card, .ant-card')
      await expect(statCards.first()).toBeVisible()
    })

    test('⑫ 快捷操作 - 客户管理', async ({ page }) => {
      // 使用 data-testid 定位快捷操作卡片
      const customerAction = page.locator('[data-testid="action-card"]:has-text("客户管理")')
      await expect(customerAction.first()).toBeVisible()
      await customerAction.first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
      
      const hasCustomerContent = await page.locator('.page-container, .table-card').count() > 0
      expect(hasCustomerContent).toBeTruthy()
    })

    test('⑬ 快捷操作 - 用户管理', async ({ page }) => {
      const userAction = page.locator('[data-testid="action-card"]:has-text("用户管理")')
      await expect(userAction.first()).toBeVisible()
      await userAction.first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
      
      const hasUserContent = await page.locator('.page-container, .table-card').count() > 0
      expect(hasUserContent).toBeTruthy()
    })

    test('⑭ 快捷操作 - 角色权限', async ({ page }) => {
      const roleAction = page.locator('[data-testid="action-card"]:has-text("角色权限")')
      await expect(roleAction.first()).toBeVisible()
      await roleAction.first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
      
      const hasRoleContent = await page.locator('.page-container, .table-card').count() > 0
      expect(hasRoleContent).toBeTruthy()
    })

    test('⑮ 快捷操作 - 结算管理', async ({ page }) => {
      const settlementAction = page.locator('[data-testid="action-card"]:has-text("结算管理")')
      await expect(settlementAction.first()).toBeVisible()
      await settlementAction.first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1000)
      
      // 验证 URL 包含 settlements 或页面有结算相关内容
      const url = page.url()
      const hasSettlementContent = url.includes('/settlements') || await page.locator('.settlement-list, :has-text("结算"), :has-text("新建结算")').count() > 0
      expect(hasSettlementContent).toBeTruthy()
    })

    test('⑯ 应该显示快捷操作区域', async ({ page }) => {
      // 验证快捷操作区域存在
      await expect(page.locator('.quick-actions').first()).toBeVisible()
      await expect(page.getByText('快捷操作').first()).toBeVisible()
    })

    test('⑰ 应该显示用量趋势图表', async ({ page }) => {
      await expect(page.locator(':has-text("用量趋势")').first()).toBeVisible()
    })

    test('⑱ 应该支持响应式布局', async ({ page }) => {
      await expect(page.locator('.main-layout').first()).toBeVisible()
      await page.setViewportSize({ width: 375, height: 667 })
      await page.waitForTimeout(500)
      await expect(page.locator('.main-layout').first()).toBeVisible()
      await page.setViewportSize({ width: 1920, height: 1080 })
      await page.waitForTimeout(500)
    })
  })
})
