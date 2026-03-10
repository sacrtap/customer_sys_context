#!/bin/bash

# 客户运营中台 - 快速启动脚本

echo "========================================"
echo "  客户运营中台 - 快速启动"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3"
    exit 1
fi
echo "✓ Python 版本：$(python3 --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js"
    exit 1
fi
echo "✓ Node.js 版本：$(node --version)"

# 检查 PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ 未找到 PostgreSQL"
    exit 1
fi
echo "✓ PostgreSQL 已安装"

echo ""
echo "========================================"
echo "  1. 启动后端服务"
echo "========================================"

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
pip install -q -r requirements.txt

# 检查数据库
echo "检查数据库连接..."
if ! psql -U postgres -lqt &> /dev/null; then
    echo "⚠️  PostgreSQL 未运行，请先启动 PostgreSQL 服务"
    exit 1
fi

# 创建数据库（如果不存在）
psql -U postgres -c "CREATE DATABASE customer_sys;" 2>/dev/null || echo "数据库已存在"

# 运行迁移
echo "运行数据库迁移..."
alembic upgrade head

# 初始化数据
echo "初始化基础数据..."
python scripts/init_db.py

# 启动后端
echo ""
echo "启动后端服务 (http://localhost:8000)..."
python main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

echo ""
echo "========================================"
echo "  2. 启动前端服务"
echo "========================================"

cd ../frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装 Node.js 依赖..."
    npm install
fi

# 启动前端
echo "启动前端服务 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  启动完成!"
echo "========================================"
echo ""
echo "📊 后端服务：http://localhost:8000"
echo "🌐 前端服务：http://localhost:5173"
echo ""
echo "🔑 默认登录账号:"
echo "   用户名：admin"
echo "   密码：admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '服务已停止'; exit 0" INT

wait
