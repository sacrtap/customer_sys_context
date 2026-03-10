import { test, expect } from '@playwright/test'

test.describe('用户管理和角色权限 - 简化测试', () => {
  // 使用全局认证设置
  test.use({
    storageState: async ({ browser }, use) => {
      // 先登录获取 token
      const context = await browser.newContext()
      const page = await context.newPage()
      
      await page.goto('/login')
      await page.waitForLoadState('networkidle')
      await page.locator('input[placeholder="用户名"]').fill('admin')
      await page.locator('input[placeholder="密码"]').fill('admin123')
      await page.locator('button[type="submit"]').click()
      await page.waitForTimeout(3000)
      
      // 保存 storage state
      const state = await context.storageState()
      await use(state)
      await context.close()
    },
  })

  test.describe('5. 用户管理', () => {
    test('用户列表页面加载', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(1000)
      
      // 验证表格存在
      const table = page.locator('[data-testid="user-table"]')
      await expect(table).toBeVisible()
    })

    test('用户列表数据显示', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      // 验证表头
      await expect(page.getByText('用户名')).toBeVisible()
      await expect(page.getByText('邮箱')).toBeVisible()
      await expect(page.getByText('角色')).toBeVisible()
      await expect(page.getByText('状态')).toBeVisible()
    })

    test('用户搜索功能', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      const searchInput = page.locator('input[placeholder="搜索用户名/姓名/邮箱"]')
      await expect(searchInput).toBeVisible()
    })

    test('用户分页功能', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      const pagination = page.locator('.ant-pagination')
      await expect(pagination).toBeVisible()
    })

    test('新建用户按钮', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      const addBtn = page.locator('[data-testid="add-user-btn"]')
      await expect(addBtn).toBeVisible()
      await expect(addBtn).toContainText('新建用户')
    })

    test('新建用户表单', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      await page.locator('[data-testid="add-user-btn"]').click()
      await page.waitForTimeout(500)
      
      const modal = page.locator('.ant-modal:has-text("新建用户")')
      await expect(modal).toBeVisible()
    })

    test('编辑用户按钮', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      const table = page.locator('[data-testid="user-table"]')
      const editBtn = table.locator('tbody tr').first().locator('a:has-text("编辑")')
      await expect(editBtn.first()).toBeVisible()
    })

    test('删除用户按钮', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      const table = page.locator('[data-testid="user-table"]')
      const deleteBtn = table.locator('tbody tr').first().locator('a:has-text("删除")')
      await expect(deleteBtn.first()).toBeVisible()
    })

    test('删除确认对话框', async ({ page }) => {
      await page.goto('/users')
      await page.waitForLoadState('networkidle')
      
      const table = page.locator('[data-testid="user-table"]')
      await table.locator('tbody tr').first().locator('a:has-text("删除")').first().click()
      await page.waitForTimeout(500)
      
      const modal = page.locator('.ant-modal:has-text("确认删除")')
      await expect(modal).toBeVisible()
    })
  })

  test.describe('6. 角色权限', () => {
    test('角色列表页面加载', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      const table = page.locator('[data-testid="role-table"]')
      await expect(table).toBeVisible()
    })

    test('角色列表数据显示', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      await expect(page.getByText('角色名称')).toBeVisible()
      await expect(page.getByText('描述')).toBeVisible()
      await expect(page.getByText('权限')).toBeVisible()
    })

    test('新建角色按钮', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      const addBtn = page.locator('button:has-text("新建角色")')
      await expect(addBtn).toBeVisible()
    })

    test('新建角色表单', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      await page.locator('button:has-text("新建角色")').click()
      await page.waitForTimeout(500)
      
      const modal = page.locator('.ant-modal:has-text("新建角色")')
      await expect(modal).toBeVisible()
    })

    test('角色权限分配', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      await page.locator('button:has-text("新建角色")').click()
      await page.waitForTimeout(500)
      
      const permissionSelect = page.locator('.ant-select:has-text("选择权限")')
      await expect(permissionSelect.first()).toBeVisible()
    })

    test('编辑角色按钮', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      const table = page.locator('[data-testid="role-table"]')
      const editBtn = table.locator('tbody tr').first().locator('a:has-text("编辑")')
      await expect(editBtn.first()).toBeVisible()
    })

    test('删除角色按钮', async ({ page }) => {
      await page.goto('/roles')
      await page.waitForLoadState('networkidle')
      
      const table = page.locator('[data-testid="role-table"]')
      const deleteBtn = table.locator('tbody tr').first().locator('a:has-text("删除")')
      await expect(deleteBtn.first()).toBeVisible()
    })
  })
})
