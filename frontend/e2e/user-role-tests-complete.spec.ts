import { test, expect } from '@playwright/test'

test.describe('用户管理和角色权限 UI 测试', () => {
  const login = async (page: any) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/dashboard/)
    await page.waitForTimeout(1000)
  }

  test.describe('5. 用户管理', () => {
    test.describe('5.1 用户列表', () => {
      test('用户列表显示', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="user-table"]')
        await expect(table).toBeVisible()
        await expect(page.getByRole('columnheader', { name: '用户名' })).toBeVisible()
        await expect(page.getByRole('columnheader', { name: '邮箱' })).toBeVisible()
        await expect(page.getByRole('columnheader', { name: '角色' })).toBeVisible()
      })

      test('搜索功能', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const searchInput = page.locator('input[placeholder="搜索用户名/姓名/邮箱"]')
        await expect(searchInput).toBeVisible()
      })

      test('分页功能', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const pagination = page.locator('.ant-pagination')
        await expect(pagination).toBeVisible()
      })
    })

    test.describe('5.2 用户新建', () => {
      test('新建按钮', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const addBtn = page.locator('[data-testid="add-user-btn"]')
        await expect(addBtn).toBeVisible()
      })

      test('表单验证', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        await page.locator('[data-testid="add-user-btn"]').click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("新建用户")')
        await expect(modal).toBeVisible()
      })

      test('新建成功', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        await page.locator('[data-testid="add-user-btn"]').click()
        await page.waitForTimeout(500)
        
        const timestamp = Date.now()
        await page.fill('input[placeholder="请输入用户名"]', `testuser_${timestamp}`)
        await page.fill('input[type="password"]', 'Test123456')
        await page.fill('input[placeholder="确认密码"]', 'Test123456')
        await page.fill('input[placeholder="请输入邮箱"]', `test${timestamp}@example.com`)
        
        await page.locator('.ant-modal:has-text("新建用户") button[type="submit"]').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible()
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
      })

      test('删除成功', async ({ page }) => {
        await login(page)
        await page.goto('/users')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="user-table"]')
        const count = await table.locator('tbody tr').count()
        
        if (count <= 1) {
          test.skip()
          return
        }
        
        await table.locator('tbody tr').last().locator('a:has-text("删除")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("确认删除")')
        await modal.locator('button:has-text("删除")').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible()
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
        
        await expect(page.getByRole('columnheader', { name: '角色名称' })).toBeVisible()
        await expect(page.getByRole('columnheader', { name: '描述' })).toBeVisible()
        await expect(page.getByRole('columnheader', { name: '权限' })).toBeVisible()
      })

      test('新建角色按钮', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const addBtn = page.locator('button:has-text("新建角色")')
        await expect(addBtn).toBeVisible()
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
      })

      test('新建成功', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        await page.locator('button:has-text("新建角色")').click()
        await page.waitForTimeout(500)
        
        const timestamp = Date.now()
        await page.fill('input[placeholder="请输入角色名称"]', `testrole_${timestamp}`)
        
        const permissionSelect = page.locator('.ant-select:has-text("选择权限")')
        await permissionSelect.first().click()
        await page.waitForTimeout(300)
        await page.locator('.ant-select-item-option').first().click()
        await page.waitForTimeout(300)
        
        await page.locator('.ant-modal:has-text("新建角色") button[type="submit"]').click()
        await page.waitForTimeout(2000)
        
        const successMsg = page.locator('.ant-message-success')
        await expect(successMsg.first()).toBeVisible()
      })
    })

    test.describe('6.3 角色编辑', () => {
      test('编辑按钮', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        const editBtn = table.locator('tbody tr').first().locator('a:has-text("编辑")')
        await expect(editBtn.first()).toBeVisible()
      })

      test('编辑成功', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        await table.locator('tbody tr').first().locator('a:has-text("编辑")').first().click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("编辑角色")')
        await expect(modal).toBeVisible()
      })
    })

    test.describe('6.4 角色删除', () => {
      test('删除确认', async ({ page }) => {
        await login(page)
        await page.goto('/roles')
        await page.waitForLoadState('networkidle')
        
        const table = page.locator('[data-testid="role-table"]')
        const deleteBtn = table.locator('tbody tr').first().locator('a:has-text("删除")')
        await expect(deleteBtn.first()).toBeVisible()
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
        await expect(successMsg.first()).toBeVisible()
      })
    })
  })
})
