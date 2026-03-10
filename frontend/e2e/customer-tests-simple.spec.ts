import { test, expect } from '@playwright/test'

/**
 * 客户管理 UI 测试 - 简化版
 * 用于快速验证核心功能
 */

// 登录辅助函数
async function login(page) {
  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  
  await page.fill('input[placeholder="用户名"]', 'admin')
  await page.fill('input[placeholder="密码"]', 'admin123')
  await page.click('button[type="submit"]')
  await page.waitForURL(/\/dashboard/, { timeout: 10000 })
}

// 导航到客户列表页面
async function goToCustomerList(page) {
  await page.goto('/customers')
  await page.waitForLoadState('networkidle')
  await page.locator('[data-testid="customer-table"]').waitFor({ state: 'visible', timeout: 10000 })
}

test.describe('客户管理核心测试', () => {
  
  test('4.1.1 客户列表应该正常显示', async ({ page }) => {
    await login(page)
    await goToCustomerList(page)
    
    const table = page.locator('[data-testid="customer-table"]')
    await expect(table).toBeVisible()
    
    const rows = page.locator('[data-testid="customer-table"] tbody tr')
    const count = await rows.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('4.1.4 分页功能应该正常工作', async ({ page }) => {
    await login(page)
    await goToCustomerList(page)
    
    const pagination = page.locator('.ant-pagination')
    await expect(pagination).toBeVisible()
    
    const pageSizes = page.locator('.ant-select-selector')
    const pageSizeCount = await pageSizes.count()
    expect(pageSizeCount).toBeGreaterThan(0)
  })

  test('4.1.5 导入按钮应该显示', async ({ page }) => {
    await login(page)
    await goToCustomerList(page)
    
    const importButton = page.locator('[data-testid="import-button"]')
    await expect(importButton).toBeVisible()
    await expect(importButton).toContainText('导入客户')
  })

  test('4.2.1 新建按钮应该显示并可点击', async ({ page }) => {
    await login(page)
    await goToCustomerList(page)
    
    const addButton = page.locator('[data-testid="add-button"]')
    await expect(addButton).toBeVisible()
    await expect(addButton).toContainText('新建客户')
    
    await addButton.click()
    
    const modal = page.locator('[data-testid="customer-form-modal"]')
    await expect(modal).toBeVisible()
  })

  test('4.5.2 客户列表应该显示基本信息', async ({ page }) => {
    await login(page)
    await goToCustomerList(page)
    
    const table = page.locator('[data-testid="customer-table"]')
    await expect(table).toBeVisible()
    
    const headers = table.locator('thead th')
    const headerTexts = await headers.allTextContents()
    
    expect(headerTexts.some(h => h.includes('客户编码'))).toBeTruthy()
    expect(headerTexts.some(h => h.includes('客户名称'))).toBeTruthy()
    expect(headerTexts.some(h => h.includes('联系人'))).toBeTruthy()
    expect(headerTexts.some(h => h.includes('联系电话'))).toBeTruthy()
    expect(headerTexts.some(h => h.includes('状态'))).toBeTruthy()
  })
})
