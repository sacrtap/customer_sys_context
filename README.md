# 客户运营中台

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/sacrtap/customer_sys_context)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/sacrtap/customer_sys_context)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/sacrtap/customer_sys_context)
[![Tests](https://img.shields.io/badge/tests-255_passed-brightgreen.svg)](https://github.com/sacrtap/customer_sys_context)

客户运营中台系统 - 用于管理房产行业客户的系统使用情况，支持客户管理、收入预测、用量分析、结算管理等功能。

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 一键启动

```bash
# 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python scripts/init_db.py
python main.py

# 前端（新终端）
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173，默认账号：`admin` / `admin123`

## 项目概述

### 目标用户

- **运营人员**（主要用户）：客户管理、数据分析、结算处理
- **销售人员**：客户跟进、业绩查看
- **管理层**：数据报表、收入预测

### 核心功能模块

| 优先级 | 模块 | 功能 | 状态 |
|--------|------|------|------|
| P0 | 系统用户管理 | 用户、角色、权限管理 | ✅ 已完成 |
| P0 | 客户管理 | 客户 CRUD、Excel 导入 | ✅ 已完成 |
| P1 | 用量趋势 | 客户用量统计、趋势分析 | ✅ 已完成 |
| P1 | 收入预测 | 基于用量的收入预测 | ✅ 已完成 |
| P1 | 客户健康度 | 客户活跃度评估 | ✅ 已完成 |
| P2 | 结算管理 | 结算记录、账单管理 | ✅ 已完成 |
| P2 | 数据分析报表 | 综合数据报表 | ✅ 已完成 |
| P2 | Dashboard 工作台 | 数据概览、快捷操作、最新动态 | ✅ 已完成 |

## 技术架构

### 整体架构

```
┌─────────────────┐     HTTP/REST      ┌─────────────────┐
│   前端层         │ ◄──────────────►  │   后端层         │
│  Vue 3 + Vite    │                    │  Python Sanic   │
│  Ant Design Vue  │                    │  + SQLAlchemy   │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                ▼
                                       ┌─────────────────┐
                                       │   数据库层       │
                                       │  PostgreSQL 15  │
                                       └─────────────────┘
```

### 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | Vue 3 + Vite + Ant Design Vue + Pinia + Vue Router |
| 后端 | Python 3.11+ + Sanic + SQLAlchemy + Alembic |
| 数据库 | PostgreSQL 15+ |
| 认证 | JWT (JSON Web Token) |
| API 版本 | URL 路径版本控制 (/api/v1/...) |

## 项目结构

```
customer_sys_context/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/v1/      # API v1 路由
│   │   ├── models/      # SQLAlchemy 模型
│   │   ├── schemas/     # Pydantic 数据验证
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── alembic/         # 数据库迁移
│   ├── config.py        # 配置管理
│   ├── main.py          # 应用入口
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── api/        # API 调用
│   │   ├── components/ # 公共组件
│   │   ├── views/      # 页面视图
│   │   ├── stores/     # Pinia 状态管理
│   │   └── router/     # 路由配置
│   ├── package.json    # Node 依赖
│   └── vite.config.ts  # Vite 配置
├── docs/               # 文档
└── README.md           # 本文件
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库
createdb customer_sys

# 复制并编辑环境配置
cp .env.example .env

# 运行数据库迁移
alembic upgrade head

# 初始化基础数据
python scripts/init_db.py

# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 3. 默认登录账号

- 用户名：`admin`
- 密码：`admin123`

## API 端点

### 认证
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户
- `POST /api/v1/auth/logout` - 用户登出

### 用户管理
- `GET /api/v1/users` - 用户列表
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users/{id}` - 用户详情
- `PUT /api/v1/users/{id}` - 更新用户
- `DELETE /api/v1/users/{id}` - 删除用户

### 角色管理
- `GET /api/v1/roles` - 角色列表
- `POST /api/v1/roles` - 创建角色
- `PUT /api/v1/roles/{id}` - 更新角色
- `DELETE /api/v1/roles/{id}` - 删除角色
- `GET /api/v1/permissions` - 权限列表

### 客户管理
- `GET /api/v1/customers` - 客户列表（支持筛选、分页）
- `POST /api/v1/customers` - 创建客户
- `GET /api/v1/customers/{id}` - 客户详情
- `PUT /api/v1/customers/{id}` - 更新客户
- `DELETE /api/v1/customers/{id}` - 删除客户
- `POST /api/v1/customers/import` - Excel 导入
- `GET /api/v1/customers/industries` - 行业列表
- `GET /api/v1/customers/levels` - 客户等级列表
- `GET /api/v1/customers/{id}/usages` - 客户用量历史
- `GET /api/v1/customers/{id}/settlements` - 客户结算记录

### 结算管理
- `GET /api/v1/settlements` - 结算记录列表
- `POST /api/v1/settlements` - 创建结算记录
- `PUT /api/v1/settlements/{id}` - 更新结算记录
- `DELETE /api/v1/settlements/{id}` - 删除结算记录
- `POST /api/v1/settlements/{id}/confirm` - 确认收款
- `POST /api/v1/settlements/generate-bills` - 生成月度账单
- `GET /api/v1/settlements/export` - Excel 导出

### Dashboard
- `GET /api/v1/dashboard/overview` - 数据概览
- `GET /api/v1/dashboard/quick-actions` - 快捷操作
- `GET /api/v1/dashboard/recent-activities` - 最新动态
- `GET /api/v1/dashboard/health-stats` - 健康度统计

### 数据分析
- `GET /api/v1/analytics/usage-trend` - 用量趋势
- `GET /api/v1/analytics/revenue-forecast` - 收入预测
- `GET /api/v1/analytics/customer-distribution` - 客户分布
- `GET /api/v1/analytics/settlement-stats` - 结算统计

### 健康检查
- `GET /api/v1/health` - 系统健康检查

## 开发进度

### 已完成 (v1.2.0)

**后端 API (45 个端点)**
- ✅ 认证 API (3 端点) - 登录、刷新、登出
- ✅ 用户管理 API (7 端点) - CRUD、密码修改
- ✅ 角色权限 API (8 端点) - CRUD、权限分配
- ✅ 客户管理 API (10 端点) - CRUD、导入、筛选、详情
- ✅ 结算管理 API (8 端点) - CRUD、收款确认、账单生成、导出
- ✅ Dashboard API (8 端点) - 概览、快捷操作、动态、健康度
- ✅ 数据分析 API (4 端点) - 用量趋势、收入预测、客户分布、结算统计
- ✅ 健康检查 API (1 端点)

**前端页面 (21 个页面/组件)**
- ✅ 认证页面 - 登录
- ✅ 布局组件 - MainLayout
- ✅ Dashboard - 数据概览、快捷操作、4 个图表组件
- ✅ 客户管理 - 列表、表单、详情、筛选、导入
- ✅ 用户管理 - 列表、表单
- ✅ 角色权限 - 列表、表单
- ✅ 结算管理 - 列表、筛选、收款确认对话框

**测试覆盖 (~255 个用例)**
- ✅ 后端测试 - ~141 个用例
- ✅ 前端测试 - ~114 个用例
- ✅ 综合覆盖率 - ~95%

### 待优化
- [ ] 移动端适配优化
- [ ] 高级搜索功能
- [ ] 批量操作功能
- [ ] 操作日志记录
- [ ] 数据导出功能增强

## 详细文档

- [后端服务文档](backend/README.md)
- [前端应用文档](frontend/README.md)
- [系统设计文档](docs/plans/2026-03-09-customer-platform-design.md)

## 开发规范

### Git 提交规范

```
type(scope): description

types:
  feat - 新功能
  fix - 修复 bug
  docs - 文档更新
  style - 代码格式调整
  refactor - 重构
  test - 测试相关
  chore - 构建/工具配置
```

### 代码风格

**后端 (Python)**
- 使用类型注解
- 遵循 PEP 8 规范
- 使用 Black 格式化代码

**前端 (TypeScript/Vue)**
- 使用 TypeScript 严格模式
- 使用 Composition API (`<script setup>`)
- 组件名使用 PascalCase

---

*客户运营中台 v1.2.0*  
*最后更新：2026-03-10*  
*系统状态：生产就绪 ✅*
