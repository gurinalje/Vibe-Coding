"""
Agent Coordinator for AI Agent Benchmark system.

This module provides the coordination logic for multiple agents,
managing their communication, task distribution, and result aggregation.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
import logging
from dataclasses import dataclass, field
from enum import Enum

from .base_agent import BaseAgent, AgentState, AgentMessage, MessageQueue
from .reviewer_agent import ReviewerAgent
from .developer_agent import DeveloperAgent
from .critic_agent import CriticAgent

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of tasks."""
    REVIEW = "review"
    REFACTOR = "refactor"
    CRITICIZE = "criticize"
    FULL_ANALYSIS = "full_analysis"


class TaskStatus(str, Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task definition."""
    id: str
    type: TaskType
    data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "status": self.status.value,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.completed_at - self.started_at if self.completed_at and self.started_at else None,
        }


@dataclass
class AnalysisResult:
    """Combined analysis result."""
    task_id: str
    review_result: Optional[Dict[str, Any]] = None
    refactoring_result: Optional[Dict[str, Any]] = None
    criticism_result: Optional[Dict[str, Any]] = None
    overall_score: float = 0.0
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "task_id": self.task_id,
            "review_result": self.review_result,
            "refactoring_result": self.refactoring_result,
            "criticism_result": self.criticism_result,
            "overall_score": self.overall_score,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
        }


class AgentCoordinator:
    """Coordinator for managing multiple agents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent coordinator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize message queue
        self.message_queue = MessageQueue()
        
        # Initialize agents
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
        
        # Statistics
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        logger.info("Agent coordinator initialized")
    
    def _initialize_agents(self):
        """Initialize all agents."""
        # Create agents
        reviewer = ReviewerAgent(
            name="reviewer",
            message_queue=self.message_queue,
            config=self.config.get("reviewer", {})
        )
        
        developer = DeveloperAgent(
            name="developer",
            message_queue=self.message_queue,
            config=self.config.get("developer", {})
        )
        
        critic = CriticAgent(
            name="critic",
            message_queue=self.message_queue,
            config=self.config.get("critic", {})
        )
        
        # Register agents
        self.agents["reviewer"] = reviewer
        self.agents["developer"] = developer
        self.agents["critic"] = critic
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def initialize(self):
        """Initialize all agents."""
        for agent in self.agents.values():
            await agent.initialize()
        logger.info("All agents initialized")
    
    async def shutdown(self):
        """Shutdown all agents."""
        for agent in self.agents.values():
            await agent.shutdown()
        logger.info("All agents shutdown")
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        self.task_counter += 1
        return f"task_{self.task_counter}_{int(time.time())}"
    
    async def review_code(
        self,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review code using the reviewer agent.
        
        Args:
            code: Code to review
            language: Programming language
            file_path: Optional file path
            options: Additional options
            
        Returns:
            Review result
        """
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            type=TaskType.REVIEW,
            data={
                "code": code,
                "language": language,
                "file_path": file_path,
                "options": options or {},
            },
        )
        
        self.tasks[task_id] = task
        self.total_tasks += 1
        
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = time.time()
            task.assigned_agent = "reviewer"
            
            # Run review
            result = await self.agents["reviewer"].run_task(task.data)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            self.completed_tasks += 1
            
            logger.info(f"Review completed for task {task_id}")
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            self.failed_tasks += 1
            
            logger.error(f"Review failed for task {task_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def refactor_code(
        self,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        refactoring_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Refactor code using the developer agent.
        
        Args:
            code: Code to refactor
            language: Programming language
            file_path: Optional file path
            refactoring_type: Optional specific refactoring type
            options: Additional options
            
        Returns:
            Refactoring result
        """
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            type=TaskType.REFACTOR,
            data={
                "code": code,
                "language": language,
                "file_path": file_path,
                "refactoring_type": refactoring_type,
                "options": options or {},
            },
        )
        
        self.tasks[task_id] = task
        self.total_tasks += 1
        
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = time.time()
            task.assigned_agent = "developer"
            
            # Run refactoring
            result = await self.agents["developer"].run_task(task.data)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            self.completed_tasks += 1
            
            logger.info(f"Refactoring completed for task {task_id}")
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            self.failed_tasks += 1
            
            logger.error(f"Refactoring failed for task {task_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def criticize_code(
        self,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Criticize code using the critic agent.
        
        Args:
            code: Code to criticize
            language: Programming language
            file_path: Optional file path
            context: Additional context
            options: Additional options
            
        Returns:
            Criticism result
        """
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            type=TaskType.CRITICIZE,
            data={
                "code": code,
                "language": language,
                "file_path": file_path,
                "context": context or {},
                "options": options or {},
            },
        )
        
        self.tasks[task_id] = task
        self.total_tasks += 1
        
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = time.time()
            task.assigned_agent = "critic"
            
            # Run criticism
            result = await self.agents["critic"].run_task(task.data)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            self.completed_tasks += 1
            
            logger.info(f"Criticism completed for task {task_id}")
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            self.failed_tasks += 1
            
            logger.error(f"Criticism failed for task {task_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def full_analysis(
        self,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform full analysis using all agents.
        
        Args:
            code: Code to analyze
            language: Programming language
            file_path: Optional file path
            options: Additional options
            
        Returns:
            Combined analysis result
        """
        task_id = self._generate_task_id()
        
        logger.info(f"Starting full analysis for task {task_id}")
        
        # Run all analyses in parallel
        review_task = self.review_code(code, language, file_path, options)
        refactoring_task = self.refactor_code(code, language, file_path, options=options)
        criticism_task = self.criticize_code(code, language, file_path, options=options)
        
        # Wait for all tasks to complete
        review_result, refactoring_result, criticism_result = await asyncio.gather(
            review_task, refactoring_task, criticism_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(review_result, Exception):
            review_result = {"status": "error", "error": str(review_result)}
        if isinstance(refactoring_result, Exception):
            refactoring_result = {"status": "error", "error": str(refactoring_result)}
        if isinstance(criticism_result, Exception):
            criticism_result = {"status": "error", "error": str(criticism_result)}
        
        # Combine results
        combined_result = self._combine_results(
            task_id,
            review_result if isinstance(review_result, dict) else {"status": "error", "error": str(review_result)},
            refactoring_result if isinstance(refactoring_result, dict) else {"status": "error", "error": str(refactoring_result)},
            criticism_result if isinstance(criticism_result, dict) else {"status": "error", "error": str(criticism_result)}
        )
        
        logger.info(f"Full analysis completed for task {task_id}")
        return combined_result
    
    def _combine_results(
        self,
        task_id: str,
        review_result: Dict[str, Any],
        refactoring_result: Dict[str, Any],
        criticism_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine results from all agents.
        
        Args:
            task_id: Task ID
            review_result: Review result
            refactoring_result: Refactoring result
            criticism_result: Criticism result
            
        Returns:
            Combined result
        """
        # Extract scores
        review_score = review_result.get("score", 0) if review_result.get("status") == "success" else 0
        criticism_score = criticism_result.get("score", 0) if criticism_result.get("status") == "success" else 0
        
        # Calculate overall score (weighted average)
        overall_score = (review_score * 0.4 + criticism_score * 0.6)
        
        # Combine recommendations
        recommendations = []
        if review_result.get("status") == "success":
            recommendations.extend(review_result.get("recommendations", []))
        if criticism_result.get("status") == "success":
            recommendations.extend(criticism_result.get("recommendations", []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        # Generate summary
        summary = self._generate_summary(review_result, refactoring_result, criticism_result)
        
        # Combine metrics
        metrics = {
            "review_score": review_score,
            "criticism_score": criticism_score,
            "overall_score": overall_score,
            "review_issues": len(review_result.get("issues", [])) if review_result.get("status") == "success" else 0,
            "criticism_issues": len(criticism_result.get("criticisms", [])) if criticism_result.get("status") == "success" else 0,
            "refactoring_suggestions": len(refactoring_result.get("suggestions", [])) if refactoring_result.get("status") == "success" else 0,
        }
        
        return {
            "task_id": task_id,
            "review_result": review_result,
            "refactoring_result": refactoring_result,
            "criticism_result": criticism_result,
            "overall_score": overall_score,
            "summary": summary,
            "recommendations": unique_recommendations,
            "metrics": metrics,
        }
    
    def _generate_summary(
        self,
        review_result: Dict[str, Any],
        refactoring_result: Dict[str, Any],
        criticism_result: Dict[str, Any]
    ) -> str:
        """Generate summary from results."""
        summary_parts = []
        
        # Review summary
        if review_result.get("status") == "success":
            review_score = review_result.get("score", 0)
            issue_count = len(review_result.get("issues", []))
            summary_parts.append(f"代码审查: 评分 {review_score:.1f}/100, 发现 {issue_count} 个问题")
        
        # Refactoring summary
        if refactoring_result.get("status") == "success":
            suggestion_count = len(refactoring_result.get("suggestions", []))
            changes_made = len(refactoring_result.get("changes_made", []))
            summary_parts.append(f"代码重构: 提供 {suggestion_count} 个建议, 应用 {changes_made} 个变更")
        
        # Criticism summary
        if criticism_result.get("status") == "success":
            criticism_score = criticism_result.get("score", 0)
            criticism_count = len(criticism_result.get("criticisms", []))
            summary_parts.append(f"代码批评: 评分 {criticism_score:.1f}/100, 发现 {criticism_count} 个问题")
        
        if not summary_parts:
            return "分析未完成"
        
        return "。".join(summary_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        agent_stats = {}
        for name, agent in self.agents.items():
            agent_stats[name] = agent.get_statistics()
        
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": (self.completed_tasks / max(1, self.total_tasks)) * 100,
            "agents": agent_stats,
        }
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        return [task.to_dict() for task in self.tasks.values()]
    
    async def send_message(
        self,
        sender: str,
        receiver: str,
        content: Dict[str, Any],
        message_type: str = "general"
    ) -> bool:
        """
        Send a message between agents.
        
        Args:
            sender: Sender agent name
            receiver: Receiver agent name
            content: Message content
            message_type: Type of message
            
        Returns:
            True if message sent successfully
        """
        if sender not in self.agents:
            logger.error(f"Sender agent '{sender}' not found")
            return False
        
        if receiver not in self.agents:
            logger.error(f"Receiver agent '{receiver}' not found")
            return False
        
        message = AgentMessage(
            sender=self.agents[sender].id,
            receiver=self.agents[receiver].id,
            content=content,
            message_type=message_type,
        )
        
        return await self.message_queue.send(message)