"""
Report Generator for AI Agent Benchmark system.

This module provides comprehensive report generation capabilities including
code quality analysis, trend analysis, and refactoring priority suggestions.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .code_analyzer import CodeAnalyzer, AnalysisResult, CodeIssue
from .security_scanner import SecurityScanner, ScanResult
from .refactoring_engine import RefactoringEngine, RefactoringResult, RefactoringOperation, RefactoringType
from .performance_analyzer import PerformanceAnalyzer, PerformanceAnalysisResult


class ReportFormat(str, Enum):
    """Report output formats."""
    TEXT = "text"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


class IssuePriority(str, Enum):
    """Issue priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityTrend:
    """Code quality trend data point."""
    timestamp: str
    file_path: str
    quality_score: float
    issue_count: int
    vulnerability_count: int
    complexity: int


@dataclass
class RefactoringPriority:
    """Refactoring priority suggestion."""
    operation: RefactoringOperation
    priority: IssuePriority
    reason: str
    estimated_effort: str
    impact_score: float


@dataclass
class ReportSection:
    """A section in the analysis report."""
    title: str
    content: str
    subsections: List['ReportSection'] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisReport:
    """Comprehensive analysis report."""
    project_name: str
    generated_at: str
    summary: ReportSection
    code_quality: ReportSection
    security: ReportSection
    performance: ReportSection
    refactoring: ReportSection
    trends: ReportSection
    priorities: ReportSection
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "summary": self._section_to_dict(self.summary),
            "code_quality": self._section_to_dict(self.code_quality),
            "security": self._section_to_dict(self.security),
            "performance": self._section_to_dict(self.performance),
            "refactoring": self._section_to_dict(self.refactoring),
            "trends": self._section_to_dict(self.trends),
            "priorities": self._section_to_dict(self.priorities),
            "raw_data": self.raw_data,
        }
    
    def _section_to_dict(self, section: ReportSection) -> Dict[str, Any]:
        """Convert section to dictionary."""
        return {
            "title": section.title,
            "content": section.content,
            "subsections": [self._section_to_dict(s) for s in section.subsections],
            "metrics": section.metrics,
        }


