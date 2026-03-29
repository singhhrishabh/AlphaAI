/**
 * AlphaAI — Frontend Application
 * Connects to the FastAPI backend and renders the dashboard.
 */

// ─── Configuration ───────────────────────────────────────
const CONFIG = {
    apiUrl: localStorage.getItem('alphaai_api_url') || 'http://localhost:8000',
    watchlist: (localStorage.getItem('alphaai_watchlist') || 'AAPL,MSFT,GOOGL,NVDA,TSLA,AMZN').split(','),
    refreshInterval: 30000,
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
            return await res.json();
        } catch (e) {
            console.error(`API GET ${endpoint} failed:`, e);
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
            console.error(`API POST ${endpoint} failed:`, e);
            return null;
        }
    },
};

// ─── Navigation ──────────────────────────────────────────
function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            navigateTo(page);
        });
    });

    document.getElementById('menu-toggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });
}

function navigateTo(page) {
    currentPage = page;
    // Update nav
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');

    // Update pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`)?.classList.add('active');

    // Update title
    const titles = {
        dashboard: 'Dashboard', analyze: 'Stock Analysis',
        signals: 'Trading Signals', portfolio: 'Portfolio',
        reports: 'Reports', settings: 'Settings',
    };
    document.getElementById('page-title').textContent = titles[page] || page;

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');

    // Load page data
    if (page === 'signals') loadSignals();
    if (page === 'reports') loadReports();
    if (page === 'dashboard') loadDashboard();
}

// ─── Dashboard ───────────────────────────────────────────
async function loadDashboard() {
    const data = await api.get('/api/dashboard');
    if (!data) return;

    animateCounter('stat-stocks', data.total_stocks || 0);
    animateCounter('stat-signals', data.total_signals || 0);
    animateCounter('stat-reports', data.total_reports || 0);

    // Signal distribution
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

    // Latest signals
    renderSignalsList('dashboard-signals', data.latest_signals || []);

    // Recent analyses
    if (data.recent_analyses?.length) {
        const avg = data.recent_analyses.reduce((a, r) => a + (r.confidence || 0), 0) / data.recent_analyses.length;
        document.getElementById('stat-accuracy').textContent = `${avg.toFixed(0)}%`;
    }

    // Watchlist
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
    const btn = document.getElementById('analyze-btn');
    const input = document.getElementById('analyze-ticker');
    const quickBtn = document.getElementById('quick-analyze-btn');
    const quickInput = document.getElementById('quick-ticker');

    btn.addEventListener('click', () => runAnalysis(input.value));
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') runAnalysis(input.value); });
    quickBtn.addEventListener('click', () => runAnalysis(quickInput.value));
    quickInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') runAnalysis(quickInput.value); });
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
    const result = await api.post('/api/analyze', { ticker, use_llm: useLlm });

    document.getElementById('analysis-loading').classList.add('hidden');

    if (!result || result.error) {
        showToast(`❌ Analysis failed: ${result?.error || 'Server unavailable'}`, 'error');
        return;
    }

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

    // Executive Summary
    const summary = document.getElementById('analysis-summary');
    summary.className = `glass-card analysis-summary ${borderClass}`;
    summary.innerHTML = `
        <div class="summary-signal ${signalClass}">${signal.replace('_', ' ')}</div>
        <div class="summary-confidence">
            Confidence: <strong>${(decision.confidence || 0).toFixed(0)}%</strong> • Score: <strong>${(result.overall_score || 0).toFixed(1)}</strong>
        </div>
        <div class="summary-reasoning">${decision.reasoning || result.summary || 'Analysis complete.'}</div>
        <div class="summary-meta">
            <div class="meta-item">
                <div class="meta-value">${result.current_price ? '$' + result.current_price.toFixed(2) : 'N/A'}</div>
                <div class="meta-label">Current Price</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">${result.sector || 'N/A'}</div>
                <div class="meta-label">Sector</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">${formatMarketCap(result.market_cap)}</div>
                <div class="meta-label">Market Cap</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">${result.news_count || 0}</div>
                <div class="meta-label">News Analyzed</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">${result.elapsed_seconds || 0}s</div>
                <div class="meta-label">Analysis Time</div>
            </div>
        </div>
    `;

    // Agent Cards
    const agentsGrid = document.getElementById('agents-grid');
    const agents = result.agent_signals || {};
    agentsGrid.innerHTML = Object.entries(agents).map(([name, sig]) => {
        const agentSignalClass = getSignalClass(sig.signal);
        const score = sig.score || 0;
        const scoreWidth = Math.abs(score);
        const scoreColor = score > 0 ? 'var(--accent-green)' : score < 0 ? 'var(--accent-red)' : 'var(--accent-amber)';

        const metricsHtml = sig.key_metrics ? Object.entries(sig.key_metrics).slice(0, 8).map(([k, v]) =>
            `<div class="metric-row"><span class="metric-key">${k}</span><span class="metric-val">${v}</span></div>`
        ).join('') : '';

        return `
            <div class="glass-card agent-card">
                <div class="agent-card-header">
                    <span class="agent-name">${getAgentIcon(name)} ${name}</span>
                    <span class="signal-badge ${agentSignalClass}">${sig.signal}</span>
                </div>
                <div class="agent-score">
                    <span style="font-family: var(--font-mono); font-size: 14px; min-width: 50px;">${score.toFixed(1)}</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${scoreWidth}%; background: ${scoreColor};"></div>
                    </div>
                    <span style="font-size: 13px; color: var(--text-muted);">${(sig.confidence || 0).toFixed(0)}%</span>
                </div>
                <div class="agent-reasoning">${sig.reasoning || 'No reasoning provided.'}</div>
                ${metricsHtml ? `<div class="agent-metrics">${metricsHtml}</div>` : ''}
            </div>
        `;
    }).join('');
}

