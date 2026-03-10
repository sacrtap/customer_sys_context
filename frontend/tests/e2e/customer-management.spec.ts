import { test, expect, type Page } from '@playwright/test';

const TEST_CONFIG = {
  baseURL: 'http://127.0.0.1:5173',
  username: 'admin',
  password: 'admin123',
};

async function login(page: Page) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  
  await expect(page.locator('input[type="text"]')).toBeVisible({ timeout: 10000 });
  await page.locator('input[type="text"]').first().fill(TEST_CONFIG.username);
  await page.locator('input[type="password"]').fill(TEST_CONFIG.password);
  await page.locator('button[type="submit"]').first().click();
  
  await page.waitForURL(/dashboard|customers/, { timeout: 10000 });
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

test.describe('Customer Management UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('customer list page should display', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await expect(page.locator('.customer-list')).toBeVisible();
    await expect(page.locator('table')).toBeVisible();
    await expect(page.getByText('客户编码')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/customer-list-display.png' });
  });

  test('customer list should support search', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    const searchInput = page.getByPlaceholder('搜索客户名称/编码/联系人');
    await expect(searchInput).toBeVisible();
    await searchInput.fill('测试');
    await page.waitForTimeout(500);
    
    await expect(page.locator('table')).toBeVisible();
    await page.screenshot({ path: 'test-results/customer-search.png' });
  });

  test('customer list should support reset', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    const searchInput = page.getByPlaceholder('搜索客户名称/编码/联系人');
    await searchInput.fill('测试关键词');
    await page.getByRole('button', { name: '重置' }).click();
    
    await expect(searchInput).toHaveValue('');
    await page.screenshot({ path: 'test-results/customer-reset.png' });
  });

  test('customer list should show pagination', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    const pagination = page.locator('.ant-pagination');
    await expect(pagination).toBeVisible();
    await page.screenshot({ path: 'test-results/customer-pagination.png' });
  });

  test('customer list should show import button', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    await expect(page.getByRole('button', { name: '导入客户' })).toBeVisible();
    await page.getByRole('button', { name: '导入客户' }).click();
    await expect(page.getByText('点击或拖拽文件到此处上传')).toBeVisible({ timeout: 5000 });
    
    await page.screenshot({ path: 'test-results/customer-import-dialog.png' });
    await page.keyboard.press('Escape');
  });

  test('customer list should show add button', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    await expect(page.getByRole('button', { name: '新建客户' })).toBeVisible();
    await page.getByRole('button', { name: '新建客户' }).click();
    await expect(page.locator('.ant-message')).toBeVisible({ timeout: 3000 });
    
    await page.screenshot({ path: 'test-results/customer-add-button.png' });
  });

  test('customer detail page should display structure', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const customerLinks = page.locator('.customer-link');
    const count = await customerLinks.count();
    
    if (count > 0) {
      await customerLinks.first().click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      await expect(page.locator('.customer-detail')).toBeVisible();
      await expect(page.getByText('基本信息')).toBeVisible();
      await expect(page.getByText('用量趋势')).toBeVisible();
      
      await page.screenshot({ path: 'test-results/customer-detail-display.png' });
    } else {
      test.skip();
    }
  });

  test('customer detail should show basic info', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const customerLinks = page.locator('.customer-link');
    if (await customerLinks.count() > 0) {
      await customerLinks.first().click();
      await page.waitForLoadState('networkidle');
      
      await expect(page.getByText('客户编码')).toBeVisible();
      await expect(page.getByText('客户名称')).toBeVisible();
      await expect(page.getByText('行业')).toBeVisible();
      
      await page.screenshot({ path: 'test-results/customer-detail-info.png' });
    } else {
      test.skip();
    }
  });

  test('customer detail should support back to list', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const customerLinks = page.locator('.customer-link');
    if (await customerLinks.count() > 0) {
      await customerLinks.first().click();
      await page.waitForLoadState('networkidle');
      
      await page.getByRole('button', { name: '返回列表' }).click();
      await expect(page).toHaveURL(/\/customers/, { timeout: 5000 });
      
      await page.screenshot({ path: 'test-results/customer-detail-back.png' });
    } else {
      test.skip();
    }
  });

  test('import function should show dialog', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    await page.getByRole('button', { name: '导入客户' }).click();
    
    await expect(page.getByText('导入客户')).toBeVisible();
    await expect(page.getByText('点击或拖拽文件到此处上传')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/import-dialog-display.png' });
  });

  test('import function should show upload area', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: '导入客户' }).click();
    
    const uploadArea = page.locator('.ant-upload-drag');
    await expect(uploadArea).toBeVisible();
    
    await page.screenshot({ path: 'test-results/import-drag-area.png' });
  });

  test('responsive should work on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('.customer-list')).toBeVisible();
    await expect(page.locator('.ant-table-content')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/responsive-mobile.png' });
  });

  test('responsive should work on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('.customer-list')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/responsive-tablet.png' });
  });
});
