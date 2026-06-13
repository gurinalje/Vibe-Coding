"""
Reviewer Agent for AI Agent Benchmark system.

This agent is responsible for code quality review, including
code analysis, quality assessment, and review report generation.
"""

import asyncio
import re
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)


class ReviewSeverity(str, Enum):
    """Review issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ReviewIssue:
    """A code review issue."""
    id: str
    severity: ReviewSeverity
    category: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
        }


@dataclass
class ReviewResult:
    """Code review result."""
    score: float
    issues: List[ReviewIssue]
    summary: str
    recommendations: List[str]
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
        }


class ReviewerAgent(BaseAgent):
    """Agent responsible for code review."""
    
    def __init__(
        self,
        name: str = "reviewer",
        message_queue=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize reviewer agent."""
        super().__init__(name=name, agent_type="reviewer", message_queue=message_queue, config=config)
        
        # Review rules
        self.review_rules = self._load_review_rules()
        
        # Statistics
        self.reviews_completed = 0
        self.issues_found = 0
    
    def _load_review_rules(self) -> Dict[str, Any]:
        """Load review rules."""
        return {
            "python": {
                "max_line_length": 88,
                "max_function_length": 50,
                "max_class_methods": 20,
                "naming_conventions": {
                    "function": r"^[a-z_][a-z0-9_]*$",
                    "class": r"^[A-Z][a-zA-Z0-9]*$",
                    "variable": r"^[a-z_][a-z0-9_]*$",
                    "constant": r"^[A-Z_][A-Z0-9_]*$",
                },
                "forbidden_patterns": [
                    (r"except\s*:", "使用裸 except 子句"),
                    (r"eval\s*\(", "使用 eval() 函数"),
                    (r"exec\s*\(", "使用 exec() 函数"),
                    (r"from\s+\w+\s+import\s+\*", "使用通配符导入"),
                ],
            },
            "java": {
                "max_line_length": 120,
                "max_function_length": 40,
                "max_class_methods": 25,
                "naming_conventions": {
                    "method": r"^[a-z][a-zA-Z0-9]*$",
                    "class": r"^[A-Z][a-zA-Z0-9]*$",
                    "variable": r"^[a-z][a-zA-Z0-9]*$",
                    "constant": r"^[A-Z_][A-Z0-9_]*$",
                },
                "forbidden_patterns": [
                    (r"System\.out\.print", "使用 System.out.print"),
                    (r"catch\s*\(\s*Exception\s+", "捕获通用 Exception"),
                ],
            },
        }
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a code review task.
        
        Args:
            task: Task data containing code to review
            
        Returns:
            Review result
        """
        code = task.get("code", "")
        language = task.get("language", "python")
        file_path = task.get("file_path")
        
        logger.info(f"Reviewing {language} code ({len(code)} chars)")
        
        # Perform review
        review_result = await self._review_code(code, language, file_path)
        
        # Update statistics
        self.reviews_completed += 1
        self.issues_found += len(review_result.issues)
        
        return review_result.to_dict()
    
    async def _review_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> ReviewResult:
        """
        Review code and generate result.
        
        Args:
            code: Code to review
            language: Programming language
            file_path: Optional file path
            
        Returns:
            Review result
        """
        issues = []
        
        # Get rules for language
        rules = self.review_rules.get(language, {})
        
        # Check line length
        line_issues = self._check_line_length(code, rules.get("max_line_length", 88))
        issues.extend(line_issues)
        
        # Check function length
        func_issues = self._check_function_length(code, language, rules.get("max_function_length", 50))
        issues.extend(func_issues)
        
        # Check naming conventions
        naming_issues = self._check_naming_conventions(code, language, rules.get("naming_conventions", {}))
        issues.extend(naming_issues)
        
        # Check forbidden patterns
        pattern_issues = self._check_forbidden_patterns(code, rules.get("forbidden_patterns", []))
        issues.extend(pattern_issues)
        
        # Check complexity
        complexity_issues = self._check_complexity(code, language)
        issues.extend(complexity_issues)
        
        # Check documentation
        doc_issues = self._check_documentation(code, language)
        issues.extend(doc_issues)
        
        # Calculate score
        score = self._calculate_score(issues, len(code.split("\n")))
        
        # Generate summary
        summary = self._generate_summary(issues, score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code, language, issues)
        
        return ReviewResult(
            score=score,
            issues=issues,
            summary=summary,
            recommendations=recommendations,
            metrics=metrics,
        )
    
    def _check_line_length(self, code: str, max_length: int) -> List[ReviewIssue]:
        """Check line length."""
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append(ReviewIssue(
                    id=f"line_length_{i}",
                    severity=ReviewSeverity.WARNING,
                    category="style",
                    message=f"行长度超过 {max_length} 字符 (当前: {len(line)})",
                    line_number=i,
                    code_snippet=line[:100] + "..." if len(line) > 100 else line,
                    suggestion=f"将行长度限制在 {max_length} 字符以内",
                ))
        
        return issues
    
    def _check_function_length(
        self,
        code: str,
        language: str,
        max_length: int
    ) -> List[ReviewIssue]:
        """Check function length."""
        issues = []
        
        if language == "python":
            # Simple Python function length check
            lines = code.split("\n")
            current_func = None
            func_start = 0
            
            for i, line in enumerate(lines, 1):
                if re.match(r"^\s*def\s+", line):
                    if current_func and (i - func_start) > max_length:
                        issues.append(ReviewIssue(
                            id=f"func_length_{func_start}",
                            severity=ReviewSeverity.WARNING,
                            category="complexity",
                            message=f"函数 {current_func} 过长 ({i - func_start} 行)",
                            line_number=func_start,
                            suggestion="考虑将函数拆分为更小的函数",
                        ))
                    current_func = line.strip()
                    func_start = i
            
            # Check last function
            if current_func and (len(lines) - func_start + 1) > max_length:
                issues.append(ReviewIssue(
                    id=f"func_length_{func_start}",
                    severity=ReviewSeverity.WARNING,
                    category="complexity",
                    message=f"函数 {current_func} 过长 ({len(lines) - func_start + 1} 行)",
                    line_number=func_start,
                    suggestion="考虑将函数拆分为更小的函数",
                ))
        
        return issues
    
    def _check_naming_conventions(
        self,
        code: str,
        language: str,
        conventions: Dict[str, str]
    ) -> List[ReviewIssue]:
        """Check naming conventions."""
        issues = []
        
        if language == "python":
            # Check function names
            func_pattern = r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
            for match in re.finditer(func_pattern, code, re.MULTILINE):
                func_name = match.group(1)
                if not re.match(conventions.get("function", r"^[a-z_][a-z0-9_]*$"), func_name):
                    issues.append(ReviewIssue(
                        id=f"naming_func_{func_name}",
                        severity=ReviewSeverity.INFO,
                        category="naming",
                        message=f"函数名 '{func_name}' 不符合命名规范",
                        suggestion="使用小写字母和下划线命名函数",
                    ))
            
            # Check class names
            class_pattern = r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]"
            for match in re.finditer(class_pattern, code, re.MULTILINE):
                class_name = match.group(1)
                if not re.match(conventions.get("class", r"^[A-Z][a-zA-Z0-9]*$"), class_name):
                    issues.append(ReviewIssue(
                        id=f"naming_class_{class_name}",
                        severity=ReviewSeverity.INFO,
                        category="naming",
                        message=f"类名 '{class_name}' 不符合命名规范",
                        suggestion="使用驼峰命名法命名类",
                    ))
        
        return issues
    
    def _check_forbidden_patterns(
        self,
        code: str,
        patterns: List[Tuple[str, str]]
    ) -> List[ReviewIssue]:
        """Check forbidden patterns."""
        issues = []
        
        for i, line in enumerate(code.split("\n"), 1):
            for pattern, message in patterns:
                if re.search(pattern, line):
                    issues.append(ReviewIssue(
                        id=f"forbidden_{i}_{pattern}",
                        severity=ReviewSeverity.WARNING,
                        category="best_practice",
                        message=f"发现不推荐的用法: {message}",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="避免使用此模式",
                    ))
        
        return issues
    
    def _check_complexity(self, code: str, language: str) -> List[ReviewIssue]:
        """Check code complexity."""
        issues = []
        
        # Simple complexity check based on indentation and nesting
        lines = code.split("\n")
        max_indent = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
                
                # Check for deep nesting (more than 4 levels)
                if indent > 16:  # 4 levels * 4 spaces
                    issues.append(ReviewIssue(
                        id=f"nesting_{i}",
                        severity=ReviewSeverity.WARNING,
                        category="complexity",
                        message="代码嵌套过深",
                        line_number=i,
                        code_snippet=line.strip()[:50],
                        suggestion="考虑重构以减少嵌套层级",
                    ))
        
        return issues
    
    def _check_documentation(self, code: str, language: str) -> List[ReviewIssue]:
        """Check documentation."""
        issues = []
        
        if language == "python":
            # Check for missing docstrings
            func_pattern = r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
            for match in re.finditer(func_pattern, code, re.MULTILINE):
                func_name = match.group(1)
                if func_name.startswith("_") and func_name != "__init__":
                    continue
                
                # Check if docstring follows
                func_end = match.end()
                next_lines = code[func_end:func_end+200].split("\n")[:3]
                
                has_docstring = False
                for next_line in next_lines:
                    stripped = next_line.strip()
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        has_docstring = True
                        break
                
                if not has_docstring:
                    issues.append(ReviewIssue(
                        id=f"docstring_{func_name}",
                        severity=ReviewSeverity.INFO,
                        category="documentation",
                        message=f"函数 '{func_name}' 缺少文档字符串",
                        suggestion="添加函数文档字符串说明其用途",
                    ))
        
        return issues
    
    def _calculate_score(self, issues: List[ReviewIssue], line_count: int) -> float:
        """Calculate review score (0-100)."""
        if line_count == 0:
            return 100.0
        
        # Base score
        score = 100.0
        
        # Deductions for issues
        deductions = {
            ReviewSeverity.INFO: 0.5,
            ReviewSeverity.WARNING: 2.0,
            ReviewSeverity.ERROR: 5.0,
            ReviewSeverity.CRITICAL: 10.0,
        }
        
        for issue in issues:
            score -= deductions.get(issue.severity, 1.0)
        
        # Normalize by line count (more issues per line = worse)
        issue_density = len(issues) / line_count
        if issue_density > 0.1:
            score *= 0.9
        elif issue_density > 0.05:
            score *= 0.95
        
        return max(0.0, min(100.0, score))
    
    def _generate_summary(self, issues: List[ReviewIssue], score: float) -> str:
        """Generate review summary."""
        if not issues:
            return "代码质量优秀，没有发现明显问题。"
        
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        summary_parts = []
        if ReviewSeverity.CRITICAL in severity_counts:
            summary_parts.append(f"发现 {severity_counts[ReviewSeverity.CRITICAL]} 个严重问题")
        if ReviewSeverity.ERROR in severity_counts:
            summary_parts.append(f"发现 {severity_counts[ReviewSeverity.ERROR]} 个错误")
        if ReviewSeverity.WARNING in severity_counts:
            summary_parts.append(f"发现 {severity_counts[ReviewSeverity.WARNING]} 个警告")
        if ReviewSeverity.INFO in severity_counts:
            summary_parts.append(f"发现 {severity_counts[ReviewSeverity.INFO]} 个提示")
        
        return f"代码审查完成。{'，'.join(summary_parts)}。总体评分: {score:.1f}/100"
    
    def _generate_recommendations(self, issues: List[ReviewIssue]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        # Group issues by category
        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)
        
        # Generate recommendations for each category
        if "complexity" in categories:
            recommendations.append("考虑重构复杂代码以提高可读性和可维护性")
        
        if "naming" in categories:
            recommendations.append("遵循一致的命名规范以提高代码可读性")
        
        if "documentation" in categories:
            recommendations.append("添加文档字符串以提高代码可理解性")
        
        if "style" in categories:
            recommendations.append("使用代码格式化工具保持代码风格一致")
        
        if "best_practice" in categories:
            recommendations.append("避免使用不推荐的模式，遵循最佳实践")
        
        return recommendations
    
    def _calculate_metrics(
        self,
        code: str,
        language: str,
        issues: List[ReviewIssue]
    ) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines = code.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Count different types of lines
        comment_lines = 0
        code_lines = 0
        blank_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif language == "python" and stripped.startswith("#"):
                comment_lines += 1
            elif language == "java" and (stripped.startswith("//") or stripped.startswith("/*")):
                comment_lines += 1
            else:
                code_lines += 1
        
        # Calculate metrics
        metrics = {
            "total_lines": len(lines),
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "comment_ratio": comment_lines / max(1, code_lines),
            "issue_count": len(issues),
            "issues_per_100_lines": (len(issues) / max(1, code_lines)) * 100,
        }
        
        return metrics