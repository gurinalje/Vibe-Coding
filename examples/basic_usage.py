"""
Basic Usage Example for AI Agent Benchmark system.

This example demonstrates basic usage of the multi-agent
code review and refactoring system.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.coordinator import AgentCoordinator
from benchmark.evaluator import BenchmarkEvaluator, TestCase


async def basic_review_example():
    """Basic code review example."""
    print("=" * 60)
    print("Basic Code Review Example")
    print("=" * 60)
    
    # Sample code to review
    sample_code = '''
def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def process_data(data):
    """Process input data."""
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(0)
    return result

# Global variable
GLOBAL_CONFIG = {"debug": True, "version": "1.0"}
'''
    
    # Create coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    try:
        # Review code
        print("\nReviewing code...")
        result = await coordinator.review_code(
            code=sample_code,
            language="python",
            file_path="example.py"
        )
        
        # Display results
        print(f"\nReview Score: {result.get('score', 0):.1f}/100")
        print(f"Issues Found: {len(result.get('issues', []))}")
        
        if result.get('issues'):
            print("\nIssues:")
            for issue in result['issues'][:5]:
                print(f"  - [{issue.get('severity', 'info')}] {issue.get('message', '')}")
        
        if result.get('recommendations'):
            print("\nRecommendations:")
            for rec in result['recommendations'][:3]:
                print(f"  - {rec}")
        
    finally:
        await coordinator.shutdown()


async def basic_refactoring_example():
    """Basic refactoring example."""
    print("\n" + "=" * 60)
    print("Basic Refactoring Example")
    print("=" * 60)
    
    # Sample code to refactor
    sample_code = '''
def build_string(items):
    """Build a string from items - inefficient method."""
    result = ""
    for item in items:
        result += str(item) + ", "
    return result.rstrip(", ")

def find_duplicates(items):
    """Find duplicate items - O(n^2) complexity."""
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
'''
    
    # Create coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    try:
        # Refactor code
        print("\nRefactoring code...")
        result = await coordinator.refactor_code(
            code=sample_code,
            language="python",
            file_path="example.py"
        )
        
        # Display results
        suggestions = result.get('suggestions', [])
        print(f"\nSuggestions: {len(suggestions)}")
        
        if suggestions:
            print("\nTop Suggestions:")
            for suggestion in suggestions[:3]:
                print(f"  - {suggestion.get('type', '')}: {suggestion.get('description', '')}")
        
        # Show refactored code if available
        refactored = result.get('refactored_code')
        if refactored and refactored != sample_code:
            print("\nRefactored Code:")
            print("-" * 40)
            print(refactored[:500])
            if len(refactored) > 500:
                print("... [truncated]")
        
    finally:
        await coordinator.shutdown()


async def basic_analysis_example():
    """Basic full analysis example."""
    print("\n" + "=" * 60)
    print("Basic Full Analysis Example")
    print("=" * 60)
    
    # Sample code with various issues
    sample_code = '''
import os
import pickle

# Hardcoded credentials
DATABASE_URL = "postgresql://admin:password@localhost/mydb"
API_KEY = "sk-1234567890"

def get_user(username):
    """Get user from database - has SQL injection."""
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return execute_query(query)

def load_data(file_path):
    """Load data - insecure deserialization."""
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def process_items(items):
    """Process items - nested loops."""
    result = []
    for i in range(len(items)):
        for j in range(len(items[i])):
            for k in range(len(items[i][j])):
                result.append(items[i][j][k] * 2)
    return result
'''
    
    # Create coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    try:
        # Perform full analysis
        print("\nPerforming full analysis...")
        result = await coordinator.full_analysis(
            code=sample_code,
            language="python",
            file_path="example.py"
        )
        
        # Display results
        print(f"\nOverall Score: {result.get('overall_score', 0):.1f}/100")
        print(f"\nSummary: {result.get('summary', '')}")
        
        # Show review results
        review = result.get('review_result', {})
        if review.get('status') == 'success':
            print(f"\nReview Issues: {len(review.get('issues', []))}")
        
        # Show criticism results
        criticism = result.get('criticism_result', {})
        if criticism.get('status') == 'success':
            print(f"Criticism Issues: {len(criticism.get('criticisms', []))}")
        
        # Show recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print("\nTop Recommendations:")
            for rec in recommendations[:5]:
                print(f"  - {rec}")
        
    finally:
        await coordinator.shutdown()


async def main():
    """Run all examples."""
    print("AI Agent Benchmark - Basic Usage Examples")
    print("=" * 60)
    
    await basic_review_example()
    await basic_refactoring_example()
    await basic_analysis_example()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())