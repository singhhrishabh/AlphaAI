/**
 * AlphaAI — Frontend Application
 * Static demo version for GitHub Pages with built-in demo data.
 * When backend is available, connects to API. Otherwise shows demo data.
 */

// ─── Configuration ───────────────────────────────────────
const CONFIG = {
    apiUrl: localStorage.getItem('alphaai_api_url') || 'http://localhost:8000',
    watchlist: (localStorage.getItem('alphaai_watchlist') || 'AAPL,MSFT,GOOGL,NVDA,TSLA,AMZN').split(','),
    refreshInterval: 30000,
    isDemo: false,
};

// ─── Demo Data ───────────────────────────────────────────
const DEMO_DATA = {
    dashboard: {
        total_stocks: 10,
        total_reports: 24,
        total_signals: 47,
        signal_distribution_7d: { BUY: 5, STRONG_BUY: 2, HOLD: 8, SELL: 3, STRONG_SELL: 1 },
        latest_signals: [
            { symbol: "NVDA", signal: "STRONG_BUY", confidence: 82.5, timestamp: new Date(Date.now() - 3600000).toISOString() },
            { symbol: "AAPL", signal: "HOLD", confidence: 57.5, timestamp: new Date(Date.now() - 7200000).toISOString() },
            { symbol: "MSFT", signal: "BUY", confidence: 71.3, timestamp: new Date(Date.now() - 10800000).toISOString() },
            { symbol: "TSLA", signal: "SELL", confidence: 64.0, timestamp: new Date(Date.now() - 14400000).toISOString() },
            { symbol: "GOOGL", signal: "BUY", confidence: 68.9, timestamp: new Date(Date.now() - 18000000).toISOString() },
            { symbol: "AMZN", signal: "HOLD", confidence: 52.1, timestamp: new Date(Date.now() - 21600000).toISOString() },
            { symbol: "META", signal: "BUY", confidence: 73.4, timestamp: new Date(Date.now() - 25200000).toISOString() },
            { symbol: "JPM", signal: "HOLD", confidence: 48.7, timestamp: new Date(Date.now() - 28800000).toISOString() },
        ],
        recent_analyses: [{ confidence: 68 }],
    },
    analysis: {
        symbol: "AAPL",
        company_name: "Apple Inc.",
        sector: "Technology",
        industry: "Consumer Electronics",
        current_price: 248.80,
        market_cap: 3780000000000,
        signal: "HOLD",
        confidence: 57.5,
        overall_score: -3.3,
        fundamental_score: 15.0,
        technical_score: 22.4,
        sentiment_score: 3.3,
        risk_score: -27.8,
        summary: "Portfolio decision for AAPL: HOLD with 57% confidence. Weighted score: -3.3. Fundamentals show solid profitability with 26.4% profit margin and 1.57 ROE. Technical indicators show mixed signals with RSI at 48.2 (neutral). News sentiment is slightly positive but risk metrics flag high valuation with P/E at 38.5.",
        elapsed_seconds: 4.5,
        news_count: 15,
        timestamp: new Date().toISOString(),
        final_decision: {
            signal: "HOLD",
            confidence: 57.5,
            reasoning: "Portfolio decision for AAPL: HOLD with 57% confidence. Weighted score: -3.3. Fundamentals show solid profitability with 26.4% profit margin and 1.57 ROE, but elevated valuation (P/E: 38.5, PEG: 3.26). Technical indicators are mixed — price above SMA 200 (bullish) but RSI neutral at 48.2. News sentiment is slightly positive with 8 positive vs 3 negative articles. Risk assessment flags high beta (1.24) and significant recent drawdown. Agent consensus: 0 Buy / 3 Hold / 1 Sell."
        },
        agent_signals: {
            "Fundamental Analyst": {
                signal: "HOLD", confidence: 57.5, score: 15.0,
                reasoning: "Apple shows strong fundamentals with $3.78T market cap, 26.4% profit margins, and 157% ROE. However, the stock appears richly valued with a trailing P/E of 38.5 and PEG ratio of 3.26, suggesting growth expectations are already priced in. Free cash flow remains robust at $105B, providing a solid foundation.",
                key_metrics: { "P/E Ratio": "38.50", "PEG Ratio": "3.26", "ROE": "157.4%", "Profit Margin": "26.4%", "Revenue Growth": "4.1%", "Debt/Equity": "151.86", "Free Cash Flow": "$105.61B", "Dividend Yield": "0.44%" },
                risks: ["Elevated valuation", "High debt-to-equity ratio"],
                catalysts: ["Strong profitability", "Massive free cash flow"]
            },
            "Technical Analyst": {
                signal: "BUY", confidence: 62.0, score: 22.4,
                reasoning: "AAPL shows a constructive technical setup. Price is trading above the 200-day SMA ($231.45), confirming a long-term uptrend. The Golden Cross (50 SMA > 200 SMA) is intact. RSI at 48.2 is neutral with room to run. MACD recently crossed bullish. Bollinger Bands show the stock near the middle band, suggesting moderate volatility.",
                key_metrics: { "Current Price": "$248.80", "SMA 20": "$242.56", "SMA 50": "$238.12", "SMA 200": "$231.45", "RSI (14)": "48.2", "MACD": "Bullish ✅", "MA Cross": "Golden Cross ✅", "Trend": "Uptrend 📈" },
                risks: ["Near-term overbought risk"],
                catalysts: ["Golden Cross", "Price above 200 SMA", "MACD bullish crossover"]
            },
            "Sentiment Analyst": {
                signal: "HOLD", confidence: 41.6, score: 3.3,
                reasoning: "Sentiment analysis of AAPL shows a mildly positive outlook. Analyzed 15 news articles: 8 positive, 3 negative, 4 neutral. Average sentiment compound score of 0.033, slightly favoring bulls. Headlines about new product launches provide upside catalyst, while supply chain concerns weigh on sentiment.",
                key_metrics: { "Articles Analyzed": "15", "Avg Score": "0.033", "Positive": "8", "Negative": "3", "Neutral": "4", "Overall Sentiment": "Neutral", "Most Bullish": "Apple's AI strategy could unlock $30B+ in new revenue", "Most Bearish": "Apple faces regulatory headwinds in EU market" },
                risks: ["Regulatory headwinds", "Mixed sentiment"],
                catalysts: ["AI strategy potential", "New product pipeline"]
            },
            "Risk Manager": {
                signal: "SELL", confidence: 61.1, score: -27.8,
                reasoning: "Risk assessment for AAPL flags several concerns. Beta of 1.24 indicates above-market volatility. Annualized volatility at 28.3% is moderate but the debt-to-equity ratio of 151.86 is elevated. Max drawdown in the past year was -18.4%. Sharpe ratio of 0.72 shows positive but modest risk-adjusted returns. Recommend position size of 7.0% max.",
                key_metrics: { "Beta": "1.24", "Annualized Volatility": "28.3%", "Max Drawdown (1Y)": "-18.4%", "Sharpe Ratio": "0.72", "VaR (95%, daily)": "-2.14%", "Volatility Level": "Moderate", "Recommended Position Size": "7.0%" },
                risks: ["High leverage (D/E: 151.86)", "Significant drawdown risk (-18.4%)"],
                catalysts: ["Use stop-loss orders", "Limit position to 7.0%"]
            }
        }
    }
};

