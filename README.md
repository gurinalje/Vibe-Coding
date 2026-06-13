# AI Agent 基准项目

## 多 Agent 协同代码审查和重构系统

这是一个用于评估 AI 代码审查能力的多 Agent 协同系统，包含代码审查、重构建议、安全扫描和性能分析等功能。

## 项目结构

```
ai-agent-benchmark/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python 依赖
├── setup.py                     # 项目安装脚本
├── config/
│   ├── __init__.py
│   ├── settings.py             # 配置文件
│   └── logging_config.py       # 日志配置
├── agents/
│   ├── __init__.py
│   ├── base_agent.py           # Agent 基类
│   ├── reviewer_agent.py       # 审查者 Agent
│   ├── developer_agent.py      # 开发者 Agent
│   ├── critic_agent.py         # 批评者 Agent
│   └── coordinator.py          # Agent 协调器
├── core/
│   ├── __init__.py
│   ├── code_analyzer.py        # 代码分析引擎
│   ├── refactoring_engine.py   # 重构引擎
│   ├── security_scanner.py     # 安全扫描器
│   └── performance_analyzer.py # 性能分析器
├── benchmark/
│   ├── __init__.py
│   ├── evaluator.py            # 评估器
│   ├── metrics.py              # 指标计算
│   └── test_cases/             # 基准测试用例
│       ├── __init__.py
│       ├── java_tests.py       # Java 测试用例
│       └── python_tests.py     # Python 测试用例
├── monitoring/
│   ├── __init__.py
│   ├── token_monitor.py        # Token 监控
│   └── performance_monitor.py  # 性能监控
├── utils/
│   ├── __init__.py
│   ├── git_utils.py            # Git 工具
│   ├── file_utils.py           # 文件工具
│   └── llm_utils.py            # LLM 工具
├── examples/
│   ├── basic_usage.py          # 基础使用示例
│   └── advanced_usage.py       # 高级使用示例
├── demo.py                     # 基础演示脚本
├── demo_cinema.py              # 影院系统演示脚本
├── demo_codegraph.py           # CodeGraph 图算法分析演示
└── tests/
    ├── __init__.py
    ├── test_agents.py          # Agent 测试
    ├── test_core.py            # 核心模块测试
    ├── test_cinema.py          # 影院系统测试
    ├── test_codegraph.py       # CodeGraph 图算法分析测试
    └── test_benchmark.py       # 基准测试
```

## 功能特性

### 1. 多 Agent 协同系统
- **审查者 Agent (Reviewer Agent)**: 负责代码质量审查
- **开发者 Agent (Developer Agent)**: 负责代码重构和优化
- **批评者 Agent (Critic Agent)**: 负责提出改进建议和问题
- **协调器 (Coordinator)**: 管理 Agent 间的通信和任务分配

### 2. 代码分析引擎
- AST 解析和代码结构分析
- 代码质量检测（复杂度、重复度、规范性）
- 安全漏洞扫描
- 性能瓶颈识别

### 3. 重构引擎
- 自动代码重构建议
- 重构影响分析
- 重构效果评估

### 4. 评估系统
- 代码审查准确性评估
- 重构质量评估
- 基准测试用例管理
- 性能指标计算

### 5. 监控系统
- Token 使用跟踪和成本计算
- Agent 性能监控
- 系统资源使用监控

### 6. CodeGraph 图算法分析
- 图算法模式检测（BFS、DFS、Dijkstra、拓扑排序、Floyd-Warshall 等）
- NetworkX 代码检测与最佳实践提示
- 图模型结构识别（邻接矩阵、邻接表、图类定义）
- Java 图算法检测（JGraphT、邻接表、BFS/DFS 等）
- 图代码复杂度与性能风险评估

## 安装

### 环境要求
- Python 3.8+
- Git

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd ai-agent-benchmark

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

## 快速开始

### 基本使用

```python
import asyncio
from agents.coordinator import AgentCoordinator

async def main():
    # 创建协调器
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    try:
        # 审查代码
        result = await coordinator.review_code(
            code="def add(a, b): return a + b",
            language="python"
        )
        
        print(f"审查评分: {result.get('score', 0):.1f}/100")
        print(f"发现的问题: {len(result.get('issues', []))}")
        
    finally:
        await coordinator.shutdown()

# 运行示例
asyncio.run(main())
```

## API 文档

### AgentCoordinator（协调器）

协调器是整个系统的核心，负责管理各个 Agent 并协调它们的工作。

#### 主要方法

