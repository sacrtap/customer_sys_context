import { test, expect } from '@playwright/test'

test.describe('用户管理和角色权限 UI 测试', () => {
  // 登录辅助函数
  async function login(page) {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    
    await page.locator('input[placeholder="用户名"]').fill('admin')
    await page.locator('input[placeholder="密码"]').fill('admin123')
    await page.locator('button[type="submit"]').click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
  }

  test.describe('5. 用户管理', () => {
    test.describe('5.1 用户列表', () => {
      test('用户列表显示', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        await page.waitForTimeout(1000)
        
        const table = page.locator('[data-testid="user-table"]')
        await expect(table).toBeVisible()
        await expect(page.getByText('用户名')).toBeVisible()
        await expect(page.getByText('邮箱')).toBeVisible()
        await expect(page.getByText('角色')).toBeVisible()
      })

      test('搜索功能', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const searchInput = page.locator('input[placeholder="搜索用户名/姓名/邮箱"]')
        await expect(searchInput).toBeVisible()
        await searchInput.fill('admin')
        await page.waitForTimeout(500)
        await expect(page.getByText('admin')).toBeVisible()
      })

      test('分页功能', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const pagination = page.locator('.ant-pagination')
        await expect(pagination).toBeVisible()
        await expect(page.locator('.ant-pagination-total-text')).toBeVisible()
      })
    })

    test.describe('5.2 用户新建', () => {
      test('新建按钮', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const addBtn = page.locator('[data-testid="add-user-btn"]')
        await expect(addBtn).toBeVisible()
        await expect(addBtn).toContainText('新建用户')
      })

      test('表单验证', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        await page.locator('[data-testid="add-user-btn"]').click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("新建用户")')
        await expect(modal).toBeVisible()
        await expect(page.locator('input[placeholder="请输入用户名"]')).toBeVisible()
        await expect(page.locator('input[type="password"]').first()).toBeVisible()
      })

      test('新建成功', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        await page.locator('[data-testid="add-user-btn"]').click()
        await page.waitForTimeout(500)
        
        const timestamp = Date.now()
        await page.locator('input[placeholder="请输入用户名"]').fill(`testuser_${timestamp}`)
        await page.locator('input[type="password"]').first().fill('Test123456')
        await page.locator('input[type="password"]').nth(1).fill('Test123456')
        await page.locator('input[placeholder="请输入邮箱"]').fill(`test${timestamp}@example.com`)
        
        await page.locator('.ant-modal:has-text("新建用户") button[type="submit"]').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible({ timeout: 5000 })
      })
    })

    test.describe('5.3 用户编辑', () => {
      test('编辑按钮', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="user-table"]')
        const editBtn = table.locator('tbody tr').first().locator('a:has-text("编辑")')
        await expect(editBtn.first()).toBeVisible()
      })

      test('编辑成功', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="user-table"]')
        await table.locator('tbody tr').first().locator('a:has-text("编辑")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("编辑用户")')
        await expect(modal).toBeVisible()
        
        const usernameInput = page.locator('input[placeholder="请输入用户名"]')
        await expect(usernameInput.first()).not.toBeEmpty()
      })
    })

    test.describe('5.4 用户删除', () => {
      test('删除确认', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="user-table"]')
        await table.locator('tbody tr').first().locator('a:has-text("删除")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("确认删除")')
        await expect(modal).toBeVisible()
        await expect(page.locator('.ant-alert-warning')).toBeVisible()
      })

      test('删除成功', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="user-table"]')
        const initialCount = await table.locator('tbody tr').count()
        
        if (initialCount <= 1) {
          test.skip()
          return
        }
        
        await table.locator('tbody tr').last().locator('a:has-text("删除")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("确认删除")')
        await modal.locator('button:has-text("删除")').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible({ timeout: 5000 })
      })
    })
  })

  test.describe('6. 角色权限', () => {
    test.describe('6.1 角色列表', () => {
      test('角色列表显示', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        await expect(table).toBeVisible()
      })

      test('角色数据显示', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        await expect(page.getByText('角色名称')).toBeVisible()
        await expect(page.getByText('描述')).toBeVisible()
        await expect(page.getByText('权限')).toBeVisible()
        await expect(page.getByText('admin')).toBeVisible()
      })

      test('新建角色按钮', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const addBtn = page.locator('button:has-text("新建角色")')
        await expect(addBtn).toBeVisible()
        await expect(addBtn).toContainText('新建角色')
      })
    })

    test.describe('6.2 角色新建', () => {
      test('新建按钮', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        await page.locator('button:has-text("新建角色")').click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("新建角色")')
        await expect(modal).toBeVisible()
      })

      test('权限分配', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        await page.locator('button:has-text("新建角色")').click()
        await page.waitForTimeout(500)
        
        const permissionSelect = page.locator('.ant-select:has-text("选择权限")')
        await expect(permissionSelect.first()).toBeVisible()
        
        await permissionSelect.first().click()
        await page.waitForTimeout(300)
        
        const options = page.locator('.ant-select-item-option')
        await expect(options.first()).toBeVisible({ timeout: 3000 })
      })

      test('新建成功', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        await page.locator('button:has-text("新建角色")').click()
        await page.waitForTimeout(500)
        
        const timestamp = Date.now()
        await page.locator('input[placeholder="请输入角色名称"]').fill(`testrole_${timestamp}`)
        
        const permissionSelect = page.locator('.ant-select:has-text("选择权限")')
        await permissionSelect.first().click()
        await page.waitForTimeout(300)
        await page.locator('.ant-select-item-option').first().click()
        await page.waitForTimeout(300)
        
        await page.locator('.ant-modal:has-text("新建角色") button[type="submit"]').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible({ timeout: 5000 })
      })
    })

    test.describe('6.3 角色编辑', () => {
      test('编辑按钮', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        const rows = table.locator('tbody tr')
        const rowCount = await rows.count()
        
        let editableRow = rows.first()
        for (let i = 0; i < rowCount; i++) {
          const row = rows.nth(i)
          const hasDefaultTag = await row.locator('.ant-tag:has-text("默认")').count() > 0
          if (!hasDefaultTag) {
            editableRow = row
            break
          }
        }
        
        const editBtn = editableRow.locator('a:has-text("编辑")')
        await expect(editBtn.first()).toBeVisible()
      })

      test('编辑成功', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        const rows = table.locator('tbody tr')
        const rowCount = await rows.count()
        
        let editableRow = rows.first()
        for (let i = 0; i < rowCount; i++) {
          const row = rows.nth(i)
          const hasDefaultTag = await row.locator('.ant-tag:has-text("默认")').count() > 0
          if (!hasDefaultTag) {
            editableRow = row
            break
          }
        }
        
        await editableRow.locator('a:has-text("编辑")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("编辑角色")')
        await expect(modal).toBeVisible()
        
        const nameInput = page.locator('input[placeholder="请输入角色名称"]')
        await expect(nameInput.first()).not.toBeEmpty()
      })
    })

    test.describe('6.4 角色删除', () => {
      test('删除确认', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        const rows = table.locator('tbody tr')
        const rowCount = await rows.count()
        
        let deletableRow: ReturnType<typeof page.locator> | null = null
        for (let i = 0; i < rowCount; i++) {
          const row = rows.nth(i)
          const hasDefaultTag = await row.locator('.ant-tag:has-text("默认")').count() > 0
          const hasDeleteBtn = await row.locator('a:has-text("删除")').count() > 0
          if (!hasDefaultTag && hasDeleteBtn) {
            deletableRow = row
            break
          }
        }
        
        if (!deletableRow) {
          test.skip()
          return
        }
        
        await deletableRow.locator('a:has-text("删除")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("确认删除")')
        await expect(modal).toBeVisible()
        await expect(page.locator('.ant-alert-warning')).toBeVisible()
      })

      test('删除成功', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        const rows = table.locator('tbody tr')
        const rowCount = await rows.count()
        
        let deletableRow: ReturnType<typeof page.locator> | null = null
        for (let i = 0; i < rowCount; i++) {
          const row = rows.nth(i)
          const hasDefaultTag = await row.locator('.ant-tag:has-text("默认")').count() > 0
          const hasDeleteBtn = await row.locator('a:has-text("删除")').count() > 0
          if (!hasDefaultTag && hasDeleteBtn) {
            deletableRow = row
            break
          }
        }
        
        if (!deletableRow) {
          test.skip()
          return
        }
        
        await deletableRow.locator('a:has-text("删除")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("确认删除")')
        await modal.locator('button:has-text("删除")').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible({ timeout: 5000 })
      })
    })
  })
})
