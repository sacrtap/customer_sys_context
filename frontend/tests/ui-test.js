import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 测试配置
const BASE_URL = 'http://127.0.0.1:5173';
const TEST_USERNAME = 'admin';
const TEST_PASSWORD = 'admin123';

// 确保截图目录存在
const screenshotsDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

// 测试结果
const results = [];

async function runTests() {
  console.log('🚀 开始执行 UI 自动化测试...\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // ==================== 登录页面测试 ====================
    console.log('📋 登录页面测试\n');
    
    // 测试 1: 显示登录表单
    try {
      await page.goto(`${BASE_URL}/login`, { timeout: 10000 });
      await page.screenshot({ path: path.join(screenshotsDir, 'login-page.png') });
      
      await page.waitForSelector('input[placeholder="用户名"]', { timeout: 5000 });
      await page.waitForSelector('input[placeholder="密码"]', { timeout: 5000 });
      await page.waitForSelector('button[type="submit"]', { timeout: 5000 });
      
      const title = await page.locator('.login-title').textContent();
      if (!title || !title.includes('客户运营中台')) throw new Error('标题不正确');
      
      results.push({ name: '应该显示登录表单', status: 'PASS', screenshot: 'login-page.png' });
      console.log('✅ 应该显示登录表单\n');
    } catch (error) {
      results.push({ name: '应该显示登录表单', status: 'FAIL', error: error.message });
      console.log(`❌ 应该显示登录表单 - ${error.message}\n`);
    }
    
    // 测试 2: 验证空用户名
    try {
      await page.goto(`${BASE_URL}/login`, { timeout: 10000 });
      await page.locator('input[placeholder="密码"]').fill('admin123');
      await page.locator('button[type="submit"]').click();
      await page.screenshot({ path: path.join(screenshotsDir, 'login-empty-username.png') });
      
      await page.waitForSelector('text=请输入用户名', { timeout: 5000 });
      
      results.push({ name: '应该验证空用户名', status: 'PASS', screenshot: 'login-empty-username.png' });
      console.log('✅ 应该验证空用户名\n');
    } catch (error) {
      results.push({ name: '应该验证空用户名', status: 'FAIL', error: error.message });
      console.log(`❌ 应该验证空用户名 - ${error.message}\n`);
    }
    
    // 测试 3: 验证空密码
    try {
      await page.goto(`${BASE_URL}/login`, { timeout: 10000 });
      await page.locator('input[placeholder="用户名"]').fill('admin');
      await page.locator('button[type="submit"]').click();
      await page.screenshot({ path: path.join(screenshotsDir, 'login-empty-password.png') });
      
      await page.waitForSelector('text=请输入密码', { timeout: 5000 });
      
      results.push({ name: '应该验证空密码', status: 'PASS', screenshot: 'login-empty-password.png' });
      console.log('✅ 应该验证空密码\n');
    } catch (error) {
      results.push({ name: '应该验证空密码', status: 'FAIL', error: error.message });
      console.log(`❌ 应该验证空密码 - ${error.message}\n`);
    }
    
    // 测试 4: 成功登录
    try {
      await page.goto(`${BASE_URL}/login`, { timeout: 10000 });
      await page.locator('input[placeholder="用户名"]').fill(TEST_USERNAME);
      await page.locator('input[placeholder="密码"]').fill(TEST_PASSWORD);
      await page.locator('button[type="submit"]').click();
      
      await page.waitForURL(/\/dashboard|\/customers|\/users/, { timeout: 10000 });
      await page.screenshot({ path: path.join(screenshotsDir, 'login-success.png') });
      
      results.push({ name: '应该成功登录', status: 'PASS', screenshot: 'login-success.png' });
      console.log('✅ 应该成功登录\n');
    } catch (error) {
      results.push({ name: '应该成功登录', status: 'FAIL', error: error.message });
      console.log(`❌ 应该成功登录 - ${error.message}\n`);
    }
    
    // 测试 5: 登录失败 - 重新打开登录页
    try {
      // 先退出登录（如果在主页面）
      try {
        await page.click('.user-info');
        await page.waitForTimeout(300);
        await page.click('text=退出登录');
        await page.waitForTimeout(1000);
      } catch (e) {
        // 忽略错误，直接跳转到登录页
      }
      
      await page.goto(`${BASE_URL}/login`, { timeout: 10000 });
      await page.locator('input[placeholder="用户名"]').fill('admin');
      await page.locator('input[placeholder="密码"]').fill('wrongpassword');
      await page.locator('button[type="submit"]').click();
      
      await page.waitForTimeout(3000);
      await page.screenshot({ path: path.join(screenshotsDir, 'login-failure.png') });
      
      const currentUrl = page.url();
      if (!currentUrl.includes('/login')) throw new Error('登录后应该停留在登录页');
      
      results.push({ name: '应该显示登录失败错误', status: 'PASS', screenshot: 'login-failure.png' });
      console.log('✅ 应该显示登录失败错误\n');
    } catch (error) {
      results.push({ name: '应该显示登录失败错误', status: 'FAIL', error: error.message });
      console.log(`❌ 应该显示登录失败错误 - ${error.message}\n`);
    }
    
    // ==================== 主布局测试 ====================
    console.log('📋 主布局测试\n');
    
    // 先登录
    await page.goto(`${BASE_URL}/login`, { timeout: 10000 });
    await page.locator('input[placeholder="用户名"]').fill(TEST_USERNAME);
    await page.locator('input[placeholder="密码"]').fill(TEST_PASSWORD);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL(/\/dashboard|\/customers|\/users/, { timeout: 10000 });
    
    // 测试 6: 显示侧边栏和菜单
    try {
      await page.screenshot({ path: path.join(screenshotsDir, 'main-layout-sidebar.png') });
      
      await page.waitForSelector('.sidebar', { timeout: 5000 });
      await page.waitForSelector('text=工作台', { timeout: 5000 });
      await page.waitForSelector('text=客户管理', { timeout: 5000 });
      await page.waitForSelector('text=用户管理', { timeout: 5000 });
      await page.waitForSelector('text=角色权限', { timeout: 5000 });
      
      results.push({ name: '应该显示侧边栏和菜单', status: 'PASS', screenshot: 'main-layout-sidebar.png' });
      console.log('✅ 应该显示侧边栏和菜单\n');
    } catch (error) {
      results.push({ name: '应该显示侧边栏和菜单', status: 'FAIL', error: error.message });
      console.log(`❌ 应该显示侧边栏和菜单 - ${error.message}\n`);
    }
    
    // 测试 7: 展开/收起侧边栏
    try {
      // 收起
      await page.locator('.trigger').first().click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'main-layout-collapsed.png') });
      
      const collapsedLogo = await page.locator('.logo span').first().textContent();
      if (collapsedLogo !== '运营') throw new Error('侧边栏收起后 logo 应为 "运营"');
      
      // 展开
      await page.locator('.trigger').first().click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'main-layout-expanded.png') });
      
      const expandedLogo = await page.locator('.logo span').first().textContent();
      if (expandedLogo !== '客户运营中台') throw new Error('侧边栏展开后 logo 应为 "客户运营中台"');
      
      results.push({ name: '应该可以展开/收起侧边栏', status: 'PASS', screenshot: 'main-layout-collapsed.png, main-layout-expanded.png' });
      console.log('✅ 应该可以展开/收起侧边栏\n');
    } catch (error) {
      results.push({ name: '应该可以展开/收起侧边栏', status: 'FAIL', error: error.message });
      console.log(`❌ 应该可以展开/收起侧边栏 - ${error.message}\n`);
    }
    
    // 测试 8: 切换菜单
    try {
      // 工作台
      await page.click('text=工作台');
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'menu-dashboard.png') });
      
      // 客户管理
      await page.click('text=客户管理');
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'menu-customers.png') });
      
      // 用户管理
      await page.click('text=用户管理');
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'menu-users.png') });
      
      // 角色权限
      await page.click('text=角色权限');
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'menu-roles.png') });
      
      results.push({ name: '应该可以切换菜单', status: 'PASS', screenshot: 'menu-*.png' });
      console.log('✅ 应该可以切换菜单\n');
    } catch (error) {
      results.push({ name: '应该可以切换菜单', status: 'FAIL', error: error.message });
      console.log(`❌ 应该可以切换菜单 - ${error.message}\n`);
    }
    
    // 测试 9: 显示用户信息
    try {
      await page.screenshot({ path: path.join(screenshotsDir, 'main-layout-user-info.png') });
      
      await page.waitForSelector('.username', { timeout: 5000 });
      const username = await page.locator('.username').textContent();
      if (username !== TEST_USERNAME) throw new Error('用户名不正确');
      
      results.push({ name: '应该显示用户信息', status: 'PASS', screenshot: 'main-layout-user-info.png' });
      console.log('✅ 应该显示用户信息\n');
    } catch (error) {
      results.push({ name: '应该显示用户信息', status: 'FAIL', error: error.message });
      console.log(`❌ 应该显示用户信息 - ${error.message}\n`);
    }
    
    // 测试 10: 退出登录
    try {
      await page.click('.user-info');
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(screenshotsDir, 'logout-dropdown.png') });
      
      await page.click('text=退出登录');
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(screenshotsDir, 'logout-completed.png') });
      
      await page.waitForURL(/\/login/, { timeout: 5000 });
      
      results.push({ name: '应该可以退出登录', status: 'PASS', screenshot: 'logout-*.png' });
      console.log('✅ 应该可以退出登录\n');
    } catch (error) {
      results.push({ name: '应该可以退出登录', status: 'FAIL', error: error.message });
      console.log(`❌ 应该可以退出登录 - ${error.message}\n`);
    }
    
  } finally {
    await browser.close();
  }
  
  // 生成报告
  generateReport();
}

