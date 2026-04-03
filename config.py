from __future__ import annotations
"""
AlphaAI — Central Configuration
Loads settings from .env and provides typed access across the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load .env file
load_dotenv(Path(__file__).parent / ".env")


class LLMConfig(BaseSettings):
    """LLM provider configuration."""
    provider: str = Field(default="openai", alias="LLM_PROVIDER")

    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")

    # Google Gemini
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    # Groq
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")


class DataConfig(BaseSettings):
    """Data provider configuration."""
    finnhub_api_key: str = Field(default="", alias="FINNHUB_API_KEY")
    watchlist: str = Field(
        default="AAPL,MSFT,GOOGL,NVDA,TSLA,AMZN,META,JPM,V,UNH",
        alias="WATCHLIST"
    )

    @property
    def tickers(self) -> list[str]:
        return [t.strip().upper() for t in self.watchlist.split(",") if t.strip()]


class RiskConfig(BaseSettings):
    """Risk management parameters."""
    max_position_size: float = Field(default=0.10, alias="MAX_POSITION_SIZE")
    max_sector_exposure: float = Field(default=0.30, alias="MAX_SECTOR_EXPOSURE")
    max_portfolio_stocks: int = Field(default=20, alias="MAX_PORTFOLIO_STOCKS")
    risk_free_rate: float = Field(default=0.05, alias="RISK_FREE_RATE")


class PineconeConfig(BaseSettings):
    """Pinecone Vector Database configuration."""
    api_key: str = Field(default="", alias="PINECONE_API_KEY")
    index_name: str = Field(default="alphaai-sec-rag", alias="PINECONE_INDEX_NAME")


class ServerConfig(BaseSettings):
    """Server configuration."""
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")


class AppConfig:
    """Main application configuration container."""

    def __init__(self):
        self.llm = LLMConfig()
        self.pinecone = PineconeConfig()
        self.data = DataConfig()
        self.risk = RiskConfig()
        self.server = ServerConfig()

        # Paths
        self.base_dir = Path(__file__).parent
        self.db_path = self.base_dir / "data" / "alphaai.db"
        self.reports_dir = self.base_dir / "reports" / "generated"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """Validate configuration and return list of warnings."""
        warnings = []

        if self.llm.provider == "openai" and not self.llm.openai_api_key:
            warnings.append("⚠️  OPENAI_API_KEY not set. Set it in .env or switch LLM_PROVIDER.")
        elif self.llm.provider == "gemini" and not self.llm.google_api_key:
            warnings.append("⚠️  GOOGLE_API_KEY not set. Set it in .env or switch LLM_PROVIDER.")
        elif self.llm.provider == "groq" and not self.llm.groq_api_key:
            warnings.append("⚠️  GROQ_API_KEY not set. Set it in .env or switch LLM_PROVIDER.")

        if not self.data.finnhub_api_key:
            warnings.append("⚠️  FINNHUB_API_KEY not set. News sentiment will use yfinance only.")

        if not self.data.tickers:
            warnings.append("⚠️  WATCHLIST is empty. No stocks to analyze.")

        return warnings


# Global singleton
config = AppConfig()
