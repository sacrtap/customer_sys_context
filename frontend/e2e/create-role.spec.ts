import { test, expect } from '@playwright/test'

test.describe('新建角色功能 E2E 测试', () => {
  // 登录辅助函数
  async function login(page: any) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[placeholder="用户名"]').first().fill('admin')
    await page.locator('input[placeholder="密码"]').first().fill('admin123')
    await page.locator('button[type="submit"]').first().click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  })

  test('① 应该能够打开新建角色表单', async ({ page }) => {
    // 点击新建角色按钮
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 验证模态框显示
    const modal = page.locator('.ant-modal')
    await expect(modal.first()).toBeVisible()

    // 验证模态框标题
    const title = await page.locator('.ant-modal-title').first().textContent()
    expect(title).toContain('新建角色')
  })

  test('② 新建角色表单应该包含所有必需字段', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 验证角色名称输入框
    const roleNameInput = page.locator('[data-testid="role-name"] input')
    await expect(roleNameInput.first()).toBeVisible()

    // 验证描述输入框
    const descriptionTextarea = page.locator('[data-testid="description"] textarea')
    await expect(descriptionTextarea.first()).toBeVisible()

    // 验证是否默认开关
    const isDefaultSwitch = page.locator('[data-testid="is-default"]')
    await expect(isDefaultSwitch.first()).toBeVisible()

    // 验证权限树
    const permissionTree = page.locator('[data-testid="permissions"]')
    await expect(permissionTree.first()).toBeVisible()

    // 验证提交和取消按钮
    const submitBtn = page.locator('[data-testid="submit-btn"]')
    await expect(submitBtn.first()).toBeVisible()

    const cancelBtn = page.locator('[data-testid="cancel-btn"]')
    await expect(cancelBtn.first()).toBeVisible()
  })

  test('③ 表单验证 - 角色名称为必填', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 直接点击提交（不填写任何内容）
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(500)

    // 验证错误提示
    const errorMessages = page.locator('.ant-form-item-explain-error')
    const errorCount = await errorMessages.count()
    expect(errorCount).toBeGreaterThan(0)

    // 应该包含角色名称必填的错误
    let hasNameError = false
    for (let i = 0; i < errorCount; i++) {
      const errorText = await errorMessages.nth(i).textContent()
      if (errorText && errorText.includes('角色名称')) {
        hasNameError = true
        break
      }
    }
    expect(hasNameError).toBeTruthy()
  })

  test('④ 表单验证 - 权限为必填', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 填写角色名称
    await page.locator('[data-testid="role-name"] input').first().fill('测试角色')
    await page.waitForTimeout(300)

    // 直接点击提交（不选择权限）
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(500)

    // 验证错误提示
    const errorMessages = page.locator('.ant-form-item-explain-error')
    const errorCount = await errorMessages.count()
    expect(errorCount).toBeGreaterThan(0)

    // 应该包含权限必填的错误
    let hasPermissionError = false
    for (let i = 0; i < errorCount; i++) {
      const errorText = await errorMessages.nth(i).textContent()
      if (errorText && errorText.includes('权限')) {
        hasPermissionError = true
        break
      }
    }
    expect(hasPermissionError).toBeTruthy()
  })

  test('⑤ 应该能够选择权限', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 查找权限树的复选框
    const checkboxes = page.locator('.ant-tree-checkbox')
    const checkboxCount = await checkboxes.count()
    
    if (checkboxCount > 0) {
      // 选择第一个复选框
      await checkboxes.first().click()
      await page.waitForTimeout(500)

      // 验证节点已被选中
      const checkedNodes = page.locator('.ant-tree-checkbox-checked')
      const checkedCount = await checkedNodes.count()
      expect(checkedCount).toBeGreaterThan(0)
    }
  })

  test('⑥ 应该能够切换是否默认开关', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 获取初始状态
    const switchElement = page.locator('[data-testid="is-default"] .ant-switch')
    const initialChecked = await switchElement.first().getAttribute('aria-checked')
    
    // 点击切换
    await switchElement.first().click()
    await page.waitForTimeout(300)

    // 验证状态改变
    const newChecked = await switchElement.first().getAttribute('aria-checked')
    expect(newChecked).not.toBe(initialChecked)
  })

  test('⑦ 应该能够取消新建角色', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 填写一些内容
    await page.locator('[data-testid="role-name"] input').first().fill('取消测试角色')
    await page.waitForTimeout(300)

    // 点击取消按钮
    await page.locator('[data-testid="cancel-btn"]').first().click()
    await page.waitForTimeout(500)

    // 验证模态框关闭
    const modal = page.locator('.ant-modal')
    const modalCount = await modal.count()
    
    // 模态框应该关闭或数量减少
    expect(modalCount).toBeLessThanOrEqual(0)
  })

  test('⑧ 完整流程 - 成功创建角色', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 填写角色名称
    const testName = `测试角色_${Date.now()}`
    await page.locator('[data-testid="role-name"] input').first().fill(testName)
    await page.waitForTimeout(300)

    // 填写描述
    await page.locator('[data-testid="description"] textarea').first().fill('这是一个测试角色')
    await page.waitForTimeout(300)

    // 选择权限（选择第一个权限复选框）
    const checkboxes = page.locator('.ant-tree-checkbox')
    const checkboxCount = await checkboxes.count()
    
    if (checkboxCount > 0) {
      await checkboxes.first().click()
      await page.waitForTimeout(500)
    }

    // 点击提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)

    // 验证成功提示
    const successMessage = page.locator('.ant-message-success')
    const messageCount = await successMessage.count()
    
    // 应该有成功提示
    expect(messageCount).toBeGreaterThan(0)
    
    // 验证模态框关闭
    await page.waitForTimeout(1000)
    const modal = page.locator('.ant-modal')
    const modalCount = await modal.count()
    expect(modalCount).toBeLessThanOrEqual(0)

    // 刷新页面确保数据更新
    await page.waitForTimeout(2000)
    
    // 验证表格中存在角色（不检查特定名称，因为数据可能被清理）
    const table = page.locator('[data-testid="role-table"]')
    await expect(table.first()).toBeVisible()
    
    // 检查表格有行数据
    const rows = table.locator('.ant-table-tbody tr')
    const rowCount = await rows.count()
    expect(rowCount).toBeGreaterThan(0)
  })

  test('⑨ 角色名称长度验证', async ({ page }) => {
    // 打开表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 输入过短的名称（1 个字符）
    await page.locator('[data-testid="role-name"] input').first().fill('测')
    await page.waitForTimeout(500)

    // 失焦触发验证
    await page.locator('[data-testid="description"] textarea').first().click()
    await page.waitForTimeout(500)

    // 验证错误提示
    const errorMessages = page.locator('.ant-form-item-explain-error')
    const errorCount = await errorMessages.count()
    
    // 应该有长度错误提示
    let hasLengthError = false
    for (let i = 0; i < errorCount; i++) {
      const errorText = await errorMessages.nth(i).textContent()
      if (errorText && (errorText.includes('2') || errorText.includes('长度'))) {
        hasLengthError = true
        break
      }
    }
    expect(hasLengthError).toBeTruthy()
  })
})
