"""
LLM Utilities for AI Agent Benchmark system.

This module provides LLM-related utility functions including
prompt management, response parsing, and API interactions.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM configuration."""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None


@dataclass
class LLMResponse:
    """LLM response."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
        }


class LLMUtils:
    """LLM utility functions."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LLM utilities.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        logger.info("LLM utilities initialized")
    
    def create_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Create a prompt for LLM.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            context: Optional context
            examples: Optional examples
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        # Add system message
        messages.append({"role": "system", "content": system_prompt})
        
        # Add context if provided
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})
        
        # Add examples if provided
        if examples:
            for example in examples:
                messages.append({"role": "user", "content": example.get("input", "")})
                messages.append({"role": "assistant", "content": example.get("output", "")})
        
        # Add user message
        messages.append({"role": "user", "content": user_prompt})
        
        return messages
    
    def create_code_review_prompt(
        self,
        code: str,
        language: str,
        focus_areas: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Create a code review prompt.
        
        Args:
            code: Code to review
            language: Programming language
            focus areas: Optional focus areas
            
        Returns:
            List of message dictionaries
        """
        system_prompt = """You are an expert code reviewer. Your task is to review the provided code and identify:
1. Code quality issues
2. Security vulnerabilities
3. Performance problems
4. Best practice violations
5. Potential bugs

Please provide your review in a structured format with:
- Overall assessment
- Specific issues found (with line numbers if applicable)
- Severity level for each issue
- Suggestions for improvement
"""
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nFocus areas: {', '.join(focus_areas)}"
        
        user_prompt = f"""Please review the following {language} code:

```{language}
{code}
```
{focus_text}

Provide a detailed code review."""
        
        return self.create_prompt(system_prompt, user_prompt)
    
    def create_refactoring_prompt(
        self,
        code: str,
        language: str,
        refactoring_goals: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Create a refactoring prompt.
        
        Args:
            code: Code to refactor
            language: Programming language
            refactoring goals: Optional refactoring goals
            
        Returns:
            List of message dictionaries
        """
        system_prompt = """You are an expert software developer specializing in code refactoring. Your task is to:
1. Analyze the provided code
2. Identify refactoring opportunities
3. Apply appropriate refactoring techniques
4. Ensure the refactored code maintains functionality

Please provide:
- Analysis of current code issues
- Refactoring suggestions with rationale
- Refactored code
- Explanation of changes made
"""
        
        goals_text = ""
        if refactoring_goals:
            goals_text = f"\n\nRefactoring goals: {', '.join(refactoring_goals)}"
        
        user_prompt = f"""Please refactor the following {language} code:

```{language}
{code}
```
{goals_text}

Provide refactored code with explanations."""
        
        return self.create_prompt(system_prompt, user_prompt)
    
    def create_analysis_prompt(
        self,
        code: str,
        language: str,
        analysis_type: str = "comprehensive"
    ) -> List[Dict[str, str]]:
        """
        Create an analysis prompt.
        
        Args:
            code: Code to analyze
            language: Programming language
            analysis type: Type of analysis
            
        Returns:
            List of message dictionaries
        """
        system_prompt = f"""You are an expert code analyst specializing in {analysis_type} analysis. Your task is to:
1. Analyze the provided code thoroughly
2. Identify key characteristics and patterns
3. Provide detailed insights and metrics
4. Offer recommendations for improvement

Please provide your analysis in a structured format.
"""
        
        user_prompt = f"""Please perform {analysis_type} analysis on the following {language} code:

```{language}
{code}
```

Provide detailed analysis."""
        
        return self.create_prompt(system_prompt, user_prompt)
    
    def parse_json_response(
        self,
        response: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed JSON or None
        """
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON code block
        code_block_match = re.search(r'```(?:json)?\s*\n([\s\S]*?)\n```', response)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass
        
        logger.warning("Failed to parse JSON from response")
        return None
    
    def parse_list_response(
        self,
        response: str,
        item_pattern: Optional[str] = None
    ) -> List[str]:
        """
        Parse list from LLM response.
        
        Args:
            response: LLM response text
            item_pattern: Optional regex pattern for items
            
        Returns:
            List of items
        """
        if item_pattern:
            return re.findall(item_pattern, response)
        
        # Try to find numbered list
        items = re.findall(r'(?:^|\n)\s*(?:\d+[\.\)]\s*|\-\s*|\*\s*)(.+?)(?=\n|$)', response)
        
        if items:
            return [item.strip() for item in items]
        
        # Try to find bullet points
        items = re.findall(r'(?:^|\n)\s*[-*]\s+(.+?)(?=\n|$)', response)
        
        return [item.strip() for item in items] if items else [response]
    
    def extract_code_blocks(
        self,
        response: str,
        language: Optional[str] = None
    ) -> List[str]:
        """
        Extract code blocks from response.
        
        Args:
            response: LLM response text
            language: Optional language filter
            
        Returns:
            List of code blocks
        """
        if language:
            pattern = f'```{language}\\s*\\n([\\s\\S]*?)\\n```'
        else:
            pattern = r'```(?:\w+)?\s*\n([\s\S]*?)\n```'
        
        return re.findall(pattern, response)
    
    def calculate_tokens_estimate(
        self,
        text: str,
        model: str = "gpt-4"
    ) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            model: Model name
            
        Returns:
            Estimated token count
        """
        # Simple estimation based on word count
        # Actual tokenization depends on the tokenizer used
        words = len(text.split())
        chars = len(text)
        
        # Rough estimation
        if model.startswith("gpt-4"):
            # GPT-4 tokenizer is roughly 0.75 tokens per word
            return int(words * 0.75)
        else:
            # Other models
            return int(words * 0.75)
    
    def truncate_text(
        self,
        text: str,
        max_tokens: int,
        model: str = "gpt-4"
    ) -> str:
        """
        Truncate text to fit within token limit.
        
        Args:
            text: Input text
            max_tokens: Maximum tokens
            model: Model name
            
        Returns:
            Truncated text
        """
        estimated_tokens = self.calculate_tokens_estimate(text, model)
        
        if estimated_tokens <= max_tokens:
            return text
        
        # Calculate approximate character limit
        # Assuming average 4 characters per token
        char_limit = max_tokens * 4
        
        if len(text) <= char_limit:
            return text
        
        # Truncate and add indicator
        return text[:char_limit] + "\n... [truncated]"
    
    def format_code_for_prompt(
        self,
        code: str,
        language: str,
        max_lines: int = 100
    ) -> str:
        """
        Format code for LLM prompt.
        
        Args:
            code: Code to format
            language: Programming language
            max_lines: Maximum lines to include
            
        Returns:
            Formatted code
        """
        lines = code.split('\n')
        
        if len(lines) > max_lines:
            # Include first and last lines with indicator
            half = max_lines // 2
            formatted = '\n'.join(lines[:half])
            formatted += f"\n\n... [{len(lines) - max_lines} lines omitted] ...\n\n"
            formatted += '\n'.join(lines[-half:])
        else:
            formatted = code
        
        return f"```{language}\n{formatted}\n```"
    
    def create_multi_turn_prompt(
        self,
        system_prompt: str,
        conversation: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Create multi-turn conversation prompt.
        
        Args:
            system_prompt: System prompt
            conversation: List of user/assistant messages
            
        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        for turn in conversation:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            messages.append({"role": role, "content": content})
        
        return messages