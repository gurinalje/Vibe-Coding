"""
LLM-Powered Deep Code Analyzer.

Uses OpenAI or Anthropic APIs for deep semantic code analysis.
"""

import asyncio
import json
import os
import re
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMAnalysisResult:
    """Result from LLM-powered analysis."""
    bugs: List[Dict[str, Any]] = field(default_factory=list)
    architecture_notes: List[str] = field(default_factory=list)
    explanations: List[Dict[str, str]] = field(default_factory=list)
    fixes: List[Dict[str, Any]] = field(default_factory=list)
    overall_assessment: str = ""
    confidence: float = 0.0
    tokens_used: int = 0
    model: str = ""
    latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bugs": self.bugs, "architecture_notes": self.architecture_notes,
            "explanations": self.explanations, "fixes": self.fixes,
            "overall_assessment": self.overall_assessment, "confidence": self.confidence,
            "tokens_used": self.tokens_used, "model": self.model, "latency_ms": self.latency_ms,
        }


class LLMAnalyzer:
    """LLM-powered deep code analyzer."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.provider = self.config.get("provider", os.getenv("LLM_PROVIDER", "openai"))
        self.model = self.config.get("model", os.getenv("LLM_MODEL", "gpt-4"))
        self.api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.temperature = self.config.get("temperature", 0.3)
        self.max_tokens = self.config.get("max_tokens", 4096)

    async def analyze(self, code: str, language: str, context: Optional[str] = None) -> LLMAnalysisResult:
        """Perform deep LLM-powered analysis."""
        start_time = time.time()
        if not self.api_key:
            logger.warning("No API key configured. Using rule-based fallback.")
            return self._fallback_analysis(code, language)
        try:
            if self.provider == "openai":
                result = await self._analyze_openai(code, language, context)
            elif self.provider == "anthropic":
                result = await self._analyze_anthropic(code, language, context)
            else:
                result = self._fallback_analysis(code, language)
            result.latency_ms = (time.time() - start_time) * 1000
            return result
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_analysis(code, language)

    async def _analyze_openai(self, code: str, language: str, context: Optional[str]) -> LLMAnalysisResult:
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key)
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_analysis_prompt(code, language, context)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            return self._parse_response(content, tokens)
        except ImportError:
            logger.warning("openai package not installed")
            return self._fallback_analysis(code, language)

    async def _analyze_anthropic(self, code: str, language: str, context: Optional[str]) -> LLMAnalysisResult:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_analysis_prompt(code, language, context)
            response = await client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens
            return self._parse_response(content, tokens)
        except ImportError:
            logger.warning("anthropic package not installed")
            return self._fallback_analysis(code, language)

    def _build_system_prompt(self) -> str:
        return """You are an expert code reviewer. Analyze the code and return JSON with:
{
    "bugs": [{"severity": "...", "description": "...", "line": N, "fix": "..."}],
    "architecture_notes": ["..."],
    "explanations": [{"topic": "...", "explanation": "..."}],
    "fixes": [{"issue": "...", "original": "...", "fixed": "...", "explanation": "..."}],
    "overall_assessment": "...",
    "confidence": 0.0-1.0
}"""

    def _build_analysis_prompt(self, code: str, language: str, context: Optional[str]) -> str:
        prompt = f"Analyze this {language} code:\n\n`{language}\n{code}\n`"
        if context:
            prompt += f"\n\nContext: {context}"
        return prompt

    def _parse_response(self, content: str, tokens: int) -> LLMAnalysisResult:
        try:
            data = json.loads(content)
            return LLMAnalysisResult(
                bugs=data.get("bugs", []),
                architecture_notes=data.get("architecture_notes", []),
                explanations=data.get("explanations", []),
                fixes=data.get("fixes", []),
                overall_assessment=data.get("overall_assessment", ""),
                confidence=data.get("confidence", 0.8),
                tokens_used=tokens,
                model=self.model,
            )
        except json.JSONDecodeError:
            return LLMAnalysisResult(
                overall_assessment=content[:500],
                tokens_used=tokens,
                model=self.model,
            )

    def _fallback_analysis(self, code: str, language: str) -> LLMAnalysisResult:
        """Rule-based fallback when LLM is not available."""
        bugs = []
        patterns = {
            "python": [
                (r"except\s*:", "Bare except clause", "warning"),
                (r"eval\s*\(", "eval() is a security risk", "critical"),
                (r"exec\s*\(", "exec() is a security risk", "critical"),
                (r"password\s*=\s*[\x22\x27][^\x22\x27]+[\x22\x27]", "Hardcoded password", "critical"),
                (r"pickle\.loads", "Unsafe deserialization", "error"),
                (r"subprocess\.call\(.*shell\s*=\s*True", "Shell injection risk", "critical"),
            ],
            "java": [
                (r"System\.out\.print", "Debug print statement", "warning"),
                (r"catch\s*\(\s*Exception\s+", "Catching generic Exception", "warning"),
                (r"password\s*=\s*\"[^\"]+\"", "Hardcoded password", "critical"),
            ],
            "javascript": [
                (r"eval\s*\(", "eval() is a security risk", "critical"),
                (r"innerHTML", "Potential XSS vulnerability", "error"),
                (r"console\.log", "Debug log statement", "warning"),
            ],
        }

        lang_patterns = patterns.get(language, [])
        lines = code.split("\n")
        for pattern, message, severity in lang_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    bugs.append({"severity": severity, "description": message, "line": i, "fix": f"Review line {i}"})

        return LLMAnalysisResult(
            bugs=bugs,
            overall_assessment=f"Rule-based analysis found {len(bugs)} potential issues.",
            confidence=0.6,
            model="rule-based-fallback",
        )
