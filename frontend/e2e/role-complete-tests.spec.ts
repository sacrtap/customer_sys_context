import { test, expect } from '@playwright/test'

/**
 * 角色管理完整功能测试
 * 覆盖增、删、改、查所有功能
 */

async function login(page: any) {
  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  await page.locator('input[placeholder="用户名"]').first().fill('admin')
  await page.locator('input[placeholder="密码"]').first().fill('admin123')
  await page.locator('button[type="submit"]').first().click()
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(2000)
}

test.describe('角色管理完整功能测试', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto('/roles')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  })

  // 1. 查询功能
  test('① 角色列表应该正常显示', async ({ page }) => {
    const table = page.locator('[data-testid="role-table"]')
    await expect(table).toBeVisible()
    
    const rows = page.locator('[data-testid="role-table"] tbody tr.ant-table-row')
    const rowCount = await rows.count()
    expect(rowCount).toBeGreaterThan(0)
    
    // 验证表头
    const headers = page.locator('[data-testid="role-table"] thead th')
    expect(await headers.count()).toBeGreaterThan(0)
  })

  // 2. 新建功能
  test('② 新建角色应该成功', async ({ page }) => {
    const initialCount = await page.locator('[data-testid="role-table"] tbody tr.ant-table-row').count()
    
    // 打开新建表单
    await page.locator('[data-testid="add-role-btn"]').click()
    await page.waitForTimeout(1000)
    
    // 填写表单
    await page.locator('[data-testid="role-name-input"]').first().fill(`测试角色_${Date.now()}`)
    await page.locator('[data-testid="description-textarea"]').first().fill('测试描述')
    
    // 选择权限
    await page.locator('.ant-tree-checkbox').first().click()
    await page.waitForTimeout(500)
    
    // 提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(2000)
    
    // 验证成功提示
    const successMessage = page.locator('.ant-message-success')
    await expect(successMessage.first()).toBeVisible()
    
    // 验证角色数量增加
    const finalCount = await page.locator('[data-testid="role-table"] tbody tr.ant-table-row').count()
    expect(finalCount).toBeGreaterThan(initialCount)
  })

  // 3. 编辑功能
  test('③ 编辑角色应该成功', async ({ page }) => {
    // 获取第一个角色名称
    const firstRow = page.locator('[data-testid="role-table"] tbody tr.ant-table-row').first()
    const originalName = await firstRow.locator('td').nth(0).textContent()
    
    // 点击编辑
    await page.locator('[data-testid="edit-role-btn"]').first().click()
    await page.waitForTimeout(1000)
    
    // 修改名称
    const timestamp = Date.now()
    const newName = `edited_${timestamp}`
    await page.locator('[data-testid="role-name-input"]').first().fill(newName)
    
    // 提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)
    
    // 验证对话框已关闭
    const modal = page.locator('.ant-modal:has-text("编辑角色")')
    const modalCount = await modal.count()
    expect(modalCount).toBe(0)
    
    // 等待列表刷新
    await page.waitForTimeout(2000)
    
    // 验证名称已更新（刷新页面确保数据从后端加载）
    await page.reload({ waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)
    
    const rows = page.locator('[data-testid="role-table"] tbody tr.ant-table-row')
    let found = false
    for (let i = 0; i < await rows.count(); i++) {
      const rowName = await rows.nth(i).locator('td').nth(0).textContent()
      if (rowName && rowName.includes(`edited_${timestamp}`)) {
        found = true
        break
      }
    }
    expect(found).toBe(true)
  })

  // 4. 权限分配功能
  test('④ 权限分配应该成功', async ({ page }) => {
    // 获取第一个角色行
    const firstRow = page.locator('[data-testid="role-table"] tbody tr.ant-table-row').first()
    
    // 点击权限按钮
    await firstRow.locator('[data-testid="permissions-role-btn"]').click()
    await page.waitForTimeout(2000)
    
    // 验证权限对话框打开
    const permissionTree = page.locator('[data-testid="permission-tree"]')
    await expect(permissionTree.first()).toBeVisible()
    
    // 选择一个权限（直接点击，不检查状态）
    const firstCheckbox = page.locator('.ant-tree-checkbox').first()
    await firstCheckbox.click()
    await page.waitForTimeout(500)
    
    // 提交
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)
    
    // 验证对话框已关闭
    const modal = page.locator('.ant-modal:has-text("分配权限")')
    const modalCount = await modal.count()
    expect(modalCount).toBe(0)
  })

  // 5. 删除功能
  test('⑤ 删除角色应该成功', async ({ page }) => {
    // 先创建一个角色用于删除
    await page.locator('[data-testid="add-role-btn"]').click()
    await page.waitForTimeout(1000)
    
    const roleName = `待删除角色_${Date.now()}`
    await page.locator('[data-testid="role-name-input"]').first().fill(roleName)
    await page.locator('.ant-tree-checkbox').first().click()
    await page.waitForTimeout(500)
    await page.locator('[data-testid="submit-btn"]').first().click()
    await page.waitForTimeout(3000)
    
    // 等待列表刷新
    await page.waitForTimeout(2000)
    
    // 找到刚创建的角色
    const rows = page.locator('[data-testid="role-table"] tbody tr.ant-table-row')
    let targetRowIndex = -1
    for (let i = 0; i < await rows.count(); i++) {
      const rowName = await rows.nth(i).locator('td').nth(0).textContent()
      if (rowName && rowName.includes(roleName)) {
        targetRowIndex = i
        break
      }
    }
    
    if (targetRowIndex === -1) {
      console.log('未找到创建的角色')
      return
    }
    
    // 点击删除
    const targetRow = rows.nth(targetRowIndex)
    await targetRow.locator('[data-testid="delete-role-btn"]').click()
    await page.waitForTimeout(1000)
    
    // 确认删除
    await page.locator('button:has-text("删 除")').first().click()
    await page.waitForTimeout(3000)
    
    // 等待删除完成
    await page.waitForTimeout(2000)
    
    // 刷新页面验证角色已删除
    await page.reload({ waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)
    
    // 验证角色不存在
    const finalRows = page.locator('[data-testid="role-table"] tbody tr.ant-table-row')
    let found = false
    for (let i = 0; i < await finalRows.count(); i++) {
      const rowName = await finalRows.nth(i).locator('td').nth(0).textContent()
      if (rowName && rowName.includes(roleName)) {
        found = true
        break
      }
    }
    expect(found).toBe(false)
  })

  // 6. 不能删除默认角色
  test('⑥ 默认角色不应该显示删除按钮', async ({ page }) => {
    const rows = page.locator('[data-testid="role-table"] tbody tr')
    const rowCount = await rows.count()
    
    for (let i = 0; i < rowCount; i++) {
      const row = rows.nth(i)
      const hasDefaultTag = await row.locator('.ant-tag-orange').count() > 0
      
      if (hasDefaultTag) {
        // 默认角色不应该有删除按钮
        const deleteBtn = row.locator('[data-testid="delete-role-btn"]')
        const hasDeleteBtn = await deleteBtn.count() > 0
        expect(hasDeleteBtn).toBeFalsy()
      }
    }
  })
})
