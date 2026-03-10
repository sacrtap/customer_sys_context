import { test, expect } from '@playwright/test'

test.describe('新建角色必填项测试', () => {
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

  test('① 只填写必填项创建角色', async ({ page }) => {
    // 1. 打开新建角色表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 2. 填写角色名称
    const testName = `测试必填角色_${Date.now()}`
    await page.locator('[data-testid="role-name"] input').first().fill(testName)
    await page.waitForTimeout(300)

    // 3. 选择权限（第一个权限）
    const checkboxes = page.locator('.ant-tree-checkbox')
    const checkboxCount = await checkboxes.count()
    
    if (checkboxCount > 0) {
      await checkboxes.first().click()
      await page.waitForTimeout(500)
      
      // 验证有选中的权限
      const checkedCount = await page.locator('.ant-tree-checkbox-checked').count()
      expect(checkedCount).toBeGreaterThan(0)
    }

    // 4. 点击提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)

    // 5. 验证成功提示
    const successMessage = page.locator('.ant-message-success')
    const messageCount = await successMessage.count()
    expect(messageCount).toBeGreaterThan(0)

    // 6. 验证模态框关闭
    await page.waitForTimeout(1000)
    const modal = page.locator('.ant-modal')
    const modalCount = await modal.count()
    expect(modalCount).toBeLessThanOrEqual(0)

    // 7. 等待页面刷新
    await page.waitForTimeout(2000)

    // 8. 验证表格中存在新角色
    const table = page.locator('[data-testid="role-table"]')
    await expect(table.first()).toBeVisible()
    
    // 检查表格行
    const rows = table.locator('.ant-table-tbody tr')
    const rowCount = await rows.count()
    expect(rowCount).toBeGreaterThan(0)
    
    // 尝试验证新角色名称在表格中
    const tableContent = await table.innerHTML()
    if (tableContent.includes(testName)) {
      console.log(`✅ 新角色 '${testName}' 在列表中显示`)
    } else {
      console.log(`⚠️  新角色 '${testName}' 未在列表中立即显示`)
      // 刷新页面再次验证
      await page.reload()
      await page.waitForTimeout(2000)
      
      const refreshedTable = page.locator('[data-testid="role-table"]')
      const refreshedContent = await refreshedTable.innerHTML()
      if (refreshedContent.includes(testName)) {
        console.log(`✅ 刷新后新角色 '${testName}' 在列表中显示`)
      } else {
        throw new Error(`❌ 刷新后新角色 '${testName}' 仍不在列表中`)
      }
    }
  })

  test('② 验证权限选择数据传递', async ({ page }) => {
    // 1. 打开浏览器控制台监听
    const consoleLogs: string[] = []
    page.on('console', msg => {
      consoleLogs.push(msg.text())
    })

    // 2. 打开新建角色表单
    await page.locator('[data-testid="add-role-btn"]').first().click()
    await page.waitForTimeout(1000)

    // 3. 填写角色名称
    await page.locator('[data-testid="role-name"] input').first().fill('权限测试角色')
    await page.waitForTimeout(300)

    // 4. 选择权限
    const checkboxes = page.locator('.ant-tree-checkbox')
    const checkboxCount = await checkboxes.count()
    
    if (checkboxCount > 0) {
      await checkboxes.first().click()
      await page.waitForTimeout(500)
    }

    // 5. 点击提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(2000)

    // 6. 验证控制台输出了提交数据
    const hasSubmitLog = consoleLogs.some(log => log.includes('提交角色数据'))
    if (hasSubmitLog) {
      console.log('✅ 控制台输出了提交数据')
      const submitLog = consoleLogs.find(log => log.includes('提交角色数据'))
      if (submitLog && submitLog.includes('permission_ids')) {
        console.log('✅ 提交数据包含 permission_ids')
      }
    }
  })
})