```python
class AgentCoordinator:
    def __init__(self, config: dict = None):
        """初始化协调器
        
        Args:
            config: 可选的配置字典，包含各 Agent 的配置
        """
        
    async def initialize(self):
        """初始化所有 Agent"""
        
    async def review_code(self, code: str, language: str = "python", file_path: str = None) -> dict:
        """审查代码
        
        Args:
            code: 待审查的代码
            language: 代码语言 (python/java)
            file_path: 可选的文件路径
            
        Returns:
            包含审查结果的字典
        """
        
    async def refactor_code(self, code: str, language: str = "python", file_path: str = None) -> dict:
        """重构代码
        
        Args:
            code: 待重构的代码
            language: 代码语言
            file_path: 可选的文件路径
            
        Returns:
            包含重构建议的字典
        """
        
    async def full_analysis(self, code: str, language: str = "python", file_path: str = None) -> dict:
        """执行完整分析
        
        Args:
            code: 待分析的代码
            language: 代码语言
            file_path: 可选的文件路径
            
        Returns:
            包含完整分析结果的字典
        """
        
    async def shutdown(self):
        """关闭协调器，释放资源"""
```

### BenchmarkEvaluator（评估器）

评估器用于执行基准测试并计算各种性能指标。

#### 主要方法

```python
class BenchmarkEvaluator:
    def __init__(self):
        """初始化评估器"""
        
    async def evaluate(self, agent, test_cases: List[TestCase], benchmark_name: str = "default") -> BenchmarkReport:
        """执行基准测试
        
        Args:
            agent: 要测试的 Agent 或协调器
            test_cases: 测试用例列表
            benchmark_name: 基准测试名称
            
        Returns:
            基准测试报告
        """
        
    def save_results(self, report: BenchmarkReport, output_dir: str) -> str:
        """保存测试结果
        
        Args:
            report: 基准测试报告
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
```

### TestCase（测试用例）

测试用例数据类，用于定义基准测试的输入和期望输出。

```python
@dataclass
class TestCase:
    id: str                    # 测试用例唯一标识
    name: str                  # 测试用例名称
    description: str           # 测试用例描述
    language: str              # 代码语言 (python/java)
    code: str                  # 待测试的代码
    expected_issues: List[Dict] # 期望发现的问题列表
    expected_score: float      # 期望的评分
    tags: List[str]            # 标签列表
    difficulty: str            # 难度级别 (easy/medium/hard)
    metadata: dict = None      # 额外元数据
```

### SecurityScanner（安全扫描器）

安全扫描器用于检测代码中的安全漏洞。

#### 主要方法

```python
class SecurityScanner:
    def __init__(self):
        """初始化安全扫描器"""
        
    async def scan(self, code: str, language: str = "python", file_path: str = None) -> SecurityScanResult:
        """扫描代码中的安全漏洞
        
        Args:
            code: 待扫描的代码
            language: 代码语言
            file_path: 可选的文件路径
            
        Returns:
            安全扫描结果
        """
```

### TokenMonitor（Token 监控器）

Token 监控器用于跟踪 API 调用的 Token 使用情况。

#### 主要方法

```python
class TokenMonitor:
    def __init__(self):
        """初始化 Token 监控器"""
        
    def record_usage(self, request_id: str, model: str, prompt_tokens: int, 
                     completion_tokens: int, agent_name: str, task_type: str):
        """记录 Token 使用情况
        
        Args:
            request_id: 请求 ID
            model: 使用的模型
            prompt_tokens: 提示 Token 数
            completion_tokens: 完成 Token 数
            agent_name: Agent 名称
            task_type: 任务类型
        """
        
    def get_statistics(self) -> dict:
        """获取使用统计"""
        
    def get_usage(self) -> dict:
        """获取详细使用情况"""
```

### PerformanceMonitor（性能监控器）

性能监控器用于跟踪系统性能指标。

#### 主要方法

```python
class PerformanceMonitor:
    def __init__(self):
        """初始化性能监控器"""
        
    def track(self, operation: str, agent_name: str = None) -> ContextManager:
        """跟踪操作性能
        
        Args:
            operation: 操作名称
            agent_name: Agent 名称
            
        Returns:
            上下文管理器，自动记录执行时间
        """
        
    def get_statistics(self) -> dict:
        """获取性能统计"""
```

### CodeAnalyzer（代码分析器）

代码分析器用于分析代码质量和复杂度。

#### 主要方法

```python
class CodeAnalyzer:
    def __init__(self):
        """初始化代码分析器"""
        
    async def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        """分析代码
        
        Args:
            code: 待分析的代码
            language: 代码语言
            
        Returns:
            分析结果
        """
```

### RefactoringEngine（重构引擎）

重构引擎用于生成代码重构建议。

#### 主要方法

```python
class RefactoringEngine:
    def __init__(self):
        """初始化重构引擎"""
        
    async def refactor(self, code: str, suggestions: List[dict], 
                      language: str = "python") -> RefactoringResult:
        """重构代码
        
        Args:
            code: 原始代码
            suggestions: 重构建议列表
            language: 代码语言
            
        Returns:
            重构结果
        """
```

## 使用示例

### 基础使用示例

```python
from agents.coordinator import AgentCoordinator
from benchmark.evaluator import BenchmarkEvaluator

# 创建协调器
coordinator = AgentCoordinator()

# 运行代码审查
result = coordinator.review_code("path/to/code.py")

# 评估结果
evaluator = BenchmarkEvaluator()
score = evaluator.evaluate(result)
print(f"审查评分: {score}")
```