// ─── Signals Page ────────────────────────────────────────
async function loadSignals() {
    const data = await api.get('/api/signals?limit=50');
    if (!data) return;
    renderSignalsList('signals-table', data);
}

// ─── Reports Page ────────────────────────────────────────
async function loadReports() {
    const data = await api.get('/api/reports?limit=30');
    const container = document.getElementById('reports-list');
    if (!data?.length) {
        container.innerHTML = `<div class="empty-state"><span class="empty-icon">📄</span><p>No reports yet.</p></div>`;
        return;
    }

    container.innerHTML = data.map(r => {
        const signalClass = getSignalClass(r.signal);
        return `
            <div class="signal-item" style="cursor: pointer;" onclick="viewReport('${r.symbol}')">
                <div class="signal-left">
                    <span class="signal-ticker">${r.symbol}</span>
                    <span class="signal-badge ${signalClass}">${r.signal || 'N/A'}</span>
                </div>
                <div class="signal-right">
                    <span>Score: ${(r.overall_score || 0).toFixed(1)}</span>
                    <span>${(r.confidence || 0).toFixed(0)}%</span>
                    <span style="font-size:11px;">${r.timestamp ? new Date(r.timestamp).toLocaleDateString() : ''}</span>
                </div>
            </div>
        `;
    }).join('');
}

function viewReport(ticker) {
    if (analysisCache[ticker]) {
        navigateTo('analyze');
        renderAnalysisResults(analysisCache[ticker]);
    }
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

// ─── Utility Functions ───────────────────────────────────
function getSignalClass(signal) {
    if (!signal) return 'hold';
    const s = signal.toLowerCase().replace('_', '-');
    if (s.includes('buy')) return s.includes('strong') ? 'strong-buy' : 'buy';
    if (s.includes('sell')) return s.includes('strong') ? 'strong-sell' : 'sell';
    return 'hold';
}

function getAgentIcon(name) {
    const icons = {
        'Fundamental Analyst': '🔍',
        'Technical Analyst': '📊',
        'Sentiment Analyst': '📰',
        'Risk Manager': '⚠️',
        'Portfolio Manager': '🧠',
    };
    return icons[name] || '🤖';
}

function formatMarketCap(val) {
    if (!val) return 'N/A';
    if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
    if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
    if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
    return `$${val.toFixed(0)}`;
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const start = parseInt(el.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + (target - start) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; }, 4000);
    setTimeout(() => toast.remove(), 4500);
}

function updateClock() {
    const el = document.getElementById('time-display');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
}

async function checkApiStatus() {
    const statusEl = document.getElementById('api-status');
    const dot = statusEl.querySelector('.status-dot');
    const text = statusEl.querySelector('span:last-child');

    try {
        const res = await fetch(`${CONFIG.apiUrl}/api/health`);
        if (res.ok) {
            dot.className = 'status-dot online';
            text.textContent = 'Connected';
        } else {
            dot.className = 'status-dot offline';
            text.textContent = 'API Error';
        }
    } catch {
        dot.className = 'status-dot offline';
        text.textContent = 'Disconnected';
    }
}

// Global function for watchlist clicks
window.analyzeFromWatchlist = function(ticker) {
    navigateTo('analyze');
    document.getElementById('analyze-ticker').value = ticker;
    runAnalysis(ticker);
};

// ─── Initialize ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAnalyze();
    initSettings();
    loadDashboard();
    updateClock();
    setInterval(updateClock, 1000);
    checkApiStatus();
    setInterval(checkApiStatus, CONFIG.refreshInterval);
});
