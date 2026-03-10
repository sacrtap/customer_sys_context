# 客户运营中台 - 前端

基于 Vue 3 + TypeScript 的前端应用。

## 技术栈

- **框架**: Vue 3.5 + TypeScript
- **构建工具**: Vite 7
- **UI 组件库**: Ant Design Vue 4
- **状态管理**: Pinia
- **路由**: Vue Router 5
- **HTTP 客户端**: Axios

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口
│   │   ├── request.ts    # Axios 封装
│   │   └── auth.ts       # 认证 API
│   ├── components/       # 公共组件
│   │   └── layout/       # 布局组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   │   └── auth.ts       # 认证状态
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── views/            # 页面视图
│   │   ├── auth/         # 认证页面
│   │   ├── customers/    # 客户管理
│   │   ├── users/        # 用户管理
│   │   ├── roles/        # 角色管理
│   │   └── dashboard/    # 工作台
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   └── style.css         # 全局样式
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| /login | 登录页 | 用户登录 |
| / | 工作台 | 数据概览 |
| /customers | 客户列表 | 客户管理 |
| /customers/:id | 客户详情 | 客户详细信息 |
| /users | 用户列表 | 用户管理 |
| /roles | 角色列表 | 角色权限管理 |

## 功能特性

### 认证系统
- JWT Token 认证
- 自动刷新 Token
- 登录状态持久化
- 路由守卫

### 权限控制
- 基于角色的权限控制
- 菜单权限
- 按钮权限
- API 访问权限

### UI 组件
- 响应式布局
- 统一的设计风格
- 表格分页
- 表单验证
- 消息提示

## API 代理

开发环境下，API 请求会自动代理到后端服务：

- 前端：http://localhost:5173
- 后端：http://localhost:8000

代理配置在 `vite.config.ts` 中。

## 状态管理

使用 Pinia 进行状态管理：

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  
  const login = async (username: string, password: string) => {
    // 登录逻辑
  }
  
  const logout = async () => {
    // 登出逻辑
  }
  
  return { user, token, login, logout }
})
```

## 开发规范

### 代码风格
- 使用 TypeScript 严格模式
- 使用 Composition API (`<script setup>`)
- 组件名使用 PascalCase
- 文件名使用 PascalCase.vue

### Git 提交规范

```
type(scope): description

types: feat, fix, docs, style, refactor, test, chore
```

## 待开发功能

1. 客户新建/编辑表单
2. 用户新建/编辑表单
3. 角色新建/编辑表单
4. Excel 导入前端界面
5. 数据图表（ECharts）
6. 客户健康度分析
7. 收入预测图表
8. 结算管理页面

---

*客户运营中台前端 v1.0.0*
