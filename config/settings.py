"""
Configuration settings for AI Agent Benchmark system.

This module provides centralized configuration management with support for
environment variables, config files, and default values.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    retry_attempts: int = 3


@dataclass
class AgentConfig:
    """Agent configuration."""
    name: str
    enabled: bool = True
    max_concurrent_tasks: int = 5
    timeout: int = 300
    retry_attempts: int = 2
    llm_config: LLMConfig = field(default_factory=LLMConfig)


@dataclass
class CodeAnalysisConfig:
    """Code analysis configuration."""
    languages: List[str] = field(default_factory=lambda: ["python", "java", "javascript"])
    max_file_size_mb: int = 10
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.pyc", "__pycache__", ".git"])
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "complexity": 10.0,
        "duplication": 0.05,
        "maintainability": 20.0,
        "documentation_coverage": 0.7
    })


@dataclass
class SecurityConfig:
    """Security scanning configuration."""
    enabled: bool = True
    scan_types: List[str] = field(default_factory=lambda: ["vulnerabilities", "secrets", "dependencies"])
    severity_levels: List[str] = field(default_factory=lambda: ["low", "medium", "high", "critical"])
    custom_rules_path: Optional[str] = None


@dataclass
class BenchmarkConfig:
    """Benchmark evaluation configuration."""
    metrics_weights: Dict[str, float] = field(default_factory=lambda: {
        "accuracy": 0.4,
        "completeness": 0.3,
        "efficiency": 0.2,
        "security": 0.1
    })
    test_cases_path: str = "benchmark/test_cases"
    results_path: str = "benchmark/results"
    parallel_execution: bool = True
    max_parallel_workers: int = 4


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    token_tracking: bool = True
    cost_per_1k_tokens: Dict[str, float] = field(default_factory=lambda: {
        "gpt-4": 0.03,
        "gpt-3.5-turbo": 0.002,
        "claude-3-opus": 0.015,
        "claude-3-sonnet": 0.003
    })
    performance_metrics: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "token_usage_warning": 100000,
        "token_usage_critical": 500000,
        "response_time_warning": 5.0,
        "response_time_critical": 10.0
    })


@dataclass
class Settings:
    """Main settings class."""
    # General
    project_name: str = "AI Agent Benchmark"
    version: str = "0.1.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = "app.log"
    
    # Components
    llm_config: LLMConfig = field(default_factory=LLMConfig)
    agents: List[AgentConfig] = field(default_factory=lambda: [
        AgentConfig(name="reviewer"),
        AgentConfig(name="developer"),
        AgentConfig(name="critic")
    ])
    code_analysis: CodeAnalysisConfig = field(default_factory=CodeAnalysisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    def __post_init__(self):
        """Post initialization processing."""
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        self._load_from_env()
        
        # Load config file if exists
        self._load_from_file()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # LLM configuration
        if os.getenv("LLM_PROVIDER"):
            self.llm_config.provider = os.getenv("LLM_PROVIDER", self.llm_config.provider)
        if os.getenv("LLM_MODEL"):
            self.llm_config.model = os.getenv("LLM_MODEL", self.llm_config.model)
        if os.getenv("LLM_API_KEY"):
            self.llm_config.api_key = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_TEMPERATURE"):
            try:
                self.llm_config.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
            except (ValueError, TypeError):
                pass
        if os.getenv("LLM_MAX_TOKENS"):
            try:
                self.llm_config.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
            except (ValueError, TypeError):
                pass
        
        # General settings
        if os.getenv("ENVIRONMENT"):
            try:
                self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
            except ValueError:
                pass
        if os.getenv("DEBUG"):
            debug_str = os.getenv("DEBUG", "false")
            if debug_str:
                self.debug = debug_str.lower() in ("true", "1", "yes")
        if os.getenv("LOG_LEVEL"):
            try:
                self.log_level = LogLevel(os.getenv("LOG_LEVEL", "INFO"))
            except ValueError:
                pass
    
    def _load_from_file(self):
        """Load configuration from file."""
        config_file = self.base_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)
                self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Also check for YAML config
        yaml_config = self.base_dir / "config.yaml"
        if yaml_config.exists():
            try:
                with open(yaml_config, "r") as f:
                    config_data = yaml.safe_load(f)
                self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Could not load YAML config file: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update settings from dictionary."""
        for key, value in config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "project_name": self.project_name,
            "version": self.version,
            "environment": self.environment.value,
            "debug": self.debug,
            "log_level": self.log_level.value,
            "llm_config": {
                "provider": self.llm_config.provider,
                "model": self.llm_config.model,
                "temperature": self.llm_config.temperature,
                "max_tokens": self.llm_config.max_tokens,
                "timeout": self.llm_config.timeout,
                "retry_attempts": self.llm_config.retry_attempts
            },
            "agents": [
                {
                    "name": agent.name,
                    "enabled": agent.enabled,
                    "max_concurrent_tasks": agent.max_concurrent_tasks,
                    "timeout": agent.timeout,
                    "retry_attempts": agent.retry_attempts
                }
                for agent in self.agents
            ],
            "code_analysis": {
                "languages": self.code_analysis.languages,
                "max_file_size_mb": self.code_analysis.max_file_size_mb,
                "quality_thresholds": self.code_analysis.quality_thresholds
            },
            "security": {
                "enabled": self.security.enabled,
                "scan_types": self.security.scan_types,
                "severity_levels": self.security.severity_levels
            },
            "benchmark": {
                "metrics_weights": self.benchmark.metrics_weights,
                "parallel_execution": self.benchmark.parallel_execution,
                "max_parallel_workers": self.benchmark.max_parallel_workers
            },
            "monitoring": {
                "token_tracking": self.monitoring.token_tracking,
                "performance_metrics": self.monitoring.performance_metrics,
                "alert_thresholds": self.monitoring.alert_thresholds
            }
        }
    
    def save(self, file_path: Optional[Path] = None):
        """Save settings to file."""
        if file_path is None:
            file_path = self.base_dir / "config.json"
        
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_settings(config_file: Union[str, Path]) -> Settings:
    """Load settings from specific config file."""
    global _settings
    
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    if config_path.suffix == ".json":
        with open(config_path, "r") as f:
            config_data = json.load(f)
    elif config_path.suffix in [".yaml", ".yml"]:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    _settings = Settings()
    _settings._update_from_dict(config_data)
    return _settings