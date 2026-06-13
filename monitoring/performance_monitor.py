"""
Performance Monitor for AI Agent Benchmark system.

This module provides performance monitoring capabilities including
execution time tracking, resource usage monitoring, bottleneck identification,
and performance report generation.

功能：
- 监控 Agent 处理时间
- 监控系统资源使用
- 识别性能瓶颈
- 生成性能报告
"""

import time
import json
import statistics
import psutil
from typing import Any, Dict, List, Optional, Callable
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from contextlib import contextmanager
from enum import Enum

logger = logging.getLogger(__name__)


class BottleneckType(Enum):
    """性能瓶颈类型。"""
    CPU_BOUND = "cpu_bound"  # CPU 密集
    MEMORY_BOUND = "memory_bound"  # 内存密集
    IO_BOUND = "io_bound"  # IO 密集
    SLOW_OPERATION = "slow_operation"  # 慢操作
    RESOURCE_LEAK = "resource_leak"  # 资源泄漏


@dataclass
class PerformanceRecord:
    """性能记录。
    
    属性：
        operation: 操作名称
        execution_time: 执行时间（秒）
        memory_usage: 内存使用量（字节）
        cpu_usage: CPU 使用率（%）
        timestamp: 时间戳
        agent_name: Agent 名称
        task_type: 任务类型
        metadata: 元数据
        io_read_bytes: IO 读取字节数
        io_write_bytes: IO 写入字节数
    """
    operation: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: Optional[str] = None
    task_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "operation": self.operation,
            "execution_time": self.execution_time,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "metadata": self.metadata,
            "io_read_bytes": self.io_read_bytes,
            "io_write_bytes": self.io_write_bytes,
        }


@dataclass
class PerformanceSummary:
    """性能摘要。
    
    属性：
        total_operations: 总操作数
        total_execution_time: 总执行时间
        average_execution_time: 平均执行时间
        min_execution_time: 最小执行时间
        max_execution_time: 最大执行时间
        total_memory_usage: 总内存使用量
        average_memory_usage: 平均内存使用量
        total_cpu_usage: 总 CPU 使用率
        average_cpu_usage: 平均 CPU 使用率
        operation_stats: 按操作分组的统计
        p95_execution_time: 95分位执行时间
        p99_execution_time: 99分位执行时间
    """
    total_operations: int
    total_execution_time: float
    average_execution_time: float
    min_execution_time: float
    max_execution_time: float
    total_memory_usage: float
    average_memory_usage: float
    total_cpu_usage: float
    average_cpu_usage: float
    operation_stats: Dict[str, Dict[str, Any]]
    p95_execution_time: float = 0.0
    p99_execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "total_operations": self.total_operations,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.average_execution_time,
            "min_execution_time": self.min_execution_time,
            "max_execution_time": self.max_execution_time,
            "total_memory_usage": self.total_memory_usage,
            "average_memory_usage": self.average_memory_usage,
            "total_cpu_usage": self.total_cpu_usage,
            "average_cpu_usage": self.average_cpu_usage,
            "operation_stats": self.operation_stats,
            "p95_execution_time": self.p95_execution_time,
            "p99_execution_time": self.p99_execution_time,
        }


@dataclass
class Bottleneck:
    """性能瓶颈。
    
    属性：
        bottleneck_type: 瓶颈类型
        operation: 受影响的操作
        description: 描述
        severity: 严重程度 (low, medium, high, critical)
        impact_score: 影响评分 (0-100)
        recommendation: 建议
        metrics: 相关指标
    """
    bottleneck_type: BottleneckType
    operation: str
    description: str
    severity: str
    impact_score: float
    recommendation: str
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "bottleneck_type": self.bottleneck_type.value,
            "operation": self.operation,
            "description": self.description,
            "severity": self.severity,
            "impact_score": self.impact_score,
            "recommendation": self.recommendation,
            "metrics": self.metrics,
        }


