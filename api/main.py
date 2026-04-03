from __future__ import annotations
"""
AlphaAI — FastAPI Backend Server
Serves the analysis engine and dashboard data.
"""
import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from data.database import Database
from agents.orchestrator import Orchestrator
from reports.report_generator import report_generator
from api.models import (
    AnalyzeRequest, AnalyzeMultipleRequest,
    StockAnalysisResponse, DashboardResponse, WatchlistUpdate
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("alphaai.api")

# Global instances
db = Database(config.db_path)
orchestrator = None
analysis_cache = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global orchestrator
    logger.info("🚀 AlphaAI starting up...")
    warnings = config.validate()
    for w in warnings:
        logger.warning(w)

    # Detect deployment environment
    is_render = os.environ.get('RENDER', '') == 'true'
    is_hf = os.environ.get('HF_SPACES', '') == 'true' or os.environ.get('SPACE_ID', '') != ''

    if is_render:
        use_llm = bool(config.llm.openai_api_key or config.llm.groq_api_key or config.llm.google_api_key)
        mode = "full LLM mode" if use_llm else "rule-based mode"
        logger.info(f"☁️  Running on Render — {mode} enabled based on API Keys")
    elif is_hf:
        use_llm = True
        logger.info("🤗 Running on Hugging Face Spaces — full LLM mode enabled!")
    else:
        use_llm = bool(config.llm.openai_api_key or config.llm.groq_api_key or config.llm.google_api_key)
        mode = "full LLM mode" if use_llm else "rule-based mode"
        logger.info(f"💻 Running locally — {mode} enabled")

    orchestrator = Orchestrator(use_llm=use_llm)

    # Add default watchlist stocks to DB
    for ticker in config.data.tickers:
        db.add_stock(ticker)

    logger.info(f"✅ AlphaAI ready! Watchlist: {', '.join(config.data.tickers)}")
    yield
    logger.info("👋 AlphaAI shutting down...")


app = FastAPI(
    title="AlphaAI — AI-Native Hedge Fund",
    description="Multi-agent AI investment analysis platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ───────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


# ─── Analysis Endpoints ──────────────────────────────────

@app.post("/api/analyze")
async def analyze_stock(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Trigger analysis for a single stock."""
    ticker = req.ticker.upper().strip()
    if not ticker:
        raise HTTPException(400, "Ticker is required")

    try:
        result = orchestrator.analyze_stock(ticker)

        # Save to database
        db.save_report({
            "symbol": ticker,
            "report_type": "full",
            "fundamental_score": result.get("fundamental_score"),
            "technical_score": result.get("technical_score"),
            "sentiment_score": result.get("sentiment_score"),
            "risk_score": result.get("risk_score"),
            "overall_score": result.get("overall_score"),
            "signal": result.get("signal"),
            "confidence": result.get("confidence"),
            "summary": result.get("summary"),
            "full_report": "",
            "agent_outputs": result.get("agent_signals", {}),
        })

        db.save_signal({
            "symbol": ticker,
            "signal": result.get("signal", "HOLD"),
            "confidence": result.get("confidence", 0),
            "price_at_signal": result.get("current_price"),
            "reasoning": result.get("summary"),
        })

        # Save report files in background
        background_tasks.add_task(report_generator.save_report, result)

        analysis_cache[ticker] = result
        return result

    except Exception as e:
        logger.error(f"❌ Analysis failed for {ticker}: {e}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.post("/api/analyze/batch")
async def analyze_batch(req: AnalyzeMultipleRequest):
    """Analyze multiple stocks."""
    results = []
    for ticker in req.tickers:
        try:
            result = orchestrator.analyze_stock(ticker.upper())
            db.save_report({
                "symbol": ticker.upper(), "report_type": "full",
                "fundamental_score": result.get("fundamental_score"),
                "technical_score": result.get("technical_score"),
                "sentiment_score": result.get("sentiment_score"),
                "risk_score": result.get("risk_score"),
                "overall_score": result.get("overall_score"),
                "signal": result.get("signal"),
                "confidence": result.get("confidence"),
                "summary": result.get("summary"),
                "full_report": "", "agent_outputs": result.get("agent_signals", {}),
            })
            analysis_cache[ticker.upper()] = result
            results.append(result)
        except Exception as e:
            results.append({"symbol": ticker, "error": str(e)})
    return results


# ─── Data Endpoints ───────────────────────────────────────

@app.get("/api/stocks")
async def get_stocks():
    """Get tracked stocks."""
    return db.get_stocks()


@app.get("/api/stocks/{ticker}/analysis")
async def get_stock_analysis(ticker: str):
    """Get latest analysis for a stock."""
    ticker = ticker.upper()
    if ticker in analysis_cache:
        return analysis_cache[ticker]
    report = db.get_latest_report(ticker)
    if not report:
        raise HTTPException(404, f"No analysis found for {ticker}")
    return report


@app.get("/api/signals")
async def get_signals(limit: int = 50):
    """Get recent signals."""
    return db.get_signals(limit=limit)


@app.get("/api/signals/{ticker}")
async def get_ticker_signals(ticker: str, limit: int = 20):
    """Get signals for a specific ticker."""
    return db.get_signals(symbol=ticker.upper(), limit=limit)


@app.get("/api/reports")
async def get_reports(limit: int = 50):
    """Get historical reports."""
    return db.get_reports(limit=limit)


@app.get("/api/reports/{ticker}")
async def get_ticker_reports(ticker: str, limit: int = 20):
    """Get reports for a specific ticker."""
    return db.get_reports(symbol=ticker.upper(), limit=limit)


@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard overview data."""
    stats = db.get_dashboard_stats()
    stats["recent_analyses"] = list(analysis_cache.values())[-10:]
    return stats


@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio."""
    return db.get_portfolio()


@app.put("/api/watchlist")
async def update_watchlist(req: WatchlistUpdate):
    """Update watchlist."""
    for ticker in req.tickers:
        db.add_stock(ticker.upper().strip())
    return {"status": "ok", "tickers": req.tickers}


# ─── Serve Frontend ──────────────────────────────────────

from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

frontend_dir = Path(__file__).parent.parent / "legacy_frontend"

if frontend_dir.exists():
    # Serve static assets (CSS, JS) from /static
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    logger.info(f"📁 Serving legacy frontend from {frontend_dir}")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")

    # Catch-all: serve index.html for any non-API path (SPA routing)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Prevent catching API routes if they slip through
        if path.startswith("api/"):
            raise HTTPException(404, "API route not found")
        
        # Try to serve the file directly first
        file_path = frontend_dir / path
        if file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html for SPA routing
        return FileResponse(frontend_dir / "index.html")
else:
    @app.get("/", response_class=RedirectResponse)
    async def redirect_to_docs():
        """Redirect to API documentation if frontend is missing."""
        return RedirectResponse(url="/docs")


# ─── Run Server ──────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=True,
    )
