"""
JavaScript/TypeScript Code Analyzer.

This module provides JavaScript and TypeScript specific code analysis capabilities.
"""

import re
from typing import Any, Dict, List, Optional
import logging

from .models import CodeMetrics, CodeIssue, AnalysisResult

logger = logging.getLogger(__name__)


class JavaScriptAnalyzer:
    """Analyzer for JavaScript and TypeScript code."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize JavaScript analyzer."""
        self.config = config or {}
    
    async def analyze(self, code: str, file_path: Optional[str] = None) -> AnalysisResult:
        """
        Analyze JavaScript/TypeScript code.
        
        Args:
            code: JavaScript/TypeScript code to analyze
            file_path: Optional file path
            
        Returns:
            Analysis result
        """
        issues = []
        
        # Determine if TypeScript
        is_typescript = file_path.endswith('.ts') or file_path.endswith('.tsx') if file_path else False
        language = "typescript" if is_typescript else "javascript"
        
        # Extract information
        ast_info = self._extract_js_info(code)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code)
        
        # Check for issues
        issues.extend(self._check_issues(code, is_typescript))
        
        return AnalysisResult(
            language=language,
            metrics=metrics,
            issues=issues,
            ast_info=ast_info,
        )
    
    def _extract_js_info(self, code: str) -> Dict[str, Any]:
        """Extract information from JavaScript/TypeScript code."""
        info = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
        }
        
        # Extract functions
        func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>|\w+\s*=>))'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1) or match.group(2)
            info["functions"].append({
                "name": func_name,
                "line": code[:match.start()].count('\n') + 1,
            })
        
        # Extract classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            info["classes"].append({
                "name": class_name,
                "line": code[:match.start()].count('\n') + 1,
            })
        
        # Extract imports
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, code):
            info["imports"].append(match.group(1))
        
        return info
    
    def _calculate_metrics(self, code: str) -> CodeMetrics:
        """Calculate JavaScript/TypeScript code metrics."""
        lines = code.split('\n')
        
        # Basic line counts
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == '')
        comment_lines = sum(1 for line in lines if line.strip().startswith('//') or line.strip().startswith('/*') or line.strip().startswith('*'))
        code_lines = lines_of_code - blank_lines - comment_lines
        
        # Function and class counts
        functions = len(re.findall(r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>|\w+\s*=>))', code))
        classes = len(re.findall(r'class\s+\w+', code))
        
        # Import count
        imports = len(re.findall(r'import\s+.*?from\s+[\'"][^\'"]+[\'"]', code))
        
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
            r'&&',       # Logical AND
            r'\|\|',     # Logical OR
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
        operators = set(re.findall(r'[+\-*/=<>!&|^~%?:]', code))
        operands = set(re.findall(r'\b\w+\b', code))
        
        n1 = len(operators)  # Number of unique operators
        n2 = len(operands)   # Number of unique operands
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        # Volume = N * log2(n)
        import math
        N = len(re.findall(r'[+\-*/=<>!&|^~%?:]', code)) + len(re.findall(r'\b\w+\b', code))
        n = n1 + n2
        
        return N * math.log2(n) if n > 0 else 0.0
    
    def _check_issues(self, code: str, is_typescript: bool) -> List[CodeIssue]:
        """Check for JavaScript/TypeScript code issues."""
        issues = []
        
        # Check for common issues
        issues.extend(self._check_naming_conventions(code))
        issues.extend(self._check_code_smells(code))
        issues.extend(self._check_security_issues(code))
        
        if is_typescript:
            issues.extend(self._check_typescript_issues(code))
        
        return issues
    
    def _check_naming_conventions(self, code: str) -> List[CodeIssue]:
        """Check naming conventions."""
        issues = []
        
        # Check class naming (should be PascalCase)
        class_pattern = r'class\s+(\w+)'
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
        
        # Check function/variable naming (should be camelCase)
        func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+))'
        for match in re.finditer(func_pattern, code):
            name = match.group(1) or match.group(2)
            if not re.match(r'^[a-z][a-zA-Z0-9]*$', name):
                issues.append(CodeIssue(
                    id=f"naming_{name}",
                    severity="warning",
                    category="naming",
                    message=f"名称 '{name}' 不符合 camelCase 规范",
                    line_number=code[:match.start()].count('\n') + 1,
                    suggestion="使用 camelCase 命名函数和变量",
                ))
        
        return issues
    
    def _check_code_smells(self, code: str) -> List[CodeIssue]:
        """Check for code smells."""
        issues = []
        
        # Check for console.log statements
        if 'console.log(' in code:
            issues.append(CodeIssue(
                id="code_smell_console_log",
                severity="warning",
                category="code_smell",
                message="检测到 console.log 语句",
                suggestion="生产代码中应移除 console.log",
            ))
        
        # Check for debugger statements
        if 'debugger;' in code:
            issues.append(CodeIssue(
                id="code_smell_debugger",
                severity="warning",
                category="code_smell",
                message="检测到 debugger 语句",
                suggestion="生产代码中应移除 debugger 语句",
            ))
        
        # Check for == instead of ===
        if '==' in code and '===' not in code:
            # Simple check - may have false positives
            if re.search(r'[^=!]==[^=]', code):
                issues.append(CodeIssue(
                    id="code_smell_double_equals",
                    severity="info",
                    category="code_smell",
                    message="使用 == 进行比较",
                    suggestion="使用 === 进行严格比较",
                ))
        
        return issues
    
    def _check_security_issues(self, code: str) -> List[CodeIssue]:
        """Check for security issues."""
        issues = []
        
        # Check for eval
        if 'eval(' in code:
            issues.append(CodeIssue(
                id="security_eval",
                severity="critical",
                category="security",
                message="使用 eval() 存在安全风险",
                suggestion="避免使用 eval()",
            ))
        
        # Check for innerHTML
        if 'innerHTML' in code:
            issues.append(CodeIssue(
                id="security_innerhtml",
                severity="critical",
                category="security",
                message="使用 innerHTML 存在 XSS 风险",
                suggestion="使用 textContent 或安全的 DOM 操作",
            ))
        
        # Check for document.write
        if 'document.write(' in code:
            issues.append(CodeIssue(
                id="security_document_write",
                severity="critical",
                category="security",
                message="使用 document.write() 存在安全风险",
                suggestion="使用 DOM 操作替代",
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
    
    def _check_typescript_issues(self, code: str) -> List[CodeIssue]:
        """Check for TypeScript-specific issues."""
        issues = []
        
        # Check for any type
        if ': any' in code or 'as any' in code:
            issues.append(CodeIssue(
                id="typescript_any_type",
                severity="warning",
                category="typescript",
                message="使用 'any' 类型",
                suggestion="尽量使用具体类型，避免使用 'any'",
            ))
        
        # Check for @ts-ignore
        if '@ts-ignore' in code or '@ts-expect-error' in code:
            issues.append(CodeIssue(
                id="typescript_ts_ignore",
                severity="warning",
                category="typescript",
                message="使用 @ts-ignore 或 @ts-expect-error",
                suggestion="尽量修复类型错误，而不是忽略",
            ))
        
        return issues