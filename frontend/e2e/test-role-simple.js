import { chromium } from 'playwright'

async function testRoleList() {
  console.log('🚀 开始测试角色列表页面...\n')
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox']
  })
  const context = await browser.newContext()
  const page = await context.newPage()
  
  try {
    // 1. 登录
    console.log('📝 步骤 1: 登录...')
    await page.goto('http://127.0.0.1:5173/login', { timeout: 10000 })
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/dashboard/, { timeout: 5000 })
    console.log('✅ 登录成功\n')
    
    // 2. 导航到角色列表
    console.log('📍 步骤 2: 导航到角色列表...')
    // 使用菜单项选择器（a-menu-item）
    await page.click('.ant-menu-item:has-text("角色权限")')
    await page.waitForTimeout(2000)
    
    // 3. 等待表格加载
    console.log('⏳ 等待表格加载...')
    await page.waitForTimeout(3000)
    
    // 4. 检查表格是否存在
    const table = await page.$('[data-testid="role-table"]')
    if (table) {
      console.log('✅ 表格元素找到\n')
    } else {
      console.log('❌ 表格元素未找到\n')
      // 截图调试
      await page.screenshot({ path: 'e2e/screenshots/role-list-debug.png' })
      console.log('📸 已保存调试截图\n')
    }
    
    // 5. 检查表格数据行
    const rows = await page.$$('[data-testid="role-table"] tbody tr')
    console.log(`📊 表格数据行数：${rows.length}`)
    
    if (rows.length > 0) {
      console.log('✅ 表格有数据\n')
    } else {
      console.log('⚠️  表格没有数据\n')
    }
    
    // 6. 检查新建按钮
    const addButton = await page.$('button:has-text("新建角色")')
    if (addButton) {
      console.log('✅ 新建角色按钮存在\n')
    } else {
      console.log('❌ 新建角色按钮未找到\n')
    }
    
    // 7. 检查错误信息
    const errorElements = await page.$$('.ant-alert-error, .ant-message-error')
    if (errorElements.length === 0) {
      console.log('✅ 没有错误提示\n')
    } else {
      console.log('❌ 发现错误提示\n')
    }
    
    // 保存成功截图
    await page.screenshot({ path: 'e2e/screenshots/role-list-success.png' })
    console.log('📸 已保存成功截图\n')
    
    console.log('✅ 测试完成\n')
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message)
    await page.screenshot({ path: 'e2e/screenshots/role-list-error.png' })
  } finally {
    await browser.close()
  }
}

testRoleList()
