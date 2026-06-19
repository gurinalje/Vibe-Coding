"""
AI-Powered Auto-Fixer.

Generates and applies code fixes based on analysis results.
"""

import re
import ast
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Fix:
    """A single code fix."""
    id: str
    category: str
    description: str
    severity: str
    original: str
    replacement: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    confidence: float = 0.0
    auto_applicable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "category": self.category, "description": self.description,
            "severity": self.severity, "original": self.original, "replacement": self.replacement,
            "line_start": self.line_start, "line_end": self.line_end,
            "confidence": self.confidence, "auto_applicable": self.auto_applicable,
        }


@dataclass
class FixResult:
    """Result of auto-fix operation."""
    original_code: str
    fixed_code: str
    fixes_applied: List[Fix] = field(default_factory=list)
    fixes_skipped: List[Fix] = field(default_factory=list)
    syntax_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_code": self.original_code,
            "fixed_code": self.fixed_code,
            "fixes_applied": [f.to_dict() for f in self.fixes_applied],
            "fixes_skipped": [f.to_dict() for f in self.fixes_skipped],
            "syntax_valid": self.syntax_valid,
        }


class AutoFixer:
    """AI-powered code auto-fixer."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load fix rules for each language."""
        return {
            "python": [
                {
                    "id": "fix_bare_except",
                    "pattern": r"except\s*:",
                    "replacement": "except Exception:",
                    "description": "Replace bare except with except Exception",
                    "confidence": 0.95,
                },
                {
                    "id": "fix_is_none",
                    "pattern": r"(\w+)\s*==\s*None",
                    "replacement": r"\1 is None",
                    "description": "Use is None instead of == None",
                    "confidence": 0.95,
                },
                {
                    "id": "fix_is_not_none",
                    "pattern": r"(\w+)\s*!=\s*None",
                    "replacement": r"\1 is not None",
                    "description": "Use is not None instead of != None",
                    "confidence": 0.95,
                },
                {
                    "id": "fix_true_comparison",
                    "pattern": r"(\w+)\s*==\s*True",
                    "replacement": r"\1",
                    "description": "Simplify == True comparison",
                    "confidence": 0.9,
                },
                {
                    "id": "fix_false_comparison",
                    "pattern": r"(\w+)\s*==\s*False",
                    "replacement": r"not \1",
                    "description": "Simplify == False comparison",
                    "confidence": 0.9,
                },
                {
                    "id": "fix_len_comparison",
                    "pattern": r"len\(([^)]+)\)\s*==\s*0",
                    "replacement": r"not \1",
                    "description": "Use not x instead of len(x) == 0",
                    "confidence": 0.85,
                },
            ],
            "java": [
                {
                    "id": "fix_system_out",
                    "pattern": r"System\.out\.print(ln)?\(",
                    "replacement": "logger.info(",
                    "description": "Replace System.out with logger",
                    "confidence": 0.8,
                },
            ],
            "javascript": [
                {
                    "id": "fix_double_equals",
                    "pattern": r"([^=!])==([^=])",
                    "replacement": r"\1===\2",
                    "description": "Use === instead of ==",
                    "confidence": 0.9,
                },
                {
                    "id": "fix_var_to_const",
                    "pattern": r"\bvar\b\s+(\w+)\s*=",
                    "replacement": r"const \1 =",
                    "description": "Use const instead of var",
                    "confidence": 0.7,
                },
            ],
        }

    def fix(self, code: str, language: str, issues: Optional[List[Dict[str, Any]]] = None) -> FixResult:
        """Apply auto-fixes to code."""
        fixes_applied = []
        fixes_skipped = []
        fixed_code = code

        rules = self.rules.get(language, [])
        for rule in rules:
            pattern = rule["pattern"]
            replacement = rule["replacement"]

            new_code = re.sub(pattern, replacement, fixed_code, flags=re.MULTILINE)

            if new_code != fixed_code:
                fix = Fix(
                    id=rule["id"],
                    category="style",
                    description=rule["description"],
                    severity="info",
                    original=fixed_code,
                    replacement=new_code,
                    confidence=rule.get("confidence", 0.8),
                )
                fixed_code = new_code
                fixes_applied.append(fix)

        # Validate syntax for Python
        syntax_valid = True
        if language == "python":
            try:
                ast.parse(fixed_code)
            except SyntaxError:
                syntax_valid = False
                fixed_code = code
                fixes_skipped.extend(fixes_applied)
                fixes_applied = []

        return FixResult(
            original_code=code,
            fixed_code=fixed_code,
            fixes_applied=fixes_applied,
            fixes_skipped=fixes_skipped,
            syntax_valid=syntax_valid,
        )

    def get_available_fixes(self, language: str) -> List[Dict[str, Any]]:
        """Get list of available fixes for a language."""
        rules = self.rules.get(language, [])
        return [{"id": r["id"], "description": r["description"], "confidence": r.get("confidence", 0.8)} for r in rules]
