# AI Agent Benchmark - Multi-Agent Collaborative Code Review System

<div align="center">

**[English](README_EN.md) | [中文](README.md)**

</div>

**Last Updated:** 2026-06-13

---

## Project Overview

A comprehensive **AI-powered code review and refactoring system** that implements multi-agent collaborative architecture for automated code analysis, security scanning, performance optimization, and code quality assessment.

This project serves as a **benchmark platform** for evaluating AI capabilities in code understanding, review, and refactoring tasks.

---

## Key Features

### Multi-Agent Architecture

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Reviewer Agent** | Code Quality Guardian | Identifies code smells, anti-patterns, and coding standard violations |
| **Developer Agent** | Refactoring Executor | Executes safe code refactoring and verifies results |
| **Critic Agent** | Review Quality Evaluator | Evaluates review accuracy, detects false positives/negatives |

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **Code Analysis** | AST parsing, code metrics (cyclomatic complexity, maintainability), code smell detection |
| **Security Scanning** | Vulnerability detection (SQL injection, XSS, command injection), secret scanning |
| **Performance Analysis** | Complexity analysis, bottleneck identification, optimization suggestions |
| **Refactoring Engine** | Refactoring opportunity detection, safe execution, result verification |
| **Architecture Analysis** | Circular dependency detection, God Class identification, Feature Envy detection |
| **Graph Algorithms** | PageRank, betweenness centrality, community detection |

### Evaluation System

| Feature | Description |
|---------|-------------|
| **Benchmark Testing** | Pre-built test cases for Java, Python, and JavaScript |
| **Metrics Calculation** | Precision, recall, F1-score, token efficiency |
| **Configuration Comparison** | Compare different agent configurations |
| **Report Generation** | Comprehensive analysis reports in multiple formats |

### Monitoring System

| Feature | Description |
|---------|-------------|
| **Token Monitoring** | Track token usage, cost analysis, efficiency patterns |
| **Performance Monitoring** | Bottleneck identification, percentile statistics |
| **Cost Analysis** | Cost-per-issue, budget compliance tracking |

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core Language |
| NetworkX | Latest | Graph Algorithms |
| FastAPI | Latest | Web API Server |
| Click | Latest | CLI Interface |
| PyYAML | Latest | Configuration |
| aiofiles | Latest | Async File Operations |

---

## Project Structure

```
ai-agent-benchmark/
├── README.md                    # Project Documentation
├── requirements.txt             # Python Dependencies
├── setup.py                     # Installation Script
├── config/                      # Configuration Module
│   ├── settings.py             # Global Settings
│   └── logging_config.py       # Logging Configuration
├── agents/                      # Agent Module
│   ├── base_agent.py           # Agent Base Class
│   ├── reviewer_agent.py       # Code Reviewer Agent
│   ├── developer_agent.py      # Refactoring Developer Agent
│   ├── critic_agent.py         # Review Quality Critic Agent
│   └── coordinator.py          # Agent Coordinator
├── core/                        # Core Analysis Module
│   ├── code_analyzer.py        # Code Analysis Engine
│   ├── security_scanner.py     # Security Vulnerability Scanner
│   ├── performance_analyzer.py # Performance Analyzer
│   ├── refactoring_engine.py   # Refactoring Engine
│   ├── architecture_analyzer.py # Architecture Analyzer
│   ├── report_generator.py     # Report Generator
│   └── query_engine.py         # Query Engine
├── graph/                       # Graph Analysis Module
│   ├── models.py               # Graph Data Models
│   ├── algorithms.py           # Graph Algorithms
│   └── storage.py              # Graph Storage
├── benchmark/                   # Evaluation Benchmark
│   ├── evaluator.py            # Benchmark Evaluator
│   ├── metrics.py              # Metrics Calculator
│   └── test_cases/             # Test Cases
├── monitoring/                  # Monitoring System
│   ├── token_monitor.py        # Token Usage Monitor
│   └── performance_monitor.py  # Performance Monitor
├── visualization/               # Visualization Module
│   └── renderer.py             # Interactive Visualization
├── api/                         # Web API Server
│   └── server.py               # FastAPI Server
├── cli/                         # Command Line Interface
│   └── main.py                 # CLI Tool
├── examples/                    # Example Scripts
│   ├── basic_usage.py          # Basic Usage Examples
│   └── advanced_usage.py       # Advanced Usage Examples
└── tests/                       # Test Suite
    ├── test_agents.py          # Agent Tests
    ├── test_core.py            # Core Module Tests
    ├── test_benchmark.py       # Benchmark Tests
    └── test_codegraph.py       # CodeGraph Analysis Tests
```

---

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/gurinalje/Vibe-Coding.git
cd Vibe-Coding

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

```python
import asyncio
from agents.coordinator import AgentCoordinator

async def main():
    # Create agent coordinator
    coordinator = AgentCoordinator()
    
    # Code to review
    code = """
    def authenticate_user(username, password):
        # Hardcoded password (security issue)
        admin_password = "admin123"
        if username == "admin" and password == admin_password:
            return True
        return False
    """
    
    # Run review cycle
    result = await coordinator.review_code(code, "python")
    print(f"Found {len(result.get('comments', []))} issues")

asyncio.run(main())
```

### Run Demo

```bash
# Basic demo
python demo.py

# CodeGraph analysis demo
python demo_codegraph.py

# Cinema system analysis demo
python demo_cinema.py
```

### CLI Usage

```bash
# Analyze code
python -m cli.main analyze /path/to/code

# Check architecture issues
python -m cli.main check /path/to/code

# Query code
python -m cli.main query /path/to/code "find all classes"

# Generate visualization
python -m cli.main visualize /path/to/code

# Start web server
python -m cli.main serve
```

---

## API Reference

### Agent Coordinator

```python
# Review code
result = await coordinator.review_code(code, language="python")

# Refactor code
result = await coordinator.refactor_code(code, language="python")

# Run full review cycle
result = await coordinator.run_review_cycle(code, language="python")
```

### Code Analyzer

```python
from core.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
result = await analyzer.analyze(code, "python")

print(f"Lines of code: {result.metrics.lines_of_code}")
print(f"Cyclomatic complexity: {result.metrics.cyclomatic_complexity}")
print(f"Quality score: {result.quality_score}")
```

### Security Scanner

```python
from core.security_scanner import SecurityScanner

scanner = SecurityScanner()
result = await scanner.scan(code, "python")

print(f"Vulnerabilities found: {len(result.vulnerabilities)}")
print(f"Risk score: {result.risk_score}")
```

---

## Test Cases

### Run All Tests

```bash
pytest tests/ -v
```

### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| Core Module | 18 | Code analyzer, security scanner, refactoring engine |
| Agent Tests | 16 | Reviewer, Developer, Critic agents |
| Benchmark Tests | 16 | Evaluation metrics, benchmark execution |
| CodeGraph Tests | 20 | Graph algorithm detection, NetworkX patterns |

---

## Benchmark Results

### Supported Languages

| Language | Support Level | Features |
|----------|---------------|----------|
| Python | Full | AST parsing, code metrics, security scanning |
| Java | Full | Regex parsing, architecture analysis |
| JavaScript | Partial | Basic analysis, security scanning |

### Detection Capabilities

| Category | Patterns Detected |
|----------|-------------------|
| Code Smells | Long methods, deep nesting, god classes, feature envy |
| Security | SQL injection, XSS, command injection, hardcoded secrets |
| Performance | N+1 queries, string concatenation, memory issues |
| Architecture | Circular dependencies, tight coupling, low cohesion |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is for learning and research purposes only.
