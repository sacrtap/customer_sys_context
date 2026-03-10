#!/bin/bash
set -e

echo "====================================="
echo "= 客户运营中台前端部署脚本          ="
echo "====================================="

# 1. 检查 Node.js 版本
echo "🔍 检查 Node.js 版本..."
NODE_VERSION=$(node -v | cut -d 'v' -f 2)
REQUIRED_NODE_VERSION=18.0.0
if [ "$(printf '%s\n' "$REQUIRED_NODE_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE_VERSION" ]; then
    echo "❌ Node.js 版本过低，需要 >= $REQUIRED_NODE_VERSION，当前版本: $NODE_VERSION"
    exit 1
fi
echo "✅ Node.js 版本: $NODE_VERSION"

# 2. 安装依赖
echo "📦 安装项目依赖..."
npm install
echo "✅ 依赖安装完成"

# 3. 类型检查
echo "🔍 运行 TypeScript 类型检查..."
npm run type-check
if [ $? -ne 0 ]; then
    echo "❌ 类型检查失败，请修复错误后重试"
    exit 1
fi
echo "✅ 类型检查通过"

# 4. 代码检查
echo "🔍 运行 ESLint 代码检查..."
npm run lint
if [ $? -ne 0 ]; then
    echo "⚠️  代码检查存在警告，请确认是否可忽略"
    read -p "是否继续部署？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        exit 1
    fi
fi
echo "✅ 代码检查完成"

# 5. 构建生产版本
echo "🏗️  构建生产版本..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 构建失败，请检查错误信息"
    exit 1
fi

# 6. 检查构建产物
echo "🔍 检查构建产物..."
if [ -d "dist" ]; then
    echo "✅ 构建成功"
    echo "📊 构建产物大小统计:"
    du -sh dist/
    echo "📦 JS 资源大小:"
    du -sh dist/assets/js/* 2>/dev/null | sort -hr
    echo "🎨 CSS 资源大小:"
    du -sh dist/assets/css/* 2>/dev/null | sort -hr
    echo "🖼️  其他资源大小:"
    du -sh dist/assets/*/* 2>/dev/null | grep -v js | grep -v css | sort -hr
else
    echo "❌ 构建失败，dist 目录不存在"
    exit 1
fi

echo "====================================="
echo "✅ 前端构建完成，可部署 dist 目录"
echo "📝 部署路径: $(pwd)/dist"
echo "====================================="
