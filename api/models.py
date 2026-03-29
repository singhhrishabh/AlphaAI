from __future__ import annotations
"""
AlphaAI — Pydantic Models for API request/response schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    use_llm: bool = Field(default=True, description="Whether to use LLM for analysis")


class AnalyzeMultipleRequest(BaseModel):
    tickers: list[str] = Field(description="List of stock tickers")
    use_llm: bool = Field(default=True)


class SignalResponse(BaseModel):
    symbol: str
    signal: str
    confidence: float
    score: float
    reasoning: str
    timestamp: str


class StockAnalysisResponse(BaseModel):
    symbol: str
    company_name: str
    sector: str
    industry: str
    current_price: Optional[float]
    market_cap: Optional[float]
    signal: str
    confidence: float
    overall_score: float
    fundamental_score: Optional[float]
    technical_score: Optional[float]
    sentiment_score: Optional[float]
    risk_score: Optional[float]
    summary: str
    timestamp: str
    elapsed_seconds: float
    agent_signals: dict
    final_decision: dict
    news_count: int


class DashboardResponse(BaseModel):
    total_stocks: int
    total_reports: int
    total_signals: int
    signal_distribution_7d: dict
    latest_signals: list[dict]
    recent_analyses: list[dict] = []


class PortfolioItem(BaseModel):
    symbol: str
    quantity: float
    avg_cost: float
    current_value: float = 0
    unrealized_pnl: float = 0
    sector: str = ""


class WatchlistUpdate(BaseModel):
    tickers: list[str]
