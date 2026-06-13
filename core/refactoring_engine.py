"""
Refactoring Engine for AI Agent Benchmark system.

This module provides code refactoring capabilities including
automatic refactoring suggestions and code transformations.
"""

import ast
import re
from typing import Any, Dict, List, Optional, Tuple, Set
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RefactoringType(str, Enum):
    """Types of refactoring operations."""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    RENAME = "rename"
    INLINE = "inline"
    MOVE = "move"
    SIMPLIFY = "simplify"
    OPTIMIZE = "optimize"
    FORMAT = "format"
    REMOVE_DUPLICATION = "remove_duplication"
    INTRODUCE_PARAMETER = "introduce_parameter"
    REMOVE_PARAMETER = "remove_parameter"
    MODERNIZE = "modernize"


@dataclass
class RefactoringOperation:
    """A refactoring operation."""
    id: str
    type: RefactoringType
    description: str
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    original_code: Optional[str] = None
    refactored_code: Optional[str] = None
    impact: str = "low"  # "low", "medium", "high"
    confidence: float = 0.8  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "original_code": self.original_code,
            "refactored_code": self.refactored_code,
            "impact": self.impact,
            "confidence": self.confidence,
        }


@dataclass
class RefactoringResult:
    """Refactoring result."""
    success: bool
    operations: List[RefactoringOperation]
    refactored_code: Optional[str] = None
    changes_made: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "operations": [op.to_dict() for op in self.operations],
            "refactored_code": self.refactored_code,
            "changes_made": self.changes_made,
            "metrics": self.metrics,
        }


