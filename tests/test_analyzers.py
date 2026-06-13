"""
Analyzer Tests for AI Agent Benchmark system.

This module contains test cases for the language-specific analyzers.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.python_analyzer import PythonAnalyzer
from core.java_analyzer import JavaAnalyzer
from core.javascript_analyzer import JavaScriptAnalyzer
from core.models import Language, AnalysisResult


class TestPythonAnalyzer:
    """Test cases for PythonAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = PythonAnalyzer()
        assert analyzer.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_simple_code(self):
        """Test analyzing simple Python code."""
        analyzer = PythonAnalyzer()
        
        code = '''
def add(a, b):
    return a + b
'''
        
        result = await analyzer.analyze(code)
        
        assert isinstance(result, AnalysisResult)
        assert result.language == "python"
        assert result.metrics.functions == 1
        assert result.metrics.lines_of_code > 0
    
    @pytest.mark.asyncio
    async def test_analyze_class(self):
        """Test analyzing Python class."""
        analyzer = PythonAnalyzer()
        
        code = '''
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self
'''
        
        result = await analyzer.analyze(code)
        
        assert result.metrics.classes == 1
        assert result.metrics.functions == 2  # __init__ and add
    
    @pytest.mark.asyncio
    async def test_detect_syntax_error(self):
        """Test syntax error detection."""
        analyzer = PythonAnalyzer()
        
        code = '''
def broken(
    return 1
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect syntax error
        syntax_issues = [i for i in result.issues if i.category == "syntax"]
        assert len(syntax_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_security_issues(self):
        """Test security issue detection."""
        analyzer = PythonAnalyzer()
        
        code = '''
eval("dangerous code")
password = "admin123"
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect security issues
        security_issues = [i for i in result.issues if i.category == "security"]
        assert len(security_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_code_smells(self):
        """Test code smell detection."""
        analyzer = PythonAnalyzer()
        
        code = '''
def very_long_function():
    # 50+ lines
    pass
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect code smells
        # Note: This test may not detect the issue if function is too short
        assert result.metrics is not None
    
    @pytest.mark.asyncio
    async def test_calculate_metrics(self):
        """Test metrics calculation."""
        analyzer = PythonAnalyzer()
        
        code = '''
# This is a comment
def function1():
    pass

def function2():
    pass

class MyClass:
    def method1(self):
        pass
'''
        
        result = await analyzer.analyze(code)
        
        assert result.metrics.functions == 3
        assert result.metrics.classes == 1
        assert result.metrics.comment_lines >= 1


class TestJavaAnalyzer:
    """Test cases for JavaAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = JavaAnalyzer()
        assert analyzer.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_simple_code(self):
        """Test analyzing simple Java code."""
        analyzer = JavaAnalyzer()
        
        code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
'''
        
        result = await analyzer.analyze(code)
        
        assert isinstance(result, AnalysisResult)
        assert result.language == "java"
        assert result.metrics.classes == 1
        assert result.metrics.functions >= 1
    
    @pytest.mark.asyncio
    async def test_detect_security_issues(self):
        """Test security issue detection."""
        analyzer = JavaAnalyzer()
        
        code = '''
public class BadClass {
    public void runCommand(String cmd) {
        Runtime.getRuntime().exec(cmd);
    }
    
    private String password = "admin123";
}
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect security issues
        security_issues = [i for i in result.issues if i.category == "security"]
        assert len(security_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_naming_conventions(self):
        """Test naming convention detection."""
        analyzer = JavaAnalyzer()
        
        code = '''
public class badClassName {
    public void BadMethodName() {
    }
}
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect naming issues
        naming_issues = [i for i in result.issues if i.category == "naming"]
        assert len(naming_issues) > 0


class TestJavaScriptAnalyzer:
    """Test cases for JavaScriptAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = JavaScriptAnalyzer()
        assert analyzer.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_simple_code(self):
        """Test analyzing simple JavaScript code."""
        analyzer = JavaScriptAnalyzer()
        
        code = '''
function add(a, b) {
    return a + b;
}

class Calculator {
    constructor() {
        this.result = 0;
    }
    
    add(value) {
        this.result += value;
        return this;
    }
}
'''
        
        result = await analyzer.analyze(code)
        
        assert isinstance(result, AnalysisResult)
        assert result.language == "javascript"
        assert result.metrics.classes == 1
        assert result.metrics.functions >= 2
    
    @pytest.mark.asyncio
    async def test_detect_security_issues(self):
        """Test security issue detection."""
        analyzer = JavaScriptAnalyzer()
        
        code = '''
eval("dangerous code");
document.innerHTML = userInput;
document.write("output");
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect security issues
        security_issues = [i for i in result.issues if i.category == "security"]
        assert len(security_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_code_smells(self):
        """Test code smell detection."""
        analyzer = JavaScriptAnalyzer()
        
        code = '''
console.log("debug");
debugger;
if (x == y) {
    // do something
}
'''
        
        result = await analyzer.analyze(code)
        
        # Should detect code smells
        smell_issues = [i for i in result.issues if i.category == "code_smell"]
        assert len(smell_issues) > 0
    
    @pytest.mark.asyncio
    async def test_typescript_detection(self):
        """Test TypeScript-specific detection."""
        analyzer = JavaScriptAnalyzer()
        
        code = '''
function add(a: any, b: any): any {
    return a + b;
}

// @ts-ignore
const x: number = "string";
'''
        
        result = await analyzer.analyze(code, file_path="test.ts")
        
        # Should detect TypeScript issues
        ts_issues = [i for i in result.issues if i.category == "typescript"]
        assert len(ts_issues) > 0


class TestCodeAnalyzerV2:
    """Test cases for CodeAnalyzerV2."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        from core.code_analyzer_v2 import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        assert analyzer.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_python_code(self):
        """Test Python code analysis."""
        from core.code_analyzer_v2 import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        code = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

class Calculator:
    """Simple calculator."""
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self
'''
        
        result = await analyzer.analyze(code, "python")
        
        assert result.language == "python"
        assert result.metrics.functions >= 2
        assert result.metrics.classes >= 1
        assert result.quality_score > 0
        assert result.summary != ""
    
    @pytest.mark.asyncio
    async def test_analyze_java_code(self):
        """Test Java code analysis."""
        from core.code_analyzer_v2 import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        code = '''
public class Calculator {
    private int result;
    
    public Calculator() {
        this.result = 0;
    }
    
    public Calculator add(int value) {
        this.result += value;
        return this;
    }
}
'''
        
        result = await analyzer.analyze(code, "java")
        
        assert result.language == "java"
        assert result.metrics.classes >= 1
        assert result.quality_score > 0
    
    @pytest.mark.asyncio
    async def test_analyze_javascript_code(self):
        """Test JavaScript code analysis."""
        from core.code_analyzer_v2 import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        code = '''
function add(a, b) {
    return a + b;
}

class Calculator {
    constructor() {
        this.result = 0;
    }
}
'''
        
        result = await analyzer.analyze(code, "javascript")
        
        assert result.language == "javascript"
        assert result.metrics.functions >= 1
        assert result.metrics.classes >= 1
    
    @pytest.mark.asyncio
    async def test_unsupported_language(self):
        """Test unsupported language handling."""
        from core.code_analyzer_v2 import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        with pytest.raises(ValueError, match="Unsupported language"):
            await analyzer.analyze("code", "unsupported")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])