"""
Token Monitor for AI Agent Benchmark system.

This module provides token usage tracking, cost calculation,
efficiency analysis, and monitoring for LLM API calls.

功能：
- 跟踪每个 Agent 的 Token 使用
- 计算成本效益
- 识别低效使用模式
- 生成监控报告
"""

import time
import json
import statistics
from typing import Any, Dict, List, Optional, Tuple, Set
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class InefficiencyType(Enum):
    """低效使用模式类型。"""
    HIGH_PROMPT_RATIO = "high_prompt_ratio"  # 输入比例过高
    REDUNDANT_REQUESTS = "redundant_requests"  # 重复请求
    EXCESSIVE_TOKENS = "excessive_tokens"  # 单次请求Token过多
    LOW_OUTPUT_QUALITY = "low_output_quality"  # 输出质量低
    COST_WASTE = "cost_waste"  # 成本浪费


@dataclass
class TokenUsage:
    """Token 使用记录。
    
    属性：
        request_id: 请求唯一标识
        model: 模型名称
        prompt_tokens: 输入 Token 数
        completion_tokens: 输出 Token 数
        total_tokens: 总 Token 数
        cost: 成本（美元）
        timestamp: 时间戳
        agent_name: Agent 名称
        task_type: 任务类型
        task_description: 任务描述
        input_hash: 输入内容哈希（用于检测重复请求）
    """
    request_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: Optional[str] = None
    task_type: Optional[str] = None
    task_description: Optional[str] = None
    input_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "request_id": self.request_id,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "task_description": self.task_description,
            "input_hash": self.input_hash,
        }


@dataclass
class UsageSummary:
    """使用摘要。
    
    属性：
        total_requests: 总请求数
        total_prompt_tokens: 总输入 Token 数
        total_completion_tokens: 总输出 Token 数
        total_tokens: 总 Token 数
        total_cost: 总成本
        average_tokens_per_request: 平均每请求 Token 数
        average_cost_per_request: 平均每请求成本
        model_usage: 按模型分组的使用统计
        agent_usage: 按 Agent 分组的使用统计
    """
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost: float
    average_tokens_per_request: float
    average_cost_per_request: float
    model_usage: Dict[str, Dict[str, Any]]
    agent_usage: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "average_tokens_per_request": self.average_tokens_per_request,
            "average_cost_per_request": self.average_cost_per_request,
            "model_usage": self.model_usage,
            "agent_usage": self.agent_usage,
        }


@dataclass
class InefficiencyPattern:
    """低效使用模式。
    
    属性：
        pattern_type: 模式类型
        description: 描述
        affected_requests: 受影响的请求数量
        wasted_tokens: 浪费的 Token 数量
        wasted_cost: 浪费的成本
        recommendation: 建议
    """
    pattern_type: InefficiencyType
    description: str
    affected_requests: int
    wasted_tokens: int
    wasted_cost: float
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "pattern_type": self.pattern_type.value,
            "description": self.description,
            "affected_requests": self.affected_requests,
            "wasted_tokens": self.wasted_tokens,
            "wasted_cost": self.wasted_cost,
            "recommendation": self.recommendation,
        }