class RefactoringEngine:
    """Engine for code refactoring."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize refactoring engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.refactoring_rules = self._load_refactoring_rules()
        
        logger.info("Refactoring engine initialized")
    
    def _load_refactoring_rules(self) -> Dict[str, Any]:
        """Load refactoring rules."""
        return {
            "python": {
                "max_line_length": 88,
                "indentation": 4,
                "formatting": {
                    "trailing_commas": True,
                    "string_quotes": "double",
                },
            },
            "java": {
                "max_line_length": 120,
                "indentation": 4,
                "braces": "same_line",
            },
            "javascript": {
                "max_line_length": 100,
                "indentation": 2,
                "semicolons": True,
            },
        }
    
    async def analyze(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> RefactoringResult:
        """
        Analyze code for refactoring opportunities.
        
        Args:
            code: Code to analyze
            language: Programming language
            file_path: Optional file path
            
        Returns:
            Refactoring result with suggestions
        """
        logger.info(f"Analyzing code for refactoring opportunities ({language})")
        
        operations = []
        
        # Analyze based on language
        if language == "python":
            operations.extend(await self._analyze_python(code, file_path))
        elif language == "java":
            operations.extend(await self._analyze_java(code, file_path))
        elif language in ["javascript", "typescript"]:
            operations.extend(await self._analyze_javascript(code, file_path))
        
        # Sort operations by confidence
        operations.sort(key=lambda x: x.confidence, reverse=True)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code, operations)
        
        logger.info(f"Found {len(operations)} refactoring opportunities")
        
        return RefactoringResult(
            success=True,
            operations=operations,
            metrics=metrics,
        )
    
    async def apply_refactoring(
        self,
        code: str,
        operations: List[RefactoringOperation],
        language: str
    ) -> RefactoringResult:
        """
        Apply refactoring operations to code.
        
        Args:
            code: Original code
            operations: Operations to apply
            language: Programming language
            
        Returns:
            Refactoring result with refactored code
        """
        logger.info(f"Applying {len(operations)} refactoring operations")
        
        refactored_code = code
        changes_made = []
        applied_operations = []
        
        # Apply operations in order
        for operation in operations:
            if operation.confidence < 0.5:
                logger.warning(f"Skipping low confidence operation: {operation.id}")
                continue
            
            try:
                new_code = await self._apply_operation(refactored_code, operation, language)
                if new_code != refactored_code:
                    refactored_code = new_code
                    changes_made.append(f"Applied {operation.type.value}: {operation.description}")
                    applied_operations.append(operation)
                    logger.debug(f"Applied operation: {operation.id}")
            except Exception as e:
                logger.error(f"Failed to apply operation {operation.id}: {e}")
        
        # Calculate metrics
        metrics = self._calculate_metrics(refactored_code, applied_operations)
        
        logger.info(f"Successfully applied {len(applied_operations)} operations")
        
        return RefactoringResult(
            success=True,
            operations=applied_operations,
            refactored_code=refactored_code,
            changes_made=changes_made,
            metrics=metrics,
        )
    
    async def _analyze_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Analyze Python code for refactoring."""
        operations = []
        
        # Check for long functions
        operations.extend(self._check_long_functions_python(code, file_path))
        
        # Check for duplicated code
        operations.extend(self._check_duplicated_code_python(code, file_path))
        
        # Check for complex conditionals
        operations.extend(self._check_complex_conditionals_python(code, file_path))
        
        # Check for string concatenation
        operations.extend(self._check_string_concatenation_python(code, file_path))
        
        # Check for list comprehension opportunities
        operations.extend(self._check_list_comprehension_python(code, file_path))
        
        return operations
    
    async def _analyze_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Analyze Java code for refactoring."""
        operations = []
        
        # Check for long methods
        operations.extend(self._check_long_methods_java(code, file_path))
        
        # Check for duplicated code
        operations.extend(self._check_duplicated_code_java(code, file_path))
        
        # Check for complex conditionals
        operations.extend(self._check_complex_conditionals_java(code, file_path))
        
        return operations
    
    async def _analyze_javascript(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Analyze JavaScript code for refactoring."""
        operations = []
        
        # Check for long functions
        operations.extend(self._check_long_functions_javascript(code, file_path))
        
        # Check for var usage
        operations.extend(self._check_var_usage_javascript(code, file_path))
        
        # Check for callback hell
        operations.extend(self._check_callback_hell_javascript(code, file_path))
        
        return operations
    
    def _check_long_functions_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for long functions in Python code."""
        operations = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Calculate function length
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        func_length = node.end_lineno - node.lineno + 1
                    else:
                        func_length = code.count("\n", node.lineno) + 1
                    
                    if func_length > 30:
                        operations.append(RefactoringOperation(
                            id=f"extract_method_{node.name}",
                            type=RefactoringType.EXTRACT_METHOD,
                            description=f"函数 '{node.name}' 过长 ({func_length} 行)，考虑拆分为更小的函数",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno if hasattr(node, 'end_lineno') else None,
                            impact="medium",
                            confidence=0.7,
                        ))
        except SyntaxError:
            pass
        
        return operations
    
    def _check_long_methods_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for long methods in Java code."""
        operations = []
        
        # Simple pattern matching for Java methods
        method_pattern = r"(?:public|private|protected)\s+(?:static)?\s+\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{"
        
        for match in re.finditer(method_pattern, code):
            method_name = match.group(1)
            start_pos = match.start()
            
            # Find method end (simplified)
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
            
            # Calculate method length
            method_code = code[start_pos:method_end]
            method_length = method_code.count('\n') + 1
            
            if method_length > 30:
                operations.append(RefactoringOperation(
                    id=f"extract_method_{method_name}",
                    type=RefactoringType.EXTRACT_METHOD,
                    description=f"方法 '{method_name}' 过长 ({method_length} 行)，考虑拆分",
                    file_path=file_path,
                    impact="medium",
                    confidence=0.7,
                ))
        
        return operations
    
    def _check_long_functions_javascript(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for long functions in JavaScript code."""
        operations = []
        
        # Simple pattern matching for JavaScript functions
        func_pattern = r"(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s*)?\([^)]*\)\s*=>|function\s*\([^)]*\))"
        
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            start_pos = match.start()
            
            # Find function end (simplified)
            brace_count = 0
            func_end = start_pos
            started = False
            for i, char in enumerate(code[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
                    if started and brace_count == 0:
                        func_end = i
                        break
            
            # Calculate function length
            func_code = code[start_pos:func_end]
            func_length = func_code.count('\n') + 1
            
            if func_length > 30:
                operations.append(RefactoringOperation(
                    id=f"extract_function_{func_name}",
                    type=RefactoringType.EXTRACT_METHOD,
                    description=f"函数 '{func_name}' 过长 ({func_length} 行)，考虑拆分",
                    file_path=file_path,
                    impact="medium",
                    confidence=0.7,
                ))
        
        return operations
    
    def _check_duplicated_code_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for duplicated code in Python."""
        operations = []
        
        lines = code.split('\n')
        line_groups: Dict[str, List[int]] = {}
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and len(stripped) > 10:
                if stripped not in line_groups:
                    line_groups[stripped] = []
                line_groups[stripped].append(i)
        
        for line_content, line_numbers in line_groups.items():
            if len(line_numbers) > 2:
                operations.append(RefactoringOperation(
                    id=f"remove_duplication_{line_numbers[0]}",
                    type=RefactoringType.REMOVE_DUPLICATION,
                    description=f"发现重复代码 (行 {', '.join(map(str, line_numbers[:5]))}...)",
                    file_path=file_path,
                    line_start=line_numbers[0],
                    impact="medium",
                    confidence=0.6,
                ))
        
        return operations
    
    def _check_duplicated_code_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for duplicated code in Java."""
        # Similar implementation as Python
        return self._check_duplicated_code_python(code, file_path)
    
    def _check_complex_conditionals_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for complex conditionals in Python."""
        operations = []
        
        # Check for nested ifs
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('if ') and stripped.endswith(':'):
                # Check for complex conditions
                condition = stripped[3:-1]
                if ' and ' in condition and ' or ' in condition:
                    operations.append(RefactoringOperation(
                        id=f"complex_conditional_{i}",
                        type=RefactoringType.SIMPLIFY,
                        description=f"第 {i} 行的条件表达式过于复杂",
                        file_path=file_path,
                        line_start=i,
                        impact="low",
                        confidence=0.6,
                    ))
        
        return operations
    
    def _check_complex_conditionals_java(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for complex conditionals in Java."""
        operations = []
        
        # Check for complex conditions
        if_pattern = r"if\s*\(([^)]+)\)"
        for match in re.finditer(if_pattern, code):
            condition = match.group(1)
            if '&&' in condition and '||' in condition:
                operations.append(RefactoringOperation(
                    id=f"complex_conditional_{match.start()}",
                    type=RefactoringType.SIMPLIFY,
                    description="条件表达式过于复杂",
                    file_path=file_path,
                    impact="low",
                    confidence=0.6,
                ))
        
        return operations
    
    def _check_string_concatenation_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for string concatenation in Python."""
        operations = []
        
        # Check for string concatenation in loops
        lines = code.split('\n')
        in_loop = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('for ') or stripped.startswith('while '):
                in_loop = True
            elif in_loop and '+' in stripped and ('"' in stripped or "'" in stripped):
                operations.append(RefactoringOperation(
                    id=f"string_concat_{i}",
                    type=RefactoringType.OPTIMIZE,
                    description=f"第 {i} 行在循环中使用字符串拼接",
                    file_path=file_path,
                    line_start=i,
                    impact="low",
                    confidence=0.7,
                ))
        
        return operations
    
    def _check_list_comprehension_python(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for list comprehension opportunities in Python."""
        operations = []
        
        # Simple pattern: for x in list: result.append(x)
        pattern = r"(\w+)\s*=\s*\[\]\s*\n\s*for\s+(\w+)\s+in\s+(\w+):\s*\n\s*\1\.append\((\w+)\)"
        
        for match in re.finditer(pattern, code):
            result_var = match.group(1)
            loop_var = match.group(2)
            iterable = match.group(3)
            append_var = match.group(4)
            
            if loop_var == append_var:
                operations.append(RefactoringOperation(
                    id=f"list_comprehension_{match.start()}",
                    type=RefactoringType.OPTIMIZE,
                    description=f"考虑使用列表推导式替代 for 循环",
                    file_path=file_path,
                    impact="low",
                    confidence=0.8,
                ))
        
        return operations
    
    def _check_var_usage_javascript(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for var usage in JavaScript."""
        operations = []
        
        var_pattern = r"\bvar\s+(\w+)"
        for match in re.finditer(var_pattern, code):
            operations.append(RefactoringOperation(
                id=f"var_usage_{match.start()}",
                type=RefactoringType.MODERNIZE,
                description=f"使用 var 声明变量 '{match.group(1)}'",
                file_path=file_path,
                impact="low",
                confidence=0.9,
            ))
        
        return operations
    
    def _check_callback_hell_javascript(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[RefactoringOperation]:
        """Check for callback hell in JavaScript."""
        operations = []
        
        # Check for nested callbacks
        lines = code.split('\n')
        nesting_level = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if 'function(' in stripped or '=>' in stripped:
                nesting_level += 1
                if nesting_level > 3:
                    operations.append(RefactoringOperation(
                        id=f"callback_hell_{i}",
                        type=RefactoringType.SIMPLIFY,
                        description=f"第 {i} 行存在嵌套回调（回调地狱）",
                        file_path=file_path,
                        line_start=i,
                        impact="medium",
                        confidence=0.7,
                    ))
            elif stripped.endswith('}') and nesting_level > 0:
                nesting_level -= 1
        
        return operations
    
    async def _apply_operation(
        self,
        code: str,
        operation: RefactoringOperation,
        language: str
    ) -> str:
        """Apply a single refactoring operation."""
        # This is a simplified implementation
        # In a real system, this would perform actual code transformations
        
        if operation.type == RefactoringType.FORMAT:
            return await self._apply_formatting(code, language)
        elif operation.type == RefactoringType.SIMPLIFY:
            return await self._apply_simplification(code, operation, language)
        elif operation.type == RefactoringType.OPTIMIZE:
            return await self._apply_optimization(code, operation, language)
        
        return code
    
    async def _apply_formatting(self, code: str, language: str) -> str:
        """Apply formatting to code."""
        # Simple formatting
        lines = code.split('\n')
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in lines]
        
        # Ensure single newline at end
        formatted = '\n'.join(lines)
        if formatted and not formatted.endswith('\n'):
            formatted += '\n'
        
        # Remove multiple blank lines
        while '\n\n\n' in formatted:
            formatted = formatted.replace('\n\n\n', '\n\n')
        
        return formatted
    
    async def _apply_simplification(
        self,
        code: str,
        operation: RefactoringOperation,
        language: str
    ) -> str:
        """Apply simplification to code."""
        # Simplified implementation
        return code
    
    async def _apply_optimization(
        self,
        code: str,
        operation: RefactoringOperation,
        language: str
    ) -> str:
        """Apply optimization to code."""
        # Simplified implementation
        return code
    
    def _calculate_metrics(
        self,
        code: str,
        operations: List[RefactoringOperation]
    ) -> Dict[str, Any]:
        """Calculate refactoring metrics."""
        lines = code.split('\n')
        
        # Count operation types
        type_counts = {}
        for op in operations:
            type_counts[op.type.value] = type_counts.get(op.type.value, 0) + 1
        
        # Calculate average confidence
        avg_confidence = 0.0
        if operations:
            avg_confidence = sum(op.confidence for op in operations) / len(operations)
        
        return {
            "total_lines": len(lines),
            "total_operations": len(operations),
            "operation_types": type_counts,
            "average_confidence": avg_confidence,
            "high_impact_operations": sum(1 for op in operations if op.impact == "high"),
            "medium_impact_operations": sum(1 for op in operations if op.impact == "medium"),
            "low_impact_operations": sum(1 for op in operations if op.impact == "low"),
        }