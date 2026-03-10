import { test, expect } from '@playwright/test';

test.describe('用户管理和角色权限 UI 测试', () => {
  // 登录辅助函数
  async function login(page) {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const inputs = page.locator('input');
    if (await inputs.count() >= 2) {
      await inputs.nth(0).fill('admin');
      await inputs.nth(1).fill('admin123');
      await page.locator('button').first().click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
    }
  }

  test.describe('用户管理', () => {
    test('用户列表页面加载', async ({ page }) => {
      await login(page);
      
      // 导航到用户管理
      const userMenu = page.getByRole('menuitem', { name: /用户/i });
      if (await userMenu.count() > 0) {
        await userMenu.first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
      }
      
      // 验证表格存在
      const table = page.getByRole('table');
      await expect(table).toBeVisible({ timeout: 10000 });
    });

    test('新建用户按钮可点击', async ({ page }) => {
      await login(page);
      
      const userMenu = page.getByRole('menuitem', { name: /用户/i });
      if (await userMenu.count() > 0) {
        await userMenu.first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
      }
      
      // 查找新建按钮
      const buttons = page.getByRole('button');
      let createButton = null;
      for (let i = 0; i < await buttons.count(); i++) {
        const btn = buttons.nth(i);
        const text = await btn.textContent();
        if (text && text.includes('新建')) {
          createButton = btn;
          break;
        }
      }
      
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(500);
        
        // 验证弹窗出现
        const dialogs = page.getByRole('dialog');
        await expect(dialogs.first()).toBeVisible({ timeout: 5000 });
      }
    });

    test('删除确认弹窗', async ({ page }) => {
      await login(page);
      
      const userMenu = page.getByRole('menuitem', { name: /用户/i });
      if (await userMenu.count() > 0) {
        await userMenu.first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
      }
      
      await page.waitForSelector('table.ant-table', { timeout: 10000 });
      
      // 查找删除链接
      const links = page.getByRole('link');
      let deleteLink = null;
      for (let i = 0; i < await links.count(); i++) {
        const link = links.nth(i);
        const text = await link.textContent();
        if (text && text.includes('删除')) {
          deleteLink = link;
          break;
        }
      }
      
      if (deleteLink) {
        await deleteLink.click();
        await page.waitForTimeout(500);
        
        // 验证确认弹窗
        const dialogs = page.getByRole('dialog');
        await expect(dialogs.first()).toBeVisible({ timeout: 5000 });
        
        // 点击取消
        const cancelButtons = page.getByRole('button', { name: /取消/i });
        if (await cancelButtons.count() > 0) {
          await cancelButtons.first().click();
          await page.waitForTimeout(500);
        }
      }
    });
  });

  test.describe('角色权限', () => {
    test('角色列表页面加载', async ({ page }) => {
      await login(page);
      
      const roleMenu = page.getByRole('menuitem', { name: /角色/i });
      if (await roleMenu.count() > 0) {
        await roleMenu.first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
      }
      
      // 验证表格存在
      const table = page.getByRole('table');
      await expect(table).toBeVisible({ timeout: 10000 });
    });

    test('新建角色按钮可点击', async ({ page }) => {
      await login(page);
      
      const roleMenu = page.getByRole('menuitem', { name: /角色/i });
      if (await roleMenu.count() > 0) {
        await roleMenu.first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
      }
      
      // 查找新建按钮
      const buttons = page.getByRole('button');
      let createButton = null;
      for (let i = 0; i < await buttons.count(); i++) {
        const btn = buttons.nth(i);
        const text = await btn.textContent();
        if (text && text.includes('新建')) {
          createButton = btn;
          break;
        }
      }
      
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(500);
        
        // 验证弹窗出现
        const dialogs = page.getByRole('dialog');
        await expect(dialogs.first()).toBeVisible({ timeout: 5000 });
      }
    });

    test('权限分配按钮', async ({ page }) => {
      await login(page);
      
      const roleMenu = page.getByRole('menuitem', { name: /角色/i });
      if (await roleMenu.count() > 0) {
        await roleMenu.first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
      }
      
      await page.waitForSelector('table.ant-table', { timeout: 10000 });
      
      // 查找权限链接
      const links = page.getByRole('link');
      let permissionLink = null;
      for (let i = 0; i < await links.count(); i++) {
        const link = links.nth(i);
        const text = await link.textContent();
        if (text && text.includes('权限')) {
          permissionLink = link;
          break;
        }
      }
      
      if (permissionLink) {
        await permissionLink.click();
        await page.waitForTimeout(500);
        
        // 验证权限分配弹窗
        const dialogs = page.getByRole('dialog');
        await expect(dialogs.first()).toBeVisible({ timeout: 5000 });
        
        // 点击取消
        const cancelButtons = page.getByRole('button', { name: /取消/i });
        if (await cancelButtons.count() > 0) {
          await cancelButtons.first().click();
          await page.waitForTimeout(500);
        }
      }
    });
  });
});
