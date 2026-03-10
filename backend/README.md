# 客户运营中台 - 后端服务

基于 Python Sanic 的异步 API 服务。

## 技术栈

- **框架**: Sanic 23.6
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库**: PostgreSQL 15+
- **认证**: JWT
- **验证**: Pydantic 2

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置数据库

```bash
# 创建数据库
createdb customer_sys

# 或手动执行
psql -U postgres
CREATE DATABASE customer_sys;
```

### 3. 配置文件

```bash
# 复制环境配置
cp .env.example .env

# 编辑 .env 文件，更新数据库连接等配置
```

### 4. 数据库迁移

```bash
# 初始化 Alembic（首次）
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── auth.py       # 认证路由
│   │       │   ├── users.py      # 用户管理
│   │       │   ├── roles.py      # 角色管理
│   │       │   └── customers.py  # 客户管理
│   │       └── __init__.py
│   ├── models/
│   │   ├── user.py      # 用户模型
│   │   ├── role.py      # 角色权限模型
│   │   └── customer.py  # 客户模型
│   ├── schemas/
│   │   ├── auth.py      # 认证 Schema
│   │   ├── user.py      # 用户 Schema
│   │   ├── role.py      # 角色 Schema
│   │   └── customer.py  # 客户 Schema
│   ├── services/        # 业务逻辑层
│   ├── utils/
│   │   ├── deps.py           # 依赖注入
│   │   ├── pagination.py     # 分页工具
│   │   └── excel_import.py   # Excel 导入
│   └── database.py    # 数据库配置
├── alembic/           # 数据库迁移
├── config.py          # 配置管理
├── main.py            # 应用入口
├── requirements.txt   # 依赖
└── .env.example       # 环境配置示例
```

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

## 权限码

| 模块 | 权限码 | 说明 |
|------|--------|------|
| 用户 | `users:read` | 查看用户 |
| 用户 | `users:create` | 创建用户 |
| 用户 | `users:update` | 更新用户 |
| 用户 | `users:delete` | 删除用户 |
| 角色 | `roles:read` | 查看角色 |
| 角色 | `roles:create` | 创建角色 |
| 角色 | `roles:update` | 更新角色 |
| 角色 | `roles:delete` | 删除角色 |
| 客户 | `customers:read` | 查看客户 |
| 客户 | `customers:create` | 创建客户 |
| 客户 | `customers:update` | 更新客户 |
| 客户 | `customers:delete` | 删除客户 |

## 开发

### 运行测试

```bash
pytest tests/ -v
```

### 代码格式化

```bash
# 安装开发工具
pip install black isort flake8

# 格式化
black .
isort .

# 检查
flake8 .
```

## 数据库迁移命令

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1

# 查看历史
alembic history

# 查看当前版本
alembic current
```

---

*客户运营中台后端服务 v1.0.0*
