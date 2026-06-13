"""
Java Code Analyzer.

This module provides Java-specific code analysis capabilities.
"""

import re
from typing import Any, Dict, List, Optional
import logging

from .models import CodeMetrics, CodeIssue, AnalysisResult

logger = logging.getLogger(__name__)


class JavaAnalyzer:
    """Analyzer for Java code."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Java analyzer."""
        self.config = config or {}
    
    async def analyze(self, code: str, file_path: Optional[str] = None) -> AnalysisResult:
        """
        Analyze Java code.
        
        Args:
            code: Java code to analyze
            file_path: Optional file path
            
        Returns:
            Analysis result
        """
        issues = []
        
        # Extract information
        ast_info = self._extract_java_info(code)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code)
        
        # Check for issues
        issues.extend(self._check_issues(code))
        
        return AnalysisResult(
            language="java",
            metrics=metrics,
            issues=issues,
            ast_info=ast_info,
        )
    
    def _extract_java_info(self, code: str) -> Dict[str, Any]:
        """Extract information from Java code."""
        info = {
            "classes": [],
            "methods": [],
            "imports": [],
        }
        
        # Extract classes
        class_pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            info["classes"].append({
                "name": class_name,
                "line": code[:match.start()].count('\n') + 1,
            })
        
        # Extract methods
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(method_pattern, code):
            method_name = match.group(1)
            info["methods"].append({
                "name": method_name,
                "line": code[:match.start()].count('\n') + 1,
            })
        
        # Extract imports
        import_pattern = r'import\s+(?:static\s+)?([\w.]+);'
        for match in re.finditer(import_pattern, code):
            info["imports"].append(match.group(1))
        
        return info
    
    def _calculate_metrics(self, code: str) -> CodeMetrics:
        """Calculate Java code metrics."""
        lines = code.split('\n')
        
        # Basic line counts
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == '')
        comment_lines = sum(1 for line in lines if line.strip().startswith('//') or line.strip().startswith('/*') or line.strip().startswith('*'))
        code_lines = lines_of_code - blank_lines - comment_lines
        
        # Function and class counts
        functions = len(re.findall(r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?[\w<>\[\]]+\s+\w+\s*\([^)]*\)', code))
        classes = len(re.findall(r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+\w+', code))
        
        # Import count
        imports = len(re.findall(r'import\s+(?:static\s+)?[\w.]+;', code))
        
        # Calculate complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code)
        maintainability_index = self._calculate_maintainability_index(code_lines, cyclomatic_complexity)
        halstead_volume = self._calculate_halstead_volume(code)
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            cyclomatic_complexity=cyclomatic_complexity,
            maintainability_index=maintainability_index,
            halstead_volume=halstead_volume,
        )
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        # Count control structures
        control_patterns = [
            r'\bif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bdo\s*\{',
            r'\bcatch\s*\(',
            r'\bcase\s+',
            r'\b\?\s*',  # Ternary operator
        ]
        
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _calculate_maintainability_index(self, code_lines: int, cyclomatic_complexity: int) -> float:
        """Calculate maintainability index."""
        if code_lines == 0:
            return 100.0
        
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
        import math
        N = len(re.findall(r'[+\-*/=<>!&|^~%]', code)) + len(re.findall(r'\b\w+\b', code))
        n = n1 + n2
        
        return N * math.log2(n) if n > 0 else 0.0
    
    def _check_issues(self, code: str) -> List[CodeIssue]:
        """Check for Java code issues."""
        issues = []
        
        # Check for common issues
        issues.extend(self._check_naming_conventions(code))
        issues.extend(self._check_code_smells(code))
        issues.extend(self._check_security_issues(code))
        
        return issues
    
    def _check_naming_conventions(self, code: str) -> List[CodeIssue]:
        """Check naming conventions."""
        issues = []
        
        # Check class naming (should be PascalCase)
        class_pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                issues.append(CodeIssue(
                    id=f"naming_class_{class_name}",
                    severity="warning",
                    category="naming",
                    message=f"类名 '{class_name}' 不符合 PascalCase 规范",
                    line_number=code[:match.start()].count('\n') + 1,
                    suggestion="使用 PascalCase 命名类",
                ))
        
        # Check method naming (should be camelCase)
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(method_pattern, code):
            method_name = match.group(1)
            if not re.match(r'^[a-z][a-zA-Z0-9]*$', method_name):
                issues.append(CodeIssue(
                    id=f"naming_method_{method_name}",
                    severity="warning",
                    category="naming",
                    message=f"方法名 '{method_name}' 不符合 camelCase 规范",
                    line_number=code[:match.start()].count('\n') + 1,
                    suggestion="使用 camelCase 命名方法",
                ))
        
        return issues
    
    def _check_code_smells(self, code: str) -> List[CodeIssue]:
        """Check for code smells."""
        issues = []
        
        # Check for long methods
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        for match in re.finditer(method_pattern, code):
            method_name = match.group(1)
            start_pos = match.end()
            
            # Find matching closing brace
            brace_count = 1
            pos = start_pos
            while pos < len(code) and brace_count > 0:
                if code[pos] == '{':
                    brace_count += 1
                elif code[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            method_code = code[start_pos:pos]
            method_lines = method_code.count('\n') + 1
            
            if method_lines > 50:
                issues.append(CodeIssue(
                    id=f"long_method_{method_name}",
                    severity="warning",
                    category="code_smell",
                    message=f"方法 '{method_name}' 过长 ({method_lines} 行)",
                    line_number=code[:match.start()].count('\n') + 1,
                    suggestion="考虑将方法拆分为更小的方法",
                ))
        
        return issues
    
    def _check_security_issues(self, code: str) -> List[CodeIssue]:
        """Check for security issues."""
        issues = []
        
        # Check for SQL injection
        if 'executeQuery(' in code or 'execute(' in code:
            if '+' in code or 'String.format' in code:
                issues.append(CodeIssue(
                    id="security_sql_injection",
                    severity="critical",
                    category="security",
                    message="可能存在 SQL 注入风险",
                    suggestion="使用 PreparedStatement 进行参数化查询",
                ))
        
        # Check for hardcoded passwords
        password_patterns = [
            r'password\s*=\s*"[^"]+"',
            r'pwd\s*=\s*"[^"]+"',
            r'secret\s*=\s*"[^"]+"',
        ]
        
        for pattern in password_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(CodeIssue(
                    id="security_hardcoded_password",
                    severity="critical",
                    category="security",
                    message="检测到硬编码的密码或密钥",
                    suggestion="使用配置文件或环境变量存储敏感信息",
                ))
                break
        
        # Check for Runtime.exec
        if 'Runtime.getRuntime().exec(' in code:
            issues.append(CodeIssue(
                id="security_runtime_exec",
                severity="critical",
                category="security",
                message="使用 Runtime.exec() 存在安全风险",
                suggestion="避免执行外部命令，或使用安全的替代方案",
            ))
        
        return issues