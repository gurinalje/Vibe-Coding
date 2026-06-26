"""
Metrics Calculator for AI Agent Benchmark system.

This module provides metrics calculation for evaluating
code review quality, agent performance, refactoring effectiveness,
and token efficiency.

功能：
- 计算代码质量指标
- 计算 Agent 性能指标
- 计算重构效果指标
- 计算 Token 效能指标
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """单个指标结果。
    
    属性：
        name: 指标名称
        value: 指标值
        description: 指标描述
        threshold: 阈值
        passed: 是否通过
        unit: 单位
    """
    name: str
    value: float
    description: str
    threshold: Optional[float] = None
    passed: Optional[bool] = None
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "name": self.name,
            "value": self.value,
            "description": self.description,
            "threshold": self.threshold,
            "passed": self.passed,
            "unit": self.unit,
        }


class MetricsCalculator:
    """指标计算器。
    
    提供各种指标的计算方法，包括：
    - 基础分类指标（精确率、召回率、F1等）
    - 代码质量指标
    - Agent 性能指标
    - 重构效果指标
    - Token 效能指标
    
    使用示例：
        ```python
        calculator = MetricsCalculator()
        precision = calculator.calculate_precision(tp=8, fp=2)
        token_efficiency = calculator.calculate_token_efficiency(
            tokens_used=1000, issues_found=5
        )
        ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化指标计算器。
        
        Args:
            config: 配置字典，可包含：
                - thresholds: 指标阈值字典
                - cost_rates: Token 成本费率
        """
        self.config = config or {}
        self.thresholds = self._load_thresholds()
        self.cost_rates = self._load_cost_rates()
        
        logger.info("指标计算器已初始化")
    
    def _load_thresholds(self) -> Dict[str, float]:
        """加载指标阈值。"""
        default_thresholds = {
            "precision": 0.7,
            "recall": 0.7,
            "f1_score": 0.7,
            "accuracy": 80.0,
            "response_time": 5.0,
            "code_quality_score": 70.0,
            "refactoring_improvement": 10.0,
            "token_efficiency": 0.1,
        }
        
        # 合并用户配置的阈值
        user_thresholds = self.config.get("thresholds", {})
        default_thresholds.update(user_thresholds)
        
        return default_thresholds
    
    def _load_cost_rates(self) -> Dict[str, Dict[str, float]]:
        """加载 Token 成本费率（每1K token）。"""
        default_rates = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        }
        
        user_rates = self.config.get("cost_rates", {})
        default_rates.update(user_rates)
        
        return default_rates
    
    # ==================== 基础分类指标 ====================
    
    def calculate_precision(
        self,
        true_positives: int,
        false_positives: int
    ) -> MetricResult:
        """
        计算精确率。
        
        精确率 = TP / (TP + FP)
        
        Args:
            true_positives: 真阳性数量（正确识别的问题）
            false_positives: 假阳性数量（错误识别的问题）
            
        Returns:
            精确率指标结果
        """
        precision = true_positives / max(1, true_positives + false_positives)
        threshold = self.thresholds.get("precision", 0.7)
        
        return MetricResult(
            name="precision",
            value=precision,
            description="精确率：正确识别的问题占所有识别问题的比例",
            threshold=threshold,
            passed=precision >= threshold,
        )
    
    def calculate_recall(
        self,
        true_positives: int,
        false_negatives: int
    ) -> MetricResult:
        """
        计算召回率。
        
        召回率 = TP / (TP + FN)
        
        Args:
            true_positives: 真阳性数量
            false_negatives: 假阴性数量（漏检的问题）
            
        Returns:
            召回率指标结果
        """
        recall = true_positives / max(1, true_positives + false_negatives)
        threshold = self.thresholds.get("recall", 0.7)
        
        return MetricResult(
            name="recall",
            value=recall,
            description="召回率：正确识别的问题占所有实际问题的比例",
            threshold=threshold,
            passed=recall >= threshold,
        )
    
    def calculate_f1_score(
        self,
        precision: float,
        recall: float
    ) -> MetricResult:
        """
        计算 F1 分数。
        
        F1 = 2 * (Precision * Recall) / (Precision + Recall)
        
        Args:
            precision: 精确率
            recall: 召回率
            
        Returns:
            F1 分数指标结果
        """
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = round(2 * precision * recall / (precision + recall), 10)
        
        threshold = self.thresholds.get("f1_score", 0.7)
        
        return MetricResult(
            name="f1_score",
            value=f1,
            description="F1 分数：精确率和召回率的调和平均",
            threshold=threshold,
            passed=f1 >= threshold,
        )
    
    def calculate_accuracy(
        self,
        correct_predictions: int,
        total_predictions: int
    ) -> MetricResult:
        """
        计算准确率。
        
        准确率 = (TP + TN) / 总数
        
        Args:
            correct_predictions: 正确预测数量
            total_predictions: 总预测数量
            
        Returns:
            准确率指标结果
        """
        accuracy = (correct_predictions / max(1, total_predictions)) * 100
        threshold = self.thresholds.get("accuracy", 80.0)
        
        return MetricResult(
            name="accuracy",
            value=accuracy,
            description="准确率：正确预测占所有预测的百分比",
            threshold=threshold,
            passed=accuracy >= threshold,
            unit="%",
        )
    
    # ==================== 代码质量指标 ====================
    
    def calculate_code_quality_score(
        self,
        issues_found: int,
        total_lines: int,
        issue_weight: float = 1.0
    ) -> MetricResult:
        """
        计算代码质量评分。
        
        评分基于问题密度计算，问题越少质量越高。
        
        Args:
            issues_found: 发现的问题数量
            total_lines: 代码总行数
            issue_weight: 每个问题的权重
            
        Returns:
            质量评分指标结果
        """
        if total_lines == 0:
            score = 100.0
        else:
            issue_density = (issues_found * issue_weight) / total_lines
            score = max(0, 100 - issue_density * 1000)
        
        threshold = self.thresholds.get("code_quality_score", 70.0)
        
        return MetricResult(
            name="code_quality_score",
            value=score,
            description="代码质量评分（0-100）",
            threshold=threshold,
            passed=score >= threshold,
            unit="分",
        )
    
    def calculate_code_complexity(
        self,
        cyclomatic_complexity: int,
        cognitive_complexity: int
    ) -> MetricResult:
        """
        计算代码复杂度评分。
        
        综合考虑圈复杂度和认知复杂度。
        
        Args:
            cyclomatic_complexity: 圈复杂度
            cognitive_complexity: 认知复杂度
            
        Returns:
            复杂度评分指标结果
        """
        # 理想复杂度：圈复杂度 < 10，认知复杂度 < 15
        cc_score = max(0, 100 - (cyclomatic_complexity - 5) * 10)
        cog_score = max(0, 100 - (cognitive_complexity - 10) * 7)
        
        # 综合评分（各占50%）
        score = (cc_score + cog_score) / 2
        
        return MetricResult(
            name="code_complexity",
            value=score,
            description="代码复杂度评分（越高越简单）",
            threshold=70.0,
            passed=score >= 70.0,
            unit="分",
        )
    
    def calculate_issue_density(
        self,
        issues_found: int,
        total_lines: int
    ) -> MetricResult:
        """
        计算问题密度。
        
        问题密度 = 问题数 / 100行代码
        
        Args:
            issues_found: 问题数量
            total_lines: 代码行数
            
        Returns:
            问题密度指标结果
        """
        if total_lines == 0:
            density = 0.0
        else:
            density = (issues_found / total_lines) * 100
        
        # 低密度为好，阈值为每100行不超过2个问题
        threshold = 2.0
        
        return MetricResult(
            name="issue_density",
            value=density,
            description="问题密度（每100行代码的问题数）",
            threshold=threshold,
            passed=density <= threshold,
            unit="问题/100行",
        )
    
    def calculate_severity_distribution(
        self,
        severity_counts: Dict[str, int]
    ) -> MetricResult:
        """
        计算严重程度分布评分。
        
        基于问题严重程度的加权评分。
        
        Args:
            severity_counts: 各严重程度的问题数量 {"critical": 2, "major": 5, "minor": 10}
            
        Returns:
            分布评分指标结果
        """
        weights = {
            "critical": 4.0,
            "major": 2.0,
            "minor": 1.0,
            "info": 0.5,
        }
        
        total_issues = sum(severity_counts.values())
        if total_issues == 0:
            return MetricResult(
                name="severity_distribution",
                value=100.0,
                description="严重程度分布评分",
                threshold=70.0,
                passed=True,
                unit="分",
            )
        
        # 计算加权分数
        weighted_sum = sum(
            count * weights.get(severity, 1.0)
            for severity, count in severity_counts.items()
        )
        
        # 归一化到0-100（权重越低越好）
        max_possible = total_issues * max(weights.values())
        score = max(0, 100 - (weighted_sum / max_possible) * 100)
        
        return MetricResult(
            name="severity_distribution",
            value=score,
            description="严重程度分布评分（问题越轻微分数越高）",
            threshold=70.0,
            passed=score >= 70.0,
            unit="分",
        )
    
    # ==================== Agent 性能指标 ====================
    
    def calculate_response_time(
        self,
        execution_time: float,
        timeout: float = 5.0
    ) -> MetricResult:
        """
        计算响应时间指标。
        
        Args:
            execution_time: 执行时间（秒）
            timeout: 超时阈值（秒）
            
        Returns:
            响应时间指标结果
        """
        threshold = self.thresholds.get("response_time", timeout)
        
        return MetricResult(
            name="response_time",
            value=execution_time,
            description="响应时间（秒）",
            threshold=threshold,
            passed=execution_time <= threshold,
            unit="秒",
        )
    
    def calculate_throughput(
        self,
        tasks_completed: int,
        time_period: float
    ) -> MetricResult:
        """
        计算吞吐量。
        
        吞吐量 = 任务数 / 时间（任务/秒）
        
        Args:
            tasks_completed: 完成的任务数
            time_period: 时间周期（秒）
            
        Returns:
            吞吐量指标结果
        """
        throughput = tasks_completed / max(0.001, time_period)
        
        # 期望每秒至少处理0.5个任务
        threshold = 0.5
        
        return MetricResult(
            name="throughput",
            value=throughput,
            description="吞吐量（任务/秒）",
            threshold=threshold,
            passed=throughput >= threshold,
            unit="任务/秒",
        )
    
    def calculate_success_rate(
        self,
        successful: int,
        total: int
    ) -> MetricResult:
        """
        计算成功率。
        
        成功率 = 成功数 / 总数 * 100
        
        Args:
            successful: 成功数量
            total: 总数量
            
        Returns:
            成功率指标结果
        """
        rate = (successful / max(1, total)) * 100
        
        threshold = 90.0
        
        return MetricResult(
            name="success_rate",
            value=rate,
            description="成功率",
            threshold=threshold,
            passed=rate >= threshold,
            unit="%",
        )
    
    def calculate_error_rate(
        self,
        errors: int,
        total: int
    ) -> MetricResult:
        """
        计算错误率。
        
        错误率 = 错误数 / 总数 * 100
        
        Args:
            errors: 错误数量
            total: 总数量
            
        Returns:
            错误率指标结果
        """
        rate = (errors / max(1, total)) * 100
        
        # 错误率应低于10%
        threshold = 10.0
        
        return MetricResult(
            name="error_rate",
            value=rate,
            description="错误率",
            threshold=threshold,
            passed=rate <= threshold,
            unit="%",
        )
    
    # ==================== 重构效果指标 ====================
    
    def calculate_refactoring_improvement(
        self,
        before_score: float,
        after_score: float
    ) -> MetricResult:
        """
        计算重构改进度。
        
        改进度 = (after - before) / before * 100
        
        Args:
            before_score: 重构前评分
            after_score: 重构后评分
            
        Returns:
            重构改进度指标结果
        """
        if before_score == 0:
            improvement = 0.0
        else:
            improvement = ((after_score - before_score) / before_score) * 100
        
        threshold = self.thresholds.get("refactoring_improvement", 10.0)
        
        return MetricResult(
            name="refactoring_improvement",
            value=improvement,
            description="重构改进度（百分比）",
            threshold=threshold,
            passed=improvement >= threshold,
            unit="%",
        )
    
    def calculate_code_simplification(
        self,
        before_complexity: float,
        after_complexity: float
    ) -> MetricResult:
        """
        计算代码简化度。
        
        简化度 = (before - after) / before * 100
        
        Args:
            before_complexity: 重构前复杂度
            after_complexity: 重构后复杂度
            
        Returns:
            代码简化度指标结果
        """
        if before_complexity == 0:
            simplification = 0.0
        else:
            simplification = ((before_complexity - after_complexity) / before_complexity) * 100
        
        threshold = 10.0
        
        return MetricResult(
            name="code_simplification",
            value=simplification,
            description="代码简化度（复杂度降低百分比）",
            threshold=threshold,
            passed=simplification >= threshold,
            unit="%",
        )
    
    def calculate_maintainability_improvement(
        self,
        before_maintainability: float,
        after_maintainability: float
    ) -> MetricResult:
        """
        计算可维护性改进度。
        
        Args:
            before_maintainability: 重构前可维护性评分
            after_maintainability: 重构后可维护性评分
            
        Returns:
            可维护性改进度指标结果
        """
        if before_maintainability == 0:
            improvement = 0.0
        else:
            improvement = ((after_maintainability - before_maintainability) / before_maintainability) * 100
        
        threshold = 15.0
        
        return MetricResult(
            name="maintainability_improvement",
            value=improvement,
            description="可维护性改进度",
            threshold=threshold,
            passed=improvement >= threshold,
            unit="%",
        )
    
    def calculate_test_coverage_impact(
        self,
        before_coverage: float,
        after_coverage: float,
        test_lines_added: int
    ) -> MetricResult:
        """
        计算测试覆盖率影响。
        
        评估重构对测试覆盖率的影响。
        
        Args:
            before_coverage: 重构前覆盖率
            after_coverage: 重构后覆盖率
            test_lines_added: 新增测试代码行数
            
        Returns:
            测试覆盖率影响指标结果
        """
        coverage_change = after_coverage - before_coverage
        
        # 覆盖率应该提高或保持，且新增测试代码应该有效
        if coverage_change >= 0 and test_lines_added > 0:
            score = coverage_change * 10 + min(100, test_lines_added / 10)
        elif coverage_change >= 0:
            score = coverage_change * 10
        else:
            score = coverage_change * 20  # 覆盖率下降是严重问题
        
        return MetricResult(
            name="test_coverage_impact",
            value=score,
            description="测试覆盖率影响评分",
            threshold=0.0,
            passed=coverage_change >= 0,
            unit="分",
        )
    
    # ==================== Token 效能指标 ====================
    
    def calculate_token_efficiency(
        self,
        tokens_used: int,
        issues_found: int,
        task_complexity: float = 1.0
    ) -> MetricResult:
        """
        计算 Token 效能。
        
        Token 效能 = 有效产出 / Token 消耗
        
        Args:
            tokens_used: Token 使用量
            issues_found: 发现的问题数量
            task_complexity: 任务复杂度系数
            
        Returns:
            Token 效能指标结果
        """
        if tokens_used == 0:
            efficiency = 0.0
        else:
            # 每发现一个问题消耗的Token数（越少越好）
            tokens_per_issue = tokens_used / max(1, issues_found)
            # 归一化效率（理想情况：每问题100 token = 1.0效率）
            efficiency = 100.0 / max(1, tokens_per_issue) * task_complexity
        
        threshold = self.thresholds.get("token_efficiency", 0.1)
        
        return MetricResult(
            name="token_efficiency",
            value=efficiency,
            description="Token 效能（有效产出/Token消耗）",
            threshold=threshold,
            passed=efficiency >= threshold,
        )
    
    def calculate_cost_efficiency(
        self,
        total_cost: float,
        issues_found: int,
        code_lines_reviewed: int
    ) -> MetricResult:
        """
        计算成本效益。
        
        成本效益 = 产出价值 / 成本
        
        Args:
            total_cost: 总成本（美元）
            issues_found: 发现的问题数量
            code_lines_reviewed: 审查的代码行数
            
        Returns:
            成本效益指标结果
        """
        if total_cost == 0:
            efficiency = 0.0
        else:
            # 每美元发现的问题数
            issues_per_dollar = issues_found / total_cost
            # 每美元审查的行数
            lines_per_dollar = code_lines_reviewed / total_cost
            # 综合效益（标准化到0-100范围）
            efficiency = min(100, (issues_per_dollar * 10 + lines_per_dollar / 100))
        
        threshold = 50.0
        
        return MetricResult(
            name="cost_efficiency",
            value=efficiency,
            description="成本效益评分",
            threshold=threshold,
            passed=efficiency >= threshold,
            unit="分",
        )
    
    def calculate_token_usage_breakdown(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, Any]:
        """
        计算 Token 使用分解。
        
        Args:
            prompt_tokens: 输入 Token 数
            completion_tokens: 输出 Token 数
            
        Returns:
            Token 使用分解字典
        """
        total = prompt_tokens + completion_tokens
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total,
            "prompt_ratio": prompt_tokens / max(1, total),
            "completion_ratio": completion_tokens / max(1, total),
            "compression_ratio": completion_tokens / max(1, prompt_tokens),
        }
    
    def calculate_model_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, float]:
        """
        计算模型调用成本。
        
        Args:
            model: 模型名称
            prompt_tokens: 输入 Token 数
            completion_tokens: 输出 Token 数
            
        Returns:
            成本计算结果字典
        """
        rates = self.cost_rates.get(model, {"input": 0.01, "output": 0.03})
        
        input_cost = (prompt_tokens / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "cost_per_1k_tokens": total_cost / max(0.001, (prompt_tokens + completion_tokens) / 1000),
        }
    
    def calculate_token_budget_compliance(
        self,
        tokens_used: int,
        token_budget: int
    ) -> MetricResult:
        """
        计算 Token 预算合规性。
        
        Args:
            tokens_used: 使用的 Token 数
            token_budget: Token 预算
            
        Returns:
            预算合规性指标结果
        """
        if token_budget == 0:
            compliance = 100.0
        else:
            compliance = max(0, 100 - ((tokens_used - token_budget) / token_budget * 100))
        
        threshold = 100.0
        
        return MetricResult(
            name="token_budget_compliance",
            value=compliance,
            description="Token 预算合规性（%）",
            threshold=threshold,
            passed=tokens_used <= token_budget,
            unit="%",
        )
    
    # ==================== 综合指标 ====================
    
    def calculate_completeness(
        self,
        issues_expected: int,
        issues_found: int
    ) -> MetricResult:
        """
        计算完整性评分。
        
        Args:
            issues_expected: 期望的问题数量
            issues_found: 发现的问题数量
            
        Returns:
            完整性指标结果
        """
        if issues_expected == 0:
            completeness = 100.0 if issues_found == 0 else 50.0
        else:
            completeness = min(100.0, (issues_found / issues_expected) * 100)
        
        return MetricResult(
            name="completeness",
            value=completeness,
            description="完整性：发现的问题占预期问题的百分比",
            threshold=80.0,
            passed=completeness >= 80.0,
            unit="%",
        )
    
    def calculate_severity_accuracy(
        self,
        severity_matches: Dict[str, int],
        severity_totals: Dict[str, int]
    ) -> MetricResult:
        """
        计算严重程度分类准确率。
        
        Args:
            severity_matches: 正确分类的严重程度数量
            severity_totals: 各严重程度的总数量
            
        Returns:
            严重程度准确率指标结果
        """
        total_matches = sum(severity_matches.values())
        total_issues = sum(severity_totals.values())
        
        accuracy = (total_matches / max(1, total_issues)) * 100
        
        return MetricResult(
            name="severity_accuracy",
            value=accuracy,
            description="严重程度分类准确率",
            threshold=75.0,
            passed=accuracy >= 75.0,
            unit="%",
        )
    
    def calculate_position_accuracy(
        self,
        correct_positions: int,
        total_issues: int
    ) -> MetricResult:
        """
        计算位置（行号）准确率。
        
        Args:
            correct_positions: 正确识别位置的问题数
            total_issues: 总问题数
            
        Returns:
            位置准确率指标结果
        """
        accuracy = (correct_positions / max(1, total_issues)) * 100
        
        return MetricResult(
            name="position_accuracy",
            value=accuracy,
            description="位置准确率：正确识别问题位置的比例",
            threshold=70.0,
            passed=accuracy >= 70.0,
            unit="%",
        )
    
    def calculate_suggestion_quality(
        self,
        useful_suggestions: int,
        total_suggestions: int
    ) -> MetricResult:
        """
        计算建议质量评分。
        
        Args:
            useful_suggestions: 有用建议数量
            total_suggestions: 总建议数量
            
        Returns:
            建议质量指标结果
        """
        quality = (useful_suggestions / max(1, total_suggestions)) * 100
        
        return MetricResult(
            name="suggestion_quality",
            value=quality,
            description="建议质量：有用建议占所有建议的百分比",
            threshold=60.0,
            passed=quality >= 60.0,
            unit="%",
        )
    
    def calculate_weighted_score(
        self,
        metrics: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> MetricResult:
        """
        计算加权综合评分。
        
        Args:
            metrics: 指标值字典
            weights: 各指标的权重
            
        Returns:
            加权评分指标结果
        """
        if weights is None:
            weights = {
                "precision": 0.25,
                "recall": 0.25,
                "f1_score": 0.3,
                "accuracy": 0.2,
            }
        
        total_weight = 0
        weighted_sum = 0
        
        for metric_name, value in metrics.items():
            weight = weights.get(metric_name, 0)
            weighted_sum += value * weight
            total_weight += weight
        
        if total_weight == 0:
            score = 0.0
        else:
            score = weighted_sum / total_weight
        
        return MetricResult(
            name="weighted_score",
            value=score,
            description="加权综合评分",
            threshold=70.0,
            passed=score >= 70.0,
            unit="分",
        )
    
    def calculate_geometric_mean(
        self,
        values: List[float]
    ) -> MetricResult:
        """
        计算几何平均值。
        
        几何平均值适合用于综合多个比率型指标。
        
        Args:
            values: 值列表
            
        Returns:
            几何平均值指标结果
        """
        if not values or any(v <= 0 for v in values):
            geo_mean = 0.0
        else:
            geo_mean = math.exp(sum(math.log(v) for v in values) / len(values))
        
        return MetricResult(
            name="geometric_mean",
            value=geo_mean,
            description="几何平均值",
            threshold=0.7,
            passed=geo_mean >= 0.7,
        )
    
    def generate_metrics_summary(
        self,
        metrics: List[MetricResult]
    ) -> Dict[str, Any]:
        """
        生成多个指标的汇总。
        
        Args:
            metrics: 指标结果列表
            
        Returns:
            汇总字典
        """
        total = len(metrics)
        passed = sum(1 for m in metrics if m.passed)
        failed = total - passed
        
        values = [m.value for m in metrics]
        avg_value = sum(values) / max(1, len(values))
        
        # 按类别分组
        categories = {
            "basic": ["precision", "recall", "f1_score", "accuracy"],
            "quality": ["code_quality_score", "code_complexity", "issue_density"],
            "performance": ["response_time", "throughput", "success_rate"],
            "refactoring": ["refactoring_improvement", "code_simplification"],
            "token": ["token_efficiency", "cost_efficiency"],
        }
        
        category_results = {}
        for category, metric_names in categories.items():
            category_metrics = [m for m in metrics if m.name in metric_names]
            if category_metrics:
                category_passed = sum(1 for m in category_metrics if m.passed)
                category_results[category] = {
                    "total": len(category_metrics),
                    "passed": category_passed,
                    "pass_rate": (category_passed / len(category_metrics)) * 100,
                }
        
        return {
            "total_metrics": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / max(1, total)) * 100,
            "average_value": avg_value,
            "category_results": category_results,
            "metrics": {m.name: m.to_dict() for m in metrics},
        }
