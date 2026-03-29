from __future__ import annotations
"""
AlphaAI — Market Data Pipeline
Fetches historical prices, fundamentals, and financial statements using yfinance.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import numpy as np
import yfinance as yf

logger = logging.getLogger("alphaai.data.market")


class MarketDataProvider:
    """Fetches and caches market data from yfinance."""

    def __init__(self):
        self._cache: dict[str, dict] = {}
        self._cache_expiry: dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=15)

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get or create a yfinance Ticker object."""
        return yf.Ticker(symbol)

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache_expiry:
            return False
        return datetime.now() < self._cache_expiry[key]

    def _set_cache(self, key: str, data: dict):
        self._cache[key] = data
        self._cache_expiry[key] = datetime.now() + self._cache_ttl

    # ─── Price Data ───────────────────────────────────────────

    def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.

        Args:
            symbol: Stock ticker (e.g., "AAPL")
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume, Adj Close
        """
        cache_key = f"prices_{symbol}_{period}_{interval}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        try:
            ticker = self._get_ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No price data found for {symbol}")
                return pd.DataFrame()

            # Clean up
            df.index = pd.to_datetime(df.index)
            df = df.dropna()

            self._set_cache(cache_key, df)
            logger.info(f"✅ Fetched {len(df)} price records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"❌ Error fetching prices for {symbol}: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> Optional[dict]:
        """Get current/latest price info."""
        try:
            ticker = self._get_ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose"),
                "open": info.get("open") or info.get("regularMarketOpen"),
                "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            }
        except Exception as e:
            logger.error(f"❌ Error fetching current price for {symbol}: {e}")
            return None

    # ─── Company Fundamentals ─────────────────────────────────

    def get_company_info(self, symbol: str) -> Optional[dict]:
        """Get comprehensive company information."""
        cache_key = f"info_{symbol}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        try:
            ticker = self._get_ticker(symbol)
            info = ticker.info

            company_data = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "country": info.get("country", "Unknown"),
                "website": info.get("website", ""),
                "description": info.get("longBusinessSummary", ""),
                "employees": info.get("fullTimeEmployees", 0),
                "market_cap": info.get("marketCap", 0),
                "enterprise_value": info.get("enterpriseValue", 0),

                # Valuation Metrics
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "ev_to_ebitda": info.get("enterpriseToEbitda"),
                "ev_to_revenue": info.get("enterpriseToRevenue"),

                # Profitability
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "gross_margin": info.get("grossMargins"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),

                # Growth
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),

                # Dividends
                "dividend_yield": info.get("dividendYield"),
                "dividend_rate": info.get("dividendRate"),
                "payout_ratio": info.get("payoutRatio"),

                # Financial Health
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash"),
                "free_cash_flow": info.get("freeCashflow"),
                "operating_cash_flow": info.get("operatingCashflow"),
                "revenue": info.get("totalRevenue"),
                "ebitda": info.get("ebitda"),

                # Share Statistics
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "short_ratio": info.get("shortRatio"),
                "short_percent": info.get("shortPercentOfFloat"),
                "beta": info.get("beta"),

                # Analyst Targets
                "target_mean_price": info.get("targetMeanPrice"),
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
                "recommendation": info.get("recommendationKey"),
                "num_analyst_opinions": info.get("numberOfAnalystOpinions"),
            }

            self._set_cache(cache_key, company_data)
            logger.info(f"✅ Fetched company info for {symbol}")
            return company_data

        except Exception as e:
            logger.error(f"❌ Error fetching company info for {symbol}: {e}")
            return None

    # ─── Financial Statements ─────────────────────────────────

    def get_income_statement(self, symbol: str, quarterly: bool = False) -> pd.DataFrame:
        """Get income statement (annual or quarterly)."""
        try:
            ticker = self._get_ticker(symbol)
            if quarterly:
                df = ticker.quarterly_income_stmt
            else:
                df = ticker.income_stmt
            logger.info(f"✅ Fetched income statement for {symbol}")
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error fetching income statement for {symbol}: {e}")
            return pd.DataFrame()

    def get_balance_sheet(self, symbol: str, quarterly: bool = False) -> pd.DataFrame:
        """Get balance sheet (annual or quarterly)."""
        try:
            ticker = self._get_ticker(symbol)
            if quarterly:
                df = ticker.quarterly_balance_sheet
            else:
                df = ticker.balance_sheet
            logger.info(f"✅ Fetched balance sheet for {symbol}")
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error fetching balance sheet for {symbol}: {e}")
            return pd.DataFrame()

    def get_cash_flow(self, symbol: str, quarterly: bool = False) -> pd.DataFrame:
        """Get cash flow statement (annual or quarterly)."""
        try:
            ticker = self._get_ticker(symbol)
            if quarterly:
                df = ticker.quarterly_cashflow
            else:
                df = ticker.cashflow
            logger.info(f"✅ Fetched cash flow for {symbol}")
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error fetching cash flow for {symbol}: {e}")
            return pd.DataFrame()

    # ─── Aggregated Data Bundle ───────────────────────────────

    def get_full_stock_data(self, symbol: str) -> dict:
        """
        Get a comprehensive data bundle for a stock.
        This is the main entry point used by the analysis agents.
        """
        logger.info(f"📊 Fetching full data bundle for {symbol}...")

        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "company_info": self.get_company_info(symbol),
            "current_price": self.get_current_price(symbol),
            "price_history_1y": self.get_historical_prices(symbol, period="1y"),
            "price_history_3mo": self.get_historical_prices(symbol, period="3mo"),
            "price_history_5d": self.get_historical_prices(symbol, period="5d", interval="1h"),
            "income_statement": self.get_income_statement(symbol),
            "income_statement_quarterly": self.get_income_statement(symbol, quarterly=True),
            "balance_sheet": self.get_balance_sheet(symbol),
            "cash_flow": self.get_cash_flow(symbol),
        }


# Global singleton
market_data = MarketDataProvider()
