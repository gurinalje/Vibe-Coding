"""
Code Analyzer for AI Agent Benchmark system.

This module provides code analysis capabilities including AST parsing,
code quality detection, and metrics calculation.

This is the refactored version that uses separate analyzers for each language.
"""

from typing import Any, Dict, Optional
import logging

from .models import Language, AnalysisResult
from .python_analyzer import PythonAnalyzer
from .java_analyzer import JavaAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Code analyzer for multiple programming languages."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize code analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize language-specific analyzers
        self.analyzers = {
            Language.PYTHON: PythonAnalyzer(config),
            Language.JAVA: JavaAnalyzer(config),
            Language.JAVASCRIPT: JavaScriptAnalyzer(config),
            Language.TYPESCRIPT: JavaScriptAnalyzer(config),
        }
        
        logger.info("Code analyzer initialized")
    
    async def analyze(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze code.
        
        Args:
            code: Code to analyze
            language: Programming language
            file_path: Optional file path
            
        Returns:
            Analysis result
        """
        try:
            lang = Language(language)
        except ValueError:
            raise ValueError(f"Unsupported language: {language}")
        analyzer = self.analyzers.get(lang)
        
        if not analyzer:
            raise ValueError(f"Unsupported language: {language}")
        
        logger.info(f"Analyzing {language} code ({len(code)} chars)")
        result = await analyzer.analyze(code, file_path)
        
        # Calculate quality score
        result.quality_score = self._calculate_quality_score(result)
        
        # Generate summary
        result.summary = self._generate_summary(result)
        
        logger.info(f"Analysis completed. Quality score: {result.quality_score:.1f}/100")
        return result
    
    def _calculate_quality_score(self, result: AnalysisResult) -> float:
        """Calculate quality score from metrics and issues."""
        # Start with maintainability index
        score = result.metrics.maintainability_index
        
        # Penalize for issues
        for issue in result.issues:
            if issue.severity == "critical":
                score -= 20
            elif issue.severity == "error":
                score -= 10
            elif issue.severity == "warning":
                score -= 5
            elif issue.severity == "info":
                score -= 1
        
        # Bonus for good practices
        if result.metrics.comment_lines > 0:
            score += 5
        if result.metrics.cyclomatic_complexity <= 5:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def _generate_summary(self, result: AnalysisResult) -> str:
        """Generate summary from analysis result."""
        parts = []
        
        # Language info
        parts.append(f"语言: {result.language}")
        
        # Metrics summary
        parts.append(f"代码行数: {result.metrics.code_lines}")
        parts.append(f"函数数量: {result.metrics.functions}")
        parts.append(f"类数量: {result.metrics.classes}")
        
        # Complexity
        parts.append(f"圈复杂度: {result.metrics.cyclomatic_complexity}")
        parts.append(f"可维护性指数: {result.metrics.maintainability_index:.1f}")
        
        # Issues summary
        if result.issues:
            critical_count = sum(1 for i in result.issues if i.severity == "critical")
            error_count = sum(1 for i in result.issues if i.severity == "error")
            warning_count = sum(1 for i in result.issues if i.severity == "warning")
            
            if critical_count > 0:
                parts.append(f"严重问题: {critical_count}")
            if error_count > 0:
                parts.append(f"错误: {error_count}")
            if warning_count > 0:
                parts.append(f"警告: {warning_count}")
        
        return " | ".join(parts)