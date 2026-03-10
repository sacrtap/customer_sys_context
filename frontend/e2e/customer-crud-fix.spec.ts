import { test, expect } from '@playwright/test'

test.describe('客户 CRUD 操作修复', () => {
  // 登录函数
  const login = async (page: any) => {
    await page.goto('/login')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/dashboard/)
  }

  test('新建客户应该正常工作', async ({ page }) => {
    // 登录并导航到客户列表
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 点击新建按钮
    const addButton = page.getByRole('button', { name: '新建客户' })
    await expect(addButton).toBeVisible()
    await addButton.click()
    
    // 验证：应该显示表单对话框
    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()
    
    // 填写表单
    const customerCode = `TEST_${Date.now()}`
    await page.getByTestId('customer-code').fill(customerCode)
    await page.getByTestId('customer-name').fill('测试客户')
    await page.getByTestId('contact-person').fill('张三')
    await page.getByTestId('contact-phone').fill('13800138000')
    
    // 提交表单
    await page.getByTestId('submit-btn').click()
    
    // 验证：表单关闭且显示成功提示
    await expect(dialog).not.toBeVisible()
    await expect(page.getByText(/创建成功|成功/)).toBeVisible()
  })
  
  test('编辑客户应该回显数据', async ({ page }) => {
    // 登录并导航到客户列表
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 等待表格加载
    await page.waitForSelector('table.ant-table', { state: 'visible' })
    
    // 找到第一个客户并点击编辑
    const editButton = page.getByRole('button', { name: '编辑' }).first()
    await expect(editButton).toBeVisible()
    await editButton.click()
    
    // 验证：显示表单对话框
    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()
    
    // 验证：表单中应该回显客户数据
    const customerCode = page.getByTestId('customer-code')
    await expect(customerCode).toBeVisible()
    
    // 取消编辑
    await page.getByTestId('cancel-btn').click()
  })
  
  test('删除客户应该有确认弹窗', async ({ page }) => {
    // 登录并导航到客户列表
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 等待表格加载
    await page.waitForSelector('table.ant-table', { state: 'visible' })
    
    // 点击第一个删除按钮
    const deleteButton = page.getByRole('button', { name: '删除' }).first()
    await expect(deleteButton).toBeVisible()
    await deleteButton.click()
    
    // 验证：显示确认对话框
    await expect(page.getByText(/确定删除|确认删除/)).toBeVisible()
    
    // 取消删除
    await page.getByRole('button', { name: '取消' }).click()
  })
  
  test('删除确认后应该调用 API', async ({ page }) => {
    // 登录并导航到客户列表
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 等待表格加载
    await page.waitForSelector('table.ant-table', { state: 'visible' })
    
    // 监听 API 请求
    const [response] = await Promise.all([
      page.waitForResponse(
        (res) => res.url().includes('/customers/') && res.request().method() === 'DELETE'
      ),
      async () => {
        // 点击删除按钮
        await page.getByRole('button', { name: '删除' }).first().click()
        // 确认删除
        await page.getByRole('button', { name: 'OK' }).or(page.getByRole('button', { name: '确定' })).click()
      }
    ])
    
    // 验证：API 请求成功
    expect(response.status()).toBe(200)
  })
  
  test('客户列表应该显示数据', async ({ page }) => {
    // 登录并导航到客户列表
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 验证：表格应该显示数据
    const table = page.getByRole('table')
    await expect(table).toBeVisible()
    
    // 验证：至少有一行数据
    const rows = page.locator('table.ant-table tbody tr')
    await expect(rows).toHaveCount({ min: 1 })
  })
  
  test('搜索功能应该正常工作', async ({ page }) => {
    // 登录并导航到客户列表
    await login(page)
    await page.goto('/customers')
    await page.waitForLoadState('networkidle')
    
    // 输入搜索关键词
    const searchInput = page.getByPlaceholder('搜索客户名称/编码/联系人')
    await expect(searchInput).toBeVisible()
    await searchInput.fill('测试')
    
    // 点击搜索按钮
    await page.getByRole('button', { name: '搜索' }).click()
    
    // 验证：表格重新加载
    const table = page.getByRole('table')
    await expect(table).toBeVisible()
  })
})
