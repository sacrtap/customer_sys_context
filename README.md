# customer_sys_context

> 客户系统上下文管理 - 集成 Obsidian 的智能文档管理系统

[![Version](https://img.shields.io/badge/version-0.1.0-blue)]()
[![Status](https://img.shields.io/badge/status-early--stage-yellow)]()
[![Obsidian](https://img.shields.io/badge/Obsidian-vault-9b4dca)]()

## 📋 项目概述

customer_sys_context 是一个用于管理客户系统上下文的工具，通过 `with-context` MCP 服务器与 Obsidian 深度集成，实现文档的智能委托和管理。

**当前状态**：早期设置阶段

## ✨ 核心特性

- 🔗 **Obsidian 集成** - 通过 with-context MCP 服务器无缝连接 Obsidian 知识库
- 📝 **智能文档委托** - 基于 Diátaxis 框架自动分类文档（教程、指南、参考、架构）
- 🔄 **双向同步** - 本地仓库与 Obsidian vault 之间的文档同步
- 📚 **文档架构优化** - 遵循 docs-as-code 最佳实践

## 🚀 快速开始

### 前置要求

- Node.js (项目使用 .opencode SDK)
- Obsidian 及 Obsidian API 服务
- with-context MCP 服务器

### 安装

```bash
# 克隆仓库
git clone https://github.com/sacrtap/customer_sys_context.git
cd customer_sys_context

# 安装依赖（如果适用）
# npm install  # 或 pnpm install
```

### 配置

在 `.env` 文件中配置 Obsidian API 连接：

```env
OBSIDIAN_VAULT="dev_project"
DELEGATION_STRATEGY="local-first"
WITH_CONTEXT_AUTO_START=true
WITH_CONTEXT_AUTO_TRACK=true
```

## 📖 使用指南

### 文档管理命令

```bash
# 验证配置
with-context-mcp validate-config

# 文档同步
with-context-mcp sync-notes          # 双向同步本地和 vault
with-context-mcp ingest-notes        # 复制本地文档到 vault
with-context-mcp teleport-notes      # 从 vault 下载文档到本地

# 会话管理
with-context-mcp start-session       # 开始文档会话
with-context-mcp end-session         # 结束文档会话

# 预览委托效果
with-context-mcp preview-delegation  # 预览哪些文件将被委托
```

### 开发指南

```bash
# Git 工作流（Conventional Commits）
git checkout -b feature/description
git add <files>
git commit -m "type: description"
git push origin feature/description
```

**Commit 类型**：`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📁 项目结构

```
customer_sys_context/
├── .opencode/             # OpenCode SDK 和插件
├── docs/                  # 文档（将移动到 Obsidian vault）
├── src/                   # 源代码
├── tests/                 # 测试文件
├── .env                   # 环境变量配置
├── .withcontextconfig.jsonc  # with-context 配置
├── AGENTS.md              # 开发指南
├── README.md              # 本文件
└── CHANGELOG.md           # 变更日志（委托到 vault）
```

## 📚 文档架构

遵循 **Diátaxis 框架** 组织文档：

| 类型 | 目的 | 位置 |
|------|------|------|
| **教程** (Tutorials) | 学习导向，逐步教学 | Obsidian vault: `docs/tutorials/` |
| **指南** (How-to) | 任务导向，解决问题 | Obsidian vault: `docs/guides/` |
| **参考** (Reference) | 信息导向，API 文档 | Obsidian vault: `docs/reference/` |
| **解释** (Explanation) | 理解导向，架构决策 | Obsidian vault: `docs/architecture/` |
| **快速参考** | 快速查阅 | 本地仓库 |

### 文档委托策略

- **本地保留**：README.md、AGENTS.md、CONTRIBUTING.md、源码文档
- **委托到 Vault**：CHANGELOG.md、详细指南、架构文档、研究笔记

## 🛠️ 开发工具

### with-context MCP 服务器

版本：2.1.0+
后端：Obsidian API
Vault：dev_project
Base Path：Obsidan_data

### Obsidian 集成

- API 端口：27123
- 自动跟踪会话：enabled
- 自动同步笔记：enabled

## 📝 相关资源

- [AGENTS.md](./AGENTS.md) - 开发指南和代码规范
- [Obsidian API 文档](https://help.obsidian.md/)
- [with-context MCP 文档](https://github.com/boxpositron/with-context-mcp)
- [Diátaxis 框架](https://diataxis.fr/)

## 🤝 贡献

我们欢迎各种形式的贡献！请查看 [贡献指南](./CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 许可证

[待添加]

---

**最后更新**: 2026-03-09  
**仓库**: [github.com/sacrtap/customer_sys_context](https://github.com/sacrtap/customer_sys_context)
