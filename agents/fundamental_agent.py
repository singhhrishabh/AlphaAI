from __future__ import annotations
"""
AlphaAI — Fundamental Analysis Agent
Analyzes company financials, valuation metrics, and financial health.
"""

import logging
import pandas as pd
from .base_agent import BaseAgent, AgentSignal

logger = logging.getLogger("alphaai.agents.fundamental")

FUNDAMENTAL_PROMPT = """You are an expert fundamental analyst at a top-tier hedge fund.
Your role is to analyze company financials and determine the intrinsic value and investment thesis.

Analyze the following financial data and provide your assessment. Consider:

1. **Valuation**: P/E, P/B, PEG, EV/EBITDA — Is the stock overvalued or undervalued?
2. **Profitability**: Profit margins, ROE, ROA — Is the company profitable and efficient?
3. **Growth**: Revenue and earnings growth — Is the company growing?
4. **Financial Health**: Debt-to-equity, current ratio, free cash flow — Is the balance sheet strong?
5. **Cash Flow**: Operating and free cash flow — Is the company generating real cash?
6. **Competitive Position**: Market cap, industry standing — How does it compare to peers?

Respond ONLY in this exact JSON format:
{
    "signal": "BUY" or "SELL" or "HOLD",
    "confidence": <0-100>,
    "score": <-100 to 100>,
    "reasoning": "<detailed 3-5 sentence analysis>",
    "valuation_assessment": "<overvalued/fairly valued/undervalued>",
    "financial_health": "<strong/moderate/weak>",
    "growth_outlook": "<strong/moderate/weak/declining>",
    "key_strengths": ["<strength1>", "<strength2>"],
    "key_risks": ["<risk1>", "<risk2>"],
    "intrinsic_value_estimate": "<estimated fair value or 'insufficient data'>"
}"""


