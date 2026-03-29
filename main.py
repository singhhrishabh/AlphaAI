from __future__ import annotations
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                    AlphaAI v1.0                              ║
║            AI-Native Hedge Fund Platform                     ║
║                                                              ║
║  Multi-agent AI investment analysis system that analyzes     ║
║  market data, fundamentals, sentiment, and risk to generate  ║
║  actionable BUY/SELL/HOLD signals.                          ║
║                                                              ║
║  ⚠️  FOR EDUCATIONAL/RESEARCH PURPOSES ONLY                 ║
║  This is NOT financial advice. Do NOT trade real money       ║
║  based on these signals without professional guidance.       ║
╚══════════════════════════════════════════════════════════════╝
"""

import argparse
import json
import logging
import sys

from config import config


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_analyze(args):
    """Run analysis on a single stock."""
    from agents.orchestrator import Orchestrator
    from reports.report_generator import report_generator
    from data.database import Database

    db = Database(config.db_path)
    orch = Orchestrator(use_llm=not args.no_llm)

    print(f"\n🚀 Analyzing {args.ticker}...\n")
    result = orch.analyze_stock(args.ticker)

    # Save report
    report_files = report_generator.save_report(result)

    # Save to DB
    db.save_report({
        "symbol": result["symbol"],
        "fundamental_score": result.get("fundamental_score"),
        "technical_score": result.get("technical_score"),
        "sentiment_score": result.get("sentiment_score"),
        "risk_score": result.get("risk_score"),
        "overall_score": result.get("overall_score"),
        "signal": result.get("signal"),
        "confidence": result.get("confidence"),
        "summary": result.get("summary"),
        "full_report": report_files.get("content", ""),
        "agent_outputs": result.get("agent_signals", {}),
    })

    # Print summary
    decision = result.get("final_decision", {})
    signal = decision.get("signal", "HOLD")
    emojis = {"STRONG_BUY": "🟢🟢", "BUY": "🟢", "HOLD": "🟡", "SELL": "🔴", "STRONG_SELL": "🔴🔴"}

    print(f"\n{'='*60}")
    print(f"  {emojis.get(signal, '⚪')} {result.get('company_name', args.ticker)} ({args.ticker})")
    print(f"  Signal: {signal} | Confidence: {decision.get('confidence', 0):.0f}%")
    print(f"  Score: {result.get('overall_score', 0):.1f} | Price: ${result.get('current_price', 'N/A')}")
    print(f"{'='*60}")
    print(f"\n  📊 Fundamental: {result.get('fundamental_score', 'N/A')}")
    print(f"  📈 Technical:   {result.get('technical_score', 'N/A')}")
    print(f"  📰 Sentiment:   {result.get('sentiment_score', 'N/A')}")
    print(f"  ⚠️  Risk:        {result.get('risk_score', 'N/A')}")
    print(f"\n  💡 {decision.get('reasoning', 'N/A')}")
    print(f"\n  📄 Report: {report_files.get('markdown', 'N/A')}")
    print(f"{'='*60}\n")


def cmd_watchlist(args):
    """Analyze all stocks in watchlist."""
    from agents.orchestrator import Orchestrator
    orch = Orchestrator(use_llm=not args.no_llm)
    results = orch.analyze_watchlist()

    print(f"\n{'='*70}")
    print(f"  📋 WATCHLIST ANALYSIS RESULTS")
    print(f"{'='*70}")

    for r in results:
        if "error" in r:
            print(f"  ❌ {r['symbol']}: {r['error']}")
            continue
        signal = r.get("signal", "HOLD")
        emojis = {"STRONG_BUY": "🟢🟢", "BUY": "🟢", "HOLD": "🟡", "SELL": "🔴", "STRONG_SELL": "🔴🔴"}
        print(f"  {emojis.get(signal, '⚪')} {r.get('symbol', '???'):6s} | {signal:11s} | "
              f"Conf: {r.get('confidence', 0):5.1f}% | Score: {r.get('overall_score', 0):6.1f} | "
              f"${r.get('current_price', 'N/A')}")

    print(f"{'='*70}\n")


def cmd_server(args):
    """Start the API server."""
    import uvicorn
    print("\n🚀 Starting AlphaAI API server...")
    print(f"   Backend:  http://localhost:{config.server.port}")
    print(f"   Docs:     http://localhost:{config.server.port}/docs")
    print(f"   Frontend: {config.server.frontend_url}\n")
    uvicorn.run(
        "api.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=args.reload,
    )


def main():
    parser = argparse.ArgumentParser(
        description="AlphaAI — AI-Native Hedge Fund Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    sub = parser.add_subparsers(dest="command", help="Commands")

    # analyze
    p_analyze = sub.add_parser("analyze", help="Analyze a single stock")
    p_analyze.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    p_analyze.add_argument("--no-llm", action="store_true", help="Skip LLM, use rule-based only")

    # watchlist
    p_watch = sub.add_parser("watchlist", help="Analyze full watchlist")
    p_watch.add_argument("--no-llm", action="store_true", help="Skip LLM, use rule-based only")

    # server
    p_server = sub.add_parser("server", help="Start the API server")
    p_server.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "watchlist":
        cmd_watchlist(args)
    elif args.command == "server":
        cmd_server(args)
    else:
        parser.print_help()
        print("\n📌 Quick Start:")
        print("  python main.py analyze AAPL        # Analyze Apple")
        print("  python main.py analyze AAPL --no-llm  # Rule-based only (no API key needed)")
        print("  python main.py watchlist            # Analyze full watchlist")
        print("  python main.py server               # Start API + Dashboard")
        print()


if __name__ == "__main__":
    main()