class ReportGenerator:
    """Generator for comprehensive analysis reports."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize report generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.code_analyzer = CodeAnalyzer()
        self.security_scanner = SecurityScanner()
        self.refactoring_engine = RefactoringEngine()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Trend history storage
        self.trend_history: List[QualityTrend] = []
        self._load_trend_history()
        
        logger.info("Report generator initialized")
    
    def _load_trend_history(self):
        """Load trend history from file."""
        history_file = self.config.get("trend_history_file", ".quality_trends.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trend_history = [QualityTrend(**item) for item in data]
            except Exception:
                self.trend_history = []
    
    def _save_trend_history(self):
        """Save trend history to file."""
        history_file = self.config.get("trend_history_file", ".quality_trends.json")
        try:
            data = [
                {
                    "timestamp": t.timestamp,
                    "file_path": t.file_path,
                    "quality_score": t.quality_score,
                    "issue_count": t.issue_count,
                    "vulnerability_count": t.vulnerability_count,
                    "complexity": t.complexity,
                }
                for t in self.trend_history
            ]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save trend history: {e}")
    
    async def generate_report(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None,
        project_name: str = "Unknown Project",
        include_raw_data: bool = False
    ) -> AnalysisReport:
        """
        Generate comprehensive analysis report.
        
        Args:
            code: Code to analyze
            language: Programming language
            file_path: Optional file path
            project_name: Name of the project
            include_raw_data: Whether to include raw analysis data
            
        Returns:
            Comprehensive analysis report
        """
        logger.info(f"Generating report for {language} code")
        
        # Run all analyses
        code_result = await self.code_analyzer.analyze(code, language, file_path)
        security_result = await self.security_scanner.scan(code, language, file_path)
        refactoring_result = await self.refactoring_engine.analyze(code, language, file_path)
        performance_result = await self.performance_analyzer.analyze(code, language, file_path)
        
        # Record trend data
        trend = QualityTrend(
            timestamp=datetime.now().isoformat(),
            file_path=file_path or "unknown",
            quality_score=code_result.quality_score,
            issue_count=len(code_result.issues),
            vulnerability_count=len(security_result.vulnerabilities),
            complexity=code_result.metrics.cyclomatic_complexity,
        )
        self.trend_history.append(trend)
        self._save_trend_history()
        
        # Generate report sections
        summary = self._generate_summary_section(
            code_result, security_result, refactoring_result, performance_result
        )
        code_quality = self._generate_code_quality_section(code_result)
        security_section = self._generate_security_section(security_result)
        performance_section = self._generate_performance_section(performance_result)
        refactoring_section = self._generate_refactoring_section(refactoring_result, code_result)
        trends_section = self._generate_trends_section(file_path)
        priorities_section = self._generate_priorities_section(
            code_result, security_result, refactoring_result, performance_result
        )
        
        # Create report
        report = AnalysisReport(
            project_name=project_name,
            generated_at=datetime.now().isoformat(),
            summary=summary,
            code_quality=code_quality,
            security=security_section,
            performance=performance_section,
            refactoring=refactoring_section,
            trends=trends_section,
            priorities=priorities_section,
        )
        
        # Add raw data if requested
        if include_raw_data:
            report.raw_data = {
                "code_analysis": code_result.to_dict(),
                "security_scan": security_result.to_dict(),
                "refactoring_analysis": refactoring_result.to_dict(),
                "performance_analysis": performance_result.to_dict(),
            }
        
        logger.info("Report generation completed")
        return report
    
    def _generate_summary_section(
        self,
        code_result: AnalysisResult,
        security_result: ScanResult,
        refactoring_result: RefactoringResult,
        performance_result: PerformanceAnalysisResult
    ) -> ReportSection:
        """Generate summary section."""
        # Calculate overall score
        code_score = code_result.quality_score
        security_score = max(0, 100 - security_result.risk_score)
        perf_score = performance_result.score
        
        overall_score = (code_score * 0.4 + security_score * 0.3 + perf_score * 0.3)
        
        # Generate summary content
        content_parts = []
        content_parts.append(f"综合评分: {overall_score:.1f}/100")
        content_parts.append("")
        content_parts.append("各维度评分:")
        content_parts.append(f"  - 代码质量: {code_score:.1f}/100")
        content_parts.append(f"  - 安全性: {security_score:.1f}/100")
        content_parts.append(f"  - 性能: {perf_score:.1f}/100")
        content_parts.append("")
        content_parts.append("关键指标:")
        content_parts.append(f"  - 代码行数: {code_result.metrics.lines_of_code}")
        content_parts.append(f"  - 圈复杂度: {code_result.metrics.cyclomatic_complexity}")
        content_parts.append(f"  - 发现问题: {len(code_result.issues)} 个")
        content_parts.append(f"  - 安全漏洞: {len(security_result.vulnerabilities)} 个")
        content_parts.append(f"  - 重构建议: {len(refactoring_result.operations)} 个")
        content_parts.append(f"  - 性能问题: {len(performance_result.issues)} 个")
        
        # Quality grade
        if overall_score >= 90:
            grade = "A (优秀)"
        elif overall_score >= 80:
            grade = "B (良好)"
        elif overall_score >= 70:
            grade = "C (中等)"
        elif overall_score >= 60:
            grade = "D (及格)"
        else:
            grade = "F (需要改进)"
        
        content_parts.append("")
        content_parts.append(f"质量等级: {grade}")
        
        metrics = {
            "overall_score": overall_score,
            "code_score": code_score,
            "security_score": security_score,
            "performance_score": perf_score,
            "grade": grade,
        }
        
        return ReportSection(
            title="综合评估摘要",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _generate_code_quality_section(self, code_result: AnalysisResult) -> ReportSection:
        """Generate code quality section."""
        content_parts = []
        
        # Metrics summary
        content_parts.append("代码度量:")
        content_parts.append(f"  - 总行数: {code_result.metrics.lines_of_code}")
        content_parts.append(f"  - 代码行: {code_result.metrics.code_lines}")
        content_parts.append(f"  - 注释行: {code_result.metrics.comment_lines}")
        content_parts.append(f"  - 空行: {code_result.metrics.blank_lines}")
        content_parts.append(f"  - 函数数: {code_result.metrics.functions}")
        content_parts.append(f"  - 类数: {code_result.metrics.classes}")
        content_parts.append(f"  - 导入数: {code_result.metrics.imports}")
        content_parts.append("")
        
        # Complexity metrics
        content_parts.append("复杂度指标:")
        content_parts.append(f"  - 圈复杂度: {code_result.metrics.cyclomatic_complexity}")
        content_parts.append(f"  - 可维护性指数: {code_result.metrics.maintainability_index:.1f}")
        content_parts.append(f"  - Halstead 体积: {code_result.metrics.halstead_volume:.1f}")
        content_parts.append("")
        
        # Function/Class length
        content_parts.append("长度指标:")
        content_parts.append(f"  - 平均函数长度: {code_result.metrics.avg_function_length:.1f} 行")
        content_parts.append(f"  - 最大函数长度: {code_result.metrics.max_function_length} 行")
        content_parts.append(f"  - 平均类长度: {code_result.metrics.avg_class_length:.1f} 行")
        content_parts.append(f"  - 最大类长度: {code_result.metrics.max_class_length} 行")
        content_parts.append("")
        
        # Issues by category
        if code_result.issues:
            content_parts.append(f"发现问题 ({len(code_result.issues)} 个):")
            
            # Group by category
            categories: Dict[str, List[CodeIssue]] = {}
            for issue in code_result.issues:
                cat = issue.category
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(issue)
            
            for cat, issues in categories.items():
                content_parts.append(f"\n  [{cat}] ({len(issues)} 个)")
                for issue in issues[:3]:  # Show top 3 per category
                    content_parts.append(f"    - [{issue.severity}] {issue.message}")
                    if issue.suggestion:
                        content_parts.append(f"      建议: {issue.suggestion}")
        
        metrics = {
            "lines_of_code": code_result.metrics.lines_of_code,
            "cyclomatic_complexity": code_result.metrics.cyclomatic_complexity,
            "maintainability_index": code_result.metrics.maintainability_index,
            "quality_score": code_result.quality_score,
            "issue_count": len(code_result.issues),
        }
        
        return ReportSection(
            title="代码质量分析",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _generate_security_section(self, security_result: ScanResult) -> ReportSection:
        """Generate security section."""
        content_parts = []
        
        content_parts.append(f"风险评分: {security_result.risk_score:.1f}/100")
        content_parts.append(f"风险等级: {security_result.summary}")
        content_parts.append("")
        
        # Vulnerabilities
        if security_result.vulnerabilities:
            content_parts.append(f"安全漏洞 ({len(security_result.vulnerabilities)} 个):")
            
            # Group by severity
            by_severity: Dict[str, List] = {}
            for vuln in security_result.vulnerabilities:
                sev = vuln.severity.value
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(vuln)
            
            severity_order = ["critical", "high", "medium", "low", "info"]
            for sev in severity_order:
                if sev in by_severity:
                    vulns = by_severity[sev]
                    content_parts.append(f"\n  [{sev.upper()}] ({len(vulns)} 个)")
                    for vuln in vulns[:3]:
                        content_parts.append(f"    - {vuln.title}")
                        if vuln.recommendation:
                            content_parts.append(f"      建议: {vuln.recommendation}")
        
        # Secrets
        if security_result.secrets:
            content_parts.append(f"\n硬编码密钥 ({len(security_result.secrets)} 个):")
            for secret in security_result.secrets[:3]:
                line_content = secret.line_content[:50] if secret.line_content else "N/A"
                content_parts.append(f"  - {secret.type}: {line_content}...")
        
        # Recommendations
        if security_result.recommendations:
            content_parts.append("\n安全建议:")
            for rec in security_result.recommendations[:5]:
                content_parts.append(f"  - {rec}")
        
        metrics = {
            "risk_score": security_result.risk_score,
            "vulnerability_count": len(security_result.vulnerabilities),
            "secret_count": len(security_result.secrets),
        }
        
        return ReportSection(
            title="安全分析",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _generate_performance_section(self, perf_result: PerformanceAnalysisResult) -> ReportSection:
        """Generate performance section."""
        content_parts = []
        
        content_parts.append(f"性能评分: {perf_result.score:.1f}/100")
        content_parts.append(f"时间复杂度: {perf_result.metrics.time_complexity}")
        content_parts.append(f"空间复杂度: {perf_result.metrics.space_complexity}")
        content_parts.append("")
        
        # Performance metrics
        content_parts.append("性能指标:")
        content_parts.append(f"  - 圈复杂度: {perf_result.metrics.cyclomatic_complexity}")
        content_parts.append(f"  - 认知复杂度: {perf_result.metrics.cognitive_complexity}")
        content_parts.append(f"  - 嵌套深度: {perf_result.metrics.nesting_depth}")
        content_parts.append(f"  - 函数数量: {perf_result.metrics.function_count}")
        content_parts.append(f"  - 类数量: {perf_result.metrics.class_count}")
        content_parts.append(f"  - 内存使用估计: {perf_result.metrics.estimated_memory_usage}")
        content_parts.append("")
        
        # Issues
        if perf_result.issues:
            content_parts.append(f"性能问题 ({len(perf_result.issues)} 个):")
            for issue in perf_result.issues[:5]:
                content_parts.append(f"  - [{issue.severity.value}] {issue.title}")
                content_parts.append(f"    {issue.description}")
                if issue.recommendation:
                    content_parts.append(f"    建议: {issue.recommendation}")
        
        # Bottlenecks
        if perf_result.metrics.potential_bottlenecks:
            content_parts.append("\n潜在瓶颈:")
            for bottleneck in perf_result.metrics.potential_bottlenecks:
                content_parts.append(f"  - {bottleneck}")
        
        # Recommendations
        if perf_result.recommendations:
            content_parts.append("\n优化建议:")
            for rec in perf_result.recommendations[:5]:
                content_parts.append(f"  - {rec}")
        
        metrics = {
            "score": perf_result.score,
            "time_complexity": perf_result.metrics.time_complexity,
            "space_complexity": perf_result.metrics.space_complexity,
            "issue_count": len(perf_result.issues),
        }
        
        return ReportSection(
            title="性能分析",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _generate_refactoring_section(
        self,
        refactoring_result: RefactoringResult,
        code_result: AnalysisResult
    ) -> ReportSection:
        """Generate refactoring section."""
        content_parts = []
        
        content_parts.append(f"重构建议总数: {len(refactoring_result.operations)}")
        content_parts.append("")
        
        # Group by type
        by_type: Dict[str, List[RefactoringOperation]] = {}
        for op in refactoring_result.operations:
            op_type = op.type.value
            if op_type not in by_type:
                by_type[op_type] = []
            by_type[op_type].append(op)
        
        type_names = {
            "extract_method": "提取方法",
            "extract_class": "拆分大型类",
            "rename": "重命名",
            "simplify": "简化逻辑",
            "optimize": "性能优化",
            "remove_duplication": "消除重复",
            "modernize": "现代化改造",
            "format": "代码格式化",
        }
        
        for op_type, ops in by_type.items():
            type_name = type_names.get(op_type, op_type)
            content_parts.append(f"[{type_name}] ({len(ops)} 个)")
            for op in ops[:3]:
                content_parts.append(f"  - {op.description}")
                content_parts.append(f"    影响: {op.impact}, 置信度: {op.confidence:.0%}")
            content_parts.append("")
        
        # Key refactoring suggestions
        content_parts.append("关键重构建议:")
        
        # Large class suggestions
        large_class_ops = [op for op in refactoring_result.operations 
                          if op.type.value == "extract_class" and op.impact in ["high", "medium"]]
        if large_class_ops:
            content_parts.append("\n  1. 拆分大型类:")
            for op in large_class_ops[:2]:
                content_parts.append(f"     - {op.description}")
        
        # Extract method suggestions
        extract_ops = [op for op in refactoring_result.operations 
                      if op.type.value == "extract_method"]
        if extract_ops:
            content_parts.append("\n  2. 提取方法:")
            for op in extract_ops[:2]:
                content_parts.append(f"     - {op.description}")
        
        # Exception handling suggestions
        exception_ops = [op for op in refactoring_result.operations 
                        if "exception" in op.description.lower() or "catch" in op.description.lower()]
        if exception_ops:
            content_parts.append("\n  3. 改进异常处理:")
            for op in exception_ops[:2]:
                content_parts.append(f"     - {op.description}")
        
        metrics = {
            "total_operations": len(refactoring_result.operations),
            "type_distribution": {k: len(v) for k, v in by_type.items()},
            "high_impact": sum(1 for op in refactoring_result.operations if op.impact == "high"),
            "medium_impact": sum(1 for op in refactoring_result.operations if op.impact == "medium"),
        }
        
        return ReportSection(
            title="重构建议",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _generate_trends_section(self, file_path: Optional[str]) -> ReportSection:
        """Generate trends section."""
        content_parts = []
        
        # Filter trends for this file
        file_trends = [t for t in self.trend_history if t.file_path == (file_path or "unknown")]
        
        if len(file_trends) < 2:
            content_parts.append("历史数据不足，无法显示趋势。")
            content_parts.append("继续使用分析工具以收集趋势数据。")
        else:
            # Calculate trend
            recent = file_trends[-5:]  # Last 5 data points
            
            scores = [t.quality_score for t in recent]
            issues = [t.issue_count for t in recent]
            vulns = [t.vulnerability_count for t in recent]
            
            # Score trend
            if len(scores) >= 2:
                score_change = scores[-1] - scores[0]
                if score_change > 5:
                    score_trend = "↑ 改善"
                elif score_change < -5:
                    score_trend = "↓ 下降"
                else:
                    score_trend = "→ 稳定"
            else:
                score_trend = "→ 稳定"
            
            content_parts.append(f"质量趋势: {score_trend}")
            content_parts.append(f"  当前评分: {scores[-1]:.1f}")
            content_parts.append(f"  历史评分: {scores[0]:.1f}")
            content_parts.append(f"  变化: {scores[-1] - scores[0]:+.1f}")
            content_parts.append("")
            
            # Issue trend
            if len(issues) >= 2:
                issue_change = issues[-1] - issues[0]
                if issue_change < -2:
                    issue_trend = "↓ 改善"
                elif issue_change > 2:
                    issue_trend = "↑ 恶化"
                else:
                    issue_trend = "→ 稳定"
            else:
                issue_trend = "→ 稳定"
            
            content_parts.append(f"问题趋势: {issue_trend}")
            content_parts.append(f"  当前问题数: {issues[-1]}")
            content_parts.append(f"  历史问题数: {issues[0]}")
            content_parts.append("")
            
            # Data points
            content_parts.append("历史数据点:")
            for t in recent:
                content_parts.append(
                    f"  - {t.timestamp[:19]}: 评分 {t.quality_score:.1f}, "
                    f"问题 {t.issue_count}, 漏洞 {t.vulnerability_count}"
                )
        
        metrics = {
            "data_points": len(file_trends),
            "has_trend": len(file_trends) >= 2,
        }
        
        return ReportSection(
            title="代码质量趋势",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _generate_priorities_section(
        self,
        code_result: AnalysisResult,
        security_result: ScanResult,
        refactoring_result: RefactoringResult,
        performance_result: PerformanceAnalysisResult
    ) -> ReportSection:
        """Generate refactoring priorities section."""
        content_parts = []
        
        priorities = self._calculate_priorities(
            code_result, security_result, refactoring_result, performance_result
        )
        
        content_parts.append("按优先级排序的改进建议:")
        content_parts.append("")
        
        # Group by priority
        by_priority: Dict[str, List[RefactoringPriority]] = {}
        for p in priorities:
            pri = p.priority.value
            if pri not in by_priority:
                by_priority[pri] = []
            by_priority[pri].append(p)
        
        priority_order = ["critical", "high", "medium", "low", "info"]
        for pri in priority_order:
            if pri in by_priority:
                items = by_priority[pri]
                content_parts.append(f"[{pri.upper()}] ({len(items)} 项)")
                for item in items[:3]:
                    content_parts.append(f"  - {item.operation.description}")
                    content_parts.append(f"    原因: {item.reason}")
                    content_parts.append(f"    预计工作量: {item.estimated_effort}")
                    content_parts.append(f"    影响分数: {item.impact_score:.1f}")
                content_parts.append("")
        
        # Summary
        content_parts.append(f"总计: {len(priorities)} 项改进建议")
        critical_count = len(by_priority.get("critical", []))
        high_count = len(by_priority.get("high", []))
        content_parts.append(f"  - 严重/高优先级: {critical_count + high_count} 项 (建议立即处理)")
        content_parts.append(f"  - 中优先级: {len(by_priority.get('medium', []))} 项 (建议近期处理)")
        content_parts.append(f"  - 低优先级: {len(by_priority.get('low', [])) + len(by_priority.get('info', []))} 项 (可选改进)")
        
        metrics = {
            "total_priorities": len(priorities),
            "critical": critical_count,
            "high": high_count,
            "medium": len(by_priority.get("medium", [])),
            "low": len(by_priority.get("low", [])) + len(by_priority.get("info", [])),
        }
        
        return ReportSection(
            title="重构优先级建议",
            content="\n".join(content_parts),
            metrics=metrics,
        )
    
    def _calculate_priorities(
        self,
        code_result: AnalysisResult,
        security_result: ScanResult,
        refactoring_result: RefactoringResult,
        performance_result: PerformanceAnalysisResult
    ) -> List[RefactoringPriority]:
        """Calculate refactoring priorities based on all analysis results."""
        priorities = []
        
        # Security issues are highest priority
        for vuln in security_result.vulnerabilities:
            if vuln.severity.value in ["critical", "high"]:
                priorities.append(RefactoringPriority(
                    operation=RefactoringOperation(
                        id=f"security_{vuln.id}",
                        type=RefactoringType.SIMPLIFY,
                        description=f"修复安全漏洞: {vuln.title}",
                    ),
                    priority=IssuePriority.CRITICAL if vuln.severity.value == "critical" else IssuePriority.HIGH,
                    reason=f"安全漏洞可能导致系统被攻击: {vuln.description}",
                    estimated_effort="中等",
                    impact_score=90.0 if vuln.severity.value == "critical" else 75.0,
                ))
        
        # Critical code issues
        for issue in code_result.issues:
            if issue.severity == "critical":
                priorities.append(RefactoringPriority(
                    operation=RefactoringOperation(
                        id=f"code_{issue.id}",
                        type=RefactoringType.SIMPLIFY,
                        description=f"修复代码问题: {issue.message}",
                    ),
                    priority=IssuePriority.CRITICAL,
                    reason=f"严重代码问题影响系统稳定性: {issue.message}",
                    estimated_effort="中等",
                    impact_score=85.0,
                ))
        
        # High impact refactoring operations
        for op in refactoring_result.operations:
            if op.impact == "high":
                priorities.append(RefactoringPriority(
                    operation=op,
                    priority=IssuePriority.HIGH,
                    reason=f"高影响重构: {op.description}",
                    estimated_effort="高" if "class" in op.type.value else "中等",
                    impact_score=70.0,
                ))
        
        # Performance critical issues
        for issue in performance_result.issues:
            if issue.severity.value in ["high", "critical"]:
                priorities.append(RefactoringPriority(
                    operation=RefactoringOperation(
                        id=f"perf_{issue.id}",
                        type=RefactoringType.OPTIMIZE,
                        description=f"优化性能问题: {issue.title}",
                    ),
                    priority=IssuePriority.HIGH if issue.severity.value == "high" else IssuePriority.CRITICAL,
                    reason=f"性能问题: {issue.description}",
                    estimated_effort="中等",
                    impact_score=65.0,
                ))
        
        # Medium priority items
        for issue in code_result.issues:
            if issue.severity == "warning":
                priorities.append(RefactoringPriority(
                    operation=RefactoringOperation(
                        id=f"code_warn_{issue.id}",
                        type=RefactoringType.MODERNIZE,
                        description=f"改进代码: {issue.message}",
                    ),
                    priority=IssuePriority.MEDIUM,
                    reason=f"代码改进建议: {issue.suggestion or issue.message}",
                    estimated_effort="低",
                    impact_score=40.0,
                ))
        
        # Sort by impact score
        priorities.sort(key=lambda x: x.impact_score, reverse=True)
        
        return priorities
    
    def export_report(
        self,
        report: AnalysisReport,
        output_path: str,
        format: ReportFormat = ReportFormat.TEXT
    ) -> str:
        """
        Export report to file.
        
        Args:
            report: Analysis report
            output_path: Output file path
            format: Output format
            
        Returns:
            Path to exported file
        """
        if format == ReportFormat.JSON:
            content = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        elif format == ReportFormat.MARKDOWN:
            content = self._to_markdown(report)
        elif format == ReportFormat.HTML:
            content = self._to_html(report)
        else:
            content = self._to_text(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Report exported to {output_path}")
        return output_path
    
    def _to_text(self, report: AnalysisReport) -> str:
        """Convert report to text format."""
        lines = []
        lines.append("=" * 70)
        lines.append(f"  {report.project_name} - 代码分析报告")
        lines.append("=" * 70)
        lines.append(f"  生成时间: {report.generated_at}")
        lines.append("")
        
        for section in [report.summary, report.code_quality, report.security,
                       report.performance, report.refactoring, report.trends,
                       report.priorities]:
            lines.append("-" * 70)
            lines.append(f"  {section.title}")
            lines.append("-" * 70)
            lines.append(section.content)
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def _to_markdown(self, report: AnalysisReport) -> str:
        """Convert report to Markdown format."""
        lines = []
        lines.append(f"# {report.project_name} - 代码分析报告")
        lines.append("")
        lines.append(f"**生成时间:** {report.generated_at}")
        lines.append("")
        
        for section in [report.summary, report.code_quality, report.security,
                       report.performance, report.refactoring, report.trends,
                       report.priorities]:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.content)
            lines.append("")
        
        return "\n".join(lines)
    
    def _to_html(self, report: AnalysisReport) -> str:
        """Convert report to HTML format."""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{report.project_name} - 代码分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .metric {{ font-weight: bold; color: #0066cc; }}
    </style>
</head>
<body>
    <h1>{report.project_name} - 代码分析报告</h1>
    <p><strong>生成时间:</strong> {report.generated_at}</p>
"""
        
        for section in [report.summary, report.code_quality, report.security,
                       report.performance, report.refactoring, report.trends,
                       report.priorities]:
            html += f"""
    <div class="section">
        <h2>{section.title}</h2>
        <pre>{section.content}</pre>
    </div>
"""
        
        html += """
</body>
</html>"""
        return html


# Add logger import
import logging
logger = logging.getLogger(__name__)
