"""
Data models for Code Analyzer.

This module contains all data classes and enums used by the code analyzer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Language(str, Enum):
    """Programming languages."""
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


@dataclass
class CodeMetrics:
    """Code metrics data."""
    lines_of_code: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0
    avg_function_length: float = 0.0
    max_function_length: int = 0
    avg_class_length: float = 0.0
    max_class_length: int = 0
    cyclomatic_complexity: int = 0
    maintainability_index: float = 0.0
    halstead_volume: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "lines_of_code": self.lines_of_code,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "avg_function_length": self.avg_function_length,
            "max_function_length": self.max_function_length,
            "avg_class_length": self.avg_class_length,
            "max_class_length": self.max_class_length,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "maintainability_index": self.maintainability_index,
            "halstead_volume": self.halstead_volume,
        }


@dataclass
class CodeIssue:
    """A code issue."""
    id: str
    severity: str  # "info", "warning", "error", "critical"
    category: str
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "line_number": self.line_number,
            "column": self.column,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
        }


@dataclass
class AnalysisResult:
    """Code analysis result."""
    language: str
    metrics: CodeMetrics
    issues: List[CodeIssue]
    ast_info: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "language": self.language,
            "metrics": self.metrics.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
            "ast_info": self.ast_info,
            "quality_score": self.quality_score,
            "summary": self.summary,
        }