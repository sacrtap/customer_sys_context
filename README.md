# 客户运营中台

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/sacrtap/customer_sys_context)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/sacrtap/customer_sys_context)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/sacrtap/customer_sys_context)

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

| 优先级 | 模块 | 功能 |
|--------|------|------|
| P0 | 系统用户管理 | 用户、角色、权限管理 |
| P0 | 客户管理 | 客户 CRUD、Excel 导入 |
| P1 | 用量趋势 | 客户用量统计、趋势分析 |
| P1 | 收入预测 | 基于用量的收入预测 |
| P1 | 客户健康度 | 客户活跃度评估 |
| P2 | 结算管理 | 结算记录、账单管理 |
| P2 | 数据分析报表 | 综合数据报表 |

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
- `GET /api/v1/customers` - 客户列表
- `POST /api/v1/customers` - 创建客户
- `GET /api/v1/customers/{id}` - 客户详情
- `PUT /api/v1/customers/{id}` - 更新客户
- `DELETE /api/v1/customers/{id}` - 删除客户
- `POST /api/v1/customers/import` - Excel 导入
- `GET /api/v1/industries` - 行业列表
- `GET /api/v1/levels` - 客户等级列表

## 开发进度

### 已完成
- [x] 后端项目框架（Sanic + SQLAlchemy + Alembic）
- [x] 前端项目框架（Vue 3 + Vite + Ant Design Vue）
- [x] 数据库模型设计（用户、角色、权限、客户、用量、结算）
- [x] 认证模块（JWT 登录）
- [x] 用户管理 API
- [x] RBAC 权限模块
- [x] 客户管理 API
- [x] Excel 导入功能（后端）
- [x] 前端登录页面
- [x] 前端用户列表页面
- [x] 前端客户列表页面
- [x] 前端角色列表页面

### 待开发
- [ ] 客户新建/编辑表单
- [ ] 用户新建/编辑表单
- [ ] 角色新建/编辑表单
- [ ] Excel 导入前端界面
- [ ] 数据图表（ECharts）
- [ ] 客户健康度分析
- [ ] 收入预测图表
- [ ] 结算管理页面
- [ ] 数据分析报表

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

*客户运营中台 v1.0.0*  
*最后更新：2026-03-09*
