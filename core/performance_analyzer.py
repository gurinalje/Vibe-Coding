"""
Performance Analyzer for AI Agent Benchmark system.

This module provides performance analysis capabilities including
complexity analysis, resource usage estimation, and optimization suggestions.
"""

import re
import math
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceIssueType(str, Enum):
    """Types of performance issues."""
    ALGORITHMIC = "algorithmic"
    MEMORY = "memory"
    I_O = "io"
    NETWORK = "network"
    DATABASE = "database"
    CACHING = "caching"
    CONCURRENCY = "concurrency"
    OPTIMIZATION = "optimization"


class PerformanceSeverity(str, Enum):
    """Performance issue severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceIssue:
    """A performance issue."""
    id: str
    type: PerformanceIssueType
    severity: PerformanceSeverity
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    impact: Optional[str] = None
    recommendation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "impact": self.impact,
            "recommendation": self.recommendation,
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    nesting_depth: int = 0
    function_count: int = 0
    class_count: int = 0
    estimated_memory_usage: str = "low"
    potential_bottlenecks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "cognitive_complexity": self.cognitive_complexity,
            "nesting_depth": self.nesting_depth,
            "function_count": self.function_count,
            "class_count": self.class_count,
            "estimated_memory_usage": self.estimated_memory_usage,
            "potential_bottlenecks": self.potential_bottlenecks,
        }


@dataclass
class PerformanceAnalysisResult:
    """Performance analysis result."""
    issues: List[PerformanceIssue]
    metrics: PerformanceMetrics
    score: float
    summary: str
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics.to_dict(),
            "score": self.score,
            "summary": self.summary,
            "recommendations": self.recommendations,
        }


class PerformanceAnalyzer:
    """Performance analyzer for code."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize performance analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.analysis_rules = self._load_analysis_rules()
        
        logger.info("Performance analyzer initialized")
    
    def _load_analysis_rules(self) -> Dict[str, Any]:
        """Load analysis rules."""
        return {
            "python": {
                "nested_loop_threshold": 3,
                "function_length_threshold": 50,
                "complexity_threshold": 10,
                "memory_patterns": [
                    (r"for\s+.*\s+in\s+range\(\d{4,}\)", "Large range iteration"),
                    (r"\[.*\s+for\s+.*\s+in\s+.*\s+for\s+.*\]", "Nested list comprehension"),
                    (r"while\s+True", "Infinite loop potential"),
                ],
                "io_patterns": [
                    (r"open\s*\(", "File I/O operation"),
                    (r"requests\.\w+\s*\(", "HTTP request"),
                    (r"socket\.\w+\s*\(", "Socket operation"),
                ],
                "database_patterns": [
                    (r"\.execute\s*\(", "Database query"),
                    (r"\.fetchall\s*\(", "Fetching all results"),
                    (r"\.fetchone\s*\(", "Fetching single result"),
                ],
            },
            "java": {
                "nested_loop_threshold": 3,
                "function_length_threshold": 40,
                "complexity_threshold": 10,
                "memory_patterns": [
                    (r"new\s+ArrayList\s*\(\)", "List creation"),
                    (r"new\s+HashMap\s*\(\)", "Map creation"),
                    (r"String\s*\+\s*", "String concatenation"),
                ],
                "io_patterns": [
                    (r"FileInputStream\s*\(", "File input stream"),
                    (r"FileOutputStream\s*\(", "File output stream"),
                    (r"HttpURLConnection", "HTTP connection"),
                ],
                "database_patterns": [
                    (r"Statement\.execute", "Database query"),
                    (r"PreparedStatement", "Prepared statement"),
                ],
            },
        }
    
    async def analyze(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> PerformanceAnalysisResult:
        """
        Analyze code for performance issues.
        
        Args:
            code: Code to analyze
            language: Programming language
            file_path: Optional file path
            
        Returns:
            Performance analysis result
        """
        logger.info(f"Analyzing {language} code for performance issues")
        
        issues = []
        
        # Analyze based on language
        if language == "python":
            issues.extend(self._analyze_python(code, file_path))
        elif language == "java":
            issues.extend(self._analyze_java(code, file_path))
        elif language in ["javascript", "typescript"]:
            issues.extend(self._analyze_javascript(code, file_path))
        
        # Calculate metrics
        metrics = self._calculate_metrics(code, language, issues)
        
        # Calculate score
        score = self._calculate_score(metrics, issues)
        
        # Generate summary
        summary = self._generate_summary(metrics, issues, score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics)
        
        logger.info(f"Analysis completed. Score: {score:.1f}/100")
        
        return PerformanceAnalysisResult(
            issues=issues,
            metrics=metrics,
            score=score,
            summary=summary,
            recommendations=recommendations,
        )
    
    def _analyze_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Analyze Python code for performance issues."""
        issues = []
        
        # Check for nested loops
        issues.extend(self._check_nested_loops(code, file_path))
        
        # Check for inefficient patterns
        issues.extend(self._check_inefficient_patterns_python(code, file_path))
        
        # Check for memory issues
        issues.extend(self._check_memory_issues_python(code, file_path))
        
        # Check for I/O issues
        issues.extend(self._check_io_issues_python(code, file_path))
        
        return issues
    
    def _analyze_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Analyze Java code for performance issues."""
        issues = []
        
        # Check for nested loops
        issues.extend(self._check_nested_loops(code, file_path))
        
        # Check for inefficient patterns
        issues.extend(self._check_inefficient_patterns_java(code, file_path))
        
        # Check for memory issues
        issues.extend(self._check_memory_issues_java(code, file_path))
        
        # Check for I/O issues
        issues.extend(self._check_io_issues_java(code, file_path))
        
        return issues
    
    def _analyze_javascript(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Analyze JavaScript code for performance issues."""
        issues = []
        
        # Check for nested loops
        issues.extend(self._check_nested_loops(code, file_path))
        
        # Check for inefficient patterns
        issues.extend(self._check_inefficient_patterns_javascript(code, file_path))
        
        # Check for DOM manipulation issues
        issues.extend(self._check_dom_issues(code, file_path))
        
        return issues
    
    def _check_nested_loops(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for nested loops."""
        issues = []
        
        lines = code.split('\n')
        loop_depth = 0
        loop_start_line = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Detect loop start
            if re.match(r'\s*(for|while)\s+', stripped):
                if loop_depth == 0:
                    loop_start_line = i
                loop_depth += 1
                
                # Check for deep nesting
                if loop_depth >= 3:
                    issues.append(PerformanceIssue(
                        id=f"nested_loop_{i}",
                        type=PerformanceIssueType.ALGORITHMIC,
                        severity=PerformanceSeverity.HIGH,
                        title="深层嵌套循环",
                        description=f"循环嵌套深度为 {loop_depth} 层",
                        file_path=file_path,
                        line_number=i,
                        impact="O(n^{}) 时间复杂度".format(loop_depth),
                        recommendation="考虑使用哈希表或提前终止来优化",
                    ))
            
            # Detect loop end (simplified)
            elif stripped.startswith('break') or (stripped == '' and loop_depth > 0):
                loop_depth = max(0, loop_depth - 1)
        
        return issues
    
    def _check_inefficient_patterns_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for inefficient patterns in Python."""
        issues = []
        
        # Check for string concatenation in loop
        lines = code.split('\n')
        in_loop = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if re.match(r'\s*(for|while)\s+', stripped):
                in_loop = True
            elif in_loop and '+=' in stripped and ('"' in stripped or "'" in stripped):
                issues.append(PerformanceIssue(
                    id=f"string_concat_loop_{i}",
                    type=PerformanceIssueType.ALGORITHMIC,
                    severity=PerformanceSeverity.MEDIUM,
                    title="循环中字符串拼接",
                    description="在循环中使用 += 拼接字符串效率低下",
                    file_path=file_path,
                    line_number=i,
                    impact="每次拼接都会创建新字符串对象",
                    recommendation="使用 join() 或 io.StringIO",
                ))
                in_loop = False
        
        # Check for list membership test in loop
        for i, line in enumerate(lines, 1):
            if re.search(r'for\s+.*\s+in\s+.*:.*\s+if\s+.*\s+in\s+\[', line):
                issues.append(PerformanceIssue(
                    id=f"list_membership_{i}",
                    type=PerformanceIssueType.ALGORITHMIC,
                    severity=PerformanceSeverity.MEDIUM,
                    title="列表成员测试效率低",
                    description="在列表中进行成员测试时间复杂度为 O(n)",
                    file_path=file_path,
                    line_number=i,
                    impact="循环中使用列表成员测试导致 O(n^2) 复杂度",
                    recommendation="使用集合 (set) 进行成员测试",
                ))
        
        return issues
    
    def _check_inefficient_patterns_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for inefficient patterns in Java."""
        issues = []
        
        # Check for string concatenation in loop
        if re.search(r'for\s*\(.*\).*\{[^}]*String\s*\+\s*', code, re.DOTALL):
            issues.append(PerformanceIssue(
                id="string_concat_java",
                type=PerformanceIssueType.ALGORITHMIC,
                severity=PerformanceSeverity.MEDIUM,
                title="循环中字符串拼接",
                description="在循环中使用 + 拼接字符串效率低下",
                file_path=file_path,
                impact="每次拼接都会创建新 String 对象",
                recommendation="使用 StringBuilder",
            ))
        
        # Check for autoboxing
        if re.search(r'List<Integer>|ArrayList<Integer>', code):
            issues.append(PerformanceIssue(
                id="autoboxing_java",
                type=PerformanceIssueType.MEMORY,
                severity=PerformanceSeverity.LOW,
                title="自动装箱开销",
                description="使用包装类型而非基本类型",
                file_path=file_path,
                impact="自动装箱会创建额外对象",
                recommendation="使用专用集合（如 IntArrayList）或基本类型数组",
            ))
        
        return issues
    
    def _check_inefficient_patterns_javascript(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for inefficient patterns in JavaScript."""
        issues = []
        
        # Check for synchronous XHR
        if re.search(r'\.open\s*\(\s*[\'"]GET[\'"]\s*,.*false\s*\)', code):
            issues.append(PerformanceIssue(
                id="sync_xhr",
                type=PerformanceIssueType.NETWORK,
                severity=PerformanceSeverity.HIGH,
                title="同步 HTTP 请求",
                description="使用同步 XMLHttpRequest 会阻塞 UI",
                file_path=file_path,
                impact="阻塞主线程，导致页面冻结",
                recommendation="使用 fetch API 或异步 XHR",
            ))
        
        # Check for frequent DOM manipulation
        dom_operations = re.findall(r'\.innerHTML\s*=|\.appendChild\s*\(|\.insertBefore\s*\(', code)
        if len(dom_operations) > 5:
            issues.append(PerformanceIssue(
                id="frequent_dom",
                type=PerformanceIssueType.OPTIMIZATION,
                severity=PerformanceSeverity.MEDIUM,
                title="频繁 DOM 操作",
                description=f"发现 {len(dom_operations)} 次 DOM 操作",
                file_path=file_path,
                impact="频繁 DOM 操作会导致重排和重绘",
                recommendation="使用 DocumentFragment 或虚拟 DOM",
            ))
        
        return issues
    
    def _check_memory_issues_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for memory issues in Python."""
        issues = []
        
        # Check for large list comprehensions
        if re.search(r'\[.*for\s+.*\s+in\s+range\(\d{5,}\)', code):
            issues.append(PerformanceIssue(
                id="large_list_comp",
                type=PerformanceIssueType.MEMORY,
                severity=PerformanceSeverity.HIGH,
                title="大型列表推导式",
                description="创建大型列表可能消耗大量内存",
                file_path=file_path,
                impact="可能耗尽可用内存",
                recommendation="使用生成器表达式替代列表推导式",
            ))
        
        # Check for global variables
        if re.search(r'^\s*[A-Z_][A-Z0-9_]*\s*=\s*\[', code, re.MULTILINE):
            issues.append(PerformanceIssue(
                id="global_list",
                type=PerformanceIssueType.MEMORY,
                severity=PerformanceSeverity.LOW,
                title="全局列表",
                description="全局列表可能在程序生命周期内占用内存",
                file_path=file_path,
                impact="内存无法被垃圾回收",
                recommendation="考虑使用局部变量或及时清理",
            ))
        
        return issues
    
    def _check_memory_issues_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for memory issues in Java."""
        issues = []
        
        # Check for large array allocation
        if re.search(r'new\s+\w+\s*\[\s*\d{7,}\s*\]', code):
            issues.append(PerformanceIssue(
                id="large_array",
                type=PerformanceIssueType.MEMORY,
                severity=PerformanceSeverity.HIGH,
                title="大型数组分配",
                description="分配大型数组可能消耗大量内存",
                file_path=file_path,
                impact="可能抛出 OutOfMemoryError",
                recommendation="考虑分块处理或使用流式处理",
            ))
        
        return issues
    
    def _check_io_issues_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for I/O issues in Python."""
        issues = []
        
        # Check for unclosed file handles
        open_count = len(re.findall(r'open\s*\(', code))
        close_count = len(re.findall(r'\.close\s*\(', code))
        with_count = len(re.findall(r'with\s+open', code))
        
        if open_count > close_count + with_count:
            issues.append(PerformanceIssue(
                id="unclosed_file",
                type=PerformanceIssueType.I_O,
                severity=PerformanceSeverity.MEDIUM,
                title="未关闭的文件句柄",
                description="文件打开后可能未正确关闭",
                file_path=file_path,
                impact="可能导致资源泄漏",
                recommendation="使用 with 语句确保文件正确关闭",
            ))
        
        return issues
    
    def _check_io_issues_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for I/O issues in Java."""
        issues = []
        
        # Check for unclosed streams
        stream_creations = len(re.findall(r'new\s+(FileInputStream|FileOutputStream|BufferedReader)', code))
        close_calls = len(re.findall(r'\.close\s*\(', code))
        
        if stream_creations > close_calls:
            issues.append(PerformanceIssue(
                id="unclosed_stream_java",
                type=PerformanceIssueType.I_O,
                severity=PerformanceSeverity.MEDIUM,
                title="未关闭的流",
                description="流可能未正确关闭",
                file_path=file_path,
                impact="可能导致资源泄漏",
                recommendation="使用 try-with-resources 语句",
            ))
        
        return issues
    
    def _check_dom_issues(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[PerformanceIssue]:
        """Check for DOM-related performance issues."""
        issues = []
        
        # Check for document.getElementById in loops
        if re.search(r'for\s*\(.*\{[^}]*getElementById', code, re.DOTALL):
            issues.append(PerformanceIssue(
                id="dom_query_loop",
                type=PerformanceIssueType.OPTIMIZATION,
                severity=PerformanceSeverity.MEDIUM,
                title="循环中 DOM 查询",
                description="在循环中查询 DOM 元素效率低下",
                file_path=file_path,
                impact="每次查询都会遍历 DOM 树",
                recommendation="将查询结果缓存到变量中",
            ))
        
        return issues
    
    def _calculate_metrics(
        self,
        code: str,
        language: str,
        issues: List[PerformanceIssue]
    ) -> PerformanceMetrics:
        """Calculate performance metrics."""
        lines = code.split('\n')
        
        # Calculate complexity metrics
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code, language)
        cognitive_complexity = self._calculate_cognitive_complexity(code, language)
        
        # Calculate nesting depth
        nesting_depth = self._calculate_nesting_depth(code)
        
        # Count functions and classes
        function_count = self._count_functions(code, language)
        class_count = self._count_classes(code, language)
        
        # Estimate time and space complexity
        time_complexity = self._estimate_time_complexity(code, language)
        space_complexity = self._estimate_space_complexity(code, language)
        
        # Estimate memory usage
        estimated_memory = self._estimate_memory_usage(code, language)
        
        # Find potential bottlenecks
        bottlenecks = self._find_bottlenecks(code, language, issues)
        
        return PerformanceMetrics(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cognitive_complexity,
            nesting_depth=nesting_depth,
            function_count=function_count,
            class_count=class_count,
            estimated_memory_usage=estimated_memory,
            potential_bottlenecks=bottlenecks,
        )
    
    def _calculate_cyclomatic_complexity(self, code: str, language: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        
        if language == "python":
            patterns = [r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b', r'\band\b', r'\bor\b']
        elif language == "java":
            patterns = [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bcase\b', r'\&\&', r'\|\|']
        else:
            patterns = [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bcase\b']
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _calculate_cognitive_complexity(self, code: str, language: str) -> int:
        """Calculate cognitive complexity."""
        # Simplified cognitive complexity calculation
        complexity = 0
        nesting_level = 0
        
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # Increase nesting for control structures
            if re.match(r'\s*(if|elif|else|for|while|try|except|finally|catch|switch|case)', stripped):
                complexity += 1 + nesting_level
                nesting_level += 1
            
            # Decrease nesting at block end
            if stripped.startswith('}') or (stripped == '' and nesting_level > 0):
                nesting_level = max(0, nesting_level - 1)
        
        return complexity
    
    def _calculate_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{' or char == ':':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _count_functions(self, code: str, language: str) -> int:
        """Count functions in code."""
        if language == "python":
            return len(re.findall(r'^\s*def\s+\w+', code, re.MULTILINE))
        elif language == "java":
            return len(re.findall(r'(?:public|private|protected)\s+(?:static)?\s+\w+\s+\w+\s*\(', code))
        else:
            return len(re.findall(r'(?:function|const|let|var)\s+\w+\s*(?:=\s*(?:async\s*)?\(|function\s*\()', code))
    
    def _count_classes(self, code: str, language: str) -> int:
        """Count classes in code."""
        if language == "python":
            return len(re.findall(r'^\s*class\s+\w+', code, re.MULTILINE))
        elif language == "java":
            return len(re.findall(r'(?:public|private)?\s*(?:abstract|final)?\s*class\s+\w+', code))
        else:
            return len(re.findall(r'class\s+\w+', code))
    
    def _estimate_time_complexity(self, code: str, language: str) -> str:
        """Estimate time complexity."""
        # Simple heuristic based on loop patterns
        if re.search(r'for.*for.*for', code):
            return "O(n^3)"
        elif re.search(r'for.*for', code):
            return "O(n^2)"
        elif re.search(r'\bfor\b|\bwhile\b', code):
            return "O(n)"
        else:
            return "O(1)"
    
    def _estimate_space_complexity(self, code: str, language: str) -> str:
        """Estimate space complexity."""
        # Simple heuristic
        if re.search(r'\[\s*.*\s+for\s+.*\s+in\s+.*\s+for\s+.*\s+in', code):
            return "O(n^2)"
        elif re.search(r'\[.*for.*in', code) or re.search(r'new\s+\w+\s*\[', code):
            return "O(n)"
        else:
            return "O(1)"
    
    def _estimate_memory_usage(self, code: str, language: str) -> str:
        """Estimate memory usage."""
        large_allocations = len(re.findall(r'range\(\d{5,}\)|new\s+\w+\s*\[\s*\d{5,}\s*\]', code))
        
        if large_allocations > 0:
            return "high"
        elif re.search(r'\[.*for.*in.*range\(\d{3,}\)', code):
            return "medium"
        else:
            return "low"
    
    def _find_bottlenecks(
        self,
        code: str,
        language: str,
        issues: List[PerformanceIssue]
    ) -> List[str]:
        """Find potential performance bottlenecks."""
        bottlenecks = []
        
        # High severity issues indicate bottlenecks
        for issue in issues:
            if issue.severity in [PerformanceSeverity.HIGH, PerformanceSeverity.CRITICAL]:
                bottlenecks.append(f"{issue.title}: {issue.description}")
        
        # Check for common bottleneck patterns
        if re.search(r'\.execute\s*\(|\.query\s*\(', code):
            bottlenecks.append("数据库查询操作")
        
        if re.search(r'requests\.\w+\s*\(|fetch\s*\(', code):
            bottlenecks.append("网络请求操作")
        
        if re.search(r'open\s*\(|FileInputStream', code):
            bottlenecks.append("文件 I/O 操作")
        
        return bottlenecks
    
    def _calculate_score(
        self,
        metrics: PerformanceMetrics,
        issues: List[PerformanceIssue]
    ) -> float:
        """Calculate performance score (0-100)."""
        score = 100.0
        
        # Deductions for issues
        severity_deductions = {
            PerformanceSeverity.LOW: 2.0,
            PerformanceSeverity.MEDIUM: 5.0,
            PerformanceSeverity.HIGH: 10.0,
            PerformanceSeverity.CRITICAL: 20.0,
        }
        
        for issue in issues:
            score -= severity_deductions.get(issue.severity, 5.0)
        
        # Deductions for complexity
        if metrics.cyclomatic_complexity > 10:
            score -= (metrics.cyclomatic_complexity - 10) * 2
        
        if metrics.nesting_depth > 4:
            score -= (metrics.nesting_depth - 4) * 3
        
        # Deductions for time complexity
        complexity_deductions = {
            "O(n^3)": 20,
            "O(n^2)": 10,
            "O(n)": 0,
            "O(1)": 0,
        }
        score -= complexity_deductions.get(metrics.time_complexity, 0)
        
        return max(0.0, min(100.0, score))
    
    def _generate_summary(
        self,
        metrics: PerformanceMetrics,
        issues: List[PerformanceIssue],
        score: float
    ) -> str:
        """Generate analysis summary."""
        parts = []
        
        parts.append(f"时间复杂度: {metrics.time_complexity}")
        parts.append(f"空间复杂度: {metrics.space_complexity}")
        parts.append(f"圈复杂度: {metrics.cyclomatic_complexity}")
        
        if issues:
            parts.append(f"发现 {len(issues)} 个性能问题")
        
        if score >= 80:
            parts.append("性能评估: 优秀")
        elif score >= 60:
            parts.append("性能评估: 良好")
        elif score >= 40:
            parts.append("性能评估: 中等")
        else:
            parts.append("性能评估: 需要改进")
        
        return "，".join(parts)
    
    def _generate_recommendations(
        self,
        issues: List[PerformanceIssue],
        metrics: PerformanceMetrics
    ) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Based on issues
        issue_types = set(issue.type for issue in issues)
        
        if PerformanceIssueType.ALGORITHMIC in issue_types:
            recommendations.append("优化算法复杂度，减少不必要的循环")
        
        if PerformanceIssueType.MEMORY in issue_types:
            recommendations.append("优化内存使用，避免不必要的对象创建")
        
        if PerformanceIssueType.I_O in issue_types:
            recommendations.append("优化 I/O 操作，使用缓冲和批处理")
        
        if PerformanceIssueType.NETWORK in issue_types:
            recommendations.append("优化网络请求，使用缓存和异步处理")
        
        # Based on metrics
        if metrics.time_complexity in ["O(n^2)", "O(n^3)"]:
            recommendations.append("考虑使用更高效的算法或数据结构")
        
        if metrics.nesting_depth > 4:
            recommendations.append("减少代码嵌套深度，提高可读性")
        
        if metrics.cyclomatic_complexity > 15:
            recommendations.append("简化复杂逻辑，拆分为更小的函数")
        
        return recommendations