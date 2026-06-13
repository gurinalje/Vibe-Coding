"""
Developer Agent for AI Agent Benchmark system.

This agent is responsible for code refactoring and optimization,
including automatic code improvements, refactoring suggestion execution,
refactoring result verification, and refactoring history management.
"""

import asyncio
import copy
import hashlib
import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .base_agent import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)


class RefactoringType(str, Enum):
    """Types of refactoring operations."""
    EXTRACT_METHOD = "extract_method"
    RENAME = "rename"
    INLINE = "inline"
    MOVE = "move"
    SIMPLIFY = "simplify"
    OPTIMIZE = "optimize"
    FORMAT = "format"


class VerificationStatus(str, Enum):
    """Status of refactoring verification."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class RefactoringSuggestion:
    """A refactoring suggestion."""
    id: str
    type: RefactoringType
    description: str
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    original_code: Optional[str] = None
    suggested_code: Optional[str] = None
    impact: str = "low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert suggestion to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "impact": self.impact,
        }


@dataclass
class VerificationResult:
    """Result of refactoring verification."""
    status: VerificationStatus
    original_hash: str
    refactored_hash: str
    syntax_valid: bool
    semantic_changes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert verification result to dictionary."""
        return {
            "status": self.status.value,
            "original_hash": self.original_hash,
            "refactored_hash": self.refactored_hash,
            "syntax_valid": self.syntax_valid,
            "semantic_changes": self.semantic_changes,
            "warnings": self.warnings,
            "details": self.details,
        }


@dataclass
class RefactoringRecord:
    """A single refactoring history record."""
    id: str
    timestamp: str
    language: str
    file_path: Optional[str]
    original_code_hash: str
    refactored_code_hash: str
    suggestions_applied: List[str]
    changes_made: List[str]
    verification_status: str
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "language": self.language,
            "file_path": self.file_path,
            "original_code_hash": self.original_code_hash,
            "refactored_code_hash": self.refactored_code_hash,
            "suggestions_applied": self.suggestions_applied,
            "changes_made": self.changes_made,
            "verification_status": self.verification_status,
            "metrics": self.metrics,
        }


@dataclass
class RefactoringResult:
    """Refactoring result."""
    success: bool
    suggestions: List[RefactoringSuggestion]
    refactored_code: Optional[str] = None
    changes_made: Optional[List[str]] = None
    verification: Optional[VerificationResult] = None
    history_record: Optional[RefactoringRecord] = None
    metrics: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.changes_made is None:
            self.changes_made = []
        if self.metrics is None:
            self.metrics = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "refactored_code": self.refactored_code,
            "changes_made": self.changes_made,
            "verification": self.verification.to_dict() if self.verification else None,
            "history_record": self.history_record.to_dict() if self.history_record else None,
            "metrics": self.metrics,
        }


