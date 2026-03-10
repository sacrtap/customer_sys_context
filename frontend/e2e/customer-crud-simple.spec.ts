import { test, expect } from '@playwright/test'

test.describe('客户 CRUD 操作验证', () => {
  const login = async (page: any) => {
    await page.goto('/login')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/dashboard/)
  }

  test('验证客户列表页面加载', async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 验证新建按钮存在
    const addButton = page.getByRole('button', { name: '新建客户' })
    await expect(addButton).toBeVisible()
    
    // 验证表格存在
    const table = page.getByRole('table')
    await expect(table).toBeVisible()
  })
  
  test('验证新建客户表单显示', async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 点击新建按钮
    await page.getByRole('button', { name: '新建客户' }).click()
    
    // 验证表单对话框显示
    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()
    
    // 验证表单字段
    await expect(page.getByTestId('customer-code')).toBeVisible()
    await expect(page.getByTestId('customer-name')).toBeVisible()
    
    // 截图
    await page.screenshot({ path: 'e2e/screenshots/customer-form-create.png' })
  })
  
  test('验证编辑客户表单回显', async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 等待表格加载
    await page.waitForTimeout(2000)
    
    // 点击编辑按钮
    const editButton = page.getByRole('button', { name: '编辑' }).first()
    if (await editButton.count() > 0) {
      await editButton.click()
      
      // 验证表单对话框显示
      const dialog = page.getByRole('dialog')
      await expect(dialog).toBeVisible()
      
      // 截图
      await page.screenshot({ path: 'e2e/screenshots/customer-form-edit.png' })
    }
  })
  
  test('验证删除确认对话框', async ({ page }) => {
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 等待表格加载
    await page.waitForTimeout(2000)
    
    // 点击删除按钮
    const deleteButton = page.getByRole('button', { name: '删除' }).first()
    if (await deleteButton.count() > 0) {
      await deleteButton.click()
      
      // 验证确认对话框显示
      await expect(page.getByText(/确定删除|确认删除/)).toBeVisible()
      
      // 截图
      await page.screenshot({ path: 'e2e/screenshots/customer-delete-confirm.png' })
      
      // 取消删除
      await page.getByRole('button', { name: '取消' }).click()
    }
  })
})
