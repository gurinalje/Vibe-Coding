# Vibe-Coding - AI 多 Agent 代码分析系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=flat&logo=openai)
![LangChain](https://img.shields.io/badge/LangChain-0.1-1c3c3c?style=flat&logo=langchain)

**AI 代码审查** | **多 Agent 协同** | **自动重构**

</div>

---

## 项目简介

一个基于大语言模型（LLM）的多 Agent 协同代码审查与自动重构系统。通过三个专业化 Agent（Reviewer、Developer、Critic）的协作，实现智能化的代码质量分析和自动优化。

**项目周期：** 1 周  
**个人角色：** 独立开发者  
**项目类型：** AI 应用开发 + 多 Agent 系统

---

## 核心功能

### 1. 多 Agent 协同架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent 协调器 (Coordinator)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Reviewer   │  │  Developer  │  │   Critic    │         │
│  │  代码审查者  │  │  代码重构者  │  │  质量评估者  │         │
│  │             │  │             │  │             │         │
│  │ - 质量评分  │  │ - 重构建议  │  │ - 误报检测  │         │
│  │ - 问题识别  │  │ - 代码优化  │  │ - 漏报发现  │         │
│  │ - 规范检查  │  │ - 性能改进  │  │ - 质量评估  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 智能代码分析

| 分析维度 | 检测内容 |
|---------|---------|
| 代码质量 | 复杂度、重复度、规范性 |
| 安全漏洞 | SQL 注入、XSS、硬编码密码 |
| 性能问题 | 算法复杂度、内存泄漏风险 |
| 架构问题 | 循环依赖、God Class、Feature Envy |

### 3. 自动重构引擎

- **代码优化建议**：基于 LLM 的智能重构方案
- **重构影响分析**：评估重构对其他模块的影响
- **重构效果评估**：对比重构前后的代码质量

### 4. Web 可视化仪表板

- 实时代码质量评分
- 问题分类统计
- 重构建议展示
- Agent 协作流程可视化

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Web 前端 (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│           交互式界面 + 实时数据展示 + 图表可视化               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent 协调层 (Coordinator)                │
├─────────────────────────────────────────────────────────────┤
│           任务分配 + Agent 通信 + 结果聚合                    │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Reviewer Agent │ │ Developer Agent │ │  Critic Agent   │
│   代码审查者     │ │   代码重构者     │ │   质量评估者     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM API (OpenAI/Anthropic)               │
├─────────────────────────────────────────────────────────────┤
│           GPT-4 / Claude 语义分析 + 代码理解                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 项目亮点

### 1. 多 Agent 协同机制

```python
class AgentCoordinator:
    """Agent 协调器 - 管理多个专业化 Agent"""
    
    def __init__(self):
        self.agents = {
            'reviewer': ReviewerAgent(),    # 代码审查
            'developer': DeveloperAgent(),  # 代码重构
            'critic': CriticAgent()         # 质量评估
        }
    
    async def analyze_code(self, code: str, language: str):
        """多 Agent 协同分析"""
        
        # 1. Reviewer 审查代码
        review_result = await self.agents['reviewer'].review(code)
        
        # 2. Developer 生成重构建议
        refactor_suggestions = await self.agents['developer'].suggest(code, review_result)
        
        # 3. Critic 评估质量
        quality_score = await self.agents['critic'].evaluate(code, review_result)
        
        return {
            'review': review_result,
            'suggestions': refactor_suggestions,
            'quality_score': quality_score
        }
```

### 2. 智能安全扫描

```python
class SecurityScanner:
    """安全漏洞扫描器"""
    
    VULNERABILITY_PATTERNS = {
        'sql_injection': [
            r'execute\(.*\+.*\)',
            r'query\(.*%s.*\)',
        ],
        'hardcoded_password': [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ],
        'xss_vulnerability': [
            r'innerHTML\s*=',
            r'document\.write\(',
        ]
    }
    
    async def scan(self, code: str, language: str):
        """扫描代码中的安全漏洞"""
        vulnerabilities = []
        
        for vuln_type, patterns in self.VULNERABILITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    vulnerabilities.append({
                        'type': vuln_type,
                        'severity': self.get_severity(vuln_type),
                        'line': code[:match.start()].count('\n') + 1,
                        'code': match.group()
                    })
        
        return vulnerabilities
```

### 3. LLM 语义分析

```python
class LLMSemanticAnalyzer:
    """基于 LLM 的语义级代码分析"""
    
    def __init__(self, model: str = "gpt-4"):
        self.client = OpenAI()
        self.model = model
    
    async def analyze_code_quality(self, code: str, language: str):
        """使用 LLM 分析代码质量"""
        
        prompt = f"""
        分析以下 {language} 代码的质量，包括：
        1. 代码可读性
        2. 性能问题
        3. 安全风险
        4. 设计模式使用
        5. 改进建议
        
        代码：
        ```{language}
        {code}
        ```
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self.parse_response(response.choices[0].message.content)
```

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 编程语言 |
| FastAPI | 0.104 | Web 框架 |
| OpenAI API | - | GPT-4 语义分析 |
| Anthropic API | - | Claude 语义分析 |
| Rich | - | CLI 美化界面 |
| Pytest | - | 单元测试 |

---

## 快速开始

### 环境要求

- Python 3.8+
- OpenAI API Key 或 Anthropic API Key

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/gurinalje/Vibe-Coding.git
cd Vibe-Coding

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
export OPENAI_API_KEY="your-api-key"
# 或
export ANTHROPIC_API_KEY="your-api-key"
```

### 使用方式

#### 1. CLI 命令行

```bash
# 代码审查
python cli.py review your_code.py

# 代码重构
python cli.py refactor your_code.py

# 安全扫描
python cli.py scan your_code.py

# 启动 Web 仪表板
python cli.py dashboard
```

#### 2. Python API

```python
import asyncio
from agents.coordinator import AgentCoordinator

async def main():
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    # 分析代码
    code = """
def vulnerable_function(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input
    return execute_query(query)
    """
    
    result = await coordinator.analyze_code(code, "python")
    print(f"质量评分: {result['quality_score']}/100")
    print(f"发现问题: {len(result['review']['issues'])} 个")

asyncio.run(main())
```

#### 3. Web 界面

```bash
# 启动 Web 服务
python cli.py dashboard --port 8000

# 访问 http://localhost:8000
```

---

## 测试结果

```bash
$ pytest tests/ -v

tests/test_agents.py::test_reviewer_agent PASSED
tests/test_agents.py::test_developer_agent PASSED
tests/test_agents.py::test_critic_agent PASSED
tests/test_agents.py::test_coordinator PASSED
tests/test_core.py::test_code_analyzer PASSED
tests/test_core.py::test_security_scanner PASSED
...
======================== 135 passed in 45.23s =========================
```

**测试覆盖率：** 87%

---

## 项目结构

```
Vibe-Coding/
├── agents/                      # Agent 模块
│   ├── base_agent.py           # Agent 基类
│   ├── reviewer_agent.py       # 代码审查者
│   ├── developer_agent.py      # 代码重构者
│   ├── critic_agent.py         # 质量评估者
│   └── coordinator.py          # Agent 协调器
├── core/                        # 核心引擎
│   ├── code_analyzer.py        # 代码分析器
│   ├── refactoring_engine.py   # 重构引擎
│   └── security_scanner.py     # 安全扫描器
├── monitoring/                  # 监控模块
│   ├── token_monitor.py        # Token 使用监控
│   └── performance_monitor.py  # 性能监控
├── tests/                       # 测试代码
│   ├── test_agents.py
│   ├── test_core.py
│   └── test_benchmark.py
├── cli.py                       # CLI 入口
├── demo.py                      # 演示脚本
└── requirements.txt             # 依赖列表
```

---

## 演示效果

### 1. 代码审查结果

```
┌─────────────────────────────────────────────────────────────┐
│                    代码质量评分: 72/100                      │
├─────────────────────────────────────────────────────────────┤
│  🔴 严重问题: 2 个                                          │
│     - SQL 注入漏洞 (第 3 行)                                 │
│     - 硬编码密码 (第 7 行)                                   │
│                                                             │
│  🟡 警告: 5 个                                              │
│     - 函数复杂度过高                                         │
│     - 缺少异常处理                                           │
│     - ...                                                   │
│                                                             │
│  🟢 建议: 8 个                                              │
│     - 使用参数化查询                                         │
│     - 添加输入验证                                           │
│     - ...                                                   │
└─────────────────────────────────────────────────────────────┘
```

### 2. 重构建议

```
重构建议 #1: 使用参数化查询防止 SQL 注入

原始代码:
query = "SELECT * FROM users WHERE id = " + user_id

重构后:
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

---

## 开发记录

- ✅ 完成多 Agent 架构设计
- ✅ 实现 Reviewer Agent
- ✅ 实现 Developer Agent
- ✅ 实现 Critic Agent
- ✅ 完成 Agent 协调器
- ✅ 实现安全扫描器
- ✅ 完成 Web 仪表板
- ✅ 编写单元测试（135 个）

---

## 许可证

MIT License

---

<div align="center">

**如果这个项目对你有帮助，欢迎 Star 支持！**

</div>
