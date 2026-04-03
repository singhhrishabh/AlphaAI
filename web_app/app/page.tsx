import React from 'react';
import { Activity, Briefcase, TrendingUp, ShieldAlert, Cpu } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            AlphaAI
          </h1>
          <p className="text-sm text-gray-400 mt-2">YC-Tier Execution Dashboard</p>
        </div>
        <div className="flex gap-4">
          <button className="px-6 py-2 rounded-full font-medium bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
            Connect Broker
          </button>
          <button className="px-6 py-2 rounded-full font-medium bg-blue-600 hover:bg-blue-500 transition-colors">
            New Analysis
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard icon={<Briefcase size={20} />} title="Portfolio Value" value="$142,400.00" trend="+2.4%" />
        <StatCard icon={<TrendingUp size={20} />} title="Active Signals" value="12" subtitle="3 pending execution" />
        <StatCard icon={<ShieldAlert size={20} />} title="Risk Level" value="Moderate" subtitle="Sharpe 1.8" />
        <StatCard icon={<Cpu size={20} />} title="AI Confidence" value="High" subtitle="Agents synced" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6 min-h-[400px]">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Activity className="text-blue-400" /> Live Feed
          </h2>
          <div className="flex flex-col gap-4">
            <FeedItem time="Live" ticker="AAPL" action="BUY" info="Fundamental Agent detected undervalued P/E relative to sector growth." />
            <FeedItem time="2m ago" ticker="TSLA" action="HOLD" info="Risk Agent vetoed trade due to high implied volatility." />
          </div>
        </div>
        <div className="glass-card p-6 min-h-[400px]">
          <h2 className="text-xl font-semibold mb-6">Recent Executions</h2>
          <div className="space-y-4 text-sm text-gray-300">
            <p className="p-3 bg-white/5 rounded-lg border border-white/5">Alpaca: BUY 12 MSFT @ $410.20</p>
            <p className="p-3 bg-white/5 rounded-lg border border-white/5">Alpaca: SELL 5 NVDA @ $122.10</p>
            <p className="text-center mt-6 text-gray-500">Backend powered by FastAPI & PostgreSQL</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, trend, subtitle }: any) {
  return (
    <div className="glass-card p-6 flex flex-col justify-between hover:border-blue-500/30 transition-colors cursor-default">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">{icon}</div>
        {trend && <span className="text-green-400 text-sm font-medium">{trend}</span>}
      </div>
      <div>
        <p className="text-gray-400 text-sm">{title}</p>
        <h3 className="text-2xl font-bold mt-1">{value}</h3>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}

function FeedItem({ time, ticker, action, info }: any) {
  const actionColor = action === 'BUY' ? 'text-green-400 border-green-400/20 bg-green-400/10' : 
                      action === 'SELL' ? 'text-red-400 border-red-400/20 bg-red-400/10' : 
                      'text-yellow-400 border-yellow-400/20 bg-yellow-400/10';

  return (
    <div className="flex gap-4 items-start p-4 bg-white/5 rounded-xl border border-white/5">
      <div className={`px-2 py-1 text-xs font-bold rounded-md border ${actionColor}`}>
        {action}
      </div>
      <div>
        <div className="flex items-baseline gap-2">
          <span className="font-bold">{ticker}</span>
          <span className="text-xs text-gray-500">{time}</span>
        </div>
        <p className="text-sm text-gray-300 mt-1">{info}</p>
      </div>
    </div>
  );
}
