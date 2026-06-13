"""
Advanced Usage Example for AI Agent Benchmark system.

This example demonstrates advanced usage including benchmarking,
custom configurations, and integration patterns.
"""

import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.coordinator import AgentCoordinator
from agents.reviewer_agent import ReviewerAgent
from agents.developer_agent import DeveloperAgent
from agents.critic_agent import CriticAgent
from benchmark.evaluator import BenchmarkEvaluator, TestCase
from benchmark.test_cases.python_tests import PythonTestCases
from benchmark.test_cases.java_tests import JavaTestCases
from monitoring.token_monitor import TokenMonitor
from monitoring.performance_monitor import PerformanceMonitor
from core.code_analyzer import CodeAnalyzer
from core.security_scanner import SecurityScanner


async def benchmark_example():
    """Benchmark evaluation example."""
    print("=" * 60)
    print("Benchmark Evaluation Example")
    print("=" * 60)
    
    # Get test cases
    python_cases = PythonTestCases.get_basic_cases()[:2]  # Use first 2 for demo
    
    # Create coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    # Create evaluator
    evaluator = BenchmarkEvaluator()
    
    try:
        # Run benchmark
        print("\nRunning benchmark with 2 test cases...")
        report = await evaluator.evaluate(
            agent=coordinator,
            test_cases=python_cases,
            benchmark_name="demo_benchmark"
        )
        
        # Display results
        print(f"\nBenchmark: {report.benchmark_name}")
        print(f"Completed: {report.completed_cases}/{report.total_test_cases} cases")
        print(f"Execution Time: {report.execution_time:.2f}s")
        
        # Display metrics
        metrics = report.overall_metrics
        print(f"\nMetrics:")
        print(f"  Average F1 Score: {metrics.get('average_f1_score', 0):.3f}")
        print(f"  Accuracy: {metrics.get('accuracy', 0):.1f}%")
        
        # Display summary
        print(f"\nSummary: {report.summary}")
        
        # Save results
        output_file = evaluator.save_results(report, "benchmark/results")
        print(f"\nResults saved to: {output_file}")
        
    finally:
        await coordinator.shutdown()


async def custom_agent_example():
    """Custom agent configuration example."""
    print("\n" + "=" * 60)
    print("Custom Agent Configuration Example")
    print("=" * 60)
    
    # Custom configuration
    custom_config = {
        "reviewer": {
            "max_concurrent_tasks": 3,
            "timeout": 120,
        },
        "developer": {
            "max_concurrent_tasks": 2,
            "timeout": 180,
        },
        "critic": {
            "max_concurrent_tasks": 4,
            "timeout": 90,
        }
    }
    
    # Create coordinator with custom config
    coordinator = AgentCoordinator(config=custom_config)
    await coordinator.initialize()
    
    # Sample code
    sample_code = '''
def vulnerable_function(user_input):
    """Function with security issues."""
    # SQL injection
    query = f"SELECT * FROM users WHERE id = {user_input}"
    
    # Command injection
    import os
    os.system(f"echo {user_input}")
    
    # Hardcoded secret
    password = "admin123"
    
    return execute_query(query)
'''
    
    try:
        # Review with custom configuration
        print("\nReviewing with custom configuration...")
        result = await coordinator.review_code(
            code=sample_code,
            language="python"
        )
        
        print(f"Score: {result.get('score', 0):.1f}")
        print(f"Issues: {len(result.get('issues', []))}")
        
    finally:
        await coordinator.shutdown()


