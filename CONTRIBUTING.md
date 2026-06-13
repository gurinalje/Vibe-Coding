# 贡献指南

感谢您对 AI Agent Benchmark 项目的关注！我们欢迎各种形式的贡献。

## 目录

- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [报告 Bug](#报告-bug)
- [功能建议](#功能建议)

## 如何贡献

### 贡献方式

1. **报告 Bug**: 在 [Issues](https://github.com/your-username/ai-agent-benchmark/issues) 中报告
2. **提出功能建议**: 在 [Discussions](https://github.com/your-username/ai-agent-benchmark/discussions) 中讨论
3. **提交代码**: 通过 Pull Request 贡献代码
4. **改进文档**: 修正错误或添加说明
5. **分享使用经验**: 在社区中帮助其他用户

## 开发环境设置

### 前置要求

- Python 3.8+
- Git
- pip 或 poetry

### 安装步骤

```bash
# 1. Fork 项目到你的 GitHub 账户

# 2. 克隆你的 Fork
git clone https://github.com/your-username/ai-agent-benchmark.git
cd ai-agent-benchmark

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装开发依赖
pip install -e .

# 6. 验证安装
pytest tests/
```

## 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用 4 个空格缩进
- 行长度限制为 100 个字符
- 使用 type hints 进行类型标注
- 为所有公共函数和类编写 docstring

### 代码格式化

我们推荐使用以下工具：

```bash
# 安装工具
pip install black isort flake8 mypy

# 格式化代码
black .
isort .

# 代码检查
flake8 .

# 类型检查
mypy .
```

### 命名规范

- **文件名**: 使用小写字母和下划线 (`snake_case`)
- **类名**: 使用大驼峰 (`PascalCase`)
- **函数名**: 使用小写字母和下划线 (`snake_case`)
- **变量名**: 使用小写字母和下划线 (`snake_case`)
- **常量名**: 使用大写字母和下划线 (`UPPER_CASE`)

## 提交规范

### Commit Message 格式

```
<类型>(<作用域>): <描述>

<可选的正文>

<可选的脚注>
```

### 类型

- **feat**: 新功能
- **fix**: Bug 修复
- **docs**: 文档更改
- **style**: 代码格式（不影响代码运行的更改）
- **refactor**: 重构（既不修复 Bug 也不添加功能）
- **perf**: 性能优化
- **test**: 添加测试
- **chore**: 构建过程或辅助工具的更改

### 示例

```bash
git commit -m "feat(analyzer): 添加 TypeScript 支持"
git commit -m "fix(security): 修复 SQL 注入检测"
git commit -m "docs: 更新 README 安装说明"
```

## Pull Request 流程

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 进行更改

- 编写代码
- 添加测试
- 更新文档

### 3. 确保代码质量

```bash
# 运行测试
pytest tests/

# 运行代码检查
flake8 .

# 运行类型检查
mypy .

# 格式化代码
black .
isort .
```

### 4. 提交更改

```bash
git add .
git commit -m "feat: 描述你的更改"
```

### 5. 推送到你的 Fork

```bash
git push origin feature/your-feature-name
```

### 6. 创建 Pull Request

- 访问原始仓库的 GitHub 页面
- 点击 "New Pull Request"
- 选择你的分支
- 填写 PR 描述
- 提交 PR

### PR 描述模板

```markdown
## 更改说明

简要描述你的更改...

## 更改类型

- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 其他

## 测试

描述你如何测试你的更改...

## 相关 Issue

关联相关的 Issue (如果有)...

Closes #123
```

## 报告 Bug

### Bug 报告模板

```markdown
## Bug 描述

简要描述遇到的问题...

## 复现步骤

1. 运行 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

## 期望行为

描述期望的行为...

## 实际行为

描述实际的行为...

## 环境信息

- 操作系统: [例如 Windows 11]
- Python 版本: [例如 3.10.0]
- 项目版本: [例如 0.2.0]

## 日志/截图

如果有的话，添加日志或截图...
```

## 功能建议

我们欢迎功能建议！请在 [Discussions](https://github.com/your-username/ai-agent-benchmark/discussions) 中提出你的想法。

### 功能建议模板

```markdown
## 功能描述

简要描述你想要的功能...

## 使用场景

描述这个功能的使用场景...

## 期望行为

描述功能的期望行为...

## 替代方案

描述你考虑过的替代方案...

## 附加信息

任何其他相关信息...
```

## 代码审查

所有 PR 都需要经过代码审查。审查者会检查：

- 代码质量
- 测试覆盖
- 文档更新
- 性能影响
- 安全考虑

## 社区准则

- 尊重所有参与者
- 接受建设性批评
- 专注于对社区最有利的事情
- 对其他社区成员表示同理心

## 许可证

贡献的代码将按照项目许可证进行许可。

## 问题

如果你有任何问题，可以在 [Issues](https://github.com/your-username/ai-agent-benchmark/issues) 中提问，或在 [Discussions](https://github.com/your-username/ai-agent-benchmark/discussions) 中讨论。

感谢你的贡献！