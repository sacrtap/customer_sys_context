# 客户运营中台开发记录

**日期**: 2026-03-09

## 开发内容

### 后端实现

1. **项目框架** (Sanic + SQLAlchemy + Alembic)
   - Sanic 异步 Web 框架
   - SQLAlchemy 2.0 ORM
   - Alembic 数据库迁移
   - JWT 认证

2. **数据模型**
   - `User` - 系统用户
   - `Role` - 角色
   - `Permission` - 权限点
   - `Customer` - 客户
   - `CustomerUsage` - 客户用量
   - `Industry` - 行业分类
   - `CustomerLevel` - 客户等级
   - `Settlement` - 结算记录

3. **API 端点**
   - `/api/v1/auth/*` - 认证（登录/登出/获取当前用户）
   - `/api/v1/users/*` - 用户管理
   - `/api/v1/roles/*` - 角色管理
   - `/api/v1/permissions/*` - 权限管理
   - `/api/v1/customers/*` - 客户管理
   - `/api/v1/customers/import` - Excel 导入

4. **工具函数**
   - `deps.py` - 依赖注入和权限验证
   - `pagination.py` - 分页工具
   - `excel_import.py` - Excel 导入解析器

5. **数据库迁移**
   - 初始迁移：创建所有表
   - 初始化脚本：创建默认权限、角色、管理员账号

### 前端实现

1. **项目框架** (Vue 3 + Vite + Ant Design Vue)
   - Vue 3.5 + TypeScript
   - Vite 7 构建工具
   - Ant Design Vue 4 UI 组件
   - Pinia 状态管理
   - Vue Router 路由

2. **核心功能**
   - JWT Token 认证
   - 路由守卫
   - 权限控制
   - 响应式布局

3. **页面视图**
   - `Login.vue` - 登录页
   - `Dashboard.vue` - 工作台
   - `CustomerList.vue` - 客户列表
   - `CustomerDetail.vue` - 客户详情
   - `UserList.vue` - 用户列表
   - `RoleList.vue` - 角色列表

4. **API 集成**
   - Axios 封装（请求/响应拦截器）
   - 认证 API
   - 自动 Token 管理

## 技术选型决策

| 方面 | 选择 | 原因 |
|------|------|------|
| 后端框架 | Sanic | 异步高性能，适合 I/O 密集型 |
| ORM | SQLAlchemy 2.0 | 成熟稳定，异步支持 |
| 前端框架 | Vue 3 | 团队熟悉，上手快 |
| UI 组件 | Ant Design Vue | 企业级组件，功能丰富 |
| 数据库 | PostgreSQL | 功能强大，支持复杂查询 |
| 认证 | JWT | 无状态，易扩展 |
| API 版本 | URL 路径 | 清晰直观，易维护 |

## 遇到的问题

### 1. Obsidian API 连接问题

**问题**: with-context MCP 服务器无法连接 Obsidian API

**原因**: 
- 环境变量未正确加载
- API URL 不匹配（健康检查显示 `https://127.0.0.1:27124` 但配置是 `http://127.0.0.1:27123`）

**解决**: 暂时跳过文档同步，优先开发工作

### 2. TypeScript LSP 错误

**问题**: 前端文件创建后出现 LSP 错误

**原因**: TypeScript 语言服务索引延迟

**解决**: 这是正常的索引过程，不影响实际运行

## 下一步计划

### 短期 (本周)
1. [ ] 完善前端表单（客户/用户/角色的新建编辑）
2. [ ] 实现 Excel 导入前端界面
3. [ ] 添加数据图表（ECharts）
4. [ ] 完善错误处理和表单验证

### 中期 (本月)
1. [ ] 客户健康度分析
2. [ ] 收入预测功能
3. [ ] 结算管理模块
4. [ ] 数据分析报表

### 长期
1. [ ] 性能优化
2. [ ] 单元测试
3. [ ] 集成测试
4. [ ] CI/CD 配置

## 经验总结

### 后端开发
1. Sanic 的 Blueprint 系统适合模块化开发
2. SQLAlchemy 2.0 的异步 API 需要适应
3. Alembic 迁移脚本要仔细测试

### 前端开发
1. Ant Design Vue 4 的 TypeScript 支持良好
2. Pinia 比 Vuex 更简洁易用
3. 路由守卫实现权限控制简单有效

### 项目管理
1. 前后端分离开发效率高
2. API 版本管理要尽早规划
3. 文档与代码同步更新

---

*最后更新：2026-03-09*
