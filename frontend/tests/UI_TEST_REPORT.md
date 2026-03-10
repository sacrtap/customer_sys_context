# UI 自动化测试报告

## 测试概况

- **测试日期**: 2026/3/10 09:46:03
- **前端地址**: http://127.0.0.1:5173
- **后端地址**: http://127.0.0.1:8000
- **测试账号**: admin / admin123
- **浏览器**: Chromium (Headless)

## 测试结果统计

| 总计 | 通过 | 失败 | 通过率 |
|------|------|------|--------|
| 10 | 10 | 0 | 100.0% |

## 详细测试结果

### 登录页面测试

| # | 测试用例 | 状态 | 截图 |
|---|----------|------|------|
| 1 | 应该显示登录表单 | ✅ | [查看](screenshots/login-page.png) |
| 2 | 应该验证空用户名 | ✅ | [查看](screenshots/login-empty-username.png) |
| 3 | 应该验证空密码 | ✅ | [查看](screenshots/login-empty-password.png) |
| 4 | 应该成功登录 | ✅ | [查看](screenshots/login-success.png) |
| 5 | 应该显示登录失败错误 | ✅ | [查看](screenshots/login-failure.png) |

### 主布局测试

| # | 测试用例 | 状态 | 截图 |
|---|----------|------|------|
| 6 | 应该显示侧边栏和菜单 | ✅ | [查看](screenshots/main-layout-sidebar.png) |
| 7 | 应该可以展开/收起侧边栏 | ✅ | [查看](screenshots/main-layout-collapsed.png, main-layout-expanded.png) |
| 8 | 应该可以切换菜单 | ✅ | [查看](screenshots/menu-*.png) |
| 9 | 应该显示用户信息 | ✅ | [查看](screenshots/main-layout-user-info.png) |
| 10 | 应该可以退出登录 | ✅ | [查看](screenshots/logout-*.png) |

## 问题清单

✅ 所有测试通过，未发现问题

## 测试截图

所有测试截图已保存至 `tests/screenshots/` 目录。

---

*生成时间：2026/3/10 09:46:03*
