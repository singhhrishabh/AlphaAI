from __future__ import annotations
"""
AlphaAI — Sentiment Analysis Agent
Analyzes news headlines using VADER + optional FinBERT.
"""
import logging
from datetime import datetime
from .base_agent import BaseAgent, AgentSignal

logger = logging.getLogger("alphaai.agents.sentiment")

SENTIMENT_PROMPT = """You are an expert market sentiment analyst at a top-tier hedge fund.
Analyze the following news headlines and sentiment data. Consider overall sentiment, trend, impact, and contrarian signals.

Respond ONLY in this exact JSON format:
{
    "signal": "BUY" or "SELL" or "HOLD",
    "confidence": <0-100>,
    "score": <-100 to 100>,
    "reasoning": "<detailed 3-5 sentence sentiment analysis>",
    "overall_sentiment": "<very bullish/bullish/neutral/bearish/very bearish>",
    "sentiment_trend": "<improving/stable/deteriorating>",
    "high_impact_headlines": ["<headline1>", "<headline2>"],
    "risks": ["<risk1>", "<risk2>"]
}"""


class SentimentAgent(BaseAgent):
    """Analyzes news sentiment using VADER and optionally FinBERT."""

    def __init__(self, config, use_llm=True):
        super().__init__(config, use_llm=use_llm)
        self._vader = None
        self._finbert = None
        self._finbert_tokenizer = None
        self._init_models()

    def _init_models(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._vader = SentimentIntensityAnalyzer()
            logger.info("✅ VADER initialized")
        except ImportError:
            logger.warning("⚠️  vaderSentiment not installed")
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            model_name = "ProsusAI/finbert"
            self._finbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._finbert = AutoModelForSequenceClassification.from_pretrained(model_name)
            self._finbert.eval()
            logger.info("✅ FinBERT loaded")
        except Exception as e:
            logger.info(f"ℹ️  FinBERT not available (VADER only): {e}")

    @property
    def name(self): return "Sentiment Analyst"
    @property
    def role(self): return "Analyzes news headlines and market sentiment using NLP"

    def _vader_score(self, text):
        if not self._vader: return {"compound": 0}
        return self._vader.polarity_scores(text)

    def _finbert_batch(self, texts):
        if not self._finbert: return []
        try:
            import torch
            results = []
            for i in range(0, len(texts), 8):
                batch = texts[i:i+8]
                inputs = self._finbert_tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
                with torch.no_grad():
                    probs = torch.nn.functional.softmax(self._finbert(**inputs).logits, dim=-1)
                for j in range(len(batch)):
                    p = {"positive": probs[j][0].item(), "negative": probs[j][1].item(), "neutral": probs[j][2].item()}
                    results.append(p)
            return results
        except Exception as e:
            logger.error(f"FinBERT error: {e}")
            return []

    def analyze(self, data):
        symbol = data.get("symbol", "UNKNOWN")
        articles = data.get("news", [])
        logger.info(f"📰 {self.name} analyzing {symbol} ({len(articles)} articles)...")

        if not articles:
            return AgentSignal(agent_name=self.name, symbol=symbol, signal="HOLD", confidence=15,
                             score=0, reasoning=f"No news for {symbol}.", key_metrics={"articles_analyzed": 0}, risks=["No news data"])

        headlines = [a.get("title", "") for a in articles if a.get("title")]
        vader_results = [self._vader_score(h) for h in headlines]
        finbert_results = self._finbert_batch(headlines)

        sentiments = []
        for i, h in enumerate(headlines):
            v_score = vader_results[i]["compound"] if i < len(vader_results) else 0
            if i < len(finbert_results):
                fb = finbert_results[i]
                combined = v_score * 0.4 + (fb["positive"] - fb["negative"]) * 0.6
            else:
                combined = v_score
            sentiments.append({"headline": h, "score": combined})

        avg = sum(s["score"] for s in sentiments) / len(sentiments) if sentiments else 0
        pos = sum(1 for s in sentiments if s["score"] > 0.1)
        neg = sum(1 for s in sentiments if s["score"] < -0.1)
        neu = len(sentiments) - pos - neg

        label = "Very Bullish" if avg > 0.3 else "Bullish" if avg > 0.1 else "Neutral" if avg > -0.1 else "Bearish" if avg > -0.3 else "Very Bearish"
        normalized = avg * 100
        metrics = {"Articles Analyzed": len(sentiments), "Avg Score": f"{avg:.3f}", "Positive": pos,
                   "Negative": neg, "Neutral": neu, "Overall Sentiment": label}

        sorted_s = sorted(sentiments, key=lambda x: x["score"])
        if sorted_s:
            metrics["Most Bullish"] = sorted_s[-1]["headline"][:100]
            metrics["Most Bearish"] = sorted_s[0]["headline"][:100]

        llm_result = None
        if self.llm and headlines:
            summary = f"## Sentiment: {symbol}\nArticles: {len(headlines)}, Sentiment: {label}, Avg: {avg:.3f}\n"
            summary += "\n".join(f"{'🟢' if s['score']>0.1 else '🔴' if s['score']<-0.1 else '⚪'} [{s['score']:+.3f}] {s['headline']}" for s in sentiments[:20])
            llm_result = self._llm_analyze(SENTIMENT_PROMPT, summary)

        if llm_result:
            signal, confidence = llm_result.get("signal", "HOLD"), llm_result.get("confidence", 50)
            reasoning, risks = llm_result.get("reasoning", ""), llm_result.get("risks", [])
            catalysts = llm_result.get("high_impact_headlines", [])
            final_score = normalized * 0.4 + llm_result.get("score", 0) * 0.6
        else:
            signal = "BUY" if normalized > 25 else "SELL" if normalized < -15 else "HOLD"
            confidence = min(75, max(15, 40 + abs(normalized) * 0.5))
            final_score = normalized
            reasoning = f"Sentiment for {symbol}: {label}. {len(headlines)} articles: {pos} positive, {neg} negative, {neu} neutral. Avg: {avg:.3f}."
            risks = ["Negative news sentiment"] if neg > pos else []
            catalysts = ["Positive news flow"] if pos > neg * 2 else []

        return AgentSignal(agent_name=self.name, symbol=symbol, signal=signal,
                         confidence=round(confidence, 1), score=round(max(-100, min(100, final_score)), 1),
                         reasoning=reasoning, key_metrics=metrics, risks=risks, catalysts=catalysts)