class FundamentalAgent(BaseAgent):
    """Analyzes company fundamentals and financial statements."""

    @property
    def name(self) -> str:
        return "Fundamental Analyst"

    @property
    def role(self) -> str:
        return "Evaluates company financials, valuation metrics, and balance sheet strength"

    def analyze(self, data: dict) -> AgentSignal:
        symbol = data.get("symbol", "UNKNOWN")
        company_info = data.get("company_info") or {}
        income_stmt = data.get("income_statement")
        balance_sheet = data.get("balance_sheet")
        cash_flow = data.get("cash_flow")

        logger.info(f"🔍 {self.name} analyzing {symbol}...")

        # ── Rule-Based Scoring ──
        scores = {}
        metrics = {}

        # Valuation scoring
        pe = company_info.get("pe_ratio")
        if pe is not None and pe > 0:
            metrics["P/E Ratio"] = round(pe, 2)
            if pe < 15:
                scores["valuation_pe"] = 30
            elif pe < 25:
                scores["valuation_pe"] = 15
            elif pe < 40:
                scores["valuation_pe"] = 0
            else:
                scores["valuation_pe"] = -20

        peg = company_info.get("peg_ratio")
        if peg is not None and peg > 0:
            metrics["PEG Ratio"] = round(peg, 2)
            if peg < 1:
                scores["valuation_peg"] = 20
            elif peg < 2:
                scores["valuation_peg"] = 5
            else:
                scores["valuation_peg"] = -10

        pb = company_info.get("price_to_book")
        if pb is not None and pb > 0:
            metrics["P/B Ratio"] = round(pb, 2)
            if pb < 3:
                scores["valuation_pb"] = 10
            elif pb < 8:
                scores["valuation_pb"] = 0
            else:
                scores["valuation_pb"] = -10

        # Profitability scoring
        roe = company_info.get("roe")
        if roe is not None:
            metrics["ROE"] = f"{roe*100:.1f}%"
            if roe > 0.20:
                scores["profitability_roe"] = 20
            elif roe > 0.10:
                scores["profitability_roe"] = 10
            elif roe > 0:
                scores["profitability_roe"] = 0
            else:
                scores["profitability_roe"] = -15

        profit_margin = company_info.get("profit_margin")
        if profit_margin is not None:
            metrics["Profit Margin"] = f"{profit_margin*100:.1f}%"
            if profit_margin > 0.20:
                scores["profitability_margin"] = 15
            elif profit_margin > 0.10:
                scores["profitability_margin"] = 5
            elif profit_margin > 0:
                scores["profitability_margin"] = 0
            else:
                scores["profitability_margin"] = -15

        # Growth scoring
        rev_growth = company_info.get("revenue_growth")
        if rev_growth is not None:
            metrics["Revenue Growth"] = f"{rev_growth*100:.1f}%"
            if rev_growth > 0.20:
                scores["growth_revenue"] = 20
            elif rev_growth > 0.10:
                scores["growth_revenue"] = 10
            elif rev_growth > 0:
                scores["growth_revenue"] = 0
            else:
                scores["growth_revenue"] = -15

        earnings_growth = company_info.get("earnings_growth")
        if earnings_growth is not None:
            metrics["Earnings Growth"] = f"{earnings_growth*100:.1f}%"
            if earnings_growth > 0.20:
                scores["growth_earnings"] = 15
            elif earnings_growth > 0:
                scores["growth_earnings"] = 5
            else:
                scores["growth_earnings"] = -10

        # Financial health scoring
        de_ratio = company_info.get("debt_to_equity")
        if de_ratio is not None:
            metrics["Debt/Equity"] = round(de_ratio, 2)
            if de_ratio < 50:
                scores["health_debt"] = 15
            elif de_ratio < 100:
                scores["health_debt"] = 5
            elif de_ratio < 200:
                scores["health_debt"] = -5
            else:
                scores["health_debt"] = -20

        current_ratio = company_info.get("current_ratio")
        if current_ratio is not None:
            metrics["Current Ratio"] = round(current_ratio, 2)
            if current_ratio > 2:
                scores["health_current"] = 10
            elif current_ratio > 1.5:
                scores["health_current"] = 5
            elif current_ratio > 1:
                scores["health_current"] = 0
            else:
                scores["health_current"] = -15

        fcf = company_info.get("free_cash_flow")
        if fcf is not None:
            metrics["Free Cash Flow"] = self._format_number(fcf, prefix="$")
            if fcf > 0:
                scores["health_fcf"] = 15
            else:
                scores["health_fcf"] = -15

        # Dividend scoring
        div_yield = company_info.get("dividend_yield")
        if div_yield is not None and div_yield > 0:
            metrics["Dividend Yield"] = f"{div_yield*100:.2f}%"
            if div_yield > 0.03:
                scores["dividend"] = 10
            elif div_yield > 0.01:
                scores["dividend"] = 5
            else:
                scores["dividend"] = 2

        # Additional metrics
        metrics["Market Cap"] = self._format_number(company_info.get("market_cap"), prefix="$")
        metrics["Sector"] = company_info.get("sector", "Unknown")
        metrics["Industry"] = company_info.get("industry", "Unknown")
        metrics["Beta"] = company_info.get("beta", "N/A")
        metrics["Analyst Target"] = self._format_number(company_info.get("target_mean_price"), prefix="$")
        metrics["Recommendation"] = company_info.get("recommendation", "N/A")

        # Calculate total score
        if scores:
            total_score = sum(scores.values())
            max_possible = len(scores) * 30  # max score per metric
            normalized_score = (total_score / max_possible) * 100 if max_possible > 0 else 0
        else:
            total_score = 0
            normalized_score = 0

        # ── LLM Enhancement + YC-Tier RAG ──
        llm_result = None
        if self.llm:
            data_summary = self._build_data_summary(symbol, company_info, income_stmt, balance_sheet, cash_flow)
            
            # Phase 2: RAG Pipeline Integration (Placeholder for Vector DB like Pinecone)
            rag_insights = self._run_sec_rag_analysis(symbol)
            if rag_insights:
                data_summary += f"\n\n### RAG Insights (SEC 10-K/10-Q)\n{rag_insights}"
            
            llm_result = self._llm_analyze(FUNDAMENTAL_PROMPT, data_summary)

        # ── Combine Results ──
        if llm_result:
            signal = llm_result.get("signal", "HOLD")
            confidence = llm_result.get("confidence", 50)
            reasoning = llm_result.get("reasoning", "LLM analysis completed.")
            risks = llm_result.get("key_risks", [])
            catalysts = llm_result.get("key_strengths", [])
            final_score = (normalized_score * 0.4) + (llm_result.get("score", 0) * 0.6)
        else:
            # Pure rule-based
            if normalized_score > 30:
                signal = "BUY"
            elif normalized_score > 10:
                signal = "HOLD"
            elif normalized_score > -10:
                signal = "HOLD"
            else:
                signal = "SELL"

            confidence = min(80, max(20, 50 + abs(normalized_score) * 0.5))
            final_score = normalized_score

            strengths = [k for k, v in scores.items() if v > 10]
            weaknesses = [k for k, v in scores.items() if v < -5]
            reasoning = (
                f"Fundamental analysis of {symbol}: Score {normalized_score:.1f}/100. "
                f"Strengths: {', '.join(strengths) if strengths else 'limited'}. "
                f"Weaknesses: {', '.join(weaknesses) if weaknesses else 'none identified'}. "
                f"{'Strong' if normalized_score > 30 else 'Moderate' if normalized_score > 0 else 'Weak'} fundamentals overall."
            )
            risks = [k.replace("_", " ").title() for k, v in scores.items() if v < 0]
            catalysts = [k.replace("_", " ").title() for k, v in scores.items() if v > 10]

        return AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal=signal,
            confidence=round(confidence, 1),
            score=round(max(-100, min(100, final_score)), 1),
            reasoning=reasoning,
            key_metrics=metrics,
            risks=risks,
            catalysts=catalysts,
        )

    def _run_sec_rag_analysis(self, symbol: str) -> str:
        """
        [YC-Tier Real-World Feature Placeholder]
        Queries Pinecone/Weaviate vector database containing embedded SEC 10-K, 10-Q filings 
        and earnings call transcripts to extract qualitative risks and growth catalysts.
        """
        logger.info(f"📚 Running SEC RAG Vector Search for {symbol}... (Placeholder)")
        # Example implementation context:
        # 1. Fetch embeddings from LangChain Pinecone init
        # 2. Similarity search for "forward guidance", "risk factors"
        # 3. Return summary
        return "Not available in prototype. Implement LangChain + Pinecone here."

    def _build_data_summary(self, symbol, info, income_stmt, balance_sheet, cash_flow) -> str:
        """Build a formatted data summary for the LLM."""
        lines = [f"## Company: {info.get('name', symbol)} ({symbol})\n"]
        lines.append(f"**Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')}")
        lines.append(f"**Market Cap:** {self._format_number(info.get('market_cap'), prefix='$')}")
        lines.append(f"**Description:** {info.get('description', 'N/A')[:300]}...\n")

        lines.append("### Valuation Metrics")
        for key in ["pe_ratio", "forward_pe", "peg_ratio", "price_to_book", "price_to_sales", "ev_to_ebitda"]:
            val = info.get(key)
            if val is not None:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {val:.2f}")

        lines.append("\n### Profitability")
        for key in ["profit_margin", "operating_margin", "gross_margin", "roe", "roa"]:
            val = info.get(key)
            if val is not None:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {val*100:.1f}%")

        lines.append("\n### Growth")
        for key in ["revenue_growth", "earnings_growth", "earnings_quarterly_growth"]:
            val = info.get(key)
            if val is not None:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {val*100:.1f}%")

        lines.append("\n### Financial Health")
        for key in ["debt_to_equity", "current_ratio", "quick_ratio"]:
            val = info.get(key)
            if val is not None:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {val:.2f}")

        for key in ["total_debt", "total_cash", "free_cash_flow", "operating_cash_flow", "revenue", "ebitda"]:
            val = info.get(key)
            if val is not None:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {self._format_number(val, prefix='$')}")

        lines.append("\n### Analyst Consensus")
        lines.append(f"- **Recommendation:** {info.get('recommendation', 'N/A')}")
        lines.append(f"- **Target Price:** ${info.get('target_mean_price', 'N/A')}")
        lines.append(f"- **# Analysts:** {info.get('num_analyst_opinions', 'N/A')}")

        # Add income statement summary if available
        if income_stmt is not None and not income_stmt.empty:
            lines.append("\n### Income Statement (Recent Years)")
            try:
                for col in income_stmt.columns[:3]:
                    year = col.strftime("%Y") if hasattr(col, "strftime") else str(col)
                    lines.append(f"\n**{year}:**")
                    for row in ["Total Revenue", "Net Income", "Operating Income", "Gross Profit", "EBITDA"]:
                        if row in income_stmt.index:
                            val = income_stmt.loc[row, col]
                            if pd.notna(val):
                                lines.append(f"  - {row}: {self._format_number(val, prefix='$')}")
            except Exception:
                pass

        return "\n".join(lines)