class DeveloperAgent(BaseAgent):
    """Agent responsible for code refactoring and optimization.

    Core capabilities:
    - Receive refactoring suggestions and execute automatic refactoring
    - Generate refactoring plans with before/after comparisons
    - Verify refactoring results (syntax check, hash comparison, semantic analysis)
    - Maintain a persistent refactoring history with full audit trail
    """

    def __init__(
        self,
        name: str = "developer",
        message_queue=None,
        config: Optional[Dict[str, Any]] = None,
        history_dir: Optional[str] = None,
    ):
        """Initialize developer agent.

        Args:
            name: Agent name identifier.
            message_queue: Shared message queue for inter-agent communication.
            config: Optional configuration overrides.
            history_dir: Directory path to persist refactoring history as JSON.
                         If None, history is kept only in memory.
        """
        super().__init__(name=name, agent_type="developer", message_queue=message_queue, config=config)

        # Refactoring rules
        self.refactoring_rules = self._load_refactoring_rules()

        # Statistics
        self.refactorings_completed = 0
        self.suggestions_made = 0
        self.verifications_performed = 0
        self.verifications_failed = 0

        # Refactoring history (in-memory list, optionally persisted to disk)
        self._history: List[RefactoringRecord] = []
        self._history_dir = history_dir
        if self._history_dir:
            os.makedirs(self._history_dir, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Rule loading
    # ------------------------------------------------------------------ #

    def _load_refactoring_rules(self) -> Dict[str, Any]:
        """Load language-specific refactoring rules.

        Returns:
            Dictionary keyed by language name with formatting and
            refactoring parameters.
        """
        return {
            "python": {
                "max_line_length": 88,
                "indentation": 4,
                "import_order": ["stdlib", "third_party", "local"],
                "formatting": {
                    "trailing_commas": True,
                    "string_quotes": "double",
                    "max_line_length": 88,
                },
            },
            "java": {
                "max_line_length": 120,
                "indentation": 4,
                "braces": "same_line",
                "naming": {
                    "methods": "camelCase",
                    "classes": "PascalCase",
                    "constants": "UPPER_SNAKE_CASE",
                },
            },
        }

    # ------------------------------------------------------------------ #
    # Process entry point
    # ------------------------------------------------------------------ #

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a refactoring task.

        The ``task`` dictionary is expected to contain:

        - ``code`` (str): Source code to refactor.
        - ``language`` (str, optional): Programming language, defaults to ``"python"``.
        - ``file_path`` (str, optional): Original file path for context.
        - ``refactoring_type`` (str, optional): Force a specific refactoring type.
        - ``suggestions`` (list[dict], optional): External suggestions to apply.
          Each dict should have ``type``, ``description``, and optionally
          ``original_code`` / ``suggested_code``.

        Args:
            task: Task data dictionary.

        Returns:
            Dictionary containing refactoring result, verification, and history record.
        """
        code = task.get("code", "")
        language = task.get("language", "python")
        file_path = task.get("file_path")
        refactoring_type = task.get("refactoring_type")
        external_suggestions = task.get("suggestions", [])

        logger.info("Refactoring %s code (%d chars)", language, len(code))

        # Perform refactoring
        refactoring_result = await self._refactor_code(
            code, language, file_path, refactoring_type, external_suggestions
        )

        # Verify the refactoring result
        verification = await self._verify_refactoring(code, refactoring_result.refactored_code or code, language)
        refactoring_result.verification = verification

        # Create history record
        history_record = self._create_history_record(
            code, refactoring_result.refactored_code or code, language, file_path,
            refactoring_result.changes_made or [], refactoring_result.suggestions,
            verification,
        )
        refactoring_result.history_record = history_record

        # Persist history
        self._history.append(history_record)
        if self._history_dir:
            self._save_history_to_disk(history_record)

        # Update statistics
        self.refactorings_completed += 1
        self.suggestions_made += len(refactoring_result.suggestions)
        self.verifications_performed += 1
        if verification.status == VerificationStatus.FAILED:
            self.verifications_failed += 1

        return refactoring_result.to_dict()

    # ------------------------------------------------------------------ #
    # Core refactoring pipeline
    # ------------------------------------------------------------------ #

    async def _refactor_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None,
        refactoring_type: Optional[str] = None,
        external_suggestions: Optional[List[Dict[str, Any]]] = None,
    ) -> RefactoringResult:
        """Refactor code and generate result.

        Args:
            code: Source code to refactor.
            language: Programming language identifier.
            file_path: Optional original file path.
            refactoring_type: Optional specific refactoring type override.
            external_suggestions: Optional list of external suggestions to apply.

        Returns:
            A ``RefactoringResult`` with refactored code, changes, and suggestions.
        """
        suggestions: List[RefactoringSuggestion] = []
        refactored_code = code
        changes_made: List[str] = []

        # Get rules for language
        rules = self.refactoring_rules.get(language, {})

        # Apply external suggestions first
        if external_suggestions:
            for ext_sug in external_suggestions:
                sug_id = ext_sug.get("id", f"external_{len(suggestions)}")
                suggestions.append(RefactoringSuggestion(
                    id=sug_id,
                    type=RefactoringType(ext_sug.get("type", "simplify")),
                    description=ext_sug.get("description", ""),
                    original_code=ext_sug.get("original_code"),
                    suggested_code=ext_sug.get("suggested_code"),
                    impact=ext_sug.get("impact", "low"),
                ))
                # If the suggestion has both original and suggested code, apply it
                if ext_sug.get("original_code") and ext_sug.get("suggested_code"):
                    if ext_sug["original_code"] in refactored_code:
                        refactored_code = refactored_code.replace(
                            ext_sug["original_code"], ext_sug["suggested_code"], 1
                        )
                        changes_made.append(f"应用外部建议: {ext_sug.get('description', sug_id)}")

        # Apply built-in refactoring operations
        if refactoring_type is None or refactoring_type == "format":
            refactored_code, format_changes = await self._format_code(refactored_code, language, rules)
            changes_made.extend(format_changes)

        if refactoring_type is None or refactoring_type == "simplify":
            refactored_code, simplify_changes, simplify_suggestions = await self._simplify_code(
                refactored_code, language
            )
            changes_made.extend(simplify_changes)
            suggestions.extend(simplify_suggestions)

        if refactoring_type is None or refactoring_type == "optimize":
            refactored_code, optimize_changes, optimize_suggestions = await self._optimize_code(
                refactored_code, language
            )
            changes_made.extend(optimize_changes)
            suggestions.extend(optimize_suggestions)

        # Generate additional suggestions
        additional_suggestions = await self._generate_suggestions(refactored_code, language)
        suggestions.extend(additional_suggestions)

        # Calculate metrics
        metrics = self._calculate_metrics(code, refactored_code, language, suggestions)

        return RefactoringResult(
            success=True,
            suggestions=suggestions,
            refactored_code=refactored_code,
            changes_made=changes_made,
            metrics=metrics,
        )

    # ------------------------------------------------------------------ #
    # Formatting
    # ------------------------------------------------------------------ #

    async def _format_code(
        self,
        code: str,
        language: str,
        rules: Dict[str, Any],
    ) -> Tuple[str, List[str]]:
        """Format code according to language rules.

        Args:
            code: Source code to format.
            language: Programming language identifier.
            rules: Language-specific formatting rules.

        Returns:
            Tuple of (formatted_code, list_of_changes).
        """
        changes: List[str] = []
        formatted_code = code

        # Fix trailing whitespace
        lines = formatted_code.split("\n")
        new_lines = []
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped != line:
                changes.append(f"移除第 {i + 1} 行尾部空白")
            new_lines.append(stripped)
        formatted_code = "\n".join(new_lines)

        # Ensure single newline at end
        if formatted_code and not formatted_code.endswith("\n"):
            formatted_code += "\n"
            changes.append("添加文件末尾换行符")

        # Fix multiple blank lines (Python)
        if language == "python":
            while "\n\n\n" in formatted_code:
                formatted_code = formatted_code.replace("\n\n\n", "\n\n")
                changes.append("减少多余空行")

        return formatted_code, changes

    # ------------------------------------------------------------------ #
    # Simplification
    # ------------------------------------------------------------------ #

    async def _simplify_code(
        self,
        code: str,
        language: str,
    ) -> Tuple[str, List[str], List[RefactoringSuggestion]]:
        """Simplify code patterns.

        Args:
            code: Source code to simplify.
            language: Programming language identifier.

        Returns:
            Tuple of (simplified_code, changes, suggestions).
        """
        changes: List[str] = []
        suggestions: List[RefactoringSuggestion] = []
        simplified_code = code

        if language == "python":
            # Remove redundant pass statements
            pass_pattern = r"^\s*pass\s*$"
            lines = simplified_code.split("\n")
            new_lines = []
            for i, line in enumerate(lines):
                if re.match(pass_pattern, line):
                    prev_line = lines[i - 1] if i > 0 else ""
                    if not (
                        prev_line.strip().endswith(":")
                        or re.match(
                            r"^\s*(class|def|if|else|elif|for|while|try|except|finally)\s+",
                            prev_line,
                        )
                    ):
                        changes.append(f"移除第 {i + 1} 行多余的 pass 语句")
                        continue
                new_lines.append(line)
            simplified_code = "\n".join(new_lines)

        return simplified_code, changes, suggestions

    # ------------------------------------------------------------------ #
    # Optimization
    # ------------------------------------------------------------------ #

    async def _optimize_code(
        self,
        code: str,
        language: str,
    ) -> Tuple[str, List[str], List[RefactoringSuggestion]]:
        """Optimize code patterns.

        Args:
            code: Source code to optimize.
            language: Programming language identifier.

        Returns:
            Tuple of (optimized_code, changes, suggestions).
        """
        changes: List[str] = []
        suggestions: List[RefactoringSuggestion] = []
        optimized_code = code

        if language == "python":
            # Optimize list comprehensions
            pattern = (
                r"(\s*)(\w+)\s*=\s*\[\]\s*\n"
                r"\s*for\s+(\w+)\s+in\s+(\w+):\s*\n"
                r"\s*\2\.append\((\w+)\)"
            )
            match = re.search(pattern, optimized_code)
            if match:
                indent = match.group(1)
                result_var = match.group(2)
                loop_var = match.group(3)
                iterable = match.group(4)
                append_var = match.group(5)

                if loop_var == append_var:
                    optimized_code = re.sub(
                        pattern,
                        f"{indent}{result_var} = [{loop_var} for {loop_var} in {iterable}]",
                        optimized_code,
                    )
                    changes.append("将 for 循环优化为列表推导式")

            # Suggest further optimizations
            if "for " in optimized_code and ".append(" in optimized_code:
                suggestions.append(RefactoringSuggestion(
                    id="optimize_list_comprehension",
                    type=RefactoringType.OPTIMIZE,
                    description="考虑使用列表推导式替代 for 循环",
                    impact="low",
                ))

        return optimized_code, changes, suggestions

    # ------------------------------------------------------------------ #
    # Suggestion generation
    # ------------------------------------------------------------------ #

    async def _generate_suggestions(
        self,
        code: str,
        language: str,
    ) -> List[RefactoringSuggestion]:
        """Generate additional refactoring suggestions.

        Args:
            code: Source code to analyze.
            language: Programming language identifier.

        Returns:
            List of ``RefactoringSuggestion`` objects.
        """
        suggestions: List[RefactoringSuggestion] = []

        if language == "python":
            # Check for long functions
            func_pattern = r"^\s*def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*\w+\s*)?:"
            for match in re.finditer(func_pattern, code, re.MULTILINE):
                func_name = match.group(1)
                func_start = match.end()

                lines = code[func_start:].split("\n")
                func_lines = 0
                for line in lines:
                    if line.strip() and not line.startswith(" "):
                        break
                    func_lines += 1

                if func_lines > 30:
                    suggestions.append(RefactoringSuggestion(
                        id=f"suggest_extract_{func_name}",
                        type=RefactoringType.EXTRACT_METHOD,
                        description=f"函数 '{func_name}' 较长 ({func_lines} 行)，考虑拆分为更小的函数",
                        impact="medium",
                    ))

            # Check for duplicated code
            lines = code.split("\n")
            line_groups: Dict[str, List[int]] = {}
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and len(stripped) > 10:
                    if stripped not in line_groups:
                        line_groups[stripped] = []
                    line_groups[stripped].append(i + 1)

            for line_content, line_numbers in line_groups.items():
                if len(line_numbers) > 2:
                    suggestions.append(RefactoringSuggestion(
                        id=f"suggest_dedup_{line_numbers[0]}",
                        type=RefactoringType.EXTRACT_METHOD,
                        description=f"发现重复代码 (行 {', '.join(map(str, line_numbers[:5]))}...)",
                        impact="medium",
                    ))

        return suggestions

    # ------------------------------------------------------------------ #
    # Verification
    # ------------------------------------------------------------------ #

    async def _verify_refactoring(
        self,
        original_code: str,
        refactored_code: str,
        language: str,
    ) -> VerificationResult:
        """Verify the refactoring result.

        Performs:
        - Hash comparison (detect if any change was actually made)
        - Syntax validity check (parse the refactored code)
        - Semantic change detection (identify structural differences)

        Args:
            original_code: The source code before refactoring.
            refactored_code: The source code after refactoring.
            language: Programming language identifier.

        Returns:
            A ``VerificationResult`` with status and detailed diagnostics.
        """
        logger.info("Verifying refactoring result for %s", language)

        original_hash = self._compute_hash(original_code)
        refactored_hash = self._compute_hash(refactored_code)

        # 1. Syntax validity check
        syntax_valid = await self._check_syntax(refactored_code, language)

        # 2. Semantic change detection
        semantic_changes = self._detect_semantic_changes(original_code, refactored_code, language)

        # 3. Determine warnings
        warnings: List[str] = []
        if original_hash == refactored_hash:
            warnings.append("重构前后代码完全相同，未产生实际变更")
        if not syntax_valid:
            warnings.append("重构后代码存在语法错误")

        # 4. Determine overall status
        if not syntax_valid:
            status = VerificationStatus.FAILED
        elif original_hash == refactored_hash:
            status = VerificationStatus.WARNING
        else:
            status = VerificationStatus.PASSED

        details = {
            "original_line_count": len(original_code.split("\n")),
            "refactored_line_count": len(refactored_code.split("\n")),
            "semantic_change_count": len(semantic_changes),
        }

        return VerificationResult(
            status=status,
            original_hash=original_hash,
            refactored_hash=refactored_hash,
            syntax_valid=syntax_valid,
            semantic_changes=semantic_changes,
            warnings=warnings,
            details=details,
        )

    @staticmethod
    def _compute_hash(code: str) -> str:
        """Compute SHA-256 hex digest for code content.

        Args:
            code: Code string to hash.

        Returns:
            Hex digest string.
        """
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    async def _check_syntax(code: str, language: str) -> bool:
        """Check whether the code has valid syntax.

        Args:
            code: Source code to validate.
            language: Programming language identifier.

        Returns:
            ``True`` if syntax is valid, ``False`` otherwise.
        """
        if language == "python":
            try:
                compile(code, "<refactored>", "exec")
                return True
            except SyntaxError:
                return False
        elif language == "java":
            # Basic brace matching check for Java
            brace_count = 0
            for char in code:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                if brace_count < 0:
                    return False
            return brace_count == 0
        # For unknown languages, assume valid
        return True

    def _detect_semantic_changes(
        self,
        original_code: str,
        refactored_code: str,
        language: str,
    ) -> List[str]:
        """Detect structural / semantic differences between two code versions.

        This performs a lightweight heuristic comparison (not full AST).

        Args:
            original_code: Source code before refactoring.
            refactored_code: Source code after refactoring.
            language: Programming language identifier.

        Returns:
            List of human-readable descriptions of semantic changes.
        """
        changes: List[str] = []

        if language == "python":
            # Compare function definitions
            orig_funcs = set(re.findall(r"def\s+(\w+)", original_code))
            new_funcs = set(re.findall(r"def\s+(\w+)", refactored_code))
            added_funcs = new_funcs - orig_funcs
            removed_funcs = orig_funcs - new_funcs
            if added_funcs:
                changes.append(f"新增函数: {', '.join(sorted(added_funcs))}")
            if removed_funcs:
                changes.append(f"移除函数: {', '.join(sorted(removed_funcs))}")

            # Compare class definitions
            orig_classes = set(re.findall(r"class\s+(\w+)", original_code))
            new_classes = set(re.findall(r"class\s+(\w+)", refactored_code))
            added_classes = new_classes - orig_classes
            removed_classes = orig_classes - new_classes
            if added_classes:
                changes.append(f"新增类: {', '.join(sorted(added_classes))}")
            if removed_classes:
                changes.append(f"移除类: {', '.join(sorted(removed_classes))}")

            # Compare import statements
            orig_imports = set(re.findall(r"^(?:import|from)\s+.+", original_code, re.MULTILINE))
            new_imports = set(re.findall(r"^(?:import|from)\s+.+", refactored_code, re.MULTILINE))
            if orig_imports != new_imports:
                changes.append("导入语句发生变化")

        elif language == "java":
            # Compare method signatures
            orig_methods = set(re.findall(r"(?:public|private|protected|static)\s+\w+\s+(\w+)\s*\(", original_code))
            new_methods = set(re.findall(r"(?:public|private|protected|static)\s+\w+\s+(\w+)\s*\(", refactored_code))
            added_methods = new_methods - orig_methods
            removed_methods = orig_methods - new_methods
            if added_methods:
                changes.append(f"新增方法: {', '.join(sorted(added_methods))}")
            if removed_methods:
                changes.append(f"移除方法: {', '.join(sorted(removed_methods))}")

            # Compare class definitions
            orig_classes = set(re.findall(r"class\s+(\w+)", original_code))
            new_classes = set(re.findall(r"class\s+(\w+)", refactored_code))
            added_classes = new_classes - orig_classes
            removed_classes = orig_classes - new_classes
            if added_classes:
                changes.append(f"新增类: {', '.join(sorted(added_classes))}")
            if removed_classes:
                changes.append(f"移除类: {', '.join(sorted(removed_classes))}")

        return changes

    # ------------------------------------------------------------------ #
    # History management
    # ------------------------------------------------------------------ #

    def _create_history_record(
        self,
        original_code: str,
        refactored_code: str,
        language: str,
        file_path: Optional[str],
        changes_made: List[str],
        suggestions: List[RefactoringSuggestion],
        verification: VerificationResult,
    ) -> RefactoringRecord:
        """Create a history record for this refactoring operation.

        Args:
            original_code: Source code before refactoring.
            refactored_code: Source code after refactoring.
            language: Programming language identifier.
            file_path: Optional original file path.
            changes_made: List of change descriptions applied.
            suggestions: List of suggestions generated.
            verification: Verification result.

        Returns:
            A ``RefactoringRecord`` summarizing the operation.
        """
        return RefactoringRecord(
            id=f"refactor_{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            language=language,
            file_path=file_path,
            original_code_hash=self._compute_hash(original_code),
            refactored_code_hash=self._compute_hash(refactored_code),
            suggestions_applied=[s.id for s in suggestions],
            changes_made=changes_made,
            verification_status=verification.status.value,
            metrics={
                "suggestions_count": len(suggestions),
                "changes_count": len(changes_made),
                "original_lines": len(original_code.split("\n")),
                "refactored_lines": len(refactored_code.split("\n")),
            },
        )

    def _save_history_to_disk(self, record: RefactoringRecord) -> None:
        """Persist a single history record to a JSON file on disk.

        Each record is saved as a separate file named by its ID to avoid
        concurrency issues.

        Args:
            record: The history record to persist.
        """
        if not self._history_dir:
            return

        file_path = os.path.join(self._history_dir, f"{record.id}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
            logger.debug("History record saved to %s", file_path)
        except OSError as exc:
            logger.error("Failed to save history record: %s", exc)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve refactoring history records.

        Args:
            limit: Maximum number of records to return (most recent first).

        Returns:
            List of history record dictionaries, ordered from most recent to oldest.
        """
        records = list(reversed(self._history))
        if limit is not None:
            records = records[:limit]
        return [r.to_dict() for r in records]

    # ------------------------------------------------------------------ #
    # Metrics
    # ------------------------------------------------------------------ #

    def _calculate_metrics(
        self,
        original_code: str,
        refactored_code: str,
        language: str,
        suggestions: List[RefactoringSuggestion],
    ) -> Dict[str, Any]:
        """Calculate refactoring metrics comparing before and after.

        Args:
            original_code: Source code before refactoring.
            refactored_code: Source code after refactoring.
            language: Programming language identifier.
            suggestions: List of suggestions generated during refactoring.

        Returns:
            Dictionary of metrics.
        """
        original_lines = len(original_code.split("\n"))
        refactored_lines = len(refactored_code.split("\n"))

        original_complexity = self._estimate_complexity(original_code, language)
        refactored_complexity = self._estimate_complexity(refactored_code, language)

        return {
            "original_lines": original_lines,
            "refactored_lines": refactored_lines,
            "line_change": refactored_lines - original_lines,
            "line_change_percent": ((refactored_lines - original_lines) / max(1, original_lines)) * 100,
            "original_complexity": original_complexity,
            "refactored_complexity": refactored_complexity,
            "complexity_change": refactored_complexity - original_complexity,
            "suggestions_count": len(suggestions),
            "suggestion_types": list(set(s.type.value for s in suggestions)),
        }

    @staticmethod
    def _estimate_complexity(code: str, language: str) -> int:
        """Estimate code complexity via control structure counting.

        Args:
            code: Source code to analyze.
            language: Programming language identifier.

        Returns:
            Estimated complexity score (higher = more complex).
        """
        complexity = 1

        if language == "python":
            control_patterns = [
                r"\bif\b", r"\belif\b", r"\belse\b",
                r"\bfor\b", r"\bwhile\b",
                r"\btry\b", r"\bexcept\b", r"\bwith\b",
            ]
        elif language == "java":
            control_patterns = [
                r"\bif\b", r"\belse\b",
                r"\bfor\b", r"\bwhile\b",
                r"\bswitch\b", r"\bcase\b",
                r"\btry\b", r"\bcatch\b",
            ]
        else:
            return complexity

        for pattern in control_patterns:
            complexity += len(re.findall(pattern, code))

        return complexity
