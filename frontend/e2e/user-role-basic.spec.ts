import { test, expect } from '@playwright/test'

test.describe('用户管理和角色权限 UI 测试', () => {
  test.describe('5. 用户管理', () => {
    test.beforeEach(async ({ page }) => {
      // 直接访问用户列表页（假设已登录）
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(2000)
    })

    test.describe('5.1 用户列表', () => {
      test('用户列表显示', async ({ page }) => {
        const table = page.locator('[data-testid="user-table"]')
        await expect(table).toBeVisible()
        await expect(page.getByText('用户名')).toBeVisible()
        await expect(page.getByText('邮箱')).toBeVisible()
      })

      test('搜索功能', async ({ page }) => {
        const searchInput = page.locator('input[placeholder="搜索用户名/姓名/邮箱"]')
        await expect(searchInput).toBeVisible()
      })

      test('分页功能', async ({ page }) => {
        const pagination = page.locator('.ant-pagination')
        await expect(pagination).toBeVisible()
      })
    })

    test.describe('5.2 用户新建', () => {
      test('新建按钮', async ({ page }) => {
        const addBtn = page.locator('[data-testid="add-user-btn"]')
        await expect(addBtn).toBeVisible()
        await expect(addBtn).toContainText('新建用户')
      })

      test('表单验证', async ({ page }) => {
        await page.locator('[data-testid="add-user-btn"]').click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("新建用户")')
        await expect(modal).toBeVisible()
        await expect(page.locator('input[placeholder="请输入用户名"]')).toBeVisible()
      })
    })

    test.describe('5.3 用户编辑', () => {
      test('编辑按钮', async ({ page }) => {
        const table = page.locator('[data-testid="user-table"]')
        const editBtn = table.locator('tbody tr').first().locator('a:has-text("编辑")')
        await expect(editBtn.first()).toBeVisible()
      })
    })

    test.describe('5.4 用户删除', () => {
      test('删除确认按钮存在', async ({ page }) => {
        const table = page.locator('[data-testid="user-table"]')
        const deleteBtn = table.locator('tbody tr').first().locator('a:has-text("删除")')
        await expect(deleteBtn.first()).toBeVisible()
      })
    })
  })

  test.describe('6. 角色权限', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(2000)
    })

    test.describe('6.1 角色列表', () => {
      test('角色列表显示', async ({ page }) => {
        const table = page.locator('[data-testid="role-table"]')
        await expect(table).toBeVisible()
      })

      test('角色数据显示', async ({ page }) => {
        await expect(page.getByText('角色名称')).toBeVisible()
        await expect(page.getByText('描述')).toBeVisible()
      })

      test('新建角色按钮', async ({ page }) => {
        const addBtn = page.locator('button:has-text("新建角色")')
        await expect(addBtn).toBeVisible()
      })
    })

    test.describe('6.2 角色新建', () => {
      test('新建按钮', async ({ page }) => {
        await page.locator('button:has-text("新建角色")').click()
        await page.waitForTimeout(500)
        
        const modal = page.locator('.ant-modal:has-text("新建角色")')
        await expect(modal).toBeVisible()
      })

      test('权限分配', async ({ page }) => {
        await page.locator('button:has-text("新建角色")').click()
        await page.waitForTimeout(500)
        
        const permissionSelect = page.locator('.ant-select:has-text("选择权限")')
        await expect(permissionSelect.first()).toBeVisible()
      })
    })

    test.describe('6.3 角色编辑', () => {
      test('编辑按钮', async ({ page }) => {
        const table = page.locator('[data-testid="role-table"]')
        const editBtn = table.locator('tbody tr').first().locator('a:has-text("编辑")')
        await expect(editBtn.first()).toBeVisible()
      })
    })

    test.describe('6.4 角色删除', () => {
      test('删除按钮存在', async ({ page }) => {
        const table = page.locator('[data-testid="role-table"]')
        const deleteBtn = table.locator('tbody tr').first().locator('a:has-text("删除")')
        await expect(deleteBtn.first()).toBeVisible()
      })
    })
  })
})
