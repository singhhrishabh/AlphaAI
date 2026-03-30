---
title: AlphaAI
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🧠 AlphaAI — AI-Native Hedge Fund Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A multi-agent AI investment analysis system that analyzes market data, fundamentals, sentiment, and risk to generate actionable BUY/SELL/HOLD signals.**

</div>

---

> ⚠️ **Disclaimer:** This project is for **educational and research purposes only**. It does NOT constitute financial advice. Do NOT trade real money based on these signals without professional guidance.

---
For real time Stock Analysis[https://alphaai-mdta.onrender.com/]
For Static WEB page[https://singhhrishabh.github.io/AlphaAI/]

---
## 📸 Dashboard Preview

The platform features a stunning dark-mode glassmorphism web dashboard:

- 📊 **Dashboard** — Portfolio overview, top signals, market sentiment
- 🔍 **Stock Analysis** — Deep-dive into any stock with all AI agent outputs
- 📡 **Signals Feed** — Real-time BUY/SELL/HOLD signals with confidence bars
- 💼 **Portfolio** — Track holdings and performance
- 📄 **Reports** — Browse historical analysis reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   DATA LAYER                         │
│  yfinance │ Finnhub News API │ RSS Feeds             │
│              ↓        ↓           ↓                  │
│         Market Data Pipeline │ News Pipeline         │
│                    ↓                                 │
│              SQLite Database                         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                AI AGENT LAYER                        │
│                                                      │
│  🔍 Fundamental    📊 Technical    📰 Sentiment     │
│     Analyst           Analyst         Analyst        │
│        │                │               │            │
│        └───────┬────────┴───────────────┘            │
│                ▼                                     │
│        ⚠️ Risk Manager                              │
│                ▼                                     │
│        🧠 Portfolio Manager (Final Decision)         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               OUTPUT LAYER                           │
│  Trading Signals │ Analysis Reports │ Web Dashboard  │
└─────────────────────────────────────────────────────┘
```

## 🤖 AI Agents

| Agent | Role |
|:---|:---|
| 🔍 **Fundamental Analyst** | P/E, ROE, revenue growth, debt analysis, DCF valuation |
| 📊 **Technical Analyst** | RSI, MACD, SMA, Bollinger Bands, volume, trend analysis |
| 📰 **Sentiment Analyst** | NLP analysis of news using VADER + FinBERT |
| ⚠️ **Risk Manager** | Volatility, Sharpe ratio, VaR, position sizing, drawdown |
| 🧠 **Portfolio Manager** | Synthesizes all signals → final BUY/SELL/HOLD decision |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/AlphaAI.git
cd AlphaAI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure (Optional)

```bash
cp .env.example .env
# Edit .env to add API keys (optional - works without them!)
```

### 3. Run Analysis (CLI)

```bash
# Analyze a stock (rule-based, no API key needed)
python main.py analyze AAPL --no-llm

# Analyze with AI enhancement (requires LLM API key in .env)
python main.py analyze AAPL

# Analyze your full watchlist
python main.py watchlist --no-llm
```

### 4. Start the Web Dashboard

```bash
python main.py server

# Open in browser:
# Dashboard → http://localhost:8000
# API Docs  → http://localhost:8000/docs
```

---

## 📁 Project Structure

```
AlphaAI/
├── main.py                  # CLI entry point
├── config.py                # Central configuration
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
│
├── agents/                  # AI Agent System
│   ├── base_agent.py        # Abstract base + LLM factory
│   ├── fundamental_agent.py # Financial analysis
│   ├── technical_agent.py   # Technical indicators
│   ├── sentiment_agent.py   # NLP sentiment (VADER/FinBERT)
│   ├── risk_agent.py        # Risk management
│   ├── portfolio_agent.py   # Final decision maker
│   └── orchestrator.py      # Agent coordinator
│
├── data/                    # Data Pipeline
│   ├── market_data.py       # yfinance data fetching
│   ├── news_data.py         # News from multiple sources
│   └── database.py          # SQLite operations
│
├── api/                     # Backend API
│   ├── main.py              # FastAPI server
│   └── models.py            # Pydantic schemas
│
├── reports/                 # Report Generation
│   └── report_generator.py  # Markdown + JSON reports
│
└── frontend/                # Web Dashboard
    ├── index.html           # SPA with 6 pages
    ├── styles.css            # Glassmorphism dark theme
    └── app.js               # Frontend logic
```

---

## ⚙️ Configuration

### LLM Providers (choose one in `.env`)

| Provider | Model | Cost | Setup |
|:---|:---|:---|:---|
| **OpenAI** | GPT-4o | ~$0.01/analysis | Set `OPENAI_API_KEY` |
| **Google Gemini** | Gemini 2.0 Flash | Free tier | Set `GOOGLE_API_KEY` |
| **Groq** | Llama 3.3 70B | Free tier | Set `GROQ_API_KEY` |
| **Ollama** | Local models | Free | Run Ollama locally |
| **None** | Rule-based only | Free | Use `--no-llm` flag |

### Risk Parameters

```env
MAX_POSITION_SIZE=0.10      # Max 10% per stock
MAX_SECTOR_EXPOSURE=0.30    # Max 30% per sector
MAX_PORTFOLIO_STOCKS=20     # Max 20 stocks
RISK_FREE_RATE=0.05         # For Sharpe ratio
```

---

## 🛠️ Tech Stack

| Component | Technology |
|:---|:---|
| Backend | Python, FastAPI |
| AI/LLM | LangChain, OpenAI/Gemini/Groq |
| Market Data | yfinance (free) |
| NLP | VADER, FinBERT |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Design | Glassmorphism, Dark Mode |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

## 👤 Author

Built by **Rishabh** — B.E. ECE, BITS Pilani Dubai Campus  
Project developed as part of independent startup exploration, 2026.


</div>
