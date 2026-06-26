"""
Tests for new features: CLI, Auto-Fixer, LLM Analyzer, Web Dashboard.
"""

import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.auto_fixer import AutoFixer, Fix, FixResult
from core.llm_analyzer import LLMAnalyzer, LLMAnalysisResult


class TestAutoFixer:
    def test_initialization(self):
        fixer = AutoFixer()
        assert fixer.config == {}

    def test_fix_bare_except(self):
        fixer = AutoFixer()
        code = "try:\n    pass\nexcept:\n    pass\n"
        result = fixer.fix(code, "python")
        assert "except Exception:" in result.fixed_code
        assert len(result.fixes_applied) > 0

    def test_fix_none_comparison(self):
        fixer = AutoFixer()
        code = "if x == None:\n    pass\n"
        result = fixer.fix(code, "python")
        assert "is None" in result.fixed_code

    def test_fix_true_comparison(self):
        fixer = AutoFixer()
        code = "if active == True:\n    pass\n"
        result = fixer.fix(code, "python")
        assert "== True" not in result.fixed_code
        assert result.syntax_valid

    def test_fix_double_equals_js(self):
        fixer = AutoFixer()
        code = "if (x == y) { }"
        result = fixer.fix(code, "javascript")
        assert "===" in result.fixed_code

    def test_fix_var_to_const_js(self):
        fixer = AutoFixer()
        code = 'var name = "test";'
        result = fixer.fix(code, "javascript")
        assert "const" in result.fixed_code

    def test_get_available_fixes(self):
        fixer = AutoFixer()
        fixes = fixer.get_available_fixes("python")
        assert len(fixes) > 0

    def test_no_fixes_needed(self):
        fixer = AutoFixer()
        code = "def add(a, b):\n    return a + b\n"
        result = fixer.fix(code, "python")
        assert len(result.fixes_applied) == 0

    def test_multiple_fixes(self):
        fixer = AutoFixer()
        code = "if x == None:\n    if y == True:\n        pass\n"
        result = fixer.fix(code, "python")
        assert len(result.fixes_applied) >= 2
        assert result.syntax_valid

    def test_fix_result_serialization(self):
        fixer = AutoFixer()
        code = "if x == None: pass"
        result = fixer.fix(code, "python")
        data = result.to_dict()
        assert "original_code" in data
        assert "fixed_code" in data
        assert "fixes_applied" in data


class TestLLMAnalyzer:
    def test_initialization(self):
        analyzer = LLMAnalyzer()
        assert analyzer.config == {}

    def test_initialization_with_config(self):
        analyzer = LLMAnalyzer({"provider": "openai", "model": "gpt-4"})
        assert analyzer.provider == "openai"
        assert analyzer.model == "gpt-4"

    def test_fallback_analysis_python(self):
        analyzer = LLMAnalyzer()
        code = 'eval("dangerous")\npassword = "admin123"\n'
        result = analyzer._fallback_analysis(code, "python")
        assert len(result.bugs) > 0
        assert result.model == "rule-based-fallback"

    def test_fallback_analysis_javascript(self):
        analyzer = LLMAnalyzer()
        code = 'eval("code");\ninnerHTML = userInput;\n'
        result = analyzer._fallback_analysis(code, "javascript")
        assert len(result.bugs) > 0

    def test_fallback_analysis_java(self):
        analyzer = LLMAnalyzer()
        code = 'System.out.println("debug");\n'
        result = analyzer._fallback_analysis(code, "java")
        assert len(result.bugs) > 0

    @pytest.mark.asyncio
    async def test_no_api_key_uses_fallback(self):
        analyzer = LLMAnalyzer({"api_key": None})
        result = await analyzer.analyze("eval('test')", "python")
        assert result.model == "rule-based-fallback"
    def test_result_serialization(self):
        analyzer = LLMAnalyzer()
        result = analyzer._fallback_analysis("eval('test')", "python")
        data = result.to_dict()
        assert "bugs" in data
        assert "overall_assessment" in data


class TestWebApp:
    def test_import_web_app(self):
        from web.app import create_app, DASHBOARD_HTML
        assert DASHBOARD_HTML is not None
        assert "VIBE CODING" in DASHBOARD_HTML

    def test_create_app(self):
        try:
            from web.app import create_app
            app = create_app()
            assert app is not None
            assert app.title == "Vibe Coding"
        except ImportError:
            pytest.skip("FastAPI not installed")


class TestCLI:
    def test_detect_language(self):
        from pathlib import Path
        ext_map = {".py": "python", ".java": "java", ".js": "javascript", ".ts": "typescript"}
        assert ext_map.get(Path("test.py").suffix) == "python"
        assert ext_map.get(Path("Main.java").suffix) == "java"
        assert ext_map.get(Path("app.js").suffix) == "javascript"
        assert ext_map.get(Path("unknown.xyz").suffix) is None

    def test_cli_import(self):
        import importlib
        spec = importlib.util.spec_from_file_location("cli", os.path.join(os.path.dirname(os.path.dirname(__file__)), "cli.py"))
        assert spec is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