// ─── State ───────────────────────────────────────────────
let currentPage = 'dashboard';
let analysisCache = {};

// ─── API Client ──────────────────────────────────────────
const api = {
    async get(endpoint) {
        try {
            const res = await fetch(`${CONFIG.apiUrl}${endpoint}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            CONFIG.isDemo = false;
            return await res.json();
        } catch (e) {
            CONFIG.isDemo = true;
            return null;
        }
    },
    async post(endpoint, data) {
        try {
            const res = await fetch(`${CONFIG.apiUrl}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (e) {
            return null;
        }
    },
};

// ─── Navigation ──────────────────────────────────────────
function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navigateTo(link.dataset.page);
        });
    });
    document.getElementById('menu-toggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });
}

function navigateTo(page) {
    currentPage = page;
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`)?.classList.add('active');
    const titles = { dashboard: 'Dashboard', analyze: 'Stock Analysis', signals: 'Trading Signals', portfolio: 'Portfolio', reports: 'Reports', settings: 'Settings' };
    document.getElementById('page-title').textContent = titles[page] || page;
    document.getElementById('sidebar').classList.remove('open');
    if (page === 'signals') loadSignals();
    if (page === 'reports') loadReports();
    if (page === 'dashboard') loadDashboard();
}

// ─── Dashboard ───────────────────────────────────────────
async function loadDashboard() {
    let data = await api.get('/api/dashboard');
    if (!data) data = DEMO_DATA.dashboard;

    animateCounter('stat-stocks', data.total_stocks || 0);
    animateCounter('stat-signals', data.total_signals || 0);
    animateCounter('stat-reports', data.total_reports || 0);

    const dist = data.signal_distribution_7d || {};
    const buyCount = (dist.BUY || 0) + (dist.STRONG_BUY || 0);
    const holdCount = dist.HOLD || 0;
    const sellCount = (dist.SELL || 0) + (dist.STRONG_SELL || 0);
    const total = buyCount + holdCount + sellCount || 1;

    setTimeout(() => {
        document.getElementById('dist-buy').style.width = `${(buyCount / total) * 100}%`;
        document.getElementById('dist-hold').style.width = `${(holdCount / total) * 100}%`;
        document.getElementById('dist-sell').style.width = `${(sellCount / total) * 100}%`;
    }, 200);
    document.getElementById('dist-buy-count').textContent = buyCount;
    document.getElementById('dist-hold-count').textContent = holdCount;
    document.getElementById('dist-sell-count').textContent = sellCount;

    renderSignalsList('dashboard-signals', data.latest_signals || []);

    if (data.recent_analyses?.length) {
        const avg = data.recent_analyses.reduce((a, r) => a + (r.confidence || 0), 0) / data.recent_analyses.length;
        document.getElementById('stat-accuracy').textContent = `${avg.toFixed(0)}%`;
    }
    renderWatchlist();
}

function renderWatchlist() {
    const container = document.getElementById('dashboard-watchlist');
    container.innerHTML = CONFIG.watchlist.map(ticker => `
        <div class="watchlist-item" onclick="analyzeFromWatchlist('${ticker}')">
            <span class="watchlist-ticker">${ticker}</span>
            <button class="watchlist-btn">Analyze →</button>
        </div>
    `).join('');
}

function renderSignalsList(containerId, signals) {
    const container = document.getElementById(containerId);
    if (!signals.length) {
        container.innerHTML = `<div class="empty-state"><span class="empty-icon">📡</span><p>No signals yet. Analyze a stock to get started!</p></div>`;
        return;
    }
    container.innerHTML = signals.map(s => {
        const signalClass = getSignalClass(s.signal);
        const confClass = s.confidence > 60 ? 'high' : s.confidence > 30 ? 'medium' : 'low';
        const time = s.timestamp ? new Date(s.timestamp).toLocaleString() : '';
        return `
            <div class="signal-item">
                <div class="signal-left">
                    <span class="signal-ticker">${s.symbol}</span>
                    <span class="signal-badge ${signalClass}">${s.signal}</span>
                </div>
                <div class="signal-right">
                    <span>${s.confidence?.toFixed(0) || 0}%</span>
                    <div class="confidence-bar">
                        <div class="confidence-fill ${confClass}" style="width: ${s.confidence || 0}%"></div>
                    </div>
                    <span style="font-size:11px; color: var(--text-muted);">${time}</span>
                </div>
            </div>
        `;
    }).join('');
}

// ─── Stock Analysis ──────────────────────────────────────
function initAnalyze() {
    document.getElementById('analyze-btn').addEventListener('click', () => runAnalysis(document.getElementById('analyze-ticker').value));
    document.getElementById('analyze-ticker').addEventListener('keypress', (e) => { if (e.key === 'Enter') runAnalysis(document.getElementById('analyze-ticker').value); });
    document.getElementById('quick-analyze-btn').addEventListener('click', () => runAnalysis(document.getElementById('quick-ticker').value));
    document.getElementById('quick-ticker').addEventListener('keypress', (e) => { if (e.key === 'Enter') runAnalysis(document.getElementById('quick-ticker').value); });
}

async function runAnalysis(ticker) {
    ticker = ticker.trim().toUpperCase();
    if (!ticker) { showToast('Please enter a ticker symbol', 'error'); return; }

    navigateTo('analyze');
    document.getElementById('analyze-ticker').value = ticker;
    document.getElementById('analysis-results').classList.add('hidden');
    document.getElementById('analysis-loading').classList.remove('hidden');
    showToast(`🚀 Analyzing ${ticker}...`, 'info');

    const useLlm = document.getElementById('use-llm')?.checked ?? true;
    let result = await api.post('/api/analyze', { ticker, use_llm: useLlm });

    // If API unavailable, show demo after a brief delay
    if (!result) {
        await new Promise(r => setTimeout(r, 2500));
        result = JSON.parse(JSON.stringify(DEMO_DATA.analysis));
        result.symbol = ticker;
        result.company_name = ticker;
        showToast(`ℹ️ Showing demo data for ${ticker} (backend not connected)`, 'info');
    }

    document.getElementById('analysis-loading').classList.add('hidden');
    analysisCache[ticker] = result;
    renderAnalysisResults(result);
    showToast(`✅ ${ticker} analysis complete: ${result.signal}`, 'success');
}

function renderAnalysisResults(result) {
    const container = document.getElementById('analysis-results');
    container.classList.remove('hidden');
    const decision = result.final_decision || {};
    const signal = decision.signal || result.signal || 'HOLD';
    const signalClass = signal.includes('BUY') ? 'buy' : signal.includes('SELL') ? 'sell' : 'hold';
    const borderClass = signal.includes('BUY') ? 'buy-signal' : signal.includes('SELL') ? 'sell-signal' : 'hold-signal';

    document.getElementById('analysis-summary').className = `glass-card analysis-summary ${borderClass}`;
    document.getElementById('analysis-summary').innerHTML = `
        <div class="summary-signal ${signalClass}">${signal.replace('_', ' ')}</div>
        <div class="summary-confidence">Confidence: <strong>${(decision.confidence || 0).toFixed(0)}%</strong> • Score: <strong>${(result.overall_score || 0).toFixed(1)}</strong></div>
        <div class="summary-reasoning">${decision.reasoning || result.summary || 'Analysis complete.'}</div>
        <div class="summary-meta">
            <div class="meta-item"><div class="meta-value">${result.current_price ? '$' + result.current_price.toFixed(2) : 'N/A'}</div><div class="meta-label">Current Price</div></div>
            <div class="meta-item"><div class="meta-value">${result.sector || 'N/A'}</div><div class="meta-label">Sector</div></div>
            <div class="meta-item"><div class="meta-value">${formatMarketCap(result.market_cap)}</div><div class="meta-label">Market Cap</div></div>
            <div class="meta-item"><div class="meta-value">${result.news_count || 0}</div><div class="meta-label">News Analyzed</div></div>
            <div class="meta-item"><div class="meta-value">${result.elapsed_seconds || 0}s</div><div class="meta-label">Analysis Time</div></div>
        </div>`;

    const agents = result.agent_signals || {};
    document.getElementById('agents-grid').innerHTML = Object.entries(agents).map(([name, sig]) => {
        const sc = sig.score || 0;
        const color = sc > 0 ? 'var(--accent-green)' : sc < 0 ? 'var(--accent-red)' : 'var(--accent-amber)';
        const metrics = sig.key_metrics ? Object.entries(sig.key_metrics).slice(0, 8).map(([k, v]) =>
            `<div class="metric-row"><span class="metric-key">${k}</span><span class="metric-val">${v}</span></div>`
        ).join('') : '';
        return `
            <div class="glass-card agent-card">
                <div class="agent-card-header"><span class="agent-name">${getAgentIcon(name)} ${name}</span><span class="signal-badge ${getSignalClass(sig.signal)}">${sig.signal}</span></div>
                <div class="agent-score"><span style="font-family:var(--font-mono);font-size:14px;min-width:50px">${sc.toFixed(1)}</span><div class="score-bar"><div class="score-fill" style="width:${Math.abs(sc)}%;background:${color}"></div></div><span style="font-size:13px;color:var(--text-muted)">${(sig.confidence||0).toFixed(0)}%</span></div>
                <div class="agent-reasoning">${sig.reasoning || ''}</div>
                ${metrics ? `<div class="agent-metrics">${metrics}</div>` : ''}
            </div>`;
    }).join('');
}

// ─── Signals & Reports ───────────────────────────────────
async function loadSignals() {
    let data = await api.get('/api/signals?limit=50');
    if (!data) data = DEMO_DATA.dashboard.latest_signals;
    renderSignalsList('signals-table', data);
}

async function loadReports() {
    let data = await api.get('/api/reports?limit=30');
    const container = document.getElementById('reports-list');
    if (!data) data = DEMO_DATA.dashboard.latest_signals.map(s => ({ ...s, overall_score: (Math.random() * 60 - 20).toFixed(1) }));
    if (!data?.length) { container.innerHTML = `<div class="empty-state"><span class="empty-icon">📄</span><p>No reports yet.</p></div>`; return; }
    container.innerHTML = data.map(r => `
        <div class="signal-item" style="cursor:pointer" onclick="viewReport('${r.symbol}')">
            <div class="signal-left"><span class="signal-ticker">${r.symbol}</span><span class="signal-badge ${getSignalClass(r.signal)}">${r.signal || 'N/A'}</span></div>
            <div class="signal-right"><span>Score: ${r.overall_score || '—'}</span><span>${(r.confidence||0).toFixed(0)}%</span><span style="font-size:11px">${r.timestamp ? new Date(r.timestamp).toLocaleDateString() : ''}</span></div>
        </div>`).join('');
}

function viewReport(ticker) {
    if (analysisCache[ticker]) { navigateTo('analyze'); renderAnalysisResults(analysisCache[ticker]); }
    else { navigateTo('analyze'); document.getElementById('analyze-ticker').value = ticker; runAnalysis(ticker); }
}

// ─── Settings ────────────────────────────────────────────
function initSettings() {
    document.getElementById('setting-api-url').value = CONFIG.apiUrl;
    document.getElementById('setting-watchlist').value = CONFIG.watchlist.join(',');
    document.getElementById('save-settings').addEventListener('click', () => {
        CONFIG.apiUrl = document.getElementById('setting-api-url').value.trim();
        CONFIG.watchlist = document.getElementById('setting-watchlist').value.split(',').map(t => t.trim().toUpperCase()).filter(Boolean);
        localStorage.setItem('alphaai_api_url', CONFIG.apiUrl);
        localStorage.setItem('alphaai_watchlist', CONFIG.watchlist.join(','));
        showToast('✅ Settings saved!', 'success');
        checkApiStatus();
    });
    document.getElementById('refresh-signals')?.addEventListener('click', loadSignals);
    document.getElementById('refresh-reports')?.addEventListener('click', loadReports);
}

// ─── Utilities ───────────────────────────────────────────
function getSignalClass(s) { if (!s) return 'hold'; s = s.toLowerCase().replace('_','-'); return s.includes('buy') ? (s.includes('strong') ? 'strong-buy' : 'buy') : s.includes('sell') ? (s.includes('strong') ? 'strong-sell' : 'sell') : 'hold'; }
function getAgentIcon(n) { return {'Fundamental Analyst':'🔍','Technical Analyst':'📊','Sentiment Analyst':'📰','Risk Manager':'⚠️','Portfolio Manager':'🧠'}[n] || '🤖'; }
function formatMarketCap(v) { if (!v) return 'N/A'; return v >= 1e12 ? `$${(v/1e12).toFixed(2)}T` : v >= 1e9 ? `$${(v/1e9).toFixed(2)}B` : v >= 1e6 ? `$${(v/1e6).toFixed(2)}M` : `$${v}`; }
function animateCounter(id, target) { const el = document.getElementById(id); if (!el) return; const start = parseInt(el.textContent)||0, dur = 1000, st = performance.now(); function u(t) { const p = Math.min((t-st)/dur,1); el.textContent = Math.round(start + (target-start) * (1-Math.pow(1-p,3))); if(p<1) requestAnimationFrame(u); } requestAnimationFrame(u); }

function showToast(message, type = 'info') {
    const c = document.getElementById('toast-container'), t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span>${{success:'✅',error:'❌',info:'ℹ️'}[type]||''}</span><span>${message}</span>`;
    c.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; }, 4000);
    setTimeout(() => t.remove(), 4500);
}

function updateClock() { const el = document.getElementById('time-display'); if (el) el.textContent = new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit', second:'2-digit' }); }

async function checkApiStatus() {
    const el = document.getElementById('api-status'), dot = el.querySelector('.status-dot'), txt = el.querySelector('span:last-child');
    try { const r = await fetch(`${CONFIG.apiUrl}/api/health`); if (r.ok) { dot.className='status-dot online'; txt.textContent='Connected'; } else { dot.className='status-dot offline'; txt.textContent='Demo Mode'; } }
    catch { dot.className = 'status-dot'; txt.textContent = 'Demo Mode'; CONFIG.isDemo = true; }
}

window.analyzeFromWatchlist = function(ticker) { navigateTo('analyze'); document.getElementById('analyze-ticker').value = ticker; runAnalysis(ticker); };

document.addEventListener('DOMContentLoaded', () => {
    initNavigation(); initAnalyze(); initSettings(); loadDashboard();
    updateClock(); setInterval(updateClock, 1000);
    checkApiStatus(); setInterval(checkApiStatus, CONFIG.refreshInterval);
});
