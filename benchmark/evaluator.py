"""
Benchmark Evaluator for AI Agent Benchmark system.

This module provides the evaluation framework for benchmarking
AI code review capabilities and measuring performance.

功能：
- 执行基准测试用例
- 收集评估指标
- 生成评估报告
- 比较不同配置效果
"""

import time
import json
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Callable, Awaitable
import logging
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .metrics import MetricsCalculator

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """基准测试用例。
    
    属性：
        id: 测试用例唯一标识
        name: 测试用例名称
        description: 测试用例描述
        language: 代码语言
        code: 待测试的代码
        expected_issues: 期望发现的问题列表
        expected_score: 期望的评分
        tags: 标签列表
        difficulty: 难度级别 (easy, medium, hard)
        metadata: 额外元数据
    """
    id: str
    name: str
    description: str
    language: str
    code: str
    expected_issues: List[Dict[str, Any]]
    expected_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    difficulty: str = "medium"
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "code": self.code,
            "expected_issues": self.expected_issues,
            "expected_score": self.expected_score,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "metadata": self.metadata,
        }


@dataclass
class BenchmarkResult:
    """基准测试结果。
    
    属性：
        test_case_id: 测试用例ID
        agent_results: Agent返回的结果
        metrics: 计算得到的指标
        execution_time: 执行时间（秒）
        timestamp: 时间戳
        agent_name: Agent名称
        config_name: 配置名称
        error: 错误信息（如果有）
    """
    test_case_id: str
    agent_results: Dict[str, Any]
    metrics: Dict[str, Any]
    execution_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_name: Optional[str] = None
    config_name: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "test_case_id": self.test_case_id,
            "agent_results": self.agent_results,
            "metrics": self.metrics,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "config_name": self.config_name,
            "error": self.error,
        }


