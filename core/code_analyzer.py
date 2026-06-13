"""
Code Analyzer for AI Agent Benchmark system.

This module provides code analysis capabilities including AST parsing,
code quality detection, and metrics calculation.
"""

import ast
import re
import math
from typing import Any, Dict, List, Optional, Tuple, Set
import logging
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter

logger = logging.getLogger(__name__)


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


class CodeAnalyzer:
    """Code analyzer for multiple programming languages."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize code analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.analyzers = {
            Language.PYTHON: self._analyze_python,
            Language.JAVA: self._analyze_java,
            Language.JAVASCRIPT: self._analyze_javascript,
            Language.TYPESCRIPT: self._analyze_typescript,
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
        lang = Language(language)
        analyzer = self.analyzers.get(lang)
        
        if not analyzer:
            raise ValueError(f"Unsupported language: {language}")
        
        logger.info(f"Analyzing {language} code ({len(code)} chars)")
        result = await analyzer(code, file_path)
        
        # Calculate quality score
        result.quality_score = self._calculate_quality_score(result.metrics, result.issues)
        
        # Generate summary
        result.summary = self._generate_summary(result)
        
        logger.info(f"Analysis completed. Quality score: {result.quality_score:.1f}/100")
        return result
    
    async def _analyze_python(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> AnalysisResult:
        """Analyze Python code."""
        issues = []
        
        # Parse AST
        tree = None
        try:
            tree = ast.parse(code)
            ast_info = self._extract_python_ast_info(tree)
        except SyntaxError as e:
            issues.append(CodeIssue(
                id="syntax_error",
                severity="critical",
                category="syntax",
                message=f"语法错误: {e.msg}",
                line_number=e.lineno,
                column=e.offset,
            ))
            ast_info = None
        
        # Calculate metrics
        metrics = self._calculate_python_metrics(code, tree)
        
        # Check for issues
        issues.extend(self._check_python_issues(code, tree))
        
        return AnalysisResult(
            language="python",
            metrics=metrics,
            issues=issues,
            ast_info=ast_info,
        )
    
    async def _analyze_java(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> AnalysisResult:
        """Analyze Java code."""
        issues = []
        
        # Simple Java analysis (without full parser)
        ast_info = self._extract_java_info(code)
        
        # Calculate metrics
        metrics = self._calculate_java_metrics(code)
        
        # Check for issues
        issues.extend(self._check_java_issues(code))
        
        return AnalysisResult(
            language="java",
            metrics=metrics,
            issues=issues,
            ast_info=ast_info,
        )
    
    async def _analyze_javascript(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> AnalysisResult:
        """Analyze JavaScript code."""
        issues = []
        
        # Simple JavaScript analysis
        ast_info = self._extract_javascript_info(code)
        
        # Calculate metrics
        metrics = self._calculate_javascript_metrics(code)
        
        # Check for issues
        issues.extend(self._check_javascript_issues(code))
        
        return AnalysisResult(
            language="javascript",
            metrics=metrics,
            issues=issues,
            ast_info=ast_info,
        )
    
    async def _analyze_typescript(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> AnalysisResult:
        """Analyze TypeScript code."""
        # TypeScript analysis is similar to JavaScript
        return await self._analyze_javascript(code, file_path)
    
    def _extract_python_ast_info(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract information from Python AST."""
        info = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                info["functions"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": len(node.args.args),
                    "decorators": len(node.decorator_list),
                })
            elif isinstance(node, ast.ClassDef):
                info["classes"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "bases": len(node.bases),
                    "methods": sum(1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef)),
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                else:
                    info["imports"].append(node.module or "")
        
        return info
    
    def _extract_java_info(self, code: str) -> Dict[str, Any]:
        """Extract information from Java code with enhanced parsing."""
        info = {
            "classes": [],
            "methods": [],
            "imports": [],
            "annotations": [],
            "fields": [],
            "interfaces": [],
            "inner_classes": [],
        }
        
        # Extract classes (including inner classes)
        class_pattern = r"(?:public|private|protected)?\s*(?:static\s+)?(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?"
        for match in re.finditer(class_pattern, code):
            info["classes"].append(match.group(1))
        
        # Extract interfaces
        interface_pattern = r"(?:public|private|protected)?\s*interface\s+(\w+)(?:\s+extends\s+[\w,\s]+)?"
        for match in re.finditer(interface_pattern, code):
            info["interfaces"].append(match.group(1))
        
        # Extract methods (enhanced with return types and parameters)
        method_pattern = r"(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)"
        for match in re.finditer(method_pattern, code):
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3)
            info["methods"].append({
                "name": method_name,
                "return_type": return_type,
                "parameters": params,
                "parameter_count": len([p for p in params.split(',') if p.strip()]) if params.strip() else 0,
            })
        
        # Extract imports
        import_pattern = r"import\s+(?:static\s+)?([\w.*]+)"
        for match in re.finditer(import_pattern, code):
            info["imports"].append(match.group(1))
        
        # Extract annotations
        annotation_pattern = r"@(\w+)(?:\([^)]*\))?"
        for match in re.finditer(annotation_pattern, code):
            info["annotations"].append(match.group(1))
        
        # Extract fields
        field_pattern = r"(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*(?:;|=)"
        for match in re.finditer(field_pattern, code):
            info["fields"].append({
                "type": match.group(1),
                "name": match.group(2),
            })
        
        return info
    
    def _extract_javascript_info(self, code: str) -> Dict[str, Any]:
        """Extract information from JavaScript code."""
        info = {
            "functions": [],
            "classes": [],
            "imports": [],
            "exports": [],
        }
        
        # Extract functions
        func_pattern = r"(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s*)?\(|function\s*\()"
        for match in re.finditer(func_pattern, code):
            info["functions"].append(match.group(1))
        
        # Extract classes
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, code):
            info["classes"].append(match.group(1))
        
        # Extract imports
        import_pattern = r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(import_pattern, code):
            info["imports"].append(match.group(1))
        
        # Extract exports
        export_pattern = r"export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)"
        for match in re.finditer(export_pattern, code):
            info["exports"].append(match.group(1))
        
        return info
    
    def _calculate_python_metrics(
        self,
        code: str,
        tree: Optional[ast.AST]
    ) -> CodeMetrics:
        """Calculate metrics for Python code."""
        lines = code.split("\n")
        
        # Basic line counts
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = lines_of_code - blank_lines - comment_lines
        
        # Function and class counts
        functions = 0
        classes = 0
        function_lengths = []
        class_lengths = []
        
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                    # Calculate function length
                    func_lines = code.count("\n", node.lineno, node.end_lineno or node.lineno) + 1
                    function_lengths.append(func_lines)
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    # Calculate class length
                    class_lines = code.count("\n", node.lineno, node.end_lineno or node.lineno) + 1
                    class_lengths.append(class_lines)
        
        # Import count
        imports = len(re.findall(r"^(?:import|from)\s+", code, re.MULTILINE))
        
        # Calculate averages
        avg_function_length = sum(function_lengths) / max(1, len(function_lengths))
        max_function_length = max(function_lengths) if function_lengths else 0
        avg_class_length = sum(class_lengths) / max(1, len(class_lengths))
        max_class_length = max(class_lengths) if class_lengths else 0
        
        # Calculate cyclomatic complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code, "python")
        
        # Calculate maintainability index
        maintainability_index = self._calculate_maintainability_index(
            code_lines, cyclomatic_complexity, avg_function_length
        )
        
        # Calculate Halstead volume (simplified)
        halstead_volume = self._calculate_halstead_volume(code)
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            avg_function_length=avg_function_length,
            max_function_length=max_function_length,
            avg_class_length=avg_class_length,
            max_class_length=max_class_length,
            cyclomatic_complexity=cyclomatic_complexity,
            maintainability_index=maintainability_index,
            halstead_volume=halstead_volume,
        )
    
    def _calculate_java_metrics(self, code: str) -> CodeMetrics:
        """Calculate metrics for Java code with enhanced accuracy."""
        lines = code.split("\n")
        
        # Basic line counts
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("//") or line.strip().startswith("/*") or line.strip().startswith("*"))
        code_lines = lines_of_code - blank_lines - comment_lines
        
        # Extract Java info for detailed analysis
        java_info = self._extract_java_info(code)
        
        # Function and class counts
        functions = len(java_info["methods"])
        classes = len(java_info["classes"])
        
        # Calculate function lengths
        function_lengths = []
        method_pattern = r"(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?\w+(?:<[^>]+>)?\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{"
        
        for match in re.finditer(method_pattern, code):
            start_pos = match.start()
            # Find method end by tracking braces
            brace_count = 0
            method_end = start_pos
            for i, char in enumerate(code[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        method_end = i
                        break
            
            method_code = code[start_pos:method_end]
            method_length = method_code.count('\n') + 1
            function_lengths.append(method_length)
        
        # Calculate class lengths
        class_lengths = []
        class_pattern = r"(?:public|private|protected)?\s*(?:static\s+)?(?:abstract|final)?\s*class\s+\w+(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*\{"
        
        for match in re.finditer(class_pattern, code):
            start_pos = match.start()
            # Find class end
            brace_count = 0
            class_end = start_pos
            for i, char in enumerate(code[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            class_code = code[start_pos:class_end]
            class_length = class_code.count('\n') + 1
            class_lengths.append(class_length)
        
        # Calculate averages
        avg_function_length = sum(function_lengths) / max(1, len(function_lengths))
        max_function_length = max(function_lengths) if function_lengths else 0
        avg_class_length = sum(class_lengths) / max(1, len(class_lengths))
        max_class_length = max(class_lengths) if class_lengths else 0
        
        # Import count
        imports = len(java_info["imports"])
        
        # Calculate cyclomatic complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code, "java")
        
        # Calculate maintainability index
        maintainability_index = self._calculate_maintainability_index(
            code_lines, cyclomatic_complexity, avg_function_length
        )
        
        # Calculate Halstead volume (simplified)
        halstead_volume = self._calculate_halstead_volume(code)
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            avg_function_length=avg_function_length,
            max_function_length=max_function_length,
            avg_class_length=avg_class_length,
            max_class_length=max_class_length,
            cyclomatic_complexity=cyclomatic_complexity,
            maintainability_index=maintainability_index,
            halstead_volume=halstead_volume,
        )
    
    def _calculate_javascript_metrics(self, code: str) -> CodeMetrics:
        """Calculate metrics for JavaScript code."""
        lines = code.split("\n")
        
        # Basic line counts
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("//") or line.strip().startswith("/*"))
        code_lines = lines_of_code - blank_lines - comment_lines
        
        # Function and class counts
        functions = len(re.findall(r"(?:function|const|let|var)\s+\w+\s*(?:=\s*(?:async\s*)?\(|function\s*\()", code))
        classes = len(re.findall(r"class\s+\w+", code))
        
        # Import count
        imports = len(re.findall(r"^import\s+", code, re.MULTILINE))
        
        # Calculate cyclomatic complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code, "javascript")
        
        # Calculate maintainability index
        maintainability_index = self._calculate_maintainability_index(
            code_lines, cyclomatic_complexity, 15  # Assume average function length
        )
        
        # Calculate Halstead volume (simplified)
        halstead_volume = self._calculate_halstead_volume(code)
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            avg_function_length=15.0,  # Simplified
            max_function_length=0,
            avg_class_length=0.0,
            max_class_length=0,
            cyclomatic_complexity=cyclomatic_complexity,
            maintainability_index=maintainability_index,
            halstead_volume=halstead_volume,
        )
    
    def _calculate_cyclomatic_complexity(self, code: str, language: str) -> int:
        """Calculate cyclomatic complexity with enhanced accuracy."""
        complexity = 1  # Base complexity
        
        if language == "python":
            # Count control structures
            patterns = [
                (r"\bif\b", 1),
                (r"\belif\b", 1),
                (r"\bfor\b", 1),
                (r"\bwhile\b", 1),
                (r"\band\b", 1),
                (r"\bor\b", 1),
                (r"\bexcept\b", 1),
                (r"\btry\b", 0),  # try itself doesn't add complexity
                (r"\byield\b", 1),
                (r"\bassert\b", 1),
                (r"\bcomprehension\b", 1),  # List/dict/set comprehension
            ]
        elif language == "java":
            patterns = [
                (r"\bif\b", 1),
                (r"\belse\s+if\b", 1),
                (r"\belse\b", 0),  # else itself doesn't add complexity
                (r"\bfor\b", 1),
                (r"\bwhile\b", 1),
                (r"\bdo\b", 1),
                (r"\bswitch\b", 1),
                (r"\bcase\b", 1),
                (r"\bcatch\b", 1),
                (r"\b&&\b", 1),
                (r"\b\|\|\b", 1),
                (r"\b\?\b", 1),  # Ternary operator
                (r"\bcatch\s*\(", 1),
                (r"\bfinally\b", 0),
                (r"\bthrow\b", 1),
                (r"\btry\b", 0),
            ]
        elif language == "javascript":
            patterns = [
                (r"\bif\b", 1),
                (r"\belse\s+if\b", 1),
                (r"\belse\b", 0),
                (r"\bfor\b", 1),
                (r"\bwhile\b", 1),
                (r"\bdo\b", 1),
                (r"\bswitch\b", 1),
                (r"\bcase\b", 1),
                (r"\bcatch\b", 1),
                (r"\b&&\b", 1),
                (r"\b\|\|\b", 1),
                (r"\b\?\b", 1),  # Ternary operator
                (r"\?\.", 1),  # Optional chaining
                (r"&&=", 1),
                (r"\|\|=", 1),
            ]
        else:
            patterns = []
        
        for pattern, weight in patterns:
            matches = re.findall(pattern, code)
            complexity += len(matches) * weight
        
        return complexity
    
    def _calculate_maintainability_index(
        self,
        code_lines: int,
        cyclomatic_complexity: int,
        avg_function_length: float
    ) -> float:
        """Calculate maintainability index."""
        # Simplified maintainability index calculation
        # Based on SEI's maintainability index formula
        
        if code_lines == 0:
            return 100.0
        
        # Volume metric (simplified)
        volume = code_lines * 0.23
        
        # Complexity metric
        complexity_factor = cyclomatic_complexity * 0.2
        
        # Length metric
        length_factor = avg_function_length * 0.1
        
        # Calculate MI
        mi = 171 - 5.2 * math.log(max(1, volume)) - 0.23 * complexity_factor - 16.2 * math.log(max(1, length_factor))
        
        # Normalize to 0-100
        mi = max(0.0, min(100.0, mi * 100 / 171))
        
        return mi
    
    def _calculate_halstead_volume(self, code: str) -> float:
        """Calculate Halstead volume (simplified)."""
        # Extract operators and operands
        operators = re.findall(r"[+\-*/=<>!&|^~%]", code)
        operands = re.findall(r"\b[a-zA-Z_]\w*\b|\b\d+\.?\d*\b", code)
        
        n1 = len(set(operators))  # Unique operators
        n2 = len(set(operands))   # Unique operands
        N1 = len(operators)       # Total operators
        N2 = len(operands)        # Total operands
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        # Calculate vocabulary and volume
        vocabulary = n1 + n2
        volume = (N1 + N2) * math.log2(max(1, vocabulary))
        
        return volume
    
    def _check_python_issues(
        self,
        code: str,
        tree: Optional[ast.AST]
    ) -> List[CodeIssue]:
        """Check for issues in Python code."""
        issues = []
        
        # Check for syntax issues (already handled in analysis)
        
        # Check for naming conventions
        func_names = re.findall(r"def\s+(\w+)", code)
        for name in func_names:
            if not re.match(r"^[a-z_][a-z0-9_]*$", name) and not name.startswith("_"):
                issues.append(CodeIssue(
                    id=f"naming_func_{name}",
                    severity="info",
                    category="naming",
                    message=f"函数名 '{name}' 不符合 Python 命名规范",
                    suggestion="使用小写字母和下划线命名函数",
                ))
        
        # Check for bare except
        if re.search(r"except\s*:", code):
            issues.append(CodeIssue(
                id="bare_except",
                severity="warning",
                category="best_practice",
                message="使用裸 except 子句",
                suggestion="指定具体的异常类型",
            ))
        
        # Check for eval/exec
        if re.search(r"eval\s*\(", code):
            issues.append(CodeIssue(
                id="use_eval",
                severity="warning",
                category="security",
                message="使用 eval() 函数",
                suggestion="避免使用 eval()，使用 ast.literal_eval() 或其他安全替代方案",
            ))
        
        # Check for wildcard imports
        if re.search(r"from\s+\w+\s+import\s+\*", code):
            issues.append(CodeIssue(
                id="wildcard_import",
                severity="info",
                category="best_practice",
                message="使用通配符导入",
                suggestion="明确导入需要的名称",
            ))
        
        # Check for mutable default arguments
        if re.search(r"def\s+\w+\s*\(.*=\s*(\[\]|\{\})\s*\)", code):
            issues.append(CodeIssue(
                id="mutable_default",
                severity="warning",
                category="design",
                message="使用可变默认参数",
                suggestion="使用 None 作为默认参数，在函数内部初始化",
            ))
        
        # Check for long lines
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 88:
                issues.append(CodeIssue(
                    id=f"long_line_{i}",
                    severity="info",
                    category="style",
                    message=f"第 {i} 行超过 88 字符",
                    line_number=i,
                    suggestion="将长行拆分为多行",
                ))
        
        return issues
    
    def _check_java_issues(self, code: str) -> List[CodeIssue]:
        """Check for issues in Java code with enhanced detection."""
        issues = []
        
        # Check for System.out
        if re.search(r"System\.out\.print", code):
            issues.append(CodeIssue(
                id="system_out",
                severity="warning",
                category="best_practice",
                message="使用 System.out.print",
                suggestion="使用日志框架（如 SLF4J/Log4j）替代 System.out",
            ))
        
        # Check for generic exception catch
        if re.search(r"catch\s*\(\s*Exception\s+", code):
            issues.append(CodeIssue(
                id="generic_catch",
                severity="warning",
                category="best_practice",
                message="捕获通用 Exception",
                suggestion="捕获具体的异常类型，避免吞没异常",
            ))
        
        # Check for magic numbers
        magic_numbers = re.findall(r"(?<!\w)\d{3,}(?!\w)", code)
        if magic_numbers:
            issues.append(CodeIssue(
                id="magic_numbers",
                severity="info",
                category="readability",
                message="存在魔法数字",
                suggestion="将魔法数字定义为命名常量",
            ))
        
        # Check for empty catch blocks
        empty_catch_pattern = r"catch\s*\([^)]+\)\s*\{\s*\}"
        if re.search(empty_catch_pattern, code, re.DOTALL):
            issues.append(CodeIssue(
                id="empty_catch",
                severity="error",
                category="error_handling",
                message="存在空的 catch 块",
                suggestion="至少记录异常信息，或重新抛出异常",
            ))
        
        # Check for deep nesting
        lines = code.split('\n')
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('{'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.startswith('}'):
                current_nesting = max(0, current_nesting - 1)
        
        if max_nesting > 4:
            issues.append(CodeIssue(
                id="deep_nesting",
                severity="warning",
                category="readability",
                message=f"代码嵌套深度过大 ({max_nesting} 层)",
                suggestion="使用提前返回（Guard Clause）或提取方法来减少嵌套",
            ))
        
        # Check for field injection (Spring)
        if re.search(r"@Autowired\s+(?:private|protected)?\s+\w+\s+\w+;", code):
            issues.append(CodeIssue(
                id="field_injection",
                severity="warning",
                category="best_practice",
                message="使用字段注入 (@Autowired on field)",
                suggestion="使用构造器注入，便于测试和保证不变性",
            ))
        
        # Check for missing @Override
        if re.search(r"public\s+\w+\s+(?:toString|equals|hashCode|clone)\s*\(", code):
            if not re.search(r"@Override\s+public\s+\w+\s+(?:toString|equals|hashCode|clone)", code):
                issues.append(CodeIssue(
                    id="missing_override",
                    severity="info",
                    category="best_practice",
                    message="重写方法缺少 @Override 注解",
                    suggestion="添加 @Override 注解提高代码可读性",
                ))
        
        # Check for raw types
        raw_type_pattern = r"(?:List|Map|Set|ArrayList|HashMap|HashSet|Iterator)\s+\w+\s*[=;]"
        if re.search(raw_type_pattern, code):
            issues.append(CodeIssue(
                id="raw_types",
                severity="warning",
                category="modern_practice",
                message="使用原始类型（Raw Types）",
                suggestion="使用泛型类型，如 List<String> 替代 List",
            ))
        
        # Check for mutable static fields
        if re.search(r"static\s+(?:private|protected|public)?\s+(?!final\s+)\w+(?:<[^>]+>)?\s+\w+\s*[=;]", code):
            issues.append(CodeIssue(
                id="mutable_static",
                severity="warning",
                category="design",
                message="存在可变的静态字段",
                suggestion="避免可变静态字段，或使用不可变对象",
            ))
        
        # Check for long methods
        java_info = self._extract_java_info(code)
        for method in java_info.get("methods", []):
            if isinstance(method, dict) and method.get("parameter_count", 0) > 5:
                issues.append(CodeIssue(
                    id=f"too_many_params_{method['name']}",
                    severity="warning",
                    category="design",
                    message=f"方法 '{method['name']}' 参数过多 ({method['parameter_count']} 个)",
                    suggestion="使用参数对象（Parameter Object）或 Builder 模式",
                ))
        
        # Check for string concatenation in loops
        lines = code.split('\n')
        in_loop = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if re.match(r'\s*(for|while)\s+', stripped):
                in_loop = True
            elif in_loop and ('+=' in stripped or '+' in stripped) and ('"' in stripped or "'" in stripped or 'String' in stripped):
                issues.append(CodeIssue(
                    id=f"string_concat_loop_{i}",
                    severity="warning",
                    category="performance",
                    message=f"第 {i} 行在循环中使用字符串拼接",
                    suggestion="使用 StringBuilder 替代字符串拼接",
                ))
                in_loop = False
        
        # Check for resource leak (streams not closed with try-with-resources)
        if re.search(r"new\s+(BufferedReader|InputStream|OutputStream|Connection)", code):
            if not re.search(r"try\s*\(", code):
                issues.append(CodeIssue(
                    id="resource_leak",
                    severity="warning",
                    category="resource_management",
                    message="可能存在资源泄漏",
                    suggestion="使用 try-with-resources 语句自动关闭资源",
                ))
        
        return issues
    
    def _check_javascript_issues(self, code: str) -> List[CodeIssue]:
        """Check for issues in JavaScript code."""
        issues = []
        
        # Check for console.log
        if re.search(r"console\.log", code):
            issues.append(CodeIssue(
                id="console_log",
                severity="warning",
                category="best_practice",
                message="使用 console.log",
                suggestion="生产代码中移除或使用日志库",
            ))
        
        # Check for == instead of ===
        if re.search(r"[^=!]==[^=]", code):
            issues.append(CodeIssue(
                id="loose_equality",
                severity="warning",
                category="best_practice",
                message="使用 == 进行比较",
                suggestion="使用 === 进行严格比较",
            ))
        
        # Check for var usage
        if re.search(r"\bvar\s+", code):
            issues.append(CodeIssue(
                id="var_usage",
                severity="info",
                category="modern_practice",
                message="使用 var 声明变量",
                suggestion="使用 const 或 let 替代 var",
            ))
        
        return issues
    
    def _calculate_quality_score(
        self,
        metrics: CodeMetrics,
        issues: List[CodeIssue]
    ) -> float:
        """Calculate quality score based on metrics and issues."""
        score = 100.0
        
        # Deductions for issues
        severity_deductions = {
            "info": 0.5,
            "warning": 2.0,
            "error": 5.0,
            "critical": 10.0,
        }
        
        for issue in issues:
            score -= severity_deductions.get(issue.severity, 1.0)
        
        # Adjust based on metrics
        if metrics.cyclomatic_complexity > 10:
            score -= (metrics.cyclomatic_complexity - 10) * 2
        
        if metrics.maintainability_index < 50:
            score -= (50 - metrics.maintainability_index) * 0.5
        
        return max(0.0, min(100.0, score))
    
    def _generate_summary(self, result: AnalysisResult) -> str:
        """Generate analysis summary."""
        parts = []
        
        # Basic metrics
        parts.append(f"代码行数: {result.metrics.lines_of_code}")
        parts.append(f"代码行: {result.metrics.code_lines}")
        parts.append(f"注释行: {result.metrics.comment_lines}")
        
        # Structure
        if result.metrics.functions > 0:
            parts.append(f"函数数: {result.metrics.functions}")
        if result.metrics.classes > 0:
            parts.append(f"类数: {result.metrics.classes}")
        
        # Quality
        parts.append(f"圈复杂度: {result.metrics.cyclomatic_complexity}")
        parts.append(f"可维护性指数: {result.metrics.maintainability_index:.1f}")
        
        # Issues
        if result.issues:
            issue_count = len(result.issues)
            parts.append(f"发现 {issue_count} 个问题")
        
        return "，".join(parts)