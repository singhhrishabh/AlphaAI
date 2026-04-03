'use client';
import React, { useEffect, useState } from 'react';
import { Activity, Briefcase, TrendingUp, ShieldAlert, Cpu } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);

  useEffect(() => {
    // Fetch data from FastAPI backend
    Promise.all([
      fetch('http://localhost:8000/api/dashboard').then(res => res.json()),
      fetch('http://localhost:8000/api/signals?limit=5').then(res => res.json())
    ]).then(([dashboardRes, signalsRes]) => {
      setData(dashboardRes);
      setSignals(signalsRes);
    }).catch(err => console.error("API Error: Maybe FastAPI is offline?", err));
  }, []);

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
        <StatCard icon={<TrendingUp size={20} />} title="Active Signals" value={data?.total_signals || 0} subtitle="Tracked via DB" />
        <StatCard icon={<ShieldAlert size={20} />} title="Tracked Stocks" value={data?.total_stocks || 0} />
        <StatCard icon={<Cpu size={20} />} title="Recent Analyses" value={data?.recent_analyses?.length || 0} subtitle="Agents synced" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6 min-h-[400px]">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Activity className="text-blue-400" /> Live Feed (FastAPI Connected)
          </h2>
          <div className="flex flex-col gap-4">
            {signals.length > 0 ? (
              signals.map((sig, idx) => (
                <FeedItem 
                  key={idx} 
                  time={new Date(sig.timestamp).toLocaleTimeString()} 
                  ticker={sig.symbol} 
                  action={sig.signal} 
                  info={sig.reasoning || "Analyzed by AI."} 
                />
              ))
            ) : (
              <p className="text-gray-500">No signals found. Run via the backend to populate.</p>
            )}
          </div>
        </div>
        <div className="glass-card p-6 min-h-[400px]">
          <h2 className="text-xl font-semibold mb-6">Recent Executions</h2>
          <div className="space-y-4 text-sm text-gray-300">
            <p className="p-3 bg-white/5 rounded-lg border border-white/5">Alpaca: Standby for Execution Webhooks</p>
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
