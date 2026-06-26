"""
Core module for AI Agent Benchmark system.

This module provides the core analysis engines for code analysis,
refactoring, security scanning, performance analysis, and report generation.
"""

from .code_analyzer import CodeAnalyzer
from .code_analyzer_v2 import CodeAnalyzer as CodeAnalyzerV2
from .refactoring_engine import RefactoringEngine
from .security_scanner import SecurityScanner
from .performance_analyzer import PerformanceAnalyzer
from .report_generator import ReportGenerator
from .models import Language, CodeMetrics, CodeIssue, AnalysisResult

# 导入语言特定的分析器
from .python_analyzer import PythonAnalyzer
from .java_analyzer import JavaAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer

# Import new modules
from .auto_fixer import AutoFixer, Fix, FixResult
from .llm_analyzer import LLMAnalyzer, LLMAnalysisResult

__all__ = [
    "CodeAnalyzer",
    "CodeAnalyzerV2",
    "RefactoringEngine",
    "SecurityScanner",
    "PerformanceAnalyzer",
    "ReportGenerator",
    "Language",
    "CodeMetrics",
    "CodeIssue",
    "AnalysisResult",
    "PythonAnalyzer",
    "JavaAnalyzer",
    "JavaScriptAnalyzer",
    "AutoFixer",
    "Fix",
    "FixResult",
    "LLMAnalyzer",
    "LLMAnalysisResult",
]