async def monitoring_example():
    """Monitoring and metrics example."""
    print("\n" + "=" * 60)
    print("Monitoring and Metrics Example")
    print("=" * 60)
    
    # Initialize monitors
    token_monitor = TokenMonitor()
    perf_monitor = PerformanceMonitor()
    
    # Create coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    # Sample code
    sample_code = '''
def calculatefibonacci(n):
    """Calculate Fibonacci number - has performance issues."""
    if n <= 1:
        return n
    return calculatefibonacci(n-1) + calculatefibonacci(n-2)

def process_large_list(items):
    """Process large list - memory intensive."""
    result = []
    for item in items:
        # String concatenation in loop
        temp = ""
        for char in str(item):
            temp += char
        result.append(temp)
    return result
'''
    
    try:
        # Track token usage
        print("\nTracking token usage...")
        token_monitor.record_usage(
            request_id="demo_request_1",
            model="gpt-4",
            prompt_tokens=500,
            completion_tokens=200,
            agent_name="reviewer",
            task_type="review"
        )
        
        # Track performance
        print("Tracking performance...")
        with perf_monitor.track("code_review", agent_name="reviewer"):
            result = await coordinator.review_code(
                code=sample_code,
                language="python"
            )
        
        # Display monitoring results
        token_stats = token_monitor.get_statistics()
        if token_stats:
            print(f"\nToken Usage:")
            print(f"  Total Requests: {token_stats.get('total_requests', 0)}")
            print(f"  Total Tokens: {token_stats.get('total_tokens', 0)}")
            print(f"  Total Cost: ${token_stats.get('total_cost', 0):.4f}")
        
        perf_stats = perf_monitor.get_statistics()
        if perf_stats:
            print(f"\nPerformance:")
            print(f"  Total Operations: {perf_stats.get('total_operations', 0)}")
            print(f"  Average Time: {perf_stats.get('average_execution_time', 0):.4f}s")
        
    finally:
        await coordinator.shutdown()


async def security_scanning_example():
    """Security scanning example."""
    print("\n" + "=" * 60)
    print("Security Scanning Example")
    print("=" * 60)
    
    # Create security scanner
    scanner = SecurityScanner()
    
    # Sample code with security issues
    sample_code = '''
import pickle
import subprocess
import sqlite3

# Hardcoded credentials
DB_PASSWORD = "admin123"
API_SECRET = "secret-key-12345"

def get_user(user_id):
    """SQL injection vulnerability."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()

def execute_command(cmd):
    """Command injection vulnerability."""
    subprocess.call(cmd, shell=True)

def load_data(data):
    """Insecure deserialization."""
    return pickle.loads(data)

def weak_crypto():
    """Weak cryptography."""
    import hashlib
    return hashlib.md5(b"password").hexdigest()
'''
    
    try:
        # Scan code
        print("\nScanning for security issues...")
        result = await scanner.scan(
            code=sample_code,
            language="python",
            file_path="vulnerable.py"
        )
        
        # Display results
        print(f"\nRisk Score: {result.risk_score:.1f}/100")
        print(f"Vulnerabilities: {len(result.vulnerabilities)}")
        print(f"Secrets Found: {len(result.secrets)}")
        
        if result.vulnerabilities:
            print("\nTop Vulnerabilities:")
            for vuln in result.vulnerabilities[:5]:
                print(f"  - [{vuln.severity.value}] {vuln.title}")
        
        if result.secrets:
            print("\nHardcoded Secrets:")
            for secret in result.secrets[:3]:
                line_content = secret.line_content[:50] if secret.line_content else "N/A"
                print(f"  - {secret.type}: {line_content}...")
        
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations[:3]:
                print(f"  - {rec}")
        
    finally:
        pass


async def multi_language_example():
    """Multi-language analysis example."""
    print("\n" + "=" * 60)
    print("Multi-Language Analysis Example")
    print("=" * 60)
    
    # Create analyzer
    analyzer = CodeAnalyzer()
    
    # Python code
    python_code = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

class Calculator:
    """Simple calculator class."""
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self
'''
    
    # Java code
    java_code = '''
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
    
    try:
        # Analyze Python code
        print("\nAnalyzing Python code...")
        python_result = await analyzer.analyze(python_code, "python")
        print(f"Python - Lines: {python_result.metrics.lines_of_code}, "
              f"Functions: {python_result.metrics.functions}, "
              f"Score: {python_result.quality_score:.1f}")
        
        # Analyze Java code
        print("\nAnalyzing Java code...")
        java_result = await analyzer.analyze(java_code, "java")
        print(f"Java - Lines: {java_result.metrics.lines_of_code}, "
              f"Functions: {java_result.metrics.functions}, "
              f"Score: {java_result.quality_score:.1f}")
        
    finally:
        pass


async def main():
    """Run all advanced examples."""
    print("AI Agent Benchmark - Advanced Usage Examples")
    print("=" * 60)
    
    await benchmark_example()
    await custom_agent_example()
    await monitoring_example()
    await security_scanning_example()
    await multi_language_example()
    
    print("\n" + "=" * 60)
    print("All advanced examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())