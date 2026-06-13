"""
Core Module Tests for AI Agent Benchmark system.

This module contains test cases for the core components
including code analyzer, refactoring engine, security scanner,
and performance analyzer.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.code_analyzer import CodeAnalyzer
from core.refactoring_engine import RefactoringEngine
from core.security_scanner import SecurityScanner
from core.performance_analyzer import PerformanceAnalyzer


class TestCodeAnalyzer:
    """Test cases for CodeAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = CodeAnalyzer()
        assert analyzer.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_python_code(self):
        """Test Python code analysis."""
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
    
    @pytest.mark.asyncio
    async def test_analyze_java_code(self):
        """Test Java code analysis."""
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
    
    public int getResult() {
        return this.result;
    }
}
'''
        
        result = await analyzer.analyze(code, "java")
        
        assert result.language == "java"
        # Enhanced Java parser detects add() and getResult() as methods
        # Constructor is not counted as a method (no return type)
        assert result.metrics.functions >= 2
        assert result.metrics.classes >= 1
    
    @pytest.mark.asyncio
    async def test_detect_issues(self):
        """Test issue detection."""
        analyzer = CodeAnalyzer()
        
        code = '''
def bad_function():
    eval("dangerous code")
    except:
        pass
'''
        
        result = await analyzer.analyze(code, "python")
        
        # Should detect security and best practice issues
        assert len(result.issues) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_metrics(self):
        """Test metrics calculation."""
        analyzer = CodeAnalyzer()
        
        code = '''
def function1():
    pass

def function2():
    pass

class MyClass:
    def method1(self):
        pass
'''
        
        result = await analyzer.analyze(code, "python")
        
        # Python AST counts all functions including class methods
        assert result.metrics.functions == 3
        assert result.metrics.classes == 1
        assert result.metrics.lines_of_code > 0


class TestRefactoringEngine:
    """Test cases for RefactoringEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test engine initialization."""
        engine = RefactoringEngine()
        assert engine.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_python_code(self):
        """Test Python code analysis for refactoring."""
        engine = RefactoringEngine()
        
        code = '''
def long_function():
    # This is a very long function
    # that should be refactored
    result = []
    for i in range(100):
        result.append(i * 2)
    return result
'''
        
        result = await engine.analyze(code, "python")
        
        assert result.success is True
        assert isinstance(result.operations, list)
    
    @pytest.mark.asyncio
    async def test_detect_refactoring_opportunities(self):
        """Test detection of refactoring opportunities."""
        engine = RefactoringEngine()
        
        code = '''
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
'''
        
        result = await engine.analyze(code, "python")
        
        # Should identify potential improvements
        assert result.success is True


class TestSecurityScanner:
    """Test cases for SecurityScanner."""
    
    @pytest.mark.asyncio
    async def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = SecurityScanner()
        assert scanner.config == {}
    
    @pytest.mark.asyncio
    async def test_scan_python_code(self):
        """Test Python code security scanning."""
        scanner = SecurityScanner()
        
        code = '''
import os
import pickle

def run_command(cmd):
    os.system(cmd)

def load_data(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

password = "admin123"
'''
        
        result = await scanner.scan(code, "python")
        
        assert len(result.vulnerabilities) > 0
        assert len(result.secrets) > 0
        assert result.risk_score > 0
    
    @pytest.mark.asyncio
    async def test_detect_sql_injection(self):
        """Test SQL injection detection."""
        scanner = SecurityScanner()
        
        code = '''
import sqlite3

def get_user(username):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()
'''
        
        result = await scanner.scan(code, "python")
        
        # Should detect SQL injection
        sql_vulns = [v for v in result.vulnerabilities if "sql" in v.type.value.lower()]
        assert len(sql_vulns) > 0
    
    @pytest.mark.asyncio
    async def test_detect_command_injection(self):
        """Test command injection detection."""
        scanner = SecurityScanner()
        
        code = '''
import subprocess

def run_command(cmd):
    subprocess.call(cmd, shell=True)
'''
        
        result = await scanner.scan(code, "python")
        
        # Should detect command injection
        cmd_vulns = [v for v in result.vulnerabilities if "command" in v.type.value.lower()]
        assert len(cmd_vulns) > 0
    
    @pytest.mark.asyncio
    async def test_detect_hardcoded_secrets(self):
        """Test hardcoded secret detection."""
        scanner = SecurityScanner()
        
        code = '''
password = "admin123"
api_key = "sk-1234567890"
secret = "my-secret-key"
'''
        
        result = await scanner.scan(code, "python")
        
        assert len(result.secrets) >= 3


class TestPerformanceAnalyzer:
    """Test cases for PerformanceAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = PerformanceAnalyzer()
        assert analyzer.config == {}
    
    @pytest.mark.asyncio
    async def test_analyze_python_code(self):
        """Test Python code performance analysis."""
        analyzer = PerformanceAnalyzer()
        
        code = '''
def calculate_sum(items):
    total = 0
    for item in items:
        total += item
    return total
'''
        
        result = await analyzer.analyze(code, "python")
        
        assert result.score > 0
        assert result.metrics is not None
    
    @pytest.mark.asyncio
    async def test_detect_nested_loops(self):
        """Test nested loop detection."""
        analyzer = PerformanceAnalyzer()
        
        code = '''
def find_pairs(matrix):
    result = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            for k in range(len(matrix)):
                result.append((i, j, k))
    return result
'''
        
        result = await analyzer.analyze(code, "python")
        
        # Should detect nested loop issues
        loop_issues = [i for i in result.issues if "loop" in i.title.lower() or "nest" in i.title.lower() or "嵌套" in i.title or "循环" in i.title]
        assert len(loop_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_string_concatenation(self):
        """Test string concatenation detection."""
        analyzer = PerformanceAnalyzer()
        
        code = '''
def build_string(items):
    result = ""
    for item in items:
        result += str(item)
    return result
'''
        
        result = await analyzer.analyze(code, "python")
        
        # Should detect string concatenation issue
        concat_issues = [i for i in result.issues if "string" in i.title.lower() or "concat" in i.title.lower() or "字符串" in i.title or "拼接" in i.title]
        assert len(concat_issues) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_complexity(self):
        """Test complexity calculation."""
        analyzer = PerformanceAnalyzer()
        
        code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                if i % 3 == 0:
                    print(i)
'''
        
        result = await analyzer.analyze(code, "python")
        
        assert result.metrics.cyclomatic_complexity > 1
        assert result.metrics.nesting_depth > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])