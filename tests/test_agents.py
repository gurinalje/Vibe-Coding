"""
Agent Tests for AI Agent Benchmark system.

This module contains test cases for the agent components
including base agent, reviewer, developer, and critic.
"""

import asyncio
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.base_agent import BaseAgent, AgentState, AgentMessage, MessageQueue
from agents.reviewer_agent import ReviewerAgent
from agents.developer_agent import DeveloperAgent
from agents.critic_agent import CriticAgent
from agents.coordinator import AgentCoordinator


class TestMessageQueue:
    """Test cases for MessageQueue."""
    
    @pytest.mark.asyncio
    async def test_create_queue(self):
        """Test queue creation."""
        queue = MessageQueue()
        await queue.create_queue("agent1")
        assert "agent1" in queue._queues
    
    @pytest.mark.asyncio
    async def test_send_receive(self):
        """Test message sending and receiving."""
        queue = MessageQueue()
        await queue.create_queue("agent1")
        
        message = AgentMessage(
            sender="sender",
            receiver="agent1",
            content={"test": "data"}
        )
        
        success = await queue.send(message)
        assert success is True
        
        received = await queue.receive("agent1")
        assert received is not None
        assert received.content == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_receive_timeout(self):
        """Test receive timeout."""
        queue = MessageQueue()
        await queue.create_queue("agent1")
        
        received = await queue.receive("agent1", timeout=0.1)
        assert received is None


class TestAgentMessage:
    """Test cases for AgentMessage."""
    
    def test_message_creation(self):
        """Test message creation."""
        message = AgentMessage(
            sender="sender",
            receiver="receiver",
            content={"key": "value"}
        )
        
        assert message.sender == "sender"
        assert message.receiver == "receiver"
        assert message.content == {"key": "value"}
        assert message.id is not None
    
    def test_message_to_dict(self):
        """Test message serialization."""
        message = AgentMessage(
            sender="sender",
            receiver="receiver",
            content={"key": "value"}
        )
        
        data = message.to_dict()
        assert data["sender"] == "sender"
        assert data["receiver"] == "receiver"
        assert data["content"] == {"key": "value"}
    
    def test_message_from_dict(self):
        """Test message deserialization."""
        data = {
            "id": "test-id",
            "sender": "sender",
            "receiver": "receiver",
            "content": {"key": "value"},
            "timestamp": "2024-01-01T00:00:00",
            "message_type": "test",
            "priority": 0,
            "requires_response": False,
            "response_timeout": 30.0
        }
        
        message = AgentMessage.from_dict(data)
        assert message.id == "test-id"
        assert message.sender == "sender"
        assert message.receiver == "receiver"


class TestReviewerAgent:
    """Test cases for ReviewerAgent."""
    
    @pytest.mark.asyncio
    async def test_reviewer_initialization(self):
        """Test reviewer initialization."""
        agent = ReviewerAgent(name="test_reviewer")
        assert agent.name == "test_reviewer"
        assert agent.agent_type == "reviewer"
    
    @pytest.mark.asyncio
    async def test_review_python_code(self):
        """Test Python code review."""
        agent = ReviewerAgent(name="test_reviewer")
        
        code = '''
def calculate_sum(a, b):
    """Calculate sum."""
    return a + b
'''
        
        result = await agent.process({
            "code": code,
            "language": "python"
        })
        
        assert "score" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)
    
    @pytest.mark.asyncio
    async def test_review_java_code(self):
        """Test Java code review."""
        agent = ReviewerAgent(name="test_reviewer")
        
        code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
'''
        
        result = await agent.process({
            "code": code,
            "language": "java"
        })
        
        assert "score" in result
        assert "issues" in result


class TestDeveloperAgent:
    """Test cases for DeveloperAgent."""
    
    @pytest.mark.asyncio
    async def test_developer_initialization(self):
        """Test developer initialization."""
        agent = DeveloperAgent(name="test_developer")
        assert agent.name == "test_developer"
        assert agent.agent_type == "developer"
    
    @pytest.mark.asyncio
    async def test_refactor_code(self):
        """Test code refactoring."""
        agent = DeveloperAgent(name="test_developer")
        
        code = '''
def build_string(items):
    result = ""
    for item in items:
        result += str(item) + ", "
    return result.rstrip(", ")
'''
        
        result = await agent.process({
            "code": code,
            "language": "python"
        })
        
        assert "success" in result
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)


class TestCriticAgent:
    """Test cases for CriticAgent."""
    
    @pytest.mark.asyncio
    async def test_critic_initialization(self):
        """Test critic initialization."""
        agent = CriticAgent(name="test_critic")
        assert agent.name == "test_critic"
        assert agent.agent_type == "critic"
    
    @pytest.mark.asyncio
    async def test_criticize_code(self):
        """Test code criticism."""
        agent = CriticAgent(name="test_critic")
        
        code = '''
import os

def run_command(cmd):
    os.system(cmd)

def get_user_input():
    return eval(input("Enter: "))
'''
        
        result = await agent.process({
            "code": code,
            "language": "python"
        })
        
        assert "criticisms" in result
        assert "score" in result
        assert isinstance(result["criticisms"], list)


class TestAgentCoordinator:
    """Test cases for AgentCoordinator."""
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        coordinator = AgentCoordinator()
        assert len(coordinator.agents) == 3
        assert "reviewer" in coordinator.agents
        assert "developer" in coordinator.agents
        assert "critic" in coordinator.agents
    
    @pytest.mark.asyncio
    async def test_review_code(self):
        """Test code review through coordinator."""
        coordinator = AgentCoordinator()
        
        code = '''
def add(a, b):
    return a + b
'''
        
        result = await coordinator.review_code(
            code=code,
            language="python"
        )
        
        assert "score" in result
        assert "issues" in result
    
    @pytest.mark.asyncio
    async def test_refactor_code(self):
        """Test code refactoring through coordinator."""
        coordinator = AgentCoordinator()
        
        code = '''
def process(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
'''
        
        result = await coordinator.refactor_code(
            code=code,
            language="python"
        )
        
        assert "suggestions" in result
    
    @pytest.mark.asyncio
    async def test_full_analysis(self):
        """Test full analysis through coordinator."""
        coordinator = AgentCoordinator()
        
        code = '''
def calculate(x, y):
    return x / y
'''
        
        result = await coordinator.full_analysis(
            code=code,
            language="python"
        )
        
        assert "review_result" in result
        assert "refactoring_result" in result
        assert "criticism_result" in result
        assert "overall_score" in result
    
    def test_statistics(self):
        """Test statistics collection."""
        coordinator = AgentCoordinator()
        
        stats = coordinator.get_statistics()
        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "agents" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])