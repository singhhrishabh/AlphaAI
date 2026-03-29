from __future__ import annotations
"""
AlphaAI — Base Agent
Abstract base class for all AI analysis agents with LLM integration.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("alphaai.agents")


# ─── Agent Output Models ──────────────────────────────────────

class AgentSignal(BaseModel):
    """Standardized output from any analysis agent."""
    agent_name: str
    symbol: str
    signal: str = Field(description="BUY, SELL, or HOLD")
    confidence: float = Field(ge=0, le=100, description="Confidence score 0-100")
    score: float = Field(ge=-100, le=100, description="Analysis score -100 (very bearish) to 100 (very bullish)")
    reasoning: str = Field(description="Detailed analysis reasoning")
    key_metrics: dict = Field(default_factory=dict, description="Key metrics used in analysis")
    risks: list[str] = Field(default_factory=list, description="Identified risk factors")
    catalysts: list[str] = Field(default_factory=list, description="Positive catalysts identified")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ─── LLM Factory ─────────────────────────────────────────────

def create_llm(config):
    """Create an LLM instance based on the configuration."""
    provider = config.llm.provider.lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.llm.openai_model,
            api_key=config.llm.openai_api_key,
            temperature=0.1,
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=config.llm.gemini_model,
            google_api_key=config.llm.google_api_key,
            temperature=0.1,
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=config.llm.groq_model,
            api_key=config.llm.groq_api_key,
            temperature=0.1,
        )
    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=config.llm.ollama_model,
            base_url=config.llm.ollama_base_url,
            temperature=0.1,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# ─── Base Agent ───────────────────────────────────────────────

class BaseAgent(ABC):
    """
    Abstract base class for all AlphaAI analysis agents.

    Each agent:
    1. Receives raw data (prices, fundamentals, news, etc.)
    2. Processes and analyzes it
    3. Generates a structured signal (BUY/SELL/HOLD with confidence)
    """

    def __init__(self, config, use_llm: bool = True):
        self.config = config
        self.llm = None

        if use_llm:
            try:
                self.llm = create_llm(config)
                logger.info(f"✅ {self.name} initialized with {config.llm.provider} LLM")
            except Exception as e:
                logger.warning(f"⚠️  {self.name}: LLM init failed ({e}). Running in rule-based mode.")

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name."""
        pass

    @property
    @abstractmethod
    def role(self) -> str:
        """Agent role description."""
        pass

    @abstractmethod
    def analyze(self, data: dict) -> AgentSignal:
        """
        Run analysis on the provided data and return a signal.

        Args:
            data: Dictionary containing relevant market/fundamental/news data

        Returns:
            AgentSignal with the analysis result
        """
        pass

    def _llm_analyze(self, prompt: str, data_summary: str) -> Optional[dict]:
        """
        Use the LLM to analyze data and return structured output.

        Args:
            prompt: The system prompt for the agent
            data_summary: Formatted data to analyze

        Returns:
            Parsed JSON dict from LLM response, or None on error
        """
        if not self.llm:
            return None

        try:
            from langchain.schema import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=data_summary),
            ]

            response = self.llm.invoke(messages)
            content = response.content

            # Try to extract JSON from the response
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]

            return json.loads(json_str.strip())

        except json.JSONDecodeError:
            logger.warning(f"⚠️  {self.name}: Could not parse LLM JSON response")
            # Return the raw text as reasoning
            return {"reasoning": content, "signal": "HOLD", "confidence": 50}
        except Exception as e:
            logger.error(f"❌ {self.name} LLM error: {e}")
            return None

    def _format_number(self, value: Any, prefix: str = "", suffix: str = "") -> str:
        """Format a number for display."""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            if abs(value) >= 1e12:
                return f"{prefix}{value/1e12:.2f}T{suffix}"
            elif abs(value) >= 1e9:
                return f"{prefix}{value/1e9:.2f}B{suffix}"
            elif abs(value) >= 1e6:
                return f"{prefix}{value/1e6:.2f}M{suffix}"
            elif abs(value) >= 1e3:
                return f"{prefix}{value/1e3:.2f}K{suffix}"
            else:
                return f"{prefix}{value:.2f}{suffix}"
        return str(value)

    def _safe_get(self, data: dict, *keys, default=None):
        """Safely get a nested value from a dict."""
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, default)
            else:
                return default
        return current if current is not None else default
