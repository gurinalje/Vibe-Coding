"""
Python Code Analyzer.

This module provides Python-specific code analysis capabilities.
"""

import ast
import re
from typing import Any, Dict, List, Optional, Set
import logging

from .models import CodeMetrics, CodeIssue, AnalysisResult

logger = logging.getLogger(__name__)


class PythonAnalyzer:
    """Analyzer for Python code."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Python analyzer."""
        self.config = config or {}
    
    async def analyze(self, code: str, file_path: Optional[str] = None) -> AnalysisResult:
        """
        Analyze Python code.
        
        Args:
            code: Python code to analyze
            file_path: Optional file path
            
        Returns:
            Analysis result
        """
        issues = []
        
        # Parse AST
        tree = None
        try:
            tree = ast.parse(code)
            ast_info = self._extract_ast_info(tree)
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
        metrics = self._calculate_metrics(code, tree)
        
        # Check for issues
        issues.extend(self._check_issues(code, tree))
        
        return AnalysisResult(
            language="python",
            metrics=metrics,
            issues=issues,
            ast_info=ast_info,
        )
    
    def _extract_ast_info(self, tree: ast.AST) -> Dict[str, Any]:
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
    
    def _calculate_metrics(self, code: str, tree: Optional[ast.AST]) -> CodeMetrics:
        """Calculate Python code metrics."""
        lines = code.split('\n')
        
        # Basic line counts
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == '')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
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
                    if hasattr(node, 'end_lineno'):
                        func_len = node.end_lineno - node.lineno + 1
                    else:
                        func_len = 1
                    function_lengths.append(func_len)
                
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    # Calculate class length
                    if hasattr(node, 'end_lineno'):
                        class_len = node.end_lineno - node.lineno + 1
                    else:
                        class_len = 1
                    class_lengths.append(class_len)
        
        # Import count
        imports = 0
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
        
        # Calculate averages
        avg_function_length = sum(function_lengths) / len(function_lengths) if function_lengths else 0
        max_function_length = max(function_lengths) if function_lengths else 0
        avg_class_length = sum(class_lengths) / len(class_lengths) if class_lengths else 0
        max_class_length = max(class_lengths) if class_lengths else 0
        
        # Calculate complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
        maintainability_index = self._calculate_maintainability_index(
            code_lines, cyclomatic_complexity, function_lengths
        )
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
    
    def _calculate_cyclomatic_complexity(self, tree: Optional[ast.AST]) -> int:
        """Calculate cyclomatic complexity."""
        if not tree:
            return 1
        
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_maintainability_index(
        self,
        code_lines: int,
        cyclomatic_complexity: int,
        function_lengths: List[int]
    ) -> float:
        """Calculate maintainability index."""
        if code_lines == 0:
            return 100.0
        
        # Simplified maintainability index
        # MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        # For simplicity, we'll use a basic formula
        
        avg_func_len = sum(function_lengths) / len(function_lengths) if function_lengths else 0
        
        # Base score
        score = 100.0
        
        # Penalize for length
        if code_lines > 500:
            score -= 20
        elif code_lines > 200:
            score -= 10
        
        # Penalize for complexity
        if cyclomatic_complexity > 10:
            score -= 20
        elif cyclomatic_complexity > 5:
            score -= 10
        
        # Penalize for long functions
        if avg_func_len > 50:
            score -= 15
        elif avg_func_len > 30:
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def _calculate_halstead_volume(self, code: str) -> float:
        """Calculate Halstead volume."""
        # Simple implementation
        operators = set(re.findall(r'[+\-*/=<>!&|^~%]', code))
        operands = set(re.findall(r'\b\w+\b', code))
        
        n1 = len(operators)  # Number of unique operators
        n2 = len(operands)   # Number of unique operands
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        # Volume = N * log2(n)
        # where N = total operators + operands, n = unique operators + operands
        import math
        N = len(re.findall(r'[+\-*/=<>!&|^~%]', code)) + len(re.findall(r'\b\w+\b', code))
        n = n1 + n2
        
        return N * math.log2(n) if n > 0 else 0.0
    
    def _check_issues(self, code: str, tree: Optional[ast.AST]) -> List[CodeIssue]:
        """Check for Python code issues."""
        issues = []
        
        # Check for common issues
        issues.extend(self._check_naming_conventions(code, tree))
        issues.extend(self._check_code_smells(code, tree))
        issues.extend(self._check_security_issues(code))
        
        return issues
    
    def _check_naming_conventions(self, code: str, tree: Optional[ast.AST]) -> List[CodeIssue]:
        """Check naming conventions."""
        issues = []
        
        if not tree:
            return issues
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function naming (should be snake_case)
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append(CodeIssue(
                        id=f"naming_function_{node.name}",
                        severity="warning",
                        category="naming",
                        message=f"函数名 '{node.name}' 不符合 snake_case 规范",
                        line_number=node.lineno,
                        suggestion="使用 snake_case 命名函数",
                    ))
            
            elif isinstance(node, ast.ClassDef):
                # Check class naming (should be PascalCase)
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(CodeIssue(
                        id=f"naming_class_{node.name}",
                        severity="warning",
                        category="naming",
                        message=f"类名 '{node.name}' 不符合 PascalCase 规范",
                        line_number=node.lineno,
                        suggestion="使用 PascalCase 命名类",
                    ))
        
        return issues
    
    def _check_code_smells(self, code: str, tree: Optional[ast.AST]) -> List[CodeIssue]:
        """Check for code smells."""
        issues = []
        
        # Check for long functions
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'end_lineno'):
                        func_len = node.end_lineno - node.lineno + 1
                        if func_len > 50:
                            issues.append(CodeIssue(
                                id=f"long_function_{node.name}",
                                severity="warning",
                                category="code_smell",
                                message=f"函数 '{node.name}' 过长 ({func_len} 行)",
                                line_number=node.lineno,
                                suggestion="考虑将函数拆分为更小的函数",
                            ))
        
        # Check for too many parameters
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    param_count = len(node.args.args)
                    if param_count > 5:
                        issues.append(CodeIssue(
                            id=f"too_many_params_{node.name}",
                            severity="warning",
                            category="code_smell",
                            message=f"函数 '{node.name}' 参数过多 ({param_count} 个)",
                            line_number=node.lineno,
                            suggestion="考虑使用配置对象或减少参数数量",
                        ))
        
        return issues
    
    def _check_security_issues(self, code: str) -> List[CodeIssue]:
        """Check for security issues."""
        issues = []
        
        # Check for eval/exec
        if 'eval(' in code or 'exec(' in code:
            issues.append(CodeIssue(
                id="security_eval_exec",
                severity="critical",
                category="security",
                message="使用 eval/exec 存在安全风险",
                suggestion="避免使用 eval/exec，使用更安全的替代方案",
            ))
        
        # Check for SQL injection
        if 'execute(' in code and ('%' in code or '+' in code):
            issues.append(CodeIssue(
                id="security_sql_injection",
                severity="critical",
                category="security",
                message="可能存在 SQL 注入风险",
                suggestion="使用参数化查询",
            ))
        
        # Check for hardcoded passwords
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]
        
        for pattern in password_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(CodeIssue(
                    id="security_hardcoded_password",
                    severity="critical",
                    category="security",
                    message="检测到硬编码的密码或密钥",
                    suggestion="使用环境变量或配置文件存储敏感信息",
                ))
                break
        
        return issues