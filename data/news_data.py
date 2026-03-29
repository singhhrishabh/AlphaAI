from __future__ import annotations
"""
AlphaAI — News & Sentiment Data Pipeline
Fetches news from yfinance, Finnhub, and RSS feeds for sentiment analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import feedparser
import yfinance as yf

logger = logging.getLogger("alphaai.data.news")


class NewsDataProvider:
    """Fetches news headlines and articles from multiple sources."""

    def __init__(self, finnhub_api_key: str = ""):
        self.finnhub_api_key = finnhub_api_key
        self._finnhub_client = None

        if finnhub_api_key:
            try:
                import finnhub
                self._finnhub_client = finnhub.Client(api_key=finnhub_api_key)
                logger.info("✅ Finnhub client initialized")
            except ImportError:
                logger.warning("⚠️  finnhub-python not installed. Install with: pip install finnhub-python")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize Finnhub client: {e}")

    # ─── yfinance News ────────────────────────────────────────

    def get_yfinance_news(self, symbol: str, max_items: int = 20) -> list[dict]:
        """Fetch news from yfinance for a given stock."""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news or []

            articles = []
            for item in news[:max_items]:
                articles.append({
                    "source": "yfinance",
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", "Unknown"),
                    "link": item.get("link", ""),
                    "published_at": datetime.fromtimestamp(
                        item.get("providerPublishTime", 0)
                    ).isoformat() if item.get("providerPublishTime") else None,
                    "type": item.get("type", "article"),
                    "thumbnail": (
                        item.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "")
                        if item.get("thumbnail") else ""
                    ),
                    "related_tickers": item.get("relatedTickers", []),
                })

            logger.info(f"✅ Fetched {len(articles)} news articles from yfinance for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"❌ Error fetching yfinance news for {symbol}: {e}")
            return []

    # ─── Finnhub News ─────────────────────────────────────────

    def get_finnhub_news(
        self,
        symbol: str,
        days_back: int = 7,
        max_items: int = 30
    ) -> list[dict]:
        """Fetch company news from Finnhub."""
        if not self._finnhub_client:
            return []

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            news = self._finnhub_client.company_news(
                symbol,
                _from=start_date.strftime("%Y-%m-%d"),
                to=end_date.strftime("%Y-%m-%d")
            )

            articles = []
            for item in (news or [])[:max_items]:
                articles.append({
                    "source": "finnhub",
                    "title": item.get("headline", ""),
                    "publisher": item.get("source", "Unknown"),
                    "link": item.get("url", ""),
                    "published_at": datetime.fromtimestamp(
                        item.get("datetime", 0)
                    ).isoformat() if item.get("datetime") else None,
                    "summary": item.get("summary", ""),
                    "category": item.get("category", ""),
                    "image": item.get("image", ""),
                    "related_tickers": [symbol],
                })

            logger.info(f"✅ Fetched {len(articles)} news articles from Finnhub for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"❌ Error fetching Finnhub news for {symbol}: {e}")
            return []

    # ─── RSS Feed News ────────────────────────────────────────

    def get_rss_news(self, symbol: str, max_items: int = 15) -> list[dict]:
        """Fetch news from financial RSS feeds."""
        rss_feeds = [
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
            f"https://www.google.com/finance/quote/{symbol}:NASDAQ?sa=X",
        ]

        articles = []
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:max_items]:
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6]).isoformat()

                    articles.append({
                        "source": "rss",
                        "title": entry.get("title", ""),
                        "publisher": feed.feed.get("title", "RSS Feed"),
                        "link": entry.get("link", ""),
                        "published_at": published,
                        "summary": entry.get("summary", ""),
                        "related_tickers": [symbol],
                    })
            except Exception as e:
                logger.warning(f"⚠️  Error parsing RSS feed: {e}")
                continue

        logger.info(f"✅ Fetched {len(articles)} news articles from RSS for {symbol}")
        return articles

    # ─── Market-Wide News ─────────────────────────────────────

    def get_market_news(self, max_items: int = 20) -> list[dict]:
        """Fetch general market news from Finnhub."""
        if not self._finnhub_client:
            return []

        try:
            news = self._finnhub_client.general_news("general", min_id=0)
            articles = []
            for item in (news or [])[:max_items]:
                articles.append({
                    "source": "finnhub_market",
                    "title": item.get("headline", ""),
                    "publisher": item.get("source", "Unknown"),
                    "link": item.get("url", ""),
                    "published_at": datetime.fromtimestamp(
                        item.get("datetime", 0)
                    ).isoformat() if item.get("datetime") else None,
                    "summary": item.get("summary", ""),
                    "category": item.get("category", "general"),
                })

            logger.info(f"✅ Fetched {len(articles)} market news articles")
            return articles
        except Exception as e:
            logger.error(f"❌ Error fetching market news: {e}")
            return []

    # ─── Aggregated News Bundle ───────────────────────────────

    def get_all_news(self, symbol: str) -> list[dict]:
        """
        Get news from all sources for a symbol.
        Deduplicates by title similarity.
        """
        all_articles = []

        # Collect from all sources
        all_articles.extend(self.get_yfinance_news(symbol))
        all_articles.extend(self.get_finnhub_news(symbol))
        all_articles.extend(self.get_rss_news(symbol))

        # Deduplicate by title (case-insensitive)
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title_key = article["title"].lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        # Sort by published date (most recent first)
        unique_articles.sort(
            key=lambda x: x.get("published_at") or "",
            reverse=True
        )

        logger.info(f"📰 Total unique news articles for {symbol}: {len(unique_articles)}")
        return unique_articles


# Factory function
def create_news_provider(finnhub_api_key: str = "") -> NewsDataProvider:
    return NewsDataProvider(finnhub_api_key=finnhub_api_key)
