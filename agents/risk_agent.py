from __future__ import annotations
"""
AlphaAI — Risk Management Agent
Evaluates portfolio risk, position sizing, and diversification.
"""
import logging
import numpy as np
import pandas as pd
from .base_agent import BaseAgent, AgentSignal

logger = logging.getLogger("alphaai.agents.risk")

RISK_PROMPT = """You are an expert risk manager at a top-tier hedge fund.
Evaluate the risk profile of the following stock and provide risk-adjusted recommendations.

Consider: volatility, beta, drawdown risk, sector concentration, correlation, and position sizing.

Respond ONLY in JSON:
{
    "signal": "BUY" or "SELL" or "HOLD",
    "confidence": <0-100>,
    "score": <-100 to 100>,
    "reasoning": "<3-5 sentence risk assessment>",
    "risk_level": "<low/moderate/high/very high>",
    "max_position_size": <0.0-1.0>,
    "stop_loss_pct": <percentage>,
    "risks": ["<risk1>", "<risk2>"],
    "mitigations": ["<mitigation1>"]
}"""


class RiskAgent(BaseAgent):
    @property
    def name(self): return "Risk Manager"
    @property
    def role(self): return "Evaluates risk profile, position sizing, and portfolio diversification"

    def analyze(self, data):
        symbol = data.get("symbol", "UNKNOWN")
        company_info = data.get("company_info") or {}
        price_history = data.get("price_history_1y")
        logger.info(f"⚠️ {self.name} analyzing {symbol}...")

        metrics = {}
        scores = {}
        risks = []
        mitigations = []

        # Beta analysis
        beta = company_info.get("beta")
        if beta is not None:
            metrics["Beta"] = f"{beta:.2f}"
            if beta < 0.5:
                scores["beta"] = 15
            elif beta < 1.0:
                scores["beta"] = 10
            elif beta < 1.5:
                scores["beta"] = 0
            elif beta < 2.0:
                scores["beta"] = -10
                risks.append(f"High beta ({beta:.2f}) — amplified market moves")
            else:
                scores["beta"] = -20
                risks.append(f"Very high beta ({beta:.2f}) — extremely volatile")

        # Volatility analysis
        if price_history is not None and not price_history.empty and len(price_history) > 20:
            returns = price_history["Close"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100
            metrics["Annualized Volatility"] = f"{volatility:.1f}%"

            if volatility < 20:
                scores["volatility"] = 15
                metrics["Volatility Level"] = "Low"
            elif volatility < 35:
                scores["volatility"] = 5
                metrics["Volatility Level"] = "Moderate"
            elif volatility < 50:
                scores["volatility"] = -10
                risks.append(f"High volatility ({volatility:.1f}%)")
                metrics["Volatility Level"] = "High"
            else:
                scores["volatility"] = -20
                risks.append(f"Extreme volatility ({volatility:.1f}%)")
                metrics["Volatility Level"] = "Very High"

            # Max drawdown
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.cummax()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_dd = drawdown.min() * 100
            metrics["Max Drawdown (1Y)"] = f"{max_dd:.1f}%"

            if max_dd > -10:
                scores["drawdown"] = 10
            elif max_dd > -20:
                scores["drawdown"] = 0
            elif max_dd > -35:
                scores["drawdown"] = -10
                risks.append(f"Significant drawdown risk ({max_dd:.1f}%)")
            else:
                scores["drawdown"] = -20
                risks.append(f"Severe drawdown history ({max_dd:.1f}%)")

            # Sharpe Ratio
            risk_free = self.config.risk.risk_free_rate
            excess_return = returns.mean() * 252 - risk_free
            sharpe = excess_return / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
            metrics["Sharpe Ratio"] = f"{sharpe:.2f}"
            if sharpe > 1.5:
                scores["sharpe"] = 15
            elif sharpe > 0.5:
                scores["sharpe"] = 5
            elif sharpe > 0:
                scores["sharpe"] = 0
            else:
                scores["sharpe"] = -10
                risks.append(f"Negative risk-adjusted returns (Sharpe: {sharpe:.2f})")

            # VaR (95%)
            var_95 = np.percentile(returns, 5) * 100
            metrics["VaR (95%, daily)"] = f"{var_95:.2f}%"

        # Financial health risk
        de = company_info.get("debt_to_equity")
        if de is not None:
            if de > 200:
                scores["leverage"] = -15
                risks.append(f"High leverage (D/E: {de:.0f})")
            elif de > 100:
                scores["leverage"] = -5
            else:
                scores["leverage"] = 10

        cr = company_info.get("current_ratio")
        if cr is not None:
            if cr < 1:
                scores["liquidity"] = -15
                risks.append(f"Liquidity risk (Current Ratio: {cr:.2f})")
            elif cr < 1.5:
                scores["liquidity"] = 0
            else:
                scores["liquidity"] = 10

        # Short interest
        short_pct = company_info.get("short_percent")
        if short_pct is not None:
            metrics["Short Interest"] = f"{short_pct*100:.1f}%"
            if short_pct > 0.20:
                risks.append(f"Very high short interest ({short_pct*100:.1f}%)")
                scores["short_interest"] = -10
            elif short_pct > 0.10:
                scores["short_interest"] = -5

        # Position sizing recommendation
        max_pos = self.config.risk.max_position_size
        if scores:
            avg_risk = sum(scores.values()) / len(scores)
            if avg_risk > 5:
                rec_size = max_pos
            elif avg_risk > -5:
                rec_size = max_pos * 0.7
            else:
                rec_size = max_pos * 0.4
        else:
            rec_size = max_pos * 0.5

        metrics["Recommended Position Size"] = f"{rec_size*100:.1f}%"
        mitigations.append(f"Limit position to {rec_size*100:.1f}% of portfolio")
        mitigations.append("Use stop-loss orders")

        # Total score
        total = sum(scores.values()) if scores else 0
        max_possible = len(scores) * 15 if scores else 1
        normalized = (total / max_possible) * 100 if max_possible > 0 else 0

        # LLM enhancement
        llm_result = None
        if self.llm:
            summary = f"## Risk Assessment: {symbol}\n" + "\n".join(f"- **{k}:** {v}" for k, v in metrics.items())
            llm_result = self._llm_analyze(RISK_PROMPT, summary)

        if llm_result:
            signal = llm_result.get("signal", "HOLD")
            confidence = llm_result.get("confidence", 50)
            reasoning = llm_result.get("reasoning", "Risk analysis completed.")
            final_score = normalized * 0.4 + llm_result.get("score", 0) * 0.6
        else:
            signal = "BUY" if normalized > 20 else "SELL" if normalized < -20 else "HOLD"
            confidence = min(80, max(20, 50 + abs(normalized) * 0.4))
            final_score = normalized
            risk_level = "Low" if normalized > 20 else "High" if normalized < -10 else "Moderate"
            reasoning = f"Risk assessment for {symbol}: {risk_level} risk. Score {normalized:.1f}. {len(risks)} risk factors identified."

        return AgentSignal(
            agent_name=self.name, symbol=symbol, signal=signal,
            confidence=round(confidence, 1), score=round(max(-100, min(100, final_score)), 1),
            reasoning=reasoning, key_metrics=metrics, risks=risks, catalysts=mitigations)