### 高级使用示例

```python
from agents.coordinator import AgentCoordinator
from core.refactoring_engine import RefactoringEngine
from monitoring.token_monitor import TokenMonitor

# 创建协调器
coordinator = AgentCoordinator()

# 运行多轮审查和重构
code = "path/to/code.py"
review_result = coordinator.review_code(code)

# 如果需要重构
if review_result.needs_refactoring:
    refactoring_engine = RefactoringEngine()
    refactored_code = refactoring_engine.refactor(code, review_result.suggestions)
    
    # 再次审查重构后的代码
    final_review = coordinator.review_code(refactored_code)

# 监控 Token 使用
token_monitor = TokenMonitor()
usage = token_monitor.get_usage()
print(f"Token 使用量: {usage}")
```

### 基准测试示例

```python
from benchmark.evaluator import BenchmarkEvaluator
from benchmark.test_cases.python_tests import PythonTestCases

# 获取测试用例
test_cases = PythonTestCases.get_all_cases()[:5]  # 使用前5个测试用例

# 创建评估器
evaluator = BenchmarkEvaluator()

# 运行基准测试
report = await evaluator.evaluate(
    agent=coordinator,
    test_cases=test_cases,
    benchmark_name="python_benchmark"
)

# 显示结果
print(f"完成测试: {report.completed_cases}/{report.total_test_cases}")
print(f"平均 F1 分数: {report.overall_metrics.get('average_f1_score', 0):.3f}")

# 保存结果
output_file = evaluator.save_results(report, "benchmark/results")
print(f"结果已保存到: {output_file}")
```

### 安全扫描示例

```python
from core.security_scanner import SecurityScanner

# 创建安全扫描器
scanner = SecurityScanner()

# 扫描代码
result = await scanner.scan(
    code="""
import pickle
import subprocess

# 硬编码密码
DB_PASSWORD = "admin123"

def get_user(user_id):
    # SQL 注入漏洞
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)

def execute_command(cmd):
    # 命令注入漏洞
    subprocess.call(cmd, shell=True)

def load_data(data):
    # 不安全的反序列化
    return pickle.loads(data)
""",
    language="python"
)

# 显示结果
print(f"风险分数: {result.risk_score:.1f}/100")
print(f"漏洞数量: {len(result.vulnerabilities)}")

for vuln in result.vulnerabilities[:3]:
    print(f"  - [{vuln.severity.value}] {vuln.title}")
```

### CodeGraph 图算法分析示例

```python
from core.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# 分析包含图算法的代码
code = """
import networkx as nx

def analyze_dependency_graph():
    G = nx.DiGraph()
    G.add_edge("module_a", "module_b")
    G.add_edge("module_b", "module_c")

    # PageRank 分析
    pr = nx.pagerank(G)

    # 最短路径
    path = nx.shortest_path(G, "module_a", "module_c")

    return pr, path
"""

result = await analyzer.analyze(code, "python")

# 查看图算法检测结果
graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
for issue in graph_issues:
    print(f"  [{issue.severity}] {issue.message}")
    if issue.suggestion:
        print(f"    建议: {issue.suggestion}")

# 运行完整演示
# python demo_codegraph.py
```

### 监控示例

```python
from monitoring.token_monitor import TokenMonitor
from monitoring.performance_monitor import PerformanceMonitor

# 初始化监控器
token_monitor = TokenMonitor()
perf_monitor = PerformanceMonitor()

# 记录 Token 使用
token_monitor.record_usage(
    request_id="request_123",
    model="gpt-4",
    prompt_tokens=500,
    completion_tokens=200,
    agent_name="reviewer",
    task_type="review"
)

# 跟踪性能
with perf_monitor.track("code_review", agent_name="reviewer"):
    result = await coordinator.review_code(code, "python")

# 获取统计信息
token_stats = token_monitor.get_statistics()
perf_stats = perf_monitor.get_statistics()

print(f"Token 使用: {token_stats.get('total_tokens', 0)}")
print(f"平均执行时间: {perf_stats.get('average_execution_time', 0):.4f}s")
```

## 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agents.py
pytest tests/test_core.py
pytest tests/test_cinema.py
pytest tests/test_codegraph.py    # CodeGraph 图算法分析测试
pytest tests/test_benchmark.py

# 运行基准测试
python -m benchmark.run
```

## 配置

配置文件位于 `config/settings.py`，可以调整以下参数：

- Agent 配置（模型、参数等）
- 代码分析规则
- 评估指标权重
- 监控设置

## 开发

### 添加新的 Agent

1. 继承 `BaseAgent` 类
2. 实现必要的方法
3. 在 `AgentCoordinator` 中注册

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
    
    def analyze(self, code: str) -> dict:
        # 实现分析逻辑
        pass
```

### 添加新的分析器

1. 继承相应的基类
2. 实现分析方法
3. 在配置中启用

## 贡献

欢迎贡献代码、报告问题或提出建议。

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系项目维护者。