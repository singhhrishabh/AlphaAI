from __future__ import annotations
"""
AlphaAI — Technical Analysis Agent
Analyzes price patterns, volume, and technical indicators.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from .base_agent import BaseAgent, AgentSignal

logger = logging.getLogger("alphaai.agents.technical")

TECHNICAL_PROMPT = """You are an expert technical analyst at a top-tier quantitative hedge fund.
Your role is to analyze price action, volume, and technical indicators to identify trading opportunities.

Analyze the following technical data and provide your assessment. Consider:

1. **Trend**: Is the stock in an uptrend, downtrend, or sideways?
2. **Momentum**: RSI, MACD signals — Is momentum bullish or bearish?
3. **Moving Averages**: SMA crossovers, price vs MA — Golden cross or death cross?
4. **Volatility**: Bollinger Bands, ATR — How volatile is the stock?
5. **Volume**: Volume trends, unusual activity — Is volume confirming the price action?
6. **Support/Resistance**: Key price levels

Respond ONLY in this exact JSON format:
{
    "signal": "BUY" or "SELL" or "HOLD",
    "confidence": <0-100>,
    "score": <-100 to 100>,
    "reasoning": "<detailed 3-5 sentence technical analysis>",
    "trend": "<bullish/bearish/neutral>",
    "momentum": "<strong bullish/bullish/neutral/bearish/strong bearish>",
    "support_level": <price>,
    "resistance_level": <price>,
    "key_patterns": ["<pattern1>", "<pattern2>"],
    "risks": ["<risk1>", "<risk2>"]
}"""


class TechnicalAgent(BaseAgent):
    """Analyzes technical indicators and price patterns."""

    @property
    def name(self) -> str:
        return "Technical Analyst"

    @property
    def role(self) -> str:
        return "Evaluates price patterns, volume, and technical indicators (RSI, MACD, SMA, Bollinger Bands)"

    def analyze(self, data: dict) -> AgentSignal:
        symbol = data.get("symbol", "UNKNOWN")
        price_history = data.get("price_history_1y")

        logger.info(f"📊 {self.name} analyzing {symbol}...")

        if price_history is None or price_history.empty or len(price_history) < 30:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal="HOLD",
                confidence=10,
                score=0,
                reasoning=f"Insufficient price data for {symbol} to perform technical analysis.",
                key_metrics={},
                risks=["Insufficient data"],
            )

        # Calculate all technical indicators
        indicators = self._calculate_indicators(price_history)
        scores = {}
        metrics = {}

        # Current price info
        current_price = price_history["Close"].iloc[-1]
        prev_close = price_history["Close"].iloc[-2] if len(price_history) > 1 else current_price
        price_change = ((current_price - prev_close) / prev_close) * 100
        metrics["Current Price"] = f"${current_price:.2f}"
        metrics["Daily Change"] = f"{price_change:+.2f}%"

        # ── Moving Average Analysis ──
        if indicators.get("sma_20") is not None:
            sma20 = indicators["sma_20"]
            metrics["SMA 20"] = f"${sma20:.2f}"
            if current_price > sma20:
                scores["ma_20"] = 10
            else:
                scores["ma_20"] = -10

        if indicators.get("sma_50") is not None:
            sma50 = indicators["sma_50"]
            metrics["SMA 50"] = f"${sma50:.2f}"
            if current_price > sma50:
                scores["ma_50"] = 15
            else:
                scores["ma_50"] = -15

        if indicators.get("sma_200") is not None:
            sma200 = indicators["sma_200"]
            metrics["SMA 200"] = f"${sma200:.2f}"
            if current_price > sma200:
                scores["ma_200"] = 20
            else:
                scores["ma_200"] = -20

        # Golden cross / Death cross
        if indicators.get("sma_50") and indicators.get("sma_200"):
            if indicators["sma_50"] > indicators["sma_200"]:
                scores["cross"] = 15
                metrics["MA Cross"] = "Golden Cross ✅"
            else:
                scores["cross"] = -15
                metrics["MA Cross"] = "Death Cross ❌"

        # ── RSI Analysis ──
        rsi = indicators.get("rsi")
        if rsi is not None:
            metrics["RSI (14)"] = f"{rsi:.1f}"
            if rsi < 30:
                scores["rsi"] = 20  # Oversold — potential buy
                metrics["RSI Signal"] = "Oversold (Bullish)"
            elif rsi < 40:
                scores["rsi"] = 10
                metrics["RSI Signal"] = "Near Oversold"
            elif rsi > 70:
                scores["rsi"] = -20  # Overbought — potential sell
                metrics["RSI Signal"] = "Overbought (Bearish)"
            elif rsi > 60:
                scores["rsi"] = -5
                metrics["RSI Signal"] = "Near Overbought"
            else:
                scores["rsi"] = 5
                metrics["RSI Signal"] = "Neutral"

        # ── MACD Analysis ──
        macd = indicators.get("macd")
        macd_signal = indicators.get("macd_signal")
        if macd is not None and macd_signal is not None:
            macd_hist = macd - macd_signal
            metrics["MACD"] = f"{macd:.3f}"
            metrics["MACD Signal"] = f"{macd_signal:.3f}"
            metrics["MACD Histogram"] = f"{macd_hist:.3f}"

            if macd > macd_signal:
                scores["macd"] = 15
                metrics["MACD Crossover"] = "Bullish ✅"
            else:
                scores["macd"] = -15
                metrics["MACD Crossover"] = "Bearish ❌"

        # ── Bollinger Bands ──
        bb_upper = indicators.get("bb_upper")
        bb_lower = indicators.get("bb_lower")
        bb_middle = indicators.get("bb_middle")
        if bb_upper and bb_lower:
            metrics["BB Upper"] = f"${bb_upper:.2f}"
            metrics["BB Lower"] = f"${bb_lower:.2f}"
            bb_width = (bb_upper - bb_lower) / bb_middle * 100 if bb_middle else 0
            metrics["BB Width"] = f"{bb_width:.1f}%"

            if current_price <= bb_lower:
                scores["bollinger"] = 15  # Near lower band — potential buy
                metrics["BB Position"] = "At Lower Band (Bullish)"
            elif current_price >= bb_upper:
                scores["bollinger"] = -15  # Near upper band — potential sell
                metrics["BB Position"] = "At Upper Band (Bearish)"
            else:
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100
                metrics["BB Position"] = f"{bb_position:.0f}% within bands"
                if bb_position < 30:
                    scores["bollinger"] = 10
                elif bb_position > 70:
                    scores["bollinger"] = -10
                else:
                    scores["bollinger"] = 0

        # ── Volume Analysis ──
        vol_ratio = indicators.get("volume_ratio")
        if vol_ratio is not None:
            metrics["Volume vs Avg"] = f"{vol_ratio:.2f}x"
            if vol_ratio > 2.0:
                # High volume — amplify the direction
                if price_change > 0:
                    scores["volume"] = 15
                else:
                    scores["volume"] = -15
            elif vol_ratio > 1.5:
                scores["volume"] = 5 if price_change > 0 else -5
            else:
                scores["volume"] = 0

        # ── Trend Analysis ──
        returns_20d = indicators.get("returns_20d")
        returns_60d = indicators.get("returns_60d")
        if returns_20d is not None:
            metrics["20-Day Return"] = f"{returns_20d:.1f}%"
        if returns_60d is not None:
            metrics["60-Day Return"] = f"{returns_60d:.1f}%"

        trend_score = 0
        if returns_20d is not None and returns_60d is not None:
            if returns_20d > 5 and returns_60d > 10:
                trend_score = 20
                metrics["Trend"] = "Strong Uptrend 📈"
            elif returns_20d > 0 and returns_60d > 0:
                trend_score = 10
                metrics["Trend"] = "Uptrend 📈"
            elif returns_20d < -5 and returns_60d < -10:
                trend_score = -20
                metrics["Trend"] = "Strong Downtrend 📉"
            elif returns_20d < 0 and returns_60d < 0:
                trend_score = -10
                metrics["Trend"] = "Downtrend 📉"
            else:
                trend_score = 0
                metrics["Trend"] = "Sideways ➡️"
        scores["trend"] = trend_score

        # ── ATR / Volatility ──
        atr = indicators.get("atr")
        if atr is not None:
            atr_pct = (atr / current_price) * 100
            metrics["ATR (14)"] = f"${atr:.2f} ({atr_pct:.1f}%)"
            if atr_pct > 5:
                metrics["Volatility"] = "Very High ⚡"
            elif atr_pct > 3:
                metrics["Volatility"] = "High"
            elif atr_pct > 1.5:
                metrics["Volatility"] = "Moderate"
            else:
                metrics["Volatility"] = "Low"

        # ── Support / Resistance ──
        support, resistance = self._find_support_resistance(price_history)
        if support:
            metrics["Support Level"] = f"${support:.2f}"
        if resistance:
            metrics["Resistance Level"] = f"${resistance:.2f}"

        # ── Calculate Total Score ──
        if scores:
            total_score = sum(scores.values())
            max_possible = len(scores) * 20
            normalized_score = (total_score / max_possible) * 100 if max_possible > 0 else 0
        else:
            total_score = 0
            normalized_score = 0

        # ── LLM Enhancement ──
        llm_result = None
        if self.llm:
            data_summary = self._build_data_summary(symbol, metrics, indicators)
            llm_result = self._llm_analyze(TECHNICAL_PROMPT, data_summary)

        # ── Combine Results ──
        if llm_result:
            signal = llm_result.get("signal", "HOLD")
            confidence = llm_result.get("confidence", 50)
            reasoning = llm_result.get("reasoning", "Technical analysis completed via LLM.")
            risks = llm_result.get("risks", [])
            catalysts = llm_result.get("key_patterns", [])
            final_score = (normalized_score * 0.4) + (llm_result.get("score", 0) * 0.6)
        else:
            if normalized_score > 25:
                signal = "BUY"
            elif normalized_score > 5:
                signal = "HOLD"
            elif normalized_score > -15:
                signal = "HOLD"
            else:
                signal = "SELL"

            confidence = min(80, max(20, 50 + abs(normalized_score) * 0.5))
            final_score = normalized_score

            bullish = [k for k, v in scores.items() if v > 5]
            bearish = [k for k, v in scores.items() if v < -5]
            reasoning = (
                f"Technical analysis of {symbol}: Score {normalized_score:.1f}/100. "
                f"Bullish signals: {', '.join(bullish) if bullish else 'none'}. "
                f"Bearish signals: {', '.join(bearish) if bearish else 'none'}. "
                f"Current price ${current_price:.2f} with RSI at {f'{rsi:.1f}' if rsi else 'N/A'}."
            )
            risks = [k.replace("_", " ").title() for k, v in scores.items() if v < -5]
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

    def _calculate_indicators(self, df: pd.DataFrame) -> dict:
        """Calculate all technical indicators."""
        indicators = {}
        close = df["Close"]
        volume = df["Volume"] if "Volume" in df.columns else None

        try:
            # Moving Averages
            if len(close) >= 20:
                indicators["sma_20"] = close.rolling(20).mean().iloc[-1]
            if len(close) >= 50:
                indicators["sma_50"] = close.rolling(50).mean().iloc[-1]
            if len(close) >= 200:
                indicators["sma_200"] = close.rolling(200).mean().iloc[-1]

            # EMA
            if len(close) >= 12:
                indicators["ema_12"] = close.ewm(span=12).mean().iloc[-1]
            if len(close) >= 26:
                indicators["ema_26"] = close.ewm(span=26).mean().iloc[-1]

            # RSI (14-period)
            if len(close) >= 15:
                delta = close.diff()
                gain = delta.clip(lower=0)
                loss = (-delta.clip(upper=0))
                avg_gain = gain.rolling(14).mean()
                avg_loss = loss.rolling(14).mean()
                rs = avg_gain / avg_loss.replace(0, np.nan)
                rsi = 100 - (100 / (1 + rs))
                indicators["rsi"] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None

            # MACD
            if len(close) >= 26:
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9).mean()
                indicators["macd"] = macd_line.iloc[-1]
                indicators["macd_signal"] = signal_line.iloc[-1]

            # Bollinger Bands (20-period, 2 std)
            if len(close) >= 20:
                sma20 = close.rolling(20).mean()
                std20 = close.rolling(20).std()
                indicators["bb_upper"] = (sma20 + 2 * std20).iloc[-1]
                indicators["bb_middle"] = sma20.iloc[-1]
                indicators["bb_lower"] = (sma20 - 2 * std20).iloc[-1]

            # ATR (14-period)
            if len(df) >= 15 and "High" in df.columns and "Low" in df.columns:
                high = df["High"]
                low = df["Low"]
                tr = pd.concat([
                    high - low,
                    (high - close.shift()).abs(),
                    (low - close.shift()).abs()
                ], axis=1).max(axis=1)
                indicators["atr"] = tr.rolling(14).mean().iloc[-1]

            # Volume ratio (vs 20-day average)
            if volume is not None and len(volume) >= 20:
                avg_vol = volume.rolling(20).mean().iloc[-1]
                if avg_vol and avg_vol > 0:
                    indicators["volume_ratio"] = volume.iloc[-1] / avg_vol

            # Returns
            if len(close) >= 21:
                indicators["returns_20d"] = ((close.iloc[-1] / close.iloc[-21]) - 1) * 100
            if len(close) >= 61:
                indicators["returns_60d"] = ((close.iloc[-1] / close.iloc[-61]) - 1) * 100

        except Exception as e:
            logger.error(f"❌ Error calculating indicators: {e}")

        return indicators

    def _find_support_resistance(self, df: pd.DataFrame) -> tuple[Optional[float], Optional[float]]:
        """Find approximate support and resistance levels using recent pivots."""
        try:
            close = df["Close"]
            current = close.iloc[-1]
            recent = close.tail(60)

            # Simple pivot-based approach
            lows = recent.rolling(5, center=True).min()
            highs = recent.rolling(5, center=True).max()

            support_levels = lows[lows == recent].dropna().unique()
            resistance_levels = highs[highs == recent].dropna().unique()

            support = max([s for s in support_levels if s < current], default=None)
            resistance = min([r for r in resistance_levels if r > current], default=None)

            return support, resistance
        except Exception:
            return None, None

    def _build_data_summary(self, symbol: str, metrics: dict, indicators: dict) -> str:
        """Build formatted data summary for LLM."""
        lines = [f"## Technical Analysis Data: {symbol}\n"]
        for key, value in metrics.items():
            lines.append(f"- **{key}:** {value}")
        return "\n".join(lines)
