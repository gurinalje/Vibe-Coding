# Vibe Coding - AI-Powered Multi-Agent Code Analysis System

<div align="center">

**[English](README_EN.md) | 中文**

[![Tests](https://img.shields.io/badge/tests-135%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

</div>

## 项目简介

Vibe Coding 是一个 AI 驱动的多 Agent 协同代码分析系统，集成了代码审查、安全扫描、性能分析、自动修复和 Web 可视化仪表板等功能。

### 核心特性

- **多 Agent 协同分析** - Reviewer、Developer、Critic 三个 Agent 协同工作
- **CLI 命令行工具** - 基于 Rich 的美观终端界面
- **Web 可视化仪表板** - FastAPI 驱动的交互式 Web 界面
- **LLM 深度分析** - 支持 OpenAI/Anthropic API 进行语义级代码分析
- **自动修复引擎** - 基于规则和 AI 的代码自动修复
- **Git 集成** - 分析 Git diff、PR 变更
- **实时监听** - 文件变化时自动分析
- **多语言支持** - Python、Java、JavaScript/TypeScript

## 安装

```bash
git clone <repository-url>
cd Vibe-Coding
pip install -r requirements.txt

# 可选依赖
pip install fastapi uvicorn  # Web 仪表板
pip install openai            # OpenAI LLM
```

## 使用方法

### CLI 命令行

```bash
python cli.py analyze ./src --language python
python cli.py review main.py
python cli.py fix main.py --dry-run
python cli.py watch ./src
python cli.py git --branch main
python cli.py dashboard --port 8080
```

### Python API

```python
from core.code_analyzer_v2 import CodeAnalyzer
from agents.coordinator import AgentCoordinator
from core.auto_fixer import AutoFixer

# 代码分析
analyzer = CodeAnalyzer()
result = await analyzer.analyze(code, "python")

# 多 Agent 审查
coordinator = AgentCoordinator()
review = await coordinator.review_code(code, "python")

# 自动修复
fixer = AutoFixer()
result = fixer.fix(code, "python")
```

## Agent 系统

| Agent | 职责 | 输出 |
|-------|------|------|
| Reviewer | 代码质量审查 | 评分、问题列表 |
| Developer | 代码重构优化 | 重构建议、优化代码 |
| Critic | 审查质量评估 | 误报检测、漏报发现 |

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT License
