"""
Base Agent class for AI Agent Benchmark system.

This module provides the foundational interface and lifecycle management
for all agents in the multi-agent collaborative system.
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent states."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class AgentMessage:
    """Message for inter-agent communication."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "general"
    priority: int = 0
    requires_response: bool = False
    response_timeout: float = 30.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "priority": self.priority,
            "requires_response": self.requires_response,
            "response_timeout": self.response_timeout,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            content=data.get("content", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            message_type=data.get("message_type", "general"),
            priority=data.get("priority", 0),
            requires_response=data.get("requires_response", False),
            response_timeout=data.get("response_timeout", 30.0),
        )


class MessageQueue:
    """Simple message queue for agent communication."""
    
    def __init__(self):
        """Initialize message queue."""
        self._queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
    
    async def create_queue(self, agent_id: str) -> asyncio.Queue:
        """Create a queue for an agent."""
        async with self._lock:
            if agent_id not in self._queues:
                self._queues[agent_id] = asyncio.Queue()
            return self._queues[agent_id]
    
    async def send(self, message: AgentMessage) -> bool:
        """Send a message to an agent's queue."""
        async with self._lock:
            if message.receiver in self._queues:
                await self._queues[message.receiver].put(message)
                logger.debug(f"Message sent from {message.sender} to {message.receiver}")
                return True
            else:
                logger.warning(f"Agent {message.receiver} not found in message queue")
                return False
    
    async def receive(self, agent_id: str, timeout: float = 1.0) -> Optional[AgentMessage]:
        """Receive a message from an agent's queue."""
        if agent_id not in self._queues:
            return None
        
        try:
            return await asyncio.wait_for(self._queues[agent_id].get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    async def get_queue_size(self, agent_id: str) -> int:
        """Get the size of an agent's queue."""
        if agent_id in self._queues:
            return self._queues[agent_id].qsize()
        return 0


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        name: str,
        agent_type: str = "base",
        message_queue: Optional[MessageQueue] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            agent_type: Type of agent
            message_queue: Shared message queue
            config: Agent configuration
        """
        self.name = name
        self.agent_type = agent_type
        self.id = f"{agent_type}_{name}_{uuid.uuid4().hex[:8]}"
        self.state = AgentState.IDLE
        self.message_queue = message_queue or MessageQueue()
        self.config = config or {}
        
        # Statistics
        self.tasks_processed = 0
        self.errors_encountered = 0
        self.total_processing_time = 0.0
        self.start_time: Optional[datetime] = None
        
        # Message history
        self.message_history: List[AgentMessage] = []
        
        logger.info(f"Agent {self.name} (ID: {self.id}) initialized")
    
    async def initialize(self):
        """Initialize agent (can be overridden by subclasses)."""
        self.start_time = datetime.now()
        await self.message_queue.create_queue(self.id)
        logger.info(f"Agent {self.name} initialized and ready")
    
    async def shutdown(self):
        """Shutdown agent."""
        self.state = AgentState.SHUTDOWN
        logger.info(f"Agent {self.name} shutdown")
    
    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task.
        
        Args:
            task: Task data
            
        Returns:
            Processing result
        """
        pass
    
    async def send_message(
        self,
        receiver: str,
        content: Dict[str, Any],
        message_type: str = "general",
        priority: int = 0,
        requires_response: bool = False,
        response_timeout: float = 30.0
    ) -> bool:
        """
        Send a message to another agent.
        
        Args:
            receiver: Receiver agent name or ID
            content: Message content
            message_type: Type of message
            priority: Message priority
            requires_response: Whether response is required
            response_timeout: Timeout for response
            
        Returns:
            True if message sent successfully
        """
        message = AgentMessage(
            sender=self.id,
            receiver=receiver,
            content=content,
            message_type=message_type,
            priority=priority,
            requires_response=requires_response,
            response_timeout=response_timeout,
        )
        
        success = await self.message_queue.send(message)
        if success:
            self.message_history.append(message)
        
        return success
    
    async def receive_message(self, timeout: float = 1.0) -> Optional[AgentMessage]:
        """
        Receive a message from the queue.
        
        Args:
            timeout: Timeout for receiving
            
        Returns:
            Received message or None
        """
        return await self.message_queue.receive(self.id, timeout)
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle a received message.
        
        Args:
            message: Received message
            
        Returns:
            Response message if required
        """
        logger.debug(f"Agent {self.name} received message from {message.sender}")
        
        # Default handling - can be overridden by subclasses
        response_content = {"status": "received", "agent": self.name}
        
        if message.requires_response:
            response = AgentMessage(
                sender=self.id,
                receiver=message.sender,
                content=response_content,
                message_type="response",
            )
            return response
        
        return None
    
    async def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a task with lifecycle management.
        
        Args:
            task: Task data
            
        Returns:
            Task result
        """
        self.state = AgentState.PROCESSING
        start_time = time.time()
        
        try:
            logger.info(f"Agent {self.name} starting task")
            result = await self.process(task)
            
            # Update statistics
            self.tasks_processed += 1
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            self.state = AgentState.IDLE
            logger.info(f"Agent {self.name} completed task in {processing_time:.4f}s")
            
            return {
                "status": "success",
                "agent": self.name,
                "result": result,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            self.errors_encountered += 1
            self.state = AgentState.ERROR
            logger.error(f"Agent {self.name} error: {e}")
            
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        uptime = 0.0
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        avg_processing_time = 0.0
        if self.tasks_processed > 0:
            avg_processing_time = self.total_processing_time / self.tasks_processed
        
        return {
            "name": self.name,
            "id": self.id,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "tasks_processed": self.tasks_processed,
            "errors_encountered": self.errors_encountered,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": avg_processing_time,
            "uptime": uptime,
            "messages_sent": len(self.message_history),
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', state={self.state.value})"