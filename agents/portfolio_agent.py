from __future__ import annotations
"""
AlphaAI — Portfolio Manager Agent
Synthesizes all agent signals into final BUY/SELL/HOLD decisions.
"""
import logging
from .base_agent import BaseAgent, AgentSignal

logger = logging.getLogger("alphaai.agents.portfolio")

PORTFOLIO_PROMPT = """You are the chief portfolio manager of a top-tier AI hedge fund.
You receive analysis from your team of specialist agents: Fundamental Analyst, Technical Analyst, Sentiment Analyst, and Risk Manager.

Your job is to synthesize their inputs and make the FINAL investment decision.

Consider:
1. Weight each agent's analysis based on confidence and relevance
2. Look for consensus or divergence among agents
3. Give extra weight to Risk Manager warnings
4. Consider the overall risk/reward ratio
5. Be decisive but conservative — protect capital first

Respond ONLY in JSON:
{
    "signal": "STRONG_BUY" or "BUY" or "HOLD" or "SELL" or "STRONG_SELL",
    "confidence": <0-100>,
    "score": <-100 to 100>,
    "reasoning": "<detailed 5-8 sentence investment thesis combining all agent inputs>",
    "target_price": <estimated target or null>,
    "stop_loss_pct": <suggested stop loss percentage>,
    "time_horizon": "<short-term/medium-term/long-term>",
    "key_factors": ["<factor1>", "<factor2>", "<factor3>"],
    "risks": ["<risk1>", "<risk2>"]
}"""


class PortfolioManager(BaseAgent):
    """Synthesizes all agent signals into final decisions."""

    AGENT_WEIGHTS = {
        "Fundamental Analyst": 0.30,
        "Technical Analyst": 0.25,
        "Sentiment Analyst": 0.15,
        "Risk Manager": 0.30,
    }

    @property
    def name(self): return "Portfolio Manager"
    @property
    def role(self): return "Synthesizes all agent analyses into final BUY/SELL/HOLD decisions"

    def analyze(self, data):
        symbol = data.get("symbol", "UNKNOWN")
        agent_signals: list[AgentSignal] = data.get("agent_signals", [])
        logger.info(f"🧠 {self.name} making decision for {symbol}...")

        if not agent_signals:
            return AgentSignal(agent_name=self.name, symbol=symbol, signal="HOLD",
                             confidence=10, score=0, reasoning="No agent signals received.",
                             key_metrics={}, risks=["No analysis data"])

        metrics = {}
        all_risks = []
        all_catalysts = []
        weighted_score = 0
        total_weight = 0

        for sig in agent_signals:
            weight = self.AGENT_WEIGHTS.get(sig.agent_name, 0.15)
            weighted_score += sig.score * weight
            total_weight += weight
            metrics[f"{sig.agent_name} Signal"] = f"{sig.signal} ({sig.confidence:.0f}%)"
            metrics[f"{sig.agent_name} Score"] = f"{sig.score:.1f}"
            all_risks.extend(sig.risks)
            all_catalysts.extend(sig.catalysts)

        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0

        metrics["Weighted Score"] = f"{final_score:.1f}"

        # Consensus analysis
        buy_count = sum(1 for s in agent_signals if s.signal in ("BUY", "STRONG_BUY"))
        sell_count = sum(1 for s in agent_signals if s.signal in ("SELL", "STRONG_SELL"))
        hold_count = sum(1 for s in agent_signals if s.signal == "HOLD")
        metrics["Consensus"] = f"{buy_count} Buy / {hold_count} Hold / {sell_count} Sell"

        avg_confidence = sum(s.confidence for s in agent_signals) / len(agent_signals)
        metrics["Avg Confidence"] = f"{avg_confidence:.1f}%"

        # LLM synthesis
        llm_result = None
        if self.llm:
            summary = self._build_summary(symbol, agent_signals, metrics)
            llm_result = self._llm_analyze(PORTFOLIO_PROMPT, summary)

        if llm_result:
            signal = llm_result.get("signal", "HOLD")
            confidence = llm_result.get("confidence", 50)
            reasoning = llm_result.get("reasoning", "Portfolio decision made.")
            risks = llm_result.get("risks", all_risks[:5])
            catalysts = llm_result.get("key_factors", all_catalysts[:5])
            final_score = final_score * 0.3 + llm_result.get("score", 0) * 0.7

            if llm_result.get("target_price"):
                metrics["Target Price"] = f"${llm_result['target_price']}"
            if llm_result.get("stop_loss_pct"):
                metrics["Stop Loss"] = f"{llm_result['stop_loss_pct']}%"
            if llm_result.get("time_horizon"):
                metrics["Time Horizon"] = llm_result["time_horizon"]
        else:
            # Rule-based decision
            if final_score > 40:
                signal = "STRONG_BUY"
            elif final_score > 15:
                signal = "BUY"
            elif final_score > -15:
                signal = "HOLD"
            elif final_score > -40:
                signal = "SELL"
            else:
                signal = "STRONG_SELL"

            confidence = min(90, max(15, avg_confidence * 0.7 + abs(final_score) * 0.3))

            agent_summaries = "; ".join(f"{s.agent_name}: {s.signal} ({s.confidence:.0f}%)" for s in agent_signals)
            reasoning = (
                f"Portfolio decision for {symbol}: {signal} with {confidence:.0f}% confidence. "
                f"Weighted score: {final_score:.1f}. Agent consensus: {buy_count}B/{hold_count}H/{sell_count}S. "
                f"Agent details — {agent_summaries}."
            )
            risks = list(set(all_risks))[:5]
            catalysts = list(set(all_catalysts))[:5]

        return AgentSignal(
            agent_name=self.name, symbol=symbol, signal=signal,
            confidence=round(confidence, 1), score=round(max(-100, min(100, final_score)), 1),
            reasoning=reasoning, key_metrics=metrics, risks=risks, catalysts=catalysts)

    def _build_summary(self, symbol, signals, metrics):
        lines = [f"## Portfolio Decision: {symbol}\n### Agent Signals:\n"]
        for s in signals:
            lines.append(f"#### {s.agent_name}")
            lines.append(f"- Signal: {s.signal} | Confidence: {s.confidence}% | Score: {s.score}")
            lines.append(f"- Reasoning: {s.reasoning}")
            lines.append(f"- Risks: {', '.join(s.risks[:3]) if s.risks else 'None'}")
            lines.append(f"- Catalysts: {', '.join(s.catalysts[:3]) if s.catalysts else 'None'}\n")
        return "\n".join(lines)