@dataclass
class PerformanceReport:
    """性能报告。
    
    属性：
        report_id: 报告ID
        start_time: 开始时间
        end_time: 结束时间
        summary: 性能摘要
        bottlenecks: 瓶颈列表
        system_info: 系统信息
        recommendations: 建议列表
        timestamp: 生成时间戳
    """
    report_id: str
    start_time: datetime
    end_time: datetime
    summary: PerformanceSummary
    bottlenecks: List[Bottleneck]
    system_info: Dict[str, Any]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "report_id": self.report_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "summary": self.summary.to_dict(),
            "bottlenecks": [b.to_dict() for b in self.bottlenecks],
            "system_info": self.system_info,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }
    
    def save(self, file_path: str):
        """保存报告到文件。"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"性能报告已保存到 {file_path}")


class PerformanceMonitor:
    """性能监控器。
    
    提供操作性能跟踪、资源使用监控、瓶颈识别和性能报告生成功能。
    
    使用示例：
        ```python
        monitor = PerformanceMonitor()
        
        # 使用上下文管理器跟踪操作
        with monitor.track("code_review", agent_name="reviewer"):
            result = await agent.review_code(code)
        
        # 识别瓶颈
        bottlenecks = monitor.identify_bottlenecks()
        
        # 生成报告
        report = monitor.generate_report()
        report.save("performance_report.json")
        ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化性能监控器。
        
        Args:
            config: 配置字典，可包含：
                - thresholds: 告警阈值
                - bottleneck_thresholds: 瓶颈识别阈值
                - system_monitoring: 是否启用系统监控
        """
        self.config = config or {}
        self.records: List[PerformanceRecord] = []
        
        # 告警阈值
        self.thresholds = self.config.get("thresholds", {
            "execution_time_warning": 5.0,
            "execution_time_critical": 10.0,
            "memory_usage_warning": 100 * 1024 * 1024,  # 100MB
            "memory_usage_critical": 500 * 1024 * 1024,  # 500MB
            "cpu_usage_warning": 80.0,
            "cpu_usage_critical": 95.0,
        })
        
        # 瓶颈识别阈值
        self.bottleneck_thresholds = self.config.get("bottleneck_thresholds", {
            "slow_operation_time": 5.0,  # 慢操作阈值（秒）
            "high_memory_growth": 50 * 1024 * 1024,  # 内存增长阈值（50MB）
            "cpu_saturation": 90.0,  # CPU 饱和阈值
            "io_heavy_threshold": 10 * 1024 * 1024,  # IO 密集阈值（10MB）
        })
        
        # 系统监控
        self.system_monitoring = self.config.get("system_monitoring", True)
        
        logger.info("性能监控器已初始化")
    
    @contextmanager
    def track(
        self,
        operation: str,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        上下文管理器：跟踪操作性能。
        
        Args:
            operation: 操作名称
            agent_name: Agent 名称
            task_type: 任务类型
            metadata: 元数据
        """
        # 初始化变量
        process = psutil.Process()
        initial_memory = 0
        initial_cpu = 0.0
        initial_io_read = 0
        initial_io_write = 0
        start_time = time.time()
        final_memory = 0
        final_cpu = 0.0
        final_io_read = 0
        final_io_write = 0
        
        try:
            initial_memory = process.memory_info().rss
            initial_cpu = process.cpu_percent()
            
            # 获取 IO 计数器
            try:
                io_counters = process.io_counters()
                initial_io_read = io_counters.read_bytes
                initial_io_write = io_counters.write_bytes
            except (AttributeError, psutil.Error):
                initial_io_read = 0
                initial_io_write = 0
            
            start_time = time.time()
            
            yield
            
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 获取最终资源使用
            try:
                final_memory = process.memory_info().rss
                final_cpu = process.cpu_percent()
                
                try:
                    io_counters = process.io_counters()
                    final_io_read = io_counters.read_bytes
                    final_io_write = io_counters.write_bytes
                except (AttributeError, psutil.Error):
                    final_io_read = initial_io_read
                    final_io_write = initial_io_write
                    
            except psutil.NoSuchProcess:
                final_memory = initial_memory
                final_cpu = initial_cpu
                final_io_read = initial_io_read
                final_io_write = initial_io_write
            
            # 计算资源使用
            memory_usage = final_memory - initial_memory
            cpu_usage = (initial_cpu + final_cpu) / 2
            io_read = final_io_read - initial_io_read
            io_write = final_io_write - initial_io_write
            
            # 记录性能
            record = self.record_operation(
                operation=operation,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                agent_name=agent_name,
                task_type=task_type,
                metadata=metadata,
                io_read_bytes=io_read,
                io_write_bytes=io_write,
            )
            
            # 检查告警
            self._check_alerts(record)
    
    def record_operation(
        self,
        operation: str,
        execution_time: float,
        memory_usage: float,
        cpu_usage: float,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        io_read_bytes: int = 0,
        io_write_bytes: int = 0
    ) -> PerformanceRecord:
        """
        记录操作性能。
        
        Args:
            operation: 操作名称
            execution_time: 执行时间（秒）
            memory_usage: 内存使用量（字节）
            cpu_usage: CPU 使用率（%）
            agent_name: Agent 名称
            task_type: 任务类型
            metadata: 元数据
            io_read_bytes: IO 读取字节数
            io_write_bytes: IO 写入字节数
            
        Returns:
            性能记录
        """
        record = PerformanceRecord(
            operation=operation,
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            agent_name=agent_name,
            task_type=task_type,
            metadata=metadata,
            io_read_bytes=io_read_bytes,
            io_write_bytes=io_write_bytes,
        )
        
        self.records.append(record)
        
        logger.debug(
            f"记录性能: {operation} - "
            f"时间: {execution_time:.4f}s, "
            f"内存: {memory_usage / 1024 / 1024:.2f}MB, "
            f"CPU: {cpu_usage:.1f}%"
        )
        
        return record
    
    def _check_alerts(self, record: PerformanceRecord):
        """检查性能告警。"""
        # 执行时间告警
        if record.execution_time > self.thresholds.get("execution_time_critical", 10.0):
            logger.critical(
                f"严重执行时间: {record.operation} 耗时 {record.execution_time:.2f}s"
            )
        elif record.execution_time > self.thresholds.get("execution_time_warning", 5.0):
            logger.warning(
                f"执行时间较长: {record.operation} 耗时 {record.execution_time:.2f}s"
            )
        
        # 内存使用告警
        if record.memory_usage > self.thresholds.get("memory_usage_critical", 500 * 1024 * 1024):
            logger.critical(
                f"严重内存使用: {record.operation} 使用 {record.memory_usage / 1024 / 1024:.2f}MB"
            )
        elif record.memory_usage > self.thresholds.get("memory_usage_warning", 100 * 1024 * 1024):
            logger.warning(
                f"内存使用较高: {record.operation} 使用 {record.memory_usage / 1024 / 1024:.2f}MB"
            )
        
        # CPU 使用告警
        if record.cpu_usage > self.thresholds.get("cpu_usage_critical", 95.0):
            logger.critical(
                f"严重 CPU 使用: {record.operation} 使用 {record.cpu_usage:.1f}%"
            )
        elif record.cpu_usage > self.thresholds.get("cpu_usage_warning", 80.0):
            logger.warning(
                f"CPU 使用较高: {record.operation} 使用 {record.cpu_usage:.1f}%"
            )
    
    def get_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        operation: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> PerformanceSummary:
        """
        获取性能摘要（可选过滤条件）。
        
        Args:
            start_time: 开始时间过滤
            end_time: 结束时间过滤
            operation: 操作过滤
            agent_name: Agent 过滤
            
        Returns:
            性能摘要
        """
        filtered_records = self._filter_records(start_time, end_time, operation, agent_name)
        
        if not filtered_records:
            return PerformanceSummary(
                total_operations=0,
                total_execution_time=0.0,
                average_execution_time=0.0,
                min_execution_time=0.0,
                max_execution_time=0.0,
                total_memory_usage=0.0,
                average_memory_usage=0.0,
                total_cpu_usage=0.0,
                average_cpu_usage=0.0,
                operation_stats={},
                p95_execution_time=0.0,
                p99_execution_time=0.0,
            )
        
        # 计算总数
        total_execution_time = sum(r.execution_time for r in filtered_records)
        total_memory_usage = sum(r.memory_usage for r in filtered_records)
        total_cpu_usage = sum(r.cpu_usage for r in filtered_records)
        
        # 计算平均值
        avg_execution_time = total_execution_time / len(filtered_records)
        avg_memory_usage = total_memory_usage / len(filtered_records)
        avg_cpu_usage = total_cpu_usage / len(filtered_records)
        
        # 计算最小/最大值
        execution_times = [r.execution_time for r in filtered_records]
        min_execution_time = min(execution_times)
        max_execution_time = max(execution_times)
        
        # 计算百分位数
        sorted_times = sorted(execution_times)
        n = len(sorted_times)
        p95_index = int(n * 0.95)
        p99_index = int(n * 0.99)
        p95_execution_time = sorted_times[min(p95_index, n - 1)]
        p99_execution_time = sorted_times[min(p99_index, n - 1)]
        
        # 按操作分组统计
        operation_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "avg_memory": 0.0,
            "avg_cpu": 0.0,
        })
        
        for record in filtered_records:
            stats = operation_stats[record.operation]
            stats["count"] += 1
            stats["total_time"] += record.execution_time
            stats["min_time"] = min(stats["min_time"], record.execution_time)
            stats["max_time"] = max(stats["max_time"], record.execution_time)
            stats["avg_memory"] += record.memory_usage
            stats["avg_cpu"] += record.cpu_usage
        
        # 计算操作平均值
        for op, stats in operation_stats.items():
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["avg_memory"] = stats["avg_memory"] / stats["count"]
            stats["avg_cpu"] = stats["avg_cpu"] / stats["count"]
            if stats["min_time"] == float('inf'):
                stats["min_time"] = 0.0
        
        return PerformanceSummary(
            total_operations=len(filtered_records),
            total_execution_time=total_execution_time,
            average_execution_time=avg_execution_time,
            min_execution_time=min_execution_time,
            max_execution_time=max_execution_time,
            total_memory_usage=total_memory_usage,
            average_memory_usage=avg_memory_usage,
            total_cpu_usage=total_cpu_usage,
            average_cpu_usage=avg_cpu_usage,
            operation_stats=dict(operation_stats),
            p95_execution_time=p95_execution_time,
            p99_execution_time=p99_execution_time,
        )
    
    def _filter_records(
        self,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        operation: Optional[str],
        agent_name: Optional[str]
    ) -> List[PerformanceRecord]:
        """过滤记录。"""
        filtered = self.records
        
        if start_time:
            filtered = [r for r in filtered if r.timestamp >= start_time]
        
        if end_time:
            filtered = [r for r in filtered if r.timestamp <= end_time]
        
        if operation:
            filtered = [r for r in filtered if r.operation == operation]
        
        if agent_name:
            filtered = [r for r in filtered if r.agent_name == agent_name]
        
        return filtered
    
    # ==================== 瓶颈识别 ====================
    
    def identify_bottlenecks(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Bottleneck]:
        """
        识别性能瓶颈。
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            瓶颈列表
        """
        filtered_records = self._filter_records(start_time, end_time, None, None)
        bottlenecks: List[Bottleneck] = []
        
        if not filtered_records:
            return bottlenecks
        
        # 1. 检查慢操作
        slow_ops = self._check_slow_operations(filtered_records)
        bottlenecks.extend(slow_ops)
        
        # 2. 检查 CPU 饱和
        cpu_bottlenecks = self._check_cpu_saturation(filtered_records)
        bottlenecks.extend(cpu_bottlenecks)
        
        # 3. 检查内存问题
        memory_bottlenecks = self._check_memory_issues(filtered_records)
        bottlenecks.extend(memory_bottlenecks)
        
        # 4. 检查 IO 密集操作
        io_bottlenecks = self._check_io_intensive(filtered_records)
        bottlenecks.extend(io_bottlenecks)
        
        # 5. 检查资源泄漏模式
        leak_bottlenecks = self._check_resource_leaks(filtered_records)
        bottlenecks.extend(leak_bottlenecks)
        
        # 按影响评分排序
        bottlenecks.sort(key=lambda b: b.impact_score, reverse=True)
        
        logger.info(f"识别到 {len(bottlenecks)} 个性能瓶颈")
        return bottlenecks
    
    def _check_slow_operations(
        self,
        records: List[PerformanceRecord]
    ) -> List[Bottleneck]:
        """检查慢操作。"""
        threshold = self.bottleneck_thresholds.get("slow_operation_time", 5.0)
        bottlenecks = []
        
        # 按操作分组
        operation_times: Dict[str, List[float]] = defaultdict(list)
        for record in records:
            operation_times[record.operation].append(record.execution_time)
        
        for op, times in operation_times.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            if avg_time > threshold:
                # 计算影响评分（0-100）
                impact = min(100, (avg_time / threshold) * 50)
                
                severity = "high" if avg_time > threshold * 2 else "medium"
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.SLOW_OPERATION,
                    operation=op,
                    description=f"操作 '{op}' 平均耗时 {avg_time:.2f}s，超过阈值 {threshold}s",
                    severity=severity,
                    impact_score=impact,
                    recommendation=f"考虑优化 '{op}' 操作，当前平均耗时 {avg_time:.2f}s",
                    metrics={
                        "avg_time": avg_time,
                        "max_time": max_time,
                        "threshold": threshold,
                        "sample_count": len(times),
                    },
                ))
        
        return bottlenecks
    
    def _check_cpu_saturation(
        self,
        records: List[PerformanceRecord]
    ) -> List[Bottleneck]:
        """检查 CPU 饱和。"""
        threshold = self.bottleneck_thresholds.get("cpu_saturation", 90.0)
        bottlenecks = []
        
        # 按操作分组
        operation_cpu: Dict[str, List[float]] = defaultdict(list)
        for record in records:
            operation_cpu[record.operation].append(record.cpu_usage)
        
        for op, cpu_values in operation_cpu.items():
            avg_cpu = sum(cpu_values) / len(cpu_values)
            max_cpu = max(cpu_values)
            
            if avg_cpu > threshold:
                impact = min(100, (avg_cpu / threshold) * 60)
                severity = "critical" if avg_cpu > 95 else "high"
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.CPU_BOUND,
                    operation=op,
                    description=f"操作 '{op}' CPU 使用率平均 {avg_cpu:.1f}%，可能成为瓶颈",
                    severity=severity,
                    impact_score=impact,
                    recommendation=f"考虑异步处理或优化计算密集型代码",
                    metrics={
                        "avg_cpu": avg_cpu,
                        "max_cpu": max_cpu,
                        "threshold": threshold,
                        "sample_count": len(cpu_values),
                    },
                ))
        
        return bottlenecks
    
    def _check_memory_issues(
        self,
        records: List[PerformanceRecord]
    ) -> List[Bottleneck]:
        """检查内存问题。"""
        threshold = self.bottleneck_thresholds.get("high_memory_growth", 50 * 1024 * 1024)
        bottlenecks = []
        
        # 按操作分组
        operation_memory: Dict[str, List[float]] = defaultdict(list)
        for record in records:
            operation_memory[record.operation].append(record.memory_usage)
        
        for op, memory_values in operation_memory.items():
            avg_memory = sum(memory_values) / len(memory_values)
            max_memory = max(memory_values)
            
            if avg_memory > threshold:
                impact = min(100, (avg_memory / threshold) * 40)
                severity = "high" if avg_memory > threshold * 2 else "medium"
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.MEMORY_BOUND,
                    operation=op,
                    description=f"操作 '{op}' 内存使用平均 {avg_memory / 1024 / 1024:.2f}MB",
                    severity=severity,
                    impact_score=impact,
                    recommendation=f"考虑优化内存使用，减少大对象创建或使用流式处理",
                    metrics={
                        "avg_memory_mb": avg_memory / 1024 / 1024,
                        "max_memory_mb": max_memory / 1024 / 1024,
                        "threshold_mb": threshold / 1024 / 1024,
                        "sample_count": len(memory_values),
                    },
                ))
        
        return bottlenecks
    
    def _check_io_intensive(
        self,
        records: List[PerformanceRecord]
    ) -> List[Bottleneck]:
        """检查 IO 密集操作。"""
        threshold = self.bottleneck_thresholds.get("io_heavy_threshold", 10 * 1024 * 1024)
        bottlenecks = []
        
        # 按操作分组
        operation_io: Dict[str, Dict[str, int]] = defaultdict(lambda: {"read": 0, "write": 0})
        for record in records:
            operation_io[record.operation]["read"] += record.io_read_bytes
            operation_io[record.operation]["write"] += record.io_write_bytes
        
        for op, io_stats in operation_io.items():
            total_io = io_stats["read"] + io_stats["write"]
            
            if total_io > threshold:
                impact = min(100, (total_io / threshold) * 50)
                severity = "high" if total_io > threshold * 3 else "medium"
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.IO_BOUND,
                    operation=op,
                    description=f"操作 '{op}' IO 使用量 {total_io / 1024 / 1024:.2f}MB",
                    severity=severity,
                    impact_score=impact,
                    recommendation=f"考虑使用缓存、批量 IO 或异步 IO 操作",
                    metrics={
                        "read_mb": io_stats["read"] / 1024 / 1024,
                        "write_mb": io_stats["write"] / 1024 / 1024,
                        "total_mb": total_io / 1024 / 1024,
                        "threshold_mb": threshold / 1024 / 1024,
                    },
                ))
        
        return bottlenecks
    
    def _check_resource_leaks(
        self,
        records: List[PerformanceRecord]
    ) -> List[Bottleneck]:
        """检查资源泄漏模式。"""
        bottlenecks = []
        
        # 按操作分组，检查内存增长趋势
        operation_records: Dict[str, List[PerformanceRecord]] = defaultdict(list)
        for record in records:
            operation_records[record.operation].append(record)
        
        for op, op_records in operation_records.items():
            if len(op_records) < 3:
                continue
            
            # 按时间排序
            op_records.sort(key=lambda r: r.timestamp)
            
            # 检查内存使用趋势
            memory_values = [r.memory_usage for r in op_records]
            
            # 简单线性回归检查趋势
            n = len(memory_values)
            x_mean = (n - 1) / 2
            y_mean = sum(memory_values) / n
            
            numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(memory_values))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                continue
            
            slope = numerator / denominator
            
            # 如果内存持续增长
            if slope > 1024 * 1024:  # 每次操作增长超过1MB
                impact = min(100, slope / (1024 * 1024) * 20)
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.RESOURCE_LEAK,
                    operation=op,
                    description=f"操作 '{op}' 显示内存持续增长趋势，可能存在资源泄漏",
                    severity="high",
                    impact_score=impact,
                    recommendation=f"检查 '{op}' 操作中的资源释放逻辑，确保正确关闭文件/连接",
                    metrics={
                        "memory_growth_slope_mb": slope / 1024 / 1024,
                        "sample_count": n,
                        "first_memory_mb": memory_values[0] / 1024 / 1024,
                        "last_memory_mb": memory_values[-1] / 1024 / 1024,
                    },
                ))
        
        return bottlenecks
    
    # ==================== 系统信息 ====================
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取当前系统信息。
        
        Returns:
            系统信息字典
        """
        process = psutil.Process()
        
        try:
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            num_threads = process.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            memory_info = None
            cpu_percent = 0
            num_threads = 0
        
        system_memory = psutil.virtual_memory()
        system_cpu = psutil.cpu_percent(interval=0.1)
        
        return {
            "pid": process.pid,
            "memory_mb": memory_info.rss / 1024 / 1024 if memory_info else 0,
            "memory_virtual_mb": memory_info.vms / 1024 / 1024 if memory_info else 0,
            "cpu_percent": cpu_percent,
            "threads": num_threads,
            "system_memory_percent": system_memory.percent,
            "system_memory_available_mb": system_memory.available / 1024 / 1024,
            "system_cpu_percent": system_cpu,
            "cpu_count": psutil.cpu_count(),
        }
    
    def get_operation_history(
        self,
        operation: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取特定操作的历史记录。
        
        Args:
            operation: 操作名称
            limit: 返回记录数限制
            
        Returns:
            历史记录列表
        """
        operation_records = [r for r in self.records if r.operation == operation]
        
        # 按时间降序排序
        operation_records.sort(key=lambda r: r.timestamp, reverse=True)
        
        # 限制结果
        operation_records = operation_records[:limit]
        
        return [r.to_dict() for r in operation_records]
    
    # ==================== 性能报告 ====================
    
    def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> PerformanceReport:
        """
        生成性能报告。
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            性能报告
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.now()
        
        # 获取性能摘要
        summary = self.get_summary(start_time, end_time)
        
        # 识别瓶颈
        bottlenecks = self.identify_bottlenecks(start_time, end_time)
        
        # 获取系统信息
        system_info = self.get_system_info()
        
        # 生成建议
        recommendations = self._generate_recommendations(summary, bottlenecks, system_info)
        
        report = PerformanceReport(
            report_id=f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=start_time,
            end_time=end_time,
            summary=summary,
            bottlenecks=bottlenecks,
            system_info=system_info,
            recommendations=recommendations,
        )
        
        logger.info(f"性能报告已生成: {report.report_id}")
        return report
    
    def _generate_recommendations(
        self,
        summary: PerformanceSummary,
        bottlenecks: List[Bottleneck],
        system_info: Dict[str, Any]
    ) -> List[str]:
        """生成优化建议。"""
        recommendations = []
        
        # 基于摘要的建议
        if summary.total_operations > 0:
            if summary.average_execution_time > 5:
                recommendations.append("平均执行时间较长，考虑优化关键路径")
            
            if summary.p95_execution_time > summary.average_execution_time * 2:
                recommendations.append("P95执行时间远高于平均值，存在长尾延迟问题")
        
        # 基于瓶颈的建议
        critical_bottlenecks = [b for b in bottlenecks if b.severity in ["critical", "high"]]
        if critical_bottlenecks:
            recommendations.append(f"发现 {len(critical_bottlenecks)} 个严重瓶颈，需要优先处理")
        
        for bottleneck in critical_bottlenecks[:3]:  # 只显示前3个
            recommendations.append(bottleneck.recommendation)
        
        # 基于系统信息的建议
        if system_info.get("system_memory_percent", 0) > 80:
            recommendations.append("系统内存使用率较高，考虑优化内存使用或增加资源")
        
        if system_info.get("system_cpu_percent", 0) > 80:
            recommendations.append("系统 CPU 使用率较高，考虑优化计算密集型任务")
        
        if not recommendations:
            recommendations.append("性能表现良好，继续保持")
        
        return recommendations
    
    # ==================== 数据管理 ====================
    
    def clear_history(self, older_than_days: Optional[int] = None):
        """
        清除性能历史。
        
        Args:
            older_than_days: 如果指定，只清除早于该天数的记录
        """
        if older_than_days is None:
            self.records.clear()
        else:
            cutoff = datetime.now() - timedelta(days=older_than_days)
            self.records = [r for r in self.records if r.timestamp > cutoff]
        
        logger.info(f"已清除性能历史（{older_than_days}天之前的记录）")
    
    def export_history(self, file_path: str):
        """
        导出性能历史到 JSON 文件。
        
        Args:
            file_path: 导出文件路径
        """
        data = [record.to_dict() for record in self.records]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"已导出 {len(self.records)} 条性能记录到 {file_path}")
    
    def import_history(self, file_path: str):
        """
        从 JSON 文件导入性能历史。
        
        Args:
            file_path: 导入文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for record in data:
            perf_record = PerformanceRecord(
                operation=record["operation"],
                execution_time=record["execution_time"],
                memory_usage=record["memory_usage"],
                cpu_usage=record["cpu_usage"],
                timestamp=datetime.fromisoformat(record["timestamp"]),
                agent_name=record.get("agent_name"),
                task_type=record.get("task_type"),
                metadata=record.get("metadata"),
                io_read_bytes=record.get("io_read_bytes", 0),
                io_write_bytes=record.get("io_write_bytes", 0),
            )
            self.records.append(perf_record)
        
        logger.info(f"已从 {file_path} 导入 {len(data)} 条性能记录")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取性能统计信息。
        
        Returns:
            统计信息字典
        """
        summary = self.get_summary()
        
        # 计算额外统计
        all_times = [r.execution_time for r in self.records]
        all_memory = [r.memory_usage for r in self.records]
        
        time_std = statistics.stdev(all_times) if len(all_times) > 1 else 0
        memory_std = statistics.stdev(all_memory) if len(all_memory) > 1 else 0
        
        return {
            "total_operations": summary.total_operations,
            "total_execution_time": summary.total_execution_time,
            "average_execution_time": summary.average_execution_time,
            "min_execution_time": summary.min_execution_time,
            "max_execution_time": summary.max_execution_time,
            "p95_execution_time": summary.p95_execution_time,
            "p99_execution_time": summary.p99_execution_time,
            "average_memory_usage_mb": summary.average_memory_usage / 1024 / 1024,
            "average_cpu_usage": summary.average_cpu_usage,
            "operations_tracked": list(summary.operation_stats.keys()),
            "execution_time_std": time_std,
            "memory_usage_std": memory_std,
            "unique_operations": len(summary.operation_stats),
        }
