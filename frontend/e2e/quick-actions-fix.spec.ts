import { test, expect } from '@playwright/test'

test.describe('快捷操作组件修复验证', () => {
  // 登录辅助函数
  async function login(page) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    
    const inputs = page.locator('input')
    if (await inputs.count() >= 2) {
      await inputs.nth(0).fill('admin')
      await inputs.nth(1).fill('admin123')
      await page.locator('button').first().click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1000)
    }
  }

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  })

  test('快捷操作卡片应该存在且可点击 - 客户管理', async ({ page }) => {
    // 验证快捷操作卡片存在
    const actionCards = page.locator('[data-testid="action-card"]')
    await expect(actionCards).toHaveCount(4)
    
    // 验证第一个卡片（客户管理相关）可点击
    const firstCard = actionCards.first()
    await expect(firstCard).toBeVisible()
    await firstCard.click()
    
    // 验证跳转正确（应该跳转到客户页面）
    await expect(page).toHaveURL(/\/customers/)
  })

  test('快捷操作卡片应该存在且可点击 - 用户管理', async ({ page }) => {
    const actionCards = page.locator('[data-testid="action-card"]')
    
    // 点击第二个卡片
    await actionCards.nth(1).click()
    
    // 验证跳转到用户管理页面
    await expect(page).toHaveURL(/\/users/)
  })

  test('快捷操作卡片应该存在且可点击 - 角色权限', async ({ page }) => {
    const actionCards = page.locator('[data-testid="action-card"]')
    
    // 点击第三个卡片
    await actionCards.nth(2).click()
    
    // 验证跳转到角色权限页面
    await expect(page).toHaveURL(/\/roles/)
  })

  test('快捷操作卡片应该有 hover 效果', async ({ page }) => {
    const actionCards = page.locator('[data-testid="action-card"]')
    const firstCard = actionCards.first()
    
    // 获取初始样式
    const initialBox = await firstCard.boundingBox()
    expect(initialBox).toBeTruthy()
    
    // 悬停操作
    await firstCard.hover()
    
    // 验证 hover 效果（卡片应该上移）
    await expect(firstCard).toHaveCSS('transform', /matrix/)
  })
})
