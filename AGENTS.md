# AGENTS.md - Development Guidelines

## Project Overview

customer_sys_context 是一个客户系统上下文管理工具 - 目前处于早期设置阶段。
项目通过 `with-context` MCP 系统与 Obsidian 深度集成，实现智能文档管理。

**核心特性**:
- 🔗 Obsidian 集成 - with-context MCP 服务器 v2.1.0
- 📝 智能文档委托 - 基于 Diátaxis 框架
- 🔄 双向同步 - 本地仓库与 Obsidian vault
- 📚 文档架构优化 - docs-as-code 最佳实践

## Documentation Guidelines

- Thinking 思考过程用中文表述.
- Reply 回答也要用中文回复.
- 所有生成的文档都要使用中文，且符合中文的语法规范，且保存至docs/目录下，并合理规划目录结构.
- Use context7 for all code generation and API documentation questions.
- Use the with-context MCP server for all project documentation
- 针对所有错误后修复成功的经验进行总结，把必要的经验写更新至AGENTS.md中，以避免再犯错.

## Build / Test / Lint Commands

**Current Status:** No build system, linter, or test framework is configured yet.

When the project matures, expected commands will include:

```bash
# For Python projects (common for Obsidian integrations)
python -m pytest tests/              # Run all tests
python -m pytest tests/test_file.py  # Run single test file
python -m pytest tests/test_file.py::test_name  # Run specific test
ruff check .                         # Lint
ruff format .                        # Format
mypy .                               # Type checking

# For Node.js projects
npm test                             # Run all tests
npm test -- --testNamePattern=name   # Run specific test
npm run lint                         # Lint
npm run format                       # Format

# For Rust projects
cargo test                           # Run tests
cargo test test_name                 # Run specific test
cargo clippy                         # Lint
cargo fmt                            # Format
```

## Code Style Guidelines

**Current Status:** No code exists yet. Follow language-specific best practices when adding code.

### General Principles
- Write clear, readable code with meaningful variable/function names
- Keep functions small and focused (single responsibility)
- Add docstrings/comments for public APIs and complex logic
- Prefer explicit over implicit behavior
- Handle errors gracefully with descriptive messages

### Import Organization
- Group imports: standard library → third-party → local modules
- Use absolute imports for project modules
- Avoid circular dependencies

### Naming Conventions
- **Python:** `snake_case` for variables/functions, `PascalCase` for classes
- **JavaScript/TypeScript:** `camelCase` for variables/functions, `PascalCase` for classes
- **Rust:** `snake_case` for variables/functions, `PascalCase` for types/traits
- Use descriptive names that explain intent

### Error Handling
- Validate inputs at function boundaries
- Use exceptions/errors for exceptional cases, not control flow
- Log errors with sufficient context for debugging
- Never silently swallow exceptions

### Type Safety
- Use type hints/annotations when available
- Prefer strict type checking over loose typing
- Document complex type relationships

## Git Workflow

```bash
git checkout -b feature/description    # Create feature branch
git add <files>                         # Stage changes
git commit -m "type: description"       # Conventional commits
git push origin feature/description     # Push to remote
```

### Commit Message Format (Conventional Commits)
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Cursor / Copilot Rules

No Cursor rules (`.cursor/rules/` or `.cursorrules`) or Copilot rules (`.github/copilot-instructions.md`) are defined in this repository.

## Obsidian Integration

This project uses the `with-context` system for Obsidian vault integration:

```bash
# Environment configuration in .env
OBSIDIAN_VAULT="dev_project"
DELEGATION_STRATEGY="local-first"
WITH_CONTEXT_AUTO_START=true
WITH_CONTEXT_AUTO_TRACK=true
```

### Obsidian API Configuration

- **API Port**: 27123
- **Base Path**: Obsidan_data
- **Vault**: dev_project
- **MCP Server**: with-context-mcp v2.1.0

### Available Commands (when with-context is configured)
```bash
# 配置验证
with-context-mcp validate-config

# 会话管理
with-context-mcp start-session
with-context-mcp end-session

# 文档同步
with-context-mcp sync-notes          # 双向同步本地和 vault
with-context-mcp ingest-notes        # 复制本地文档到 vault
with-context-mcp teleport-notes      # 从 vault 下载文档到本地

# 预览委托
with-context-mcp preview-delegation  # 预览哪些文件将被委托
```

## Project Structure (Current)

```
customer_sys_context/
├── .opencode/                # OpenCode SDK 和插件
├── .withcontextconfig.jsonc  # with-context 配置
├── docs/                     # 文档（将移动到 Obsidian vault）
├── src/                      # 源代码（待添加）
├── tests/                    # 测试文件（待添加）
├── .env                      # 环境变量配置
├── AGENTS.md                 # 本文件 - 开发指南
├── README.md                 # 项目概述
└── CHANGELOG.md              # 变更日志（委托到 vault）
```

## Next Steps for Development

1. Decide on the primary programming language
2. Set up appropriate build system and dependencies
3. Configure linter and formatter
4. Set up testing framework
5. Establish CI/CD pipeline
6. Add comprehensive documentation

---

*Last updated: 2026-03-09*  
*Repository: github.com/sacrtap/customer_sys_context*