@dataclass
class MonitoringReport:
    """监控报告。
    
    属性：
        report_id: 报告ID
        start_time: 报告开始时间
        end_time: 报告结束时间
        summary: 使用摘要
        inefficiency_patterns: 低效模式列表
        cost_analysis: 成本分析
        recommendations: 建议列表
        timestamp: 生成时间戳
    """
    report_id: str
    start_time: datetime
    end_time: datetime
    summary: UsageSummary
    inefficiency_patterns: List[InefficiencyPattern]
    cost_analysis: Dict[str, Any]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "report_id": self.report_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "summary": self.summary.to_dict(),
            "inefficiency_patterns": [p.to_dict() for p in self.inefficiency_patterns],
            "cost_analysis": self.cost_analysis,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }
    
    def save(self, file_path: str):
        """保存报告到文件。"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"监控报告已保存到 {file_path}")


class TokenMonitor:
    """Token 使用监控器。
    
    提供 Token 使用跟踪、成本计算、低效模式识别和监控报告生成功能。
    
    使用示例：
        ```python
        monitor = TokenMonitor()
        
        # 记录使用
        usage = monitor.record_usage(
            request_id="req_001",
            model="gpt-4",
            prompt_tokens=500,
            completion_tokens=200,
            agent_name="reviewer"
        )
        
        # 识别低效模式
        patterns = monitor.identify_inefficiency_patterns()
        
        # 生成报告
        report = monitor.generate_report()
        report.save("token_report.json")
        ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Token 监控器。
        
        Args:
            config: 配置字典，可包含：
                - cost_rates: 模型成本费率
                - alert_thresholds: 告警阈值
                - inefficiency_thresholds: 低效识别阈值
        """
        self.config = config or {}
        self.usages: List[TokenUsage] = []
        
        # 成本费率（每1K token）
        self.cost_rates = self.config.get("cost_rates", {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        })
        
        # 告警阈值
        self.alert_thresholds = self.config.get("alert_thresholds", {
            "daily_token_limit": 1000000,
            "daily_cost_limit": 100.0,
            "request_token_limit": 10000,
        })
        
        # 低效识别阈值
        self.inefficiency_thresholds = self.config.get("inefficiency_thresholds", {
            "high_prompt_ratio": 0.85,  # 输入比例超过85%
            "redundant_request_window": 300,  # 5分钟内重复请求
            "excessive_tokens": 5000,  # 单次请求超过5000 token
            "low_output_ratio": 0.1,  # 输出比例低于10%
            "cost_per_issue_threshold": 5.0,  # 每个问题成本超过5美元
        })
        
        logger.info("Token 监控器已初始化")
    
    def record_usage(
        self,
        request_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        task_description: Optional[str] = None,
        input_hash: Optional[str] = None
    ) -> TokenUsage:
        """
        记录 Token 使用。
        
        Args:
            request_id: 请求标识
            model: 模型名称
            prompt_tokens: 输入 Token 数
            completion_tokens: 输出 Token 数
            agent_name: Agent 名称
            task_type: 任务类型
            task_description: 任务描述
            input_hash: 输入内容哈希
            
        Returns:
            Token 使用记录
        """
        total_tokens = prompt_tokens + completion_tokens
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        
        usage = TokenUsage(
            request_id=request_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            agent_name=agent_name,
            task_type=task_type,
            task_description=task_description,
            input_hash=input_hash,
        )
        
        self.usages.append(usage)
        
        # 检查告警
        self._check_alerts(usage)
        
        logger.debug(
            f"记录 Token 使用: {total_tokens} tokens, ${cost:.4f}, "
            f"Agent: {agent_name}, Model: {model}"
        )
        
        return usage
    
    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """计算成本。"""
        rates = self.cost_rates.get(model, {"input": 0.01, "output": 0.03})
        
        input_cost = (prompt_tokens / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost
    
    def _check_alerts(self, usage: TokenUsage):
        """检查告警条件。"""
        # 检查单次请求限制
        if usage.total_tokens > self.alert_thresholds.get("request_token_limit", 10000):
            logger.warning(
                f"单次请求 Token 使用过高: {usage.total_tokens} tokens "
                f"(限制: {self.alert_thresholds.get('request_token_limit', 10000)})"
            )
        
        # 检查每日限制
        daily_usage = self.get_daily_usage()
        
        if daily_usage["total_tokens"] > self.alert_thresholds.get("daily_token_limit", 1000000):
            logger.warning(
                f"每日 Token 限制已超: {daily_usage['total_tokens']} tokens "
                f"(限制: {self.alert_thresholds.get('daily_token_limit', 1000000)})"
            )
        
        if daily_usage["total_cost"] > self.alert_thresholds.get("daily_cost_limit", 100.0):
            logger.warning(
                f"每日成本限制已超: ${daily_usage['total_cost']:.2f} "
                f"(限制: ${self.alert_thresholds.get('daily_cost_limit', 100.0):.2f})"
            )
    
    def get_usage(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        model: Optional[str] = None,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> UsageSummary:
        """
        获取使用摘要（可选过滤条件）。
        
        Args:
            start_time: 开始时间过滤
            end_time: 结束时间过滤
            model: 模型过滤
            agent_name: Agent 过滤
            task_type: 任务类型过滤
            
        Returns:
            使用摘要
        """
        filtered_usages = self._filter_usages(start_time, end_time, model, agent_name, task_type)
        
        if not filtered_usages:
            return UsageSummary(
                total_requests=0,
                total_prompt_tokens=0,
                total_completion_tokens=0,
                total_tokens=0,
                total_cost=0.0,
                average_tokens_per_request=0.0,
                average_cost_per_request=0.0,
                model_usage={},
                agent_usage={},
            )
        
        # 计算总数
        total_prompt_tokens = sum(u.prompt_tokens for u in filtered_usages)
        total_completion_tokens = sum(u.completion_tokens for u in filtered_usages)
        total_tokens = sum(u.total_tokens for u in filtered_usages)
        total_cost = sum(u.cost for u in filtered_usages)
        
        # 计算平均值
        avg_tokens = total_tokens / len(filtered_usages)
        avg_cost = total_cost / len(filtered_usages)
        
        # 按模型分组
        model_usage = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        for usage in filtered_usages:
            model_usage[usage.model]["requests"] += 1
            model_usage[usage.model]["tokens"] += usage.total_tokens
            model_usage[usage.model]["cost"] += usage.cost
        
        # 按 Agent 分组
        agent_usage = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        for usage in filtered_usages:
            agent = usage.agent_name or "unknown"
            agent_usage[agent]["requests"] += 1
            agent_usage[agent]["tokens"] += usage.total_tokens
            agent_usage[agent]["cost"] += usage.cost
        
        return UsageSummary(
            total_requests=len(filtered_usages),
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            total_cost=total_cost,
            average_tokens_per_request=avg_tokens,
            average_cost_per_request=avg_cost,
            model_usage=dict(model_usage),
            agent_usage=dict(agent_usage),
        )
    
    def _filter_usages(
        self,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        model: Optional[str],
        agent_name: Optional[str],
        task_type: Optional[str] = None
    ) -> List[TokenUsage]:
        """过滤使用记录。"""
        filtered = self.usages
        
        if start_time:
            filtered = [u for u in filtered if u.timestamp >= start_time]
        
        if end_time:
            filtered = [u for u in filtered if u.timestamp <= end_time]
        
        if model:
            filtered = [u for u in filtered if u.model == model]
        
        if agent_name:
            filtered = [u for u in filtered if u.agent_name == agent_name]
        
        if task_type:
            filtered = [u for u in filtered if u.task_type == task_type]
        
        return filtered
    
    def get_daily_usage(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取指定日期的使用情况。
        
        Args:
            date: 日期（默认今天）
            
        Returns:
            每日使用字典
        """
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        summary = self.get_usage(start_time=start_of_day, end_time=end_of_day)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "total_requests": summary.total_requests,
            "total_tokens": summary.total_tokens,
            "total_cost": summary.total_cost,
        }
    
    def get_model_costs(self) -> Dict[str, Dict[str, float]]:
        """获取所有模型的成本费率。"""
        return self.cost_rates
    
    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """估算给定 Token 数的成本。"""
        return self._calculate_cost(model, prompt_tokens, completion_tokens)
    
    def get_usage_history(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """获取最近N天的使用历史。"""
        history = []
        now = datetime.now()
        
        for i in range(days):
            date = now - timedelta(days=i)
            daily_usage = self.get_daily_usage(date)
            history.append(daily_usage)
        
        return list(reversed(history))
    
    # ==================== 低效模式识别 ====================
    
    def identify_inefficiency_patterns(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[InefficiencyPattern]:
        """
        识别低效使用模式。
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            低效模式列表
        """
        filtered_usages = self._filter_usages(start_time, end_time, None, None)
        patterns: List[InefficiencyPattern] = []
        
        if not filtered_usages:
            return patterns
        
        # 1. 检查高输入比例
        high_prompt_pattern = self._check_high_prompt_ratio(filtered_usages)
        if high_prompt_pattern:
            patterns.append(high_prompt_pattern)
        
        # 2. 检查重复请求
        redundant_pattern = self._check_redundant_requests(filtered_usages)
        if redundant_pattern:
            patterns.append(redundant_pattern)
        
        # 3. 检查过度 Token 使用
        excessive_pattern = self._check_excessive_tokens(filtered_usages)
        if excessive_pattern:
            patterns.append(excessive_pattern)
        
        # 4. 检查低输出质量
        low_output_pattern = self._check_low_output_quality(filtered_usages)
        if low_output_pattern:
            patterns.append(low_output_pattern)
        
        logger.info(f"识别到 {len(patterns)} 个低效模式")
        return patterns
    
    def _check_high_prompt_ratio(
        self,
        usages: List[TokenUsage]
    ) -> Optional[InefficiencyPattern]:
        """检查高输入比例模式。"""
        threshold = self.inefficiency_thresholds.get("high_prompt_ratio", 0.85)
        
        affected = []
        wasted_tokens = 0
        
        for usage in usages:
            if usage.total_tokens > 0:
                prompt_ratio = usage.prompt_tokens / usage.total_tokens
                if prompt_ratio > threshold:
                    affected.append(usage)
                    # 估计浪费的 token（输入中可能冗余的部分）
                    excess = int(usage.prompt_tokens * (prompt_ratio - 0.5))
                    wasted_tokens += max(0, excess)
        
        if not affected:
            return None
        
        wasted_cost = sum(u.cost for u in affected) * 0.3  # 估计30%的成本浪费
        
        return InefficiencyPattern(
            pattern_type=InefficiencyType.HIGH_PROMPT_RATIO,
            description=f"发现 {len(affected)} 个请求的输入比例超过 {threshold*100:.0f}%，"
                       f"可能导致上下文冗余",
            affected_requests=len(affected),
            wasted_tokens=wasted_tokens,
            wasted_cost=wasted_cost,
            recommendation="考虑缩短输入提示、提取关键信息、或使用更高效的上下文管理策略",
        )
    
    def _check_redundant_requests(
        self,
        usages: List[TokenUsage]
    ) -> Optional[InefficiencyPattern]:
        """检查重复请求模式。"""
        window_seconds = self.inefficiency_thresholds.get("redundant_request_window", 300)
        
        # 按输入哈希分组
        hash_groups: Dict[str, List[TokenUsage]] = defaultdict(list)
        for usage in usages:
            if usage.input_hash:
                hash_groups[usage.input_hash].append(usage)
        
        affected = []
        wasted_tokens = 0
        
        for hash_val, group in hash_groups.items():
            if len(group) > 1:
                # 检查时间窗口内的重复
                group.sort(key=lambda x: x.timestamp)
                for i in range(1, len(group)):
                    time_diff = (group[i].timestamp - group[i-1].timestamp).total_seconds()
                    if time_diff < window_seconds:
                        affected.append(group[i])
                        wasted_tokens += group[i].total_tokens
        
        if not affected:
            return None
        
        wasted_cost = sum(u.cost for u in affected)
        
        return InefficiencyPattern(
            pattern_type=InefficiencyType.REDUNDANT_REQUESTS,
            description=f"发现 {len(affected)} 个可能重复的请求（{window_seconds}秒内相同输入）",
            affected_requests=len(affected),
            wasted_tokens=wasted_tokens,
            wasted_cost=wasted_cost,
            recommendation="实现请求缓存、增加去重机制、或延长重复检查窗口",
        )
    
    def _check_excessive_tokens(
        self,
        usages: List[TokenUsage]
    ) -> Optional[InefficiencyPattern]:
        """检查过度 Token 使用模式。"""
        threshold = self.inefficiency_thresholds.get("excessive_tokens", 5000)
        
        affected = []
        wasted_tokens = 0
        
        for usage in usages:
            if usage.total_tokens > threshold:
                affected.append(usage)
                wasted_tokens += usage.total_tokens - threshold
        
        if not affected:
            return None
        
        wasted_cost = sum(u.cost for u in affected) * 0.4
        
        return InefficiencyPattern(
            pattern_type=InefficiencyType.EXCESSIVE_TOKENS,
            description=f"发现 {len(affected)} 个请求超过 {threshold} tokens",
            affected_requests=len(affected),
            wasted_tokens=wasted_tokens,
            wasted_cost=wasted_cost,
            recommendation="考虑分块处理、简化任务、或使用支持更长上下文的模型",
        )
    
    def _check_low_output_quality(
        self,
        usages: List[TokenUsage]
    ) -> Optional[InefficiencyPattern]:
        """检查低输出质量模式。"""
        threshold = self.inefficiency_thresholds.get("low_output_ratio", 0.1)
        
        affected = []
        wasted_tokens = 0
        
        for usage in usages:
            if usage.total_tokens > 0:
                output_ratio = usage.completion_tokens / usage.total_tokens
                if output_ratio < threshold and usage.prompt_tokens > 100:
                    affected.append(usage)
                    # 估计浪费的输入 token
                    wasted_tokens += int(usage.prompt_tokens * 0.5)
        
        if not affected:
            return None
        
        wasted_cost = sum(u.cost for u in affected) * 0.5
        
        return InefficiencyPattern(
            pattern_type=InefficiencyType.LOW_OUTPUT_QUALITY,
            description=f"发现 {len(affected)} 个请求的输出比例低于 {threshold*100:.0f}%，"
                       f"可能输出质量不佳",
            affected_requests=len(affected),
            wasted_tokens=wasted_tokens,
            wasted_cost=wasted_cost,
            recommendation="检查任务定义是否清晰、考虑调整温度参数、或重新设计提示",
        )
    
    # ==================== 成本效益分析 ====================
    
    def calculate_cost_efficiency(
        self,
        issues_found: int,
        code_lines_reviewed: int
    ) -> Dict[str, Any]:
        """
        计算成本效益。
        
        Args:
            issues_found: 发现的问题数量
            code_lines_reviewed: 审查的代码行数
            
        Returns:
            成本效益分析字典
        """
        summary = self.get_usage()
        
        if summary.total_cost == 0:
            return {
                "cost_per_issue": 0.0,
                "cost_per_line": 0.0,
                "issues_per_dollar": 0.0,
                "lines_per_dollar": 0.0,
                "efficiency_score": 0.0,
            }
        
        cost_per_issue = summary.total_cost / max(1, issues_found)
        cost_per_line = summary.total_cost / max(1, code_lines_reviewed)
        issues_per_dollar = issues_found / summary.total_cost
        lines_per_dollar = code_lines_reviewed / summary.total_cost
        
        # 效率评分（0-100）
        efficiency_score = min(100, (issues_per_dollar * 10 + lines_per_dollar / 100))
        
        return {
            "total_cost": summary.total_cost,
            "cost_per_issue": cost_per_issue,
            "cost_per_line": cost_per_line,
            "issues_per_dollar": issues_per_dollar,
            "lines_per_dollar": lines_per_dollar,
            "efficiency_score": efficiency_score,
        }
    
    # ==================== 监控报告 ====================
    
    def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        issues_found: int = 0,
        code_lines_reviewed: int = 0
    ) -> MonitoringReport:
        """
        生成监控报告。
        
        Args:
            start_time: 报告开始时间
            end_time: 报告结束时间
            issues_found: 发现的问题数量
            code_lines_reviewed: 审查的代码行数
            
        Returns:
            监控报告
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.now()
        
        # 获取使用摘要
        summary = self.get_usage(start_time, end_time)
        
        # 识别低效模式
        patterns = self.identify_inefficiency_patterns(start_time, end_time)
        
        # 成本分析
        cost_analysis = self.calculate_cost_efficiency(issues_found, code_lines_reviewed)
        
        # 生成建议
        recommendations = self._generate_recommendations(summary, patterns, cost_analysis)
        
        # 计算总浪费
        total_wasted_tokens = sum(p.wasted_tokens for p in patterns)
        total_wasted_cost = sum(p.wasted_cost for p in patterns)
        
        report = MonitoringReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=start_time,
            end_time=end_time,
            summary=summary,
            inefficiency_patterns=patterns,
            cost_analysis={
                **cost_analysis,
                "total_wasted_tokens": total_wasted_tokens,
                "total_wasted_cost": total_wasted_cost,
                "waste_percentage": (total_wasted_cost / max(0.01, summary.total_cost)) * 100,
            },
            recommendations=recommendations,
        )
        
        logger.info(f"监控报告已生成: {report.report_id}")
        return report
    
    def _generate_recommendations(
        self,
        summary: UsageSummary,
        patterns: List[InefficiencyPattern],
        cost_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成优化建议。"""
        recommendations = []
        
        # 基于使用量的建议
        if summary.total_tokens > 500000:
            recommendations.append("Token 使用量较大，考虑优化提示或分批处理")
        
        # 基于成本的建议
        if summary.total_cost > 50:
            recommendations.append("成本较高，考虑使用更经济的模型或减少调用次数")
        
        # 基于低效模式的建议
        for pattern in patterns:
            recommendations.append(pattern.recommendation)
        
        # 基于成本效益的建议
        if cost_analysis.get("cost_per_issue", 0) > 5:
            recommendations.append("每个问题的发现成本较高，考虑优化审查策略")
        
        if not recommendations:
            recommendations.append("Token 使用效率良好，继续保持")
        
        return recommendations
    
    # ==================== 数据管理 ====================
    
    def clear_history(self, older_than_days: Optional[int] = None):
        """
        清除使用历史。
        
        Args:
            older_than_days: 如果指定，只清除早于该天数的记录
        """
        if older_than_days is None:
            self.usages.clear()
        else:
            cutoff = datetime.now() - timedelta(days=older_than_days)
            self.usages = [u for u in self.usages if u.timestamp > cutoff]
        
        logger.info(f"已清除使用历史（{older_than_days}天之前的记录）")
    
    def export_usage(self, file_path: str):
        """
        导出使用数据到 JSON 文件。
        
        Args:
            file_path: 导出文件路径
        """
        data = [usage.to_dict() for usage in self.usages]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"已导出 {len(self.usages)} 条使用记录到 {file_path}")
    
    def import_usage(self, file_path: str):
        """
        从 JSON 文件导入使用数据。
        
        Args:
            file_path: 导入文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for record in data:
            usage = TokenUsage(
                request_id=record["request_id"],
                model=record["model"],
                prompt_tokens=record["prompt_tokens"],
                completion_tokens=record["completion_tokens"],
                total_tokens=record["total_tokens"],
                cost=record["cost"],
                timestamp=datetime.fromisoformat(record["timestamp"]),
                agent_name=record.get("agent_name"),
                task_type=record.get("task_type"),
                task_description=record.get("task_description"),
                input_hash=record.get("input_hash"),
            )
            self.usages.append(usage)
        
        logger.info(f"已从 {file_path} 导入 {len(data)} 条使用记录")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取使用统计信息。
        
        Returns:
            统计信息字典
        """
        summary = self.get_usage()
        
        # 计算额外统计
        all_costs = [u.cost for u in self.usages]
        all_tokens = [u.total_tokens for u in self.usages]
        
        cost_std = statistics.stdev(all_costs) if len(all_costs) > 1 else 0
        tokens_std = statistics.stdev(all_tokens) if len(all_tokens) > 1 else 0
        
        return {
            "total_requests": summary.total_requests,
            "total_tokens": summary.total_tokens,
            "total_cost": summary.total_cost,
            "average_tokens_per_request": summary.average_tokens_per_request,
            "average_cost_per_request": summary.average_cost_per_request,
            "models_used": list(summary.model_usage.keys()),
            "agents_used": list(summary.agent_usage.keys()),
            "cost_standard_deviation": cost_std,
            "tokens_standard_deviation": tokens_std,
            "unique_models": len(summary.model_usage),
            "unique_agents": len(summary.agent_usage),
        }