@dataclass
class EvaluationReport:
    """完整评估报告。
    
    属性：
        benchmark_name: 基准测试名称
        total_test_cases: 总测试用例数
        completed_cases: 完成的测试用例数
        results: 测试结果列表
        overall_metrics: 整体指标
        summary: 评估摘要
        recommendations: 建议列表
        execution_time: 总执行时间
        timestamp: 时间戳
        config_name: 配置名称
        comparison_results: 配置比较结果
    """
    benchmark_name: str
    total_test_cases: int
    completed_cases: int
    results: List[BenchmarkResult]
    overall_metrics: Dict[str, Any]
    summary: str
    recommendations: List[str]
    execution_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    config_name: Optional[str] = None
    comparison_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "benchmark_name": self.benchmark_name,
            "total_test_cases": self.total_test_cases,
            "completed_cases": self.completed_cases,
            "results": [r.to_dict() for r in self.results],
            "overall_metrics": self.overall_metrics,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
            "config_name": self.config_name,
            "comparison_results": self.comparison_results,
        }
    
    def save(self, file_path: str):
        """保存报告到文件。"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"报告已保存到 {file_path}")


@dataclass
class ComparisonResult:
    """配置比较结果。
    
    属性：
        config_a: 配置A的名称
        config_b: 配置B的名称
        metrics_a: 配置A的指标
        metrics_b: 配置B的指标
        winner: 胜出的配置
        difference: 指标差异
        improvement: 改进百分比
    """
    config_a: str
    config_b: str
    metrics_a: Dict[str, float]
    metrics_b: Dict[str, float]
    winner: str
    difference: Dict[str, float]
    improvement: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "config_a": self.config_a,
            "config_b": self.config_b,
            "metrics_a": self.metrics_a,
            "metrics_b": self.metrics_b,
            "winner": self.winner,
            "difference": self.difference,
            "improvement": self.improvement,
        }


class BenchmarkEvaluator:
    """基准测试评估器。
    
    用于评估AI代码审查能力的基准测试框架。
    支持异步执行、配置比较和详细报告生成。
    
    使用示例：
        ```python
        evaluator = BenchmarkEvaluator()
        evaluator.load_test_cases("test_cases.json")
        report = await evaluator.evaluate(agent, benchmark_name="代码审查基准测试")
        report.save("report.json")
        ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化基准测试评估器。
        
        Args:
            config: 配置字典，可包含：
                - max_concurrent: 最大并发数（默认5）
                - timeout: 超时时间（秒，默认30）
                - retry_count: 重试次数（默认2）
                - output_dir: 输出目录（默认 benchmark/results）
        """
        self.config = config or {}
        self.metrics_calculator = MetricsCalculator()
        self.test_cases: List[TestCase] = []
        
        # 配置参数
        self.max_concurrent = self.config.get("max_concurrent", 5)
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 2)
        self.output_dir = self.config.get("output_dir", "benchmark/results")
        
        logger.info("基准测试评估器已初始化")
    
    def load_test_cases(self, file_path: str) -> int:
        """从文件加载测试用例。
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            加载的测试用例数量
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        loaded_count = 0
        for case_data in data.get('test_cases', []):
            try:
                test_case = TestCase(**case_data)
                self.test_cases.append(test_case)
                loaded_count += 1
            except Exception as e:
                logger.warning(f"跳过无效测试用例: {e}")
        
        logger.info(f"已加载 {loaded_count} 个测试用例")
        return loaded_count
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例。
        
        Args:
            test_case: 测试用例对象
        """
        self.test_cases.append(test_case)
        logger.debug(f"添加测试用例: {test_case.name}")
    
    def add_test_cases(self, test_cases: List[TestCase]):
        """批量添加测试用例。
        
        Args:
            test_cases: 测试用例列表
        """
        self.test_cases.extend(test_cases)
        logger.debug(f"批量添加 {len(test_cases)} 个测试用例")
    
    async def evaluate(
        self,
        agent,
        test_cases: Optional[List[TestCase]] = None,
        benchmark_name: str = "基准测试",
        config_name: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> EvaluationReport:
        """
        执行基准测试评估。
        
        Args:
            agent: 要评估的Agent或协调器
            test_cases: 要使用的测试用例（如果为None则使用已加载的测试用例）
            benchmark_name: 基准测试名称
            config_name: 配置名称（用于比较不同配置）
            progress_callback: 进度回调函数，接收(当前进度, 总数)
            
        Returns:
            评估报告
            
        Raises:
            ValueError: 没有可用的测试用例
        """
        if test_cases is None:
            test_cases = self.test_cases
        
        if not test_cases:
            raise ValueError("没有可用的测试用例")
        
        logger.info(f"开始基准测试评估: {benchmark_name}，共 {len(test_cases)} 个测试用例")
        
        results = []
        start_time = time.time()
        
        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def run_with_semaphore(idx: int, test_case: TestCase) -> BenchmarkResult:
            async with semaphore:
                result = await self._run_test_case_with_retry(agent, test_case)
                if progress_callback:
                    progress_callback(idx + 1, len(test_cases))
                return result
        
        # 并发执行所有测试用例
        tasks = [
            run_with_semaphore(i, tc)
            for i, tc in enumerate(test_cases)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"测试用例 {test_cases[i].id} 执行失败: {result}")
                final_results.append(BenchmarkResult(
                    test_case_id=test_cases[i].id,
                    agent_results={"error": str(result)},
                    metrics={"error": True},
                    execution_time=0.0,
                    config_name=config_name,
                    error=str(result),
                ))
            else:
                final_results.append(result)
        
        total_time = time.time() - start_time
        
        # 计算整体指标
        overall_metrics = self._calculate_overall_metrics(final_results)
        
        # 生成摘要
        summary = self._generate_summary(final_results, overall_metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(final_results, overall_metrics)
        
        report = EvaluationReport(
            benchmark_name=benchmark_name,
            total_test_cases=len(test_cases),
            completed_cases=len([r for r in final_results if not r.error]),
            results=final_results,
            overall_metrics=overall_metrics,
            summary=summary,
            recommendations=recommendations,
            execution_time=total_time,
            config_name=config_name,
        )
        
        logger.info(f"基准测试评估完成，耗时 {total_time:.2f}s")
        return report
    
    async def _run_test_case_with_retry(
        self,
        agent,
        test_case: TestCase
    ) -> BenchmarkResult:
        """带重试机制的测试用例执行。"""
        last_error = None
        
        for attempt in range(self.retry_count + 1):
            try:
                return await self._run_test_case(agent, test_case)
            except Exception as e:
                last_error = e
                if attempt < self.retry_count:
                    logger.warning(
                        f"测试用例 {test_case.id} 第 {attempt + 1} 次执行失败，"
                        f"将在 1 秒后重试: {e}"
                    )
                    await asyncio.sleep(1)
        
        # 所有重试都失败
        logger.error(f"测试用例 {test_case.id} 在 {self.retry_count + 1} 次尝试后仍然失败")
        return BenchmarkResult(
            test_case_id=test_case.id,
            agent_results={"error": str(last_error)},
            metrics={"error": True},
            execution_time=0.0,
            error=str(last_error),
        )
    
    async def _run_test_case(
        self,
        agent,
        test_case: TestCase
    ) -> BenchmarkResult:
        """运行单个测试用例。"""
        start_time = time.time()
        
        # 运行Agent
        task = {
            "code": test_case.code,
            "language": test_case.language,
            "test_case_id": test_case.id,
        }
        
        agent_result = await asyncio.wait_for(
            agent.review_code(
                code=test_case.code,
                language=test_case.language
            ),
            timeout=self.timeout
        )
        
        execution_time = time.time() - start_time
        
        # 计算指标
        metrics = self._calculate_test_metrics(test_case, agent_result)
        
        return BenchmarkResult(
            test_case_id=test_case.id,
            agent_results=agent_result,
            metrics=metrics,
            execution_time=execution_time,
        )
    
    def _calculate_test_metrics(
        self,
        test_case: TestCase,
        agent_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算单个测试用例的指标。"""
        # 从Agent结果中提取问题
        agent_issues = agent_result.get("issues", [])
        expected_issues = test_case.expected_issues
        
        # 计算精确率、召回率、F1
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        # 基于问题类型的简单匹配
        matched_expected = set()
        
        for agent_issue in agent_issues:
            agent_type = agent_issue.get("category", "")
            matched = False
            
            for i, expected in enumerate(expected_issues):
                if i not in matched_expected and expected.get("type") == agent_type:
                    true_positives += 1
                    matched_expected.add(i)
                    matched = True
                    break
            
            if not matched:
                false_positives += 1
        
        false_negatives = len(expected_issues) - len(matched_expected)
        
        # 计算指标
        precision = true_positives / max(1, true_positives + false_positives)
        recall = true_positives / max(1, true_positives + false_negatives)
        f1_score = 2 * precision * recall / max(0.001, precision + recall)
        
        # 评分比较
        agent_score = agent_result.get("score", 0)
        expected_score = test_case.expected_score
        score_difference = abs(agent_score - expected_score) if expected_score else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "agent_score": agent_score,
            "expected_score": expected_score,
            "score_difference": score_difference,
            "issues_found": len(agent_issues),
            "issues_expected": len(expected_issues),
        }
    
    def _calculate_overall_metrics(
        self,
        results: List[BenchmarkResult]
    ) -> Dict[str, Any]:
        """计算所有测试用例的整体指标。"""
        if not results:
            return {}
        
        # 聚合指标
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        total_execution_time = 0
        
        valid_results = [r for r in results if not r.error]
        
        for result in valid_results:
            metrics = result.metrics
            total_precision += metrics.get("precision", 0)
            total_recall += metrics.get("recall", 0)
            total_f1 += metrics.get("f1_score", 0)
            total_execution_time += result.execution_time
        
        count = max(1, len(valid_results))
        
        # 计算平均值
        avg_precision = total_precision / count
        avg_recall = total_recall / count
        avg_f1 = total_f1 / count
        
        # 计算准确率（基于评分比较）
        score_differences = [r.metrics.get("score_difference", 0) for r in valid_results]
        avg_score_difference = sum(score_differences) / max(1, len(score_differences))
        accuracy = max(0, 100 - avg_score_difference)
        
        return {
            "total_test_cases": len(results),
            "successful_cases": len(valid_results),
            "failed_cases": len(results) - len(valid_results),
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "average_f1_score": avg_f1,
            "accuracy": accuracy,
            "average_execution_time": total_execution_time / max(1, len(results)),
            "total_execution_time": total_execution_time,
        }
    
    def _generate_summary(
        self,
        results: List[BenchmarkResult],
        overall_metrics: Dict[str, Any]
    ) -> str:
        """生成评估摘要。"""
        successful = overall_metrics.get("successful_cases", 0)
        total = overall_metrics.get("total_test_cases", 0)
        avg_f1 = overall_metrics.get("average_f1_score", 0)
        accuracy = overall_metrics.get("accuracy", 0)
        
        summary = f"基准测试完成。"
        summary += f"成功执行 {successful}/{total} 个测试用例。"
        summary += f"平均 F1 分数: {avg_f1:.3f}。"
        summary += f"准确率: {accuracy:.1f}%。"
        
        return summary
    
    def _generate_recommendations(
        self,
        results: List[BenchmarkResult],
        overall_metrics: Dict[str, Any]
    ) -> List[str]:
        """基于结果生成建议。"""
        recommendations = []
        
        avg_f1 = overall_metrics.get("average_f1_score", 0)
        avg_precision = overall_metrics.get("average_precision", 0)
        avg_recall = overall_metrics.get("average_recall", 0)
        
        if avg_f1 < 0.5:
            recommendations.append("F1 分数较低，需要平衡精确率和召回率")
        
        if avg_precision < 0.6:
            recommendations.append("精确率较低，需要减少误报")
        
        if avg_recall < 0.6:
            recommendations.append("召回率较低，需要发现更多问题")
        
        # 检查失败的测试用例
        failed = overall_metrics.get("failed_cases", 0)
        if failed > 0:
            recommendations.append(f"有 {failed} 个测试用例执行失败，需要检查错误原因")
        
        # 检查执行时间
        avg_time = overall_metrics.get("average_execution_time", 0)
        if avg_time > 10:
            recommendations.append("执行时间较长，考虑优化性能")
        
        return recommendations
    
    def compare_configs(
        self,
        reports: List[EvaluationReport]
    ) -> ComparisonResult:
        """比较不同配置的评估结果。
        
        Args:
            reports: 评估报告列表（每个报告对应一个配置）
            
        Returns:
            配置比较结果
            
        Raises:
            ValueError: 需要至少两个报告进行比较
        """
        if len(reports) < 2:
            raise ValueError("需要至少两个报告进行配置比较")
        
        # 取前两个报告进行比较
        report_a = reports[0]
        report_b = reports[1]
        
        config_a_name = report_a.config_name or "配置A"
        config_b_name = report_b.config_name or "配置B"
        
        metrics_a = {
            "precision": report_a.overall_metrics.get("average_precision", 0),
            "recall": report_a.overall_metrics.get("average_recall", 0),
            "f1_score": report_a.overall_metrics.get("average_f1_score", 0),
            "accuracy": report_a.overall_metrics.get("accuracy", 0),
            "execution_time": report_a.overall_metrics.get("average_execution_time", 0),
        }
        
        metrics_b = {
            "precision": report_b.overall_metrics.get("average_precision", 0),
            "recall": report_b.overall_metrics.get("average_recall", 0),
            "f1_score": report_b.overall_metrics.get("average_f1_score", 0),
            "accuracy": report_b.overall_metrics.get("accuracy", 0),
            "execution_time": report_b.overall_metrics.get("average_execution_time", 0),
        }
        
        # 计算差异和改进
        difference = {}
        improvement = {}
        
        for metric in ["precision", "recall", "f1_score", "accuracy"]:
            diff = metrics_b[metric] - metrics_a[metric]
            difference[metric] = diff
            if metrics_a[metric] > 0:
                improvement[metric] = (diff / metrics_a[metric]) * 100
            else:
                improvement[metric] = 0
        
        # 对于执行时间，越小越好
        time_diff = metrics_a["execution_time"] - metrics_b["execution_time"]
        difference["execution_time"] = time_diff
        if metrics_a["execution_time"] > 0:
            improvement["execution_time"] = (time_diff / metrics_a["execution_time"]) * 100
        else:
            improvement["execution_time"] = 0
        
        # 确定胜者（基于F1分数）
        if metrics_b["f1_score"] > metrics_a["f1_score"]:
            winner = config_b_name
        elif metrics_a["f1_score"] > metrics_b["f1_score"]:
            winner = config_a_name
        else:
            # F1相同时比较准确率
            if metrics_b["accuracy"] > metrics_a["accuracy"]:
                winner = config_b_name
            else:
                winner = config_a_name
        
        comparison = ComparisonResult(
            config_a=config_a_name,
            config_b=config_b_name,
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            winner=winner,
            difference=difference,
            improvement=improvement,
        )
        
        logger.info(f"配置比较完成: 胜出者 = {winner}")
        return comparison
    
    def save_results(
        self,
        report: EvaluationReport,
        output_dir: Optional[str] = None
    ) -> str:
        """保存基准测试结果。
        
        Args:
            report: 评估报告
            output_dir: 输出目录（如果为None则使用默认目录）
            
        Returns:
            保存的文件路径
        """
        output_path = Path(output_dir or self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_suffix = f"_{report.config_name}" if report.config_name else ""
        filename = f"benchmark_report{config_suffix}_{timestamp}.json"
        file_path = output_path / filename
        
        report.save(str(file_path))
        
        # 同时保存摘要文件
        summary_path = output_path / "latest_summary.json"
        summary_data = {
            "benchmark_name": report.benchmark_name,
            "config_name": report.config_name,
            "timestamp": report.timestamp,
            "overall_metrics": report.overall_metrics,
            "summary": report.summary,
            "recommendations": report.recommendations,
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"结果已保存到 {output_path}")
        return str(file_path)
    
    def save_comparison(
        self,
        comparison: ComparisonResult,
        output_dir: Optional[str] = None
    ) -> str:
        """保存配置比较结果。
        
        Args:
            comparison: 比较结果
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        output_path = Path(output_dir or self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{comparison.config_a}_vs_{comparison.config_b}_{timestamp}.json"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(comparison.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"比较结果已保存到 {file_path}")
        return str(file_path)
