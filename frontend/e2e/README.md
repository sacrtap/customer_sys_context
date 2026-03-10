# E2E 自动化测试

本目录包含使用 Playwright 编写的端到端自动化测试。

## 快速开始

### 1. 安装依赖

```bash
npm install -D @playwright/test
npx playwright install chromium
```

### 2. 运行测试

```bash
# 运行所有测试
npx playwright test

# 运行特定测试文件
npx playwright test user-role-tests.spec.ts

# 使用 headed 模式查看浏览器
npx playwright test --headed

# 生成 HTML 报告
npx playwright show-report
```

## 测试文件

- `user-role-tests.spec.ts` - 用户管理和角色权限测试
  - 用户列表页面加载
  - 新建用户功能
  - 删除确认弹窗
  - 角色列表页面加载
  - 新建角色功能
  - 权限分配功能

## 测试配置

- **基础 URL**: http://127.0.0.1:5173
- **超时时间**: 60 秒
- **浏览器**: Chromium
- **截图**: 失败时自动截图
- **视频**: 失败时录制视频

## 测试账号

- 用户名：`admin`
- 密码：`admin123`

## 故障排查

### 测试失败常见原因

1. **前端服务未启动**: 确保 `npm run dev` 正在运行
2. **后端服务未启动**: 确保后端服务在 8000 端口运行
3. **网络延迟**: 增加超时时间或添加更多等待

### 查看失败详情

```bash
# 查看失败截图
open test-results/*/test-failed-1.png

# 查看失败视频
open test-results/*/video.webm

# 查看错误上下文
cat test-results/*/error-context.md
```

## 编写测试的最佳实践

1. **使用可靠的定位器**: 优先使用 `getByRole`, `getByText`
2. **添加适当的等待**: 使用 `waitForLoadState('networkidle')`
3. **隔离测试**: 每个测试应该独立运行
4. **清理测试数据**: 测试后清理创建的测试数据

## 资源

- [Playwright 官方文档](https://playwright.dev)
- [Playwright 测试组件](https://playwright.dev/docs/test-components)
- [Playwright 定位器](https://playwright.dev/docs/locators)
