import { test, expect } from '@playwright/test'

test.describe('客户表单 - 行业和等级字段', () => {
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').fill('admin')
    await page.locator('input[placeholder="密码"]').fill('admin123')
    await page.locator('button[type="submit"]').click()
    await page.waitForURL(/\/dashboard|\/customers/, { timeout: 10000 })
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  }

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForURL(/\/customers/, { timeout: 10000 })
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  })

  test('应该显示行业下拉选项', async ({ page }) => {
    // 点击新建客户按钮
    await page.locator('[data-testid="add-button"]').click()
    await page.waitForTimeout(500)
    
    // 点击行业选择器
    const industrySelect = page.locator('[data-testid="industry"] .ant-select-selector')
    await industrySelect.click()
    await page.waitForTimeout(300)
    
    // 验证下拉选项存在
    const dropdown = page.locator('.ant-select-dropdown')
    await expect(dropdown.first()).toBeVisible()
    
    // 验证选项数量（应该从 API 加载）
    const options = dropdown.locator('.ant-select-item-option')
    const optionCount = await options.count()
    expect(optionCount).toBeGreaterThan(0)
    
    // 验证选项内容（应该是真实数据，不是硬编码）
    const firstOption = options.first()
    const firstOptionText = await firstOption.textContent()
    expect(firstOptionText).toBeTruthy()
    expect(firstOptionText?.length).toBeGreaterThan(0)
  })

  test('应该显示客户等级下拉选项', async ({ page }) => {
    // 点击新建客户按钮
    await page.locator('[data-testid="add-button"]').click()
    await page.waitForTimeout(500)
    
    // 点击等级选择器
    const levelSelect = page.locator('[data-testid="customer-level"] .ant-select-selector')
    await levelSelect.click()
    await page.waitForTimeout(300)
    
    // 验证下拉选项存在
    const dropdown = page.locator('.ant-select-dropdown')
    await expect(dropdown.first()).toBeVisible()
    
    // 验证选项数量
    const options = dropdown.locator('.ant-select-item-option')
    const optionCount = await options.count()
    expect(optionCount).toBeGreaterThan(0)
  })

  test('新建客户应该可以选择行业和等级', async ({ page }) => {
    // 点击新建客户按钮
    await page.locator('[data-testid="add-button"]').click()
    await page.waitForTimeout(500)
    
    // 填写基本信息
    await page.locator('[data-testid="customer-code"] input').fill('TEST_API_001')
    await page.locator('[data-testid="customer-name"] input').fill('测试客户')
    
    // 选择行业
    const industrySelect = page.locator('[data-testid="industry"] .ant-select-selector')
    await industrySelect.click()
    await page.waitForTimeout(300)
    const industryOption = page.locator('.ant-select-item-option').first()
    await industryOption.click()
    await page.waitForTimeout(200)
    
    // 选择等级
    const levelSelect = page.locator('[data-testid="customer-level"] .ant-select-selector')
    await levelSelect.click()
    await page.waitForTimeout(300)
    const levelOptions = page.locator('.ant-select-item-option')
    const levelOption = levelOptions.first()
    await levelOption.click()
    await page.waitForTimeout(200)
    
    // 提交表单
    await page.locator('[data-testid="submit-btn"]').click()
    await page.waitForTimeout(1000)
    
    // 验证成功提示
    const successMessage = page.locator('.ant-message-success')
    await expect(successMessage.first()).toBeVisible()
  })
})
