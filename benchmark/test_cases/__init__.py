"""
Test Cases module for AI Agent Benchmark system.

This module provides test cases for benchmarking code review capabilities.
"""

from .python_tests import PythonTestCases
from .java_tests import JavaTestCases

__all__ = [
    "PythonTestCases",
    "JavaTestCases",
]