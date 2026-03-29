from __future__ import annotations
"""
AlphaAI — Agent Orchestrator
Coordinates all agents to run a full analysis pipeline for a stock.
"""
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import config
from data.market_data import market_data
from data.news_data import create_news_provider
from .fundamental_agent import FundamentalAgent
from .technical_agent import TechnicalAgent
from .sentiment_agent import SentimentAgent
from .risk_agent import RiskAgent
from .portfolio_agent import PortfolioManager
from .base_agent import AgentSignal

logger = logging.getLogger("alphaai.orchestrator")


class Orchestrator:
    """Coordinates all AI agents for full stock analysis."""

    def __init__(self, use_llm=True):
        self.config = config
        self.use_llm = use_llm
        self.news_provider = create_news_provider(config.data.finnhub_api_key)

        # Agents are lazy-loaded on first use to save memory
        self._fundamental = None
        self._technical = None
        self._sentiment = None
        self._risk = None
        self._portfolio_mgr = None

        logger.info("✅ Orchestrator initialized (agents will load on first analysis)")

    @property
    def fundamental(self):
        if self._fundamental is None:
            self._fundamental = FundamentalAgent(self.config, use_llm=self.use_llm)
        return self._fundamental

    @property
    def technical(self):
        if self._technical is None:
            self._technical = TechnicalAgent(self.config, use_llm=self.use_llm)
        return self._technical

    @property
    def sentiment(self):
        if self._sentiment is None:
            self._sentiment = SentimentAgent(self.config, use_llm=self.use_llm)
        return self._sentiment

    @property
    def risk(self):
        if self._risk is None:
            self._risk = RiskAgent(self.config, use_llm=self.use_llm)
        return self._risk

    @property
    def portfolio_mgr(self):
        if self._portfolio_mgr is None:
            self._portfolio_mgr = PortfolioManager(self.config, use_llm=self.use_llm)
        return self._portfolio_mgr

    def analyze_stock(self, symbol: str) -> dict:
        """
        Run full analysis pipeline for a single stock.
        Returns a comprehensive analysis result.
        """
        symbol = symbol.upper().strip()
        logger.info(f"\n{'='*60}\n🚀 Starting full analysis for {symbol}\n{'='*60}")
        start_time = datetime.now()

        # Step 1: Fetch all data
        logger.info("📊 Step 1: Fetching market data...")
        stock_data = market_data.get_full_stock_data(symbol)

        logger.info("📰 Step 2: Fetching news data...")
        news = self.news_provider.get_all_news(symbol)
        stock_data["news"] = news

        # Step 3: Run specialist agents (can be parallel)
        logger.info("🤖 Step 3: Running specialist agents...")
        agent_signals = []

        def run_agent(agent, data):
            try:
                return agent.analyze(data)
            except Exception as e:
                logger.error(f"❌ {agent.name} failed: {e}")
                return AgentSignal(
                    agent_name=agent.name, symbol=symbol, signal="HOLD",
                    confidence=0, score=0, reasoning=f"Agent error: {e}",
                    risks=[f"{agent.name} analysis failed"])

        agents_to_run = [
            (self.fundamental, stock_data),
            (self.technical, stock_data),
            (self.sentiment, stock_data),
            (self.risk, stock_data),
        ]

        for agent, data in agents_to_run:
            result = run_agent(agent, data)
            agent_signals.append(result)
            logger.info(f"  ✅ {agent.name}: {result.signal} ({result.confidence}%)")

        # Step 4: Portfolio Manager makes final decision
        logger.info("🧠 Step 4: Portfolio Manager synthesizing...")
        portfolio_data = {"symbol": symbol, "agent_signals": agent_signals}
        final_decision = self.portfolio_mgr.analyze(portfolio_data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Analysis complete for {symbol} in {elapsed:.1f}s")
        logger.info(f"📋 Decision: {final_decision.signal} ({final_decision.confidence}%)")
        logger.info(f"{'='*60}\n")

        # Build complete result
        company_info = stock_data.get("company_info") or {}
        current_price = stock_data.get("current_price") or {}

        return {
            "symbol": symbol,
            "company_name": company_info.get("name", symbol),
            "sector": company_info.get("sector", "Unknown"),
            "industry": company_info.get("industry", "Unknown"),
            "current_price": current_price.get("current_price"),
            "market_cap": company_info.get("market_cap"),
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "final_decision": final_decision.model_dump(),
            "agent_signals": {s.agent_name: s.model_dump() for s in agent_signals},
            "fundamental_score": next((s.score for s in agent_signals if s.agent_name == "Fundamental Analyst"), None),
            "technical_score": next((s.score for s in agent_signals if s.agent_name == "Technical Analyst"), None),
            "sentiment_score": next((s.score for s in agent_signals if s.agent_name == "Sentiment Analyst"), None),
            "risk_score": next((s.score for s in agent_signals if s.agent_name == "Risk Manager"), None),
            "overall_score": final_decision.score,
            "signal": final_decision.signal,
            "confidence": final_decision.confidence,
            "summary": final_decision.reasoning,
            "news_count": len(news),
        }

    def analyze_watchlist(self, tickers: list[str] = None) -> list[dict]:
        """Run analysis on the full watchlist."""
        if tickers is None:
            tickers = self.config.data.tickers
        logger.info(f"📋 Analyzing watchlist: {', '.join(tickers)}")
        results = []
        for ticker in tickers:
            try:
                result = self.analyze_stock(ticker)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Failed to analyze {ticker}: {e}")
                results.append({"symbol": ticker, "error": str(e)})
        return results
