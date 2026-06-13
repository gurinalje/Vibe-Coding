# Changelog

本项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 异步上下文管理器支持 `AgentCoordinator`
- 语言特定的代码分析器模块
  - `PythonAnalyzer`: Python 代码分析
  - `JavaAnalyzer`: Java 代码分析
  - `JavaScriptAnalyzer`: JavaScript/TypeScript 代码分析
- 数据模型模块 `models.py`
- 更多单元测试覆盖

### 改进
- 拆分 `code_analyzer.py` 大文件为多个模块
- 改进代码结构和可维护性
- 增强安全检测能力

### 修复
- 修复 Agent 间通信的错误处理
- 改进异常处理机制

## [0.2.0] - 2024-01-15

### 新增
- 多 Agent 协同系统
  - Reviewer Agent: 代码审查
  - Developer Agent: 代码重构
  - Critic Agent: 代码批评
  - Agent Coordinator: Agent 协调器
- 代码分析引擎
- 安全扫描器
- 性能分析器
- 报告生成器
- Token 监控器
- 基准测试框架

### 改进
- 完善 API 文档
- 添加使用示例

## [0.1.0] - 2024-01-01

### 新增
- 项目初始化
- 基础架构搭建
- 核心功能实现

---

## 版本说明

### 版本号格式

版本号格式为: `主版本.次版本.修订号`

- **主版本 (Major)**: 不兼容的 API 更改
- **次版本 (Minor)**: 向后兼容的功能性新增
- **修订号 (Patch)**: 向后兼容的问题修正

### 更改类型

- **新增 (Added)**: 新功能
- **改进 (Changed)**: 对现有功能的更改
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: 任何 bug 修复
- **安全 (Security)**: 安全相关的更改