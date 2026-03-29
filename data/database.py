from __future__ import annotations
"""
AlphaAI — Database Layer
SQLite-based storage for analysis results, signals, and portfolio data.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("alphaai.data.database")

DB_SCHEMA = """
-- Stock watchlist
CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    industry TEXT,
    market_cap REAL,
    added_at TEXT DEFAULT (datetime('now')),
    is_active INTEGER DEFAULT 1
);

-- Analysis reports
CREATE TABLE IF NOT EXISTS analysis_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    report_type TEXT DEFAULT 'full',
    fundamental_score REAL,
    technical_score REAL,
    sentiment_score REAL,
    risk_score REAL,
    overall_score REAL,
    signal TEXT CHECK(signal IN ('BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL')),
    confidence REAL,
    summary TEXT,
    full_report TEXT,
    agent_outputs TEXT,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- Trading signals
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    signal TEXT NOT NULL CHECK(signal IN ('BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL')),
    confidence REAL NOT NULL,
    price_at_signal REAL,
    target_price REAL,
    stop_loss REAL,
    reasoning TEXT,
    agent_source TEXT,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- Portfolio holdings
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    avg_cost REAL NOT NULL DEFAULT 0,
    current_value REAL DEFAULT 0,
    unrealized_pnl REAL DEFAULT 0,
    sector TEXT,
    added_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Sentiment scores history
CREATE TABLE IF NOT EXISTS sentiment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    score REAL NOT NULL,
    label TEXT,
    source TEXT,
    headline TEXT,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- Price snapshots (for tracking portfolio value over time)
CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    price REAL NOT NULL,
    volume REAL,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_reports_symbol ON analysis_reports(symbol);
CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON analysis_reports(timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON sentiment_history(symbol);
CREATE INDEX IF NOT EXISTS idx_sentiment_timestamp ON sentiment_history(timestamp);
"""


class Database:
    """SQLite database manager for AlphaAI."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(DB_SCHEMA)
            logger.info(f"✅ Database initialized at {self.db_path}")

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ─── Stocks ───────────────────────────────────────────────

    def add_stock(self, symbol: str, name: str = "", sector: str = "", industry: str = "", market_cap: float = 0):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO stocks (symbol, name, sector, industry, market_cap) VALUES (?, ?, ?, ?, ?)",
                (symbol, name, sector, industry, market_cap)
            )

    def get_stocks(self, active_only: bool = True) -> list[dict]:
        with self._get_conn() as conn:
            query = "SELECT * FROM stocks"
            if active_only:
                query += " WHERE is_active = 1"
            rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]

    # ─── Analysis Reports ─────────────────────────────────────

    def save_report(self, report: dict) -> int:
        with self._get_conn() as conn:
            cursor = conn.execute(
                """INSERT INTO analysis_reports
                   (symbol, report_type, fundamental_score, technical_score, sentiment_score,
                    risk_score, overall_score, signal, confidence, summary, full_report, agent_outputs)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report["symbol"],
                    report.get("report_type", "full"),
                    report.get("fundamental_score"),
                    report.get("technical_score"),
                    report.get("sentiment_score"),
                    report.get("risk_score"),
                    report.get("overall_score"),
                    report.get("signal"),
                    report.get("confidence"),
                    report.get("summary"),
                    report.get("full_report"),
                    json.dumps(report.get("agent_outputs", {})),
                )
            )
            report_id = cursor.lastrowid
            logger.info(f"✅ Saved report #{report_id} for {report['symbol']}")
            return report_id

    def get_latest_report(self, symbol: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM analysis_reports WHERE symbol = ? ORDER BY timestamp DESC LIMIT 1",
                (symbol,)
            ).fetchone()
            if row:
                result = dict(row)
                if result.get("agent_outputs"):
                    result["agent_outputs"] = json.loads(result["agent_outputs"])
                return result
            return None

    def get_reports(self, symbol: str = None, limit: int = 50) -> list[dict]:
        with self._get_conn() as conn:
            if symbol:
                rows = conn.execute(
                    "SELECT * FROM analysis_reports WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?",
                    (symbol, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM analysis_reports ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            results = []
            for row in rows:
                r = dict(row)
                if r.get("agent_outputs"):
                    r["agent_outputs"] = json.loads(r["agent_outputs"])
                results.append(r)
            return results

    # ─── Signals ──────────────────────────────────────────────

    def save_signal(self, signal: dict) -> int:
        with self._get_conn() as conn:
            cursor = conn.execute(
                """INSERT INTO signals
                   (symbol, signal, confidence, price_at_signal, target_price, stop_loss, reasoning, agent_source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    signal["symbol"],
                    signal["signal"],
                    signal["confidence"],
                    signal.get("price_at_signal"),
                    signal.get("target_price"),
                    signal.get("stop_loss"),
                    signal.get("reasoning"),
                    signal.get("agent_source", "portfolio_manager"),
                )
            )
            return cursor.lastrowid

    def get_signals(self, symbol: str = None, limit: int = 100) -> list[dict]:
        with self._get_conn() as conn:
            if symbol:
                rows = conn.execute(
                    "SELECT * FROM signals WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?",
                    (symbol, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(row) for row in rows]

    # ─── Sentiment ────────────────────────────────────────────

    def save_sentiment(self, symbol: str, score: float, label: str, source: str, headline: str = ""):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO sentiment_history (symbol, score, label, source, headline) VALUES (?, ?, ?, ?, ?)",
                (symbol, score, label, source, headline)
            )

    def get_sentiment_history(self, symbol: str, days: int = 30) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM sentiment_history
                   WHERE symbol = ? AND timestamp >= datetime('now', ?)
                   ORDER BY timestamp DESC""",
                (symbol, f"-{days} days")
            ).fetchall()
            return [dict(row) for row in rows]

    # ─── Portfolio ────────────────────────────────────────────

    def get_portfolio(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM portfolio ORDER BY current_value DESC").fetchall()
            return [dict(row) for row in rows]

    def update_portfolio(self, symbol: str, quantity: float, avg_cost: float, sector: str = ""):
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO portfolio (symbol, quantity, avg_cost, sector, updated_at)
                   VALUES (?, ?, ?, ?, datetime('now'))""",
                (symbol, quantity, avg_cost, sector)
            )

    # ─── Dashboard Stats ─────────────────────────────────────

    def get_dashboard_stats(self) -> dict:
        with self._get_conn() as conn:
            total_stocks = conn.execute("SELECT COUNT(*) FROM stocks WHERE is_active = 1").fetchone()[0]
            total_reports = conn.execute("SELECT COUNT(*) FROM analysis_reports").fetchone()[0]
            total_signals = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]

            # Recent signal distribution
            recent_signals = conn.execute(
                """SELECT signal, COUNT(*) as count FROM signals
                   WHERE timestamp >= datetime('now', '-7 days')
                   GROUP BY signal"""
            ).fetchall()

            signal_dist = {row["signal"]: row["count"] for row in recent_signals}

            # Latest signals
            latest = conn.execute(
                "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()

            return {
                "total_stocks": total_stocks,
                "total_reports": total_reports,
                "total_signals": total_signals,
                "signal_distribution_7d": signal_dist,
                "latest_signals": [dict(row) for row in latest],
            }