function generateReport() {
  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  const passRate = ((passed / results.length) * 100).toFixed(1);
  
  const getScreenshotLink = (r) => {
    if (r.screenshot) {
      return `[查看](screenshots/${r.screenshot})`;
    }
    return '-';
  };
  
  const report = `# UI 自动化测试报告

## 测试概况

- **测试日期**: ${new Date().toLocaleString('zh-CN')}
- **前端地址**: ${BASE_URL}
- **后端地址**: http://127.0.0.1:8000
- **测试账号**: ${TEST_USERNAME} / ${TEST_PASSWORD}
- **浏览器**: Chromium (Headless)

## 测试结果统计

| 总计 | 通过 | 失败 | 通过率 |
|------|------|------|--------|
| ${results.length} | ${passed} | ${failed} | ${passRate}% |

## 详细测试结果

### 登录页面测试

| # | 测试用例 | 状态 | 截图 |
|---|----------|------|------|
${results.slice(0, 5).map((r, i) => `| ${i + 1} | ${r.name} | ${r.status === 'PASS' ? '✅' : '❌'} | ${getScreenshotLink(r)} |`).join('\n')}

### 主布局测试

| # | 测试用例 | 状态 | 截图 |
|---|----------|------|------|
${results.slice(5).map((r, i) => `| ${i + 6} | ${r.name} | ${r.status === 'PASS' ? '✅' : '❌'} | ${getScreenshotLink(r)} |`).join('\n')}

## 问题清单

${failed === 0 ? '✅ 所有测试通过，未发现问题' : '### 失败测试详情\n\n' + results.filter(r => r.status === 'FAIL').map(r => `- **${r.name}**: ${r.error}`).join('\n\n')}

## 测试截图

所有测试截图已保存至 \`tests/screenshots/\` 目录。

---

*生成时间：${new Date().toLocaleString('zh-CN')}*
`;

  const reportPath = path.join(__dirname, 'UI_TEST_REPORT.md');
  fs.writeFileSync(reportPath, report, 'utf-8');
  
  console.log('='.repeat(60));
  console.log('📊 测试结果汇总');
  console.log('='.repeat(60));
  console.log(`总计：${results.length} 个测试`);
  console.log(`通过：${passed} ✅`);
  console.log(`失败：${failed} ❌`);
  console.log(`通过率：${passRate}%`);
  console.log('='.repeat(60));
  console.log(`📄 测试报告已保存至：${reportPath}`);
  console.log(`📸 测试截图目录：${screenshotsDir}`);
}

// 运行测试
runTests().catch(console.error);
