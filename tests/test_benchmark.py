"""
Benchmark Tests for AI Agent Benchmark system.

This module contains test cases for the benchmark components
including evaluator, metrics, and test cases.
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from benchmark.evaluator import BenchmarkEvaluator, TestCase
from benchmark.metrics import MetricsCalculator
from benchmark.test_cases.python_tests import PythonTestCases
from benchmark.test_cases.java_tests import JavaTestCases
from agents.coordinator import AgentCoordinator


class TestMetricsCalculator:
    """Test cases for MetricsCalculator."""
    
    def test_calculator_initialization(self):
        """Test calculator initialization."""
        calculator = MetricsCalculator()
        assert calculator.config == {}
    
    def test_calculate_precision(self):
        """Test precision calculation."""
        calculator = MetricsCalculator()
        
        result = calculator.calculate_precision(
            true_positives=8,
            false_positives=2
        )
        
        assert result.name == "precision"
        assert result.value == 0.8
        assert result.passed is True
    
    def test_calculate_recall(self):
        """Test recall calculation."""
        calculator = MetricsCalculator()
        
        result = calculator.calculate_recall(
            true_positives=8,
            false_negatives=2
        )
        
        assert result.name == "recall"
        assert result.value == 0.8
        assert result.passed is True
    
    def test_calculate_f1_score(self):
        """Test F1 score calculation."""
        calculator = MetricsCalculator()
        
        result = calculator.calculate_f1_score(
            precision=0.8,
            recall=0.8
        )
        
        assert result.name == "f1_score"
        assert result.value == 0.8
        assert result.passed is True
    
    def test_calculate_accuracy(self):
        """Test accuracy calculation."""
        calculator = MetricsCalculator()
        
        result = calculator.calculate_accuracy(
            correct_predictions=85,
            total_predictions=100
        )
        
        assert result.name == "accuracy"
        assert result.value == 85.0
        assert result.passed is True
    
    def test_calculate_code_quality_score(self):
        """Test code quality score calculation."""
        calculator = MetricsCalculator()
        
        result = calculator.calculate_code_quality_score(
            issues_found=5,
            total_lines=100
        )
        
        assert result.name == "code_quality_score"
        assert result.value > 0
    
    def test_calculate_response_time(self):
        """Test response time calculation."""
        calculator = MetricsCalculator()
        
        result = calculator.calculate_response_time(
            execution_time=2.5,
            timeout=5.0
        )
        
        assert result.name == "response_time"
        assert result.value == 2.5
        assert result.passed is True
    
    def test_calculate_weighted_score(self):
        """Test weighted score calculation."""
        calculator = MetricsCalculator()
        
        metrics = {
            "precision": 0.8,
            "recall": 0.7,
            "f1_score": 0.75,
            "accuracy": 85.0,
        }
        
        result = calculator.calculate_weighted_score(metrics)
        
        assert result.name == "weighted_score"
        assert result.value > 0
    
    def test_generate_metrics_summary(self):
        """Test metrics summary generation."""
        calculator = MetricsCalculator()
        
        metrics = [
            calculator.calculate_precision(8, 2),
            calculator.calculate_recall(8, 2),
            calculator.calculate_f1_score(0.8, 0.8),
        ]
        
        summary = calculator.generate_metrics_summary(metrics)
        
        assert summary["total_metrics"] == 3
        assert summary["passed"] == 3
        assert summary["pass_rate"] == 100.0


class TestPythonTestCases:
    """Test cases for PythonTestCases."""
    
    def test_get_all_cases(self):
        """Test getting all cases."""
        cases = PythonTestCases.get_all_cases()
        assert len(cases) > 0
    
    def test_get_basic_cases(self):
        """Test getting basic cases."""
        cases = PythonTestCases.get_basic_cases()
        assert len(cases) > 0
        
        for case in cases:
            assert case.language == "python"
            assert case.id.startswith("py_")
    
    def test_get_security_cases(self):
        """Test getting security cases."""
        cases = PythonTestCases.get_security_cases()
        assert len(cases) > 0
        
        for case in cases:
            assert "security" in case.tags
    
    def test_get_performance_cases(self):
        """Test getting performance cases."""
        cases = PythonTestCases.get_performance_cases()
        assert len(cases) > 0
        
        for case in cases:
            assert "performance" in case.tags
    
    def test_get_style_cases(self):
        """Test getting style cases."""
        cases = PythonTestCases.get_style_cases()
        assert len(cases) > 0
        
        for case in cases:
            assert "style" in case.tags


class TestJavaTestCases:
    """Test cases for JavaTestCases."""
    
    def test_get_all_cases(self):
        """Test getting all cases."""
        cases = JavaTestCases.get_all_cases()
        assert len(cases) > 0
    
    def test_get_basic_cases(self):
        """Test getting basic cases."""
        cases = JavaTestCases.get_basic_cases()
        assert len(cases) > 0
        
        for case in cases:
            assert case.language == "java"
            assert case.id.startswith("java_")
    
    def test_get_security_cases(self):
        """Test getting security cases."""
        cases = JavaTestCases.get_security_cases()
        assert len(cases) > 0
        
        for case in cases:
            assert "security" in case.tags


class TestBenchmarkEvaluator:
    """Test cases for BenchmarkEvaluator."""
    
    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        evaluator = BenchmarkEvaluator()
        assert evaluator.config == {}
        assert evaluator.test_cases == []
    
    def test_add_test_case(self):
        """Test adding test case."""
        evaluator = BenchmarkEvaluator()
        
        test_case = TestCase(
            id="test_001",
            name="Test Case",
            description="A test case",
            language="python",
            code="pass",
            expected_issues=[],
        )
        
        evaluator.add_test_case(test_case)
        assert len(evaluator.test_cases) == 1
    
    @pytest.mark.asyncio
    async def test_evaluate(self):
        """Test evaluation."""
        evaluator = BenchmarkEvaluator()
        
        # Add test case
        test_case = TestCase(
            id="test_001",
            name="Simple Test",
            description="A simple test",
            language="python",
            code="def add(a, b): return a + b",
            expected_issues=[],
        )
        evaluator.add_test_case(test_case)
        
        # Create coordinator
        coordinator = AgentCoordinator()
        
        # Run evaluation
        report = await evaluator.evaluate(
            agent=coordinator,
            benchmark_name="test_benchmark"
        )
        
        assert report.benchmark_name == "test_benchmark"
        assert report.total_test_cases == 1
        assert report.completed_cases >= 0
        assert report.results is not None


class TestTestCase:
    """Test cases for TestCase."""
    
    def test_test_case_creation(self):
        """Test test case creation."""
        test_case = TestCase(
            id="test_001",
            name="Test Case",
            description="A test case",
            language="python",
            code="pass",
            expected_issues=[],
        )
        
        assert test_case.id == "test_001"
        assert test_case.language == "python"
    
    def test_test_case_to_dict(self):
        """Test test case serialization."""
        test_case = TestCase(
            id="test_001",
            name="Test Case",
            description="A test case",
            language="python",
            code="pass",
            expected_issues=[],
        )
        
        data = test_case.to_dict()
        
        assert data["id"] == "test_001"
        assert data["language"] == "python"
        assert "code" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])