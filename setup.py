from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ai-agent-benchmark",
    version="0.1.0",
    author="AI Agent Benchmark Team",
    author_email="team@ai-agent-benchmark.com",
    description="Multi-Agent Collaborative Code Review and Refactoring System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-agent-benchmark/ai-agent-benchmark",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=0.24.0",
        "astunparse>=1.6.3",
        "tree-sitter>=0.18.0",
        "astor>=0.8.1",
        "openai>=0.27.0",
        "anthropic>=0.25.0",
        "transformers>=4.20.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "gitpython>=3.1.0",
        "rich>=12.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
            "bandit>=1.7.0",
            "safety>=2.2.0",
            "memory-profiler>=0.60.0",
            "line-profiler>=4.0.0",
        ],
        "monitoring": [
            "psutil>=5.8.0",
            "prometheus-client>=0.14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-benchmark=ai_agent_benchmark.cli:main",
        ],
    },
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
    data_files=[
        ("config", ["config/settings.py", "config/logging_config.py"]),
    ],
)