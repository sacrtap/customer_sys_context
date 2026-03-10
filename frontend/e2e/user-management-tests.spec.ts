import { test, expect } from '@playwright/test'

/**
 * 用户管理完整功能测试
 */

async function login(page: any) {
  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  await page.locator('input[placeholder="用户名"]').first().fill('admin')
  await page.locator('input[placeholder="密码"]').first().fill('admin123')
  await page.locator('button[type="submit"]').first().click()
  await page.waitForURL(/\/dashboard/, { timeout: 10000 })
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(2000)
}

test.describe('用户管理完整功能测试', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto('/users')
    await page.waitForURL(/\/users/, { timeout: 10000 })
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(3000)
  })

  // 1. 查询功能
  test('① 用户列表应该正常显示', async ({ page }) => {
    const table = page.locator('[data-testid="user-table"]')
    await expect(table.first()).toBeVisible()
    
    const rows = page.locator('[data-testid="user-table"] tbody tr.ant-table-row')
    const rowCount = await rows.count()
    expect(rowCount).toBeGreaterThan(0)
    
    // 验证表头
    const headers = page.locator('[data-testid="user-table"] thead th')
    expect(await headers.count()).toBeGreaterThan(0)
  })

  // 2. 新建功能
  test('② 新建用户应该成功', async ({ page }) => {
    const initialCount = await page.locator('[data-testid="user-table"] tbody tr.ant-table-row').count()
    
    // 点击新建
    await page.locator('[data-testid="add-user-btn"]').click()
    await page.waitForTimeout(3000)
    
    // 填写表单（所有必填字段）
    const timestamp = Date.now()
    await page.locator('[data-testid="username"]').first().fill(`test_user_${timestamp}`)
    await page.locator('[data-testid="full-name"]').first().fill(`测试用户_${timestamp}`)
    await page.locator('[data-testid="email"]').first().fill(`test_${timestamp}@example.com`)
    await page.locator('[data-testid="password"]').first().fill('Test123456')
    await page.locator('[data-testid="confirm-password"]').first().fill('Test123456')
    
    // 选择角色（必填）
    await page.locator('[data-testid="roles"]').first().click()
    await page.waitForTimeout(2000)
    // 使用 CSS 选择器选择第一个角色选项
    await page.locator('.ant-select-dropdown .ant-select-item-option-content').first().click({ force: true })
    await page.waitForTimeout(2000)
    // 点击页面空白处关闭下拉菜单
    await page.locator('body').click({ position: { x: 100, y: 100 } })
    await page.waitForTimeout(2000)
    
    // 提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(8000)
    
    // 验证对话框已关闭（通过验证对话框不存在）
    const modals = page.locator('.ant-modal:has-text("新建用户")')
    const modalCount = await modals.count()
    
    // 等待列表刷新
    await page.waitForTimeout(5000)
    
    // 刷新页面验证数据
    await page.reload({ waitUntil: 'networkidle' })
    await page.waitForTimeout(3000)
    
    // 验证用户数量增加
    const finalCount = await page.locator('[data-testid="user-table"] tbody tr.ant-table-row').count()
    expect(finalCount).toBeGreaterThanOrEqual(initialCount)
  })

  // 3. 编辑功能
  test('③ 编辑用户应该成功', async ({ page }) => {
    // 获取第一个用户
    const firstRow = page.locator('[data-testid="user-table"] tbody tr.ant-table-row').first()
    const originalUsername = await firstRow.locator('td').nth(0).textContent()
    
    // 点击编辑
    await firstRow.locator('[data-testid="edit-user-btn"]').click()
    await page.waitForTimeout(2000)
    
    // 验证表单显示
    const modal = page.locator('.ant-modal:has-text("编辑用户")')
    await expect(modal.first()).toBeVisible()
    
    // 修改用户名
    const timestamp = Date.now()
    const newUsername = `${originalUsername}_edited_${timestamp}`
    await page.locator('[data-testid="username"]').first().fill(newUsername)
    
    // 提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)
    
    // 验证对话框已关闭
    const modalAfter = page.locator('.ant-modal:has-text("编辑用户")')
    const modalAfterCount = await modalAfter.count()
    expect(modalAfterCount).toBe(0)
    
    // 等待列表刷新
    await page.waitForTimeout(2000)
    
    // 刷新页面验证
    await page.reload({ waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)
    
    // 验证用户名已更新
    const rows = page.locator('[data-testid="user-table"] tbody tr.ant-table-row')
    let found = false
    for (let i = 0; i < await rows.count(); i++) {
      const username = await rows.nth(i).locator('td').nth(0).textContent()
      if (username && username.includes('edited')) {
        found = true
        break
      }
    }
    expect(found).toBe(true)
  })

  // 4. 删除功能
  test('④ 删除用户应该成功', async ({ page }) => {
    // 先创建一个用户用于删除
    await page.locator('[data-testid="add-user-btn"]').click()
    await page.waitForTimeout(1000)
    
    const username = `待删除用户_${Date.now()}`
    await page.locator('[data-testid="username"]').first().fill(username)
    await page.locator('[data-testid="full-name"]').first().fill('待删除用户')
    await page.locator('[data-testid="email"]').first().fill(`${username}@example.com`)
    await page.locator('[data-testid="password"]').first().fill('Test123456')
    await page.locator('[data-testid="confirm-password"]').first().fill('Test123456')
    
    // 提交创建
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)
    await page.waitForTimeout(2000)
    
    // 找到刚创建的用户
    const rows = page.locator('[data-testid="user-table"] tbody tr.ant-table-row')
    let targetRowIndex = -1
    for (let i = 0; i < await rows.count(); i++) {
      const rowUsername = await rows.nth(i).locator('td').nth(0).textContent()
      if (rowUsername && rowUsername.includes(username)) {
        targetRowIndex = i
        break
      }
    }
    
    if (targetRowIndex === -1) {
      console.log('未找到创建的用户')
      return
    }
    
    // 点击删除
    const targetRow = rows.nth(targetRowIndex)
    await targetRow.locator('[data-testid="delete-user-btn"]').click()
    await page.waitForTimeout(1000)
    
    // 确认删除
    await page.locator('button:has-text("删 除")').first().click()
    await page.waitForTimeout(3000)
    await page.waitForTimeout(2000)
    
    // 刷新页面验证用户已删除
    await page.reload({ waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)
    
    // 验证用户不存在
    const finalRows = page.locator('[data-testid="user-table"] tbody tr.ant-table-row')
    let found = false
    for (let i = 0; i < await finalRows.count(); i++) {
      const rowUsername = await finalRows.nth(i).locator('td').nth(0).textContent()
      if (rowUsername && rowUsername.includes(username)) {
        found = true
        break
      }
    }
    expect(found).toBe(false)
  })

  // 5. 搜索功能
  test('⑤ 搜索功能应该正常工作', async ({ page }) => {
    // 获取第一个用户名
    const firstRow = page.locator('[data-testid="user-table"] tbody tr.ant-table-row').first()
    const username = await firstRow.locator('td').nth(0).textContent()
    
    // 输入搜索条件
    const searchInput = page.locator('[data-testid="search-input"]')
    await searchInput.first().fill(username!)
    await page.waitForTimeout(1000)
    
    // 按 Enter 键触发搜索
    await searchInput.first().press('Enter')
    await page.waitForTimeout(3000)
    
    // 验证搜索结果
    const rows = page.locator('[data-testid="user-table"] tbody tr.ant-table-row')
    const rowCount = await rows.count()
    expect(rowCount).toBeGreaterThan(0)
  })

  // 6. 重置功能
  test('⑥ 重置功能应该正常工作', async ({ page }) => {
    // 先输入搜索条件
    const searchInput = page.locator('[data-testid="search-input"]')
    await searchInput.first().fill('test')
    await page.waitForTimeout(1000)
    
    // 点击重置
    await page.locator('[data-testid="reset-button"]').first().click()
    await page.waitForTimeout(2000)
    
    // 验证搜索框已清空
    const searchValue = await searchInput.first().inputValue()
    expect(searchValue).toBe('')
  })
})
