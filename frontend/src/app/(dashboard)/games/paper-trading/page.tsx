'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, DollarSign, Target } from 'lucide-react';

const STRATEGIES = [
  { id: 'portfolio_builder', label: 'Portfolio Builder', description: 'Focus on diversification' },
  { id: 'day_trader', label: 'Day Trader', description: 'Short-term trading focus' },
  { id: 'value_investor', label: 'Value Investor', description: 'Buy undervalued stocks' },
  { id: 'etf_investor', label: 'ETF Investor', description: 'Long-term passive investing' },
  { id: 'diversifier', label: 'Diversifier', description: 'Spread across sectors' },
];

const MARKETS = [
  { id: 'india', label: '🇮🇳 Indian Market', description: 'NSE/BSE stocks' },
  { id: 'us', label: '🇺🇸 US Market', description: 'S&P 500 stocks' },
  { id: 'both', label: '🌍 Both Markets', description: 'India + US stocks' },
];

export default function PaperTradingSetup() {
  const [stage, setStage] = useState<'setup' | 'game' | 'loading'>('setup');
  const [market, setMarket] = useState('india');
  const [strategy, setStrategy] = useState('portfolio_builder');
  const [capital, setCapital] = useState(50000);
  const [isHistorical, setIsHistorical] = useState(false);
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState('');

  const handleStartGame = async () => {
    setStage('loading');
    setError('');

    try {
      const response = await fetch('/api/games/paper-trading/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          market,
          strategy,
          initial_capital: capital,
          start_date: isHistorical ? startDate : new Date().toISOString().split('T')[0],
          end_date: isHistorical ? endDate : new Date().toISOString().split('T')[0],
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setStage('game');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setStage('setup');
    }
  };

  if (stage === 'game' && sessionId) {
    return <PaperTradingGame sessionId={sessionId} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <Link href="/dashboard/games" className="mb-6 flex items-center gap-2 w-fit text-slate-600 hover:text-slate-900">
        <ArrowLeft size={20} />
        Back to Games
      </Link>

      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-block p-3 bg-blue-100 rounded-full mb-4">
            <TrendingUp className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Paper Trading</h1>
          <p className="text-lg text-slate-600">
            Learn stock trading with virtual money. No risk, real lessons!
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 space-y-8">
          {/* Market Selection */}
          <div>
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">1</span>
              Choose Market
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {MARKETS.map(m => (
                <button
                  key={m.id}
                  onClick={() => setMarket(m.id)}
                  className={`p-4 rounded-lg border-2 transition ${
                    market === m.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200 hover:border-blue-300'
                  }`}
                >
                  <div className="text-lg font-semibold">{m.label}</div>
                  <div className="text-sm text-slate-600">{m.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Strategy Selection */}
          <div>
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">2</span>
              Choose Strategy
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {STRATEGIES.map(s => (
                <button
                  key={s.id}
                  onClick={() => setStrategy(s.id)}
                  className={`p-4 rounded-lg border-2 text-left transition ${
                    strategy === s.id
                      ? 'border-green-500 bg-green-50'
                      : 'border-slate-200 hover:border-green-300'
                  }`}
                >
                  <div className="font-semibold text-slate-900">{s.label}</div>
                  <div className="text-sm text-slate-600">{s.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Capital & Period */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <DollarSign size={16} />
                Initial Capital
              </label>
              <input
                type="number"
                value={capital}
                onChange={e => setCapital(Number(e.target.value))}
                min="10000"
                max="1000000"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-slate-500 mt-1">
                {market === 'india' ? '₹' : '$'}
                {capital.toLocaleString()}
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-2">
                <input
                  type="checkbox"
                  checked={isHistorical}
                  onChange={e => setIsHistorical(e.target.checked)}
                  className="mr-2"
                />
                Historical Backtest?
              </label>
              {isHistorical && (
                <div className="space-y-2">
                  <input
                    type="date"
                    value={startDate}
                    onChange={e => setStartDate(e.target.value)}
                    max={endDate}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                  <input
                    type="date"
                    value={endDate}
                    onChange={e => setEndDate(e.target.value)}
                    min={startDate}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={handleStartGame}
            disabled={stage === 'loading'}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
          >
            <Target size={20} />
            {stage === 'loading' ? 'Starting Game...' : 'Start Trading'}
          </button>
        </div>

        {/* Info Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold text-slate-900 mb-2">📊 Real Market Data</h3>
            <p className="text-sm text-slate-600">
              Live stock prices from yfinance or historical data for backtesting
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold text-slate-900 mb-2">🎯 Multi-Dimensional Scoring</h3>
            <p className="text-sm text-slate-600">
              Scores on wealth, diversification, risk management, timing, and strategy
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold text-slate-900 mb-2">🌍 Global Markets</h3>
            <p className="text-sm text-slate-600">
              Trade Indian stocks, US stocks, or both for comparative learning
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function PaperTradingGame({ sessionId }: { sessionId: string }) {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tradeMode, setTradeMode] = useState<'buy' | 'sell' | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState(0);

  useEffect(() => {
    fetchSession();
    const interval = setInterval(fetchSession, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchSession = async () => {
    try {
      const response = await fetch(`/api/games/paper-trading/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setSession(data);
      }
    } catch (err) {
      console.error('Failed to fetch session:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrade = async () => {
    if (!session || !selectedSymbol) return;

    try {
      const response = await fetch(`/api/games/paper-trading/${sessionId}/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: selectedSymbol,
          quantity,
          price,
          side: tradeMode?.toUpperCase(),
        }),
      });

      if (response.ok) {
        await fetchSession();
        setTradeMode(null);
        setSelectedSymbol('');
        setQuantity(1);
      }
    } catch (err) {
      console.error('Trade failed:', err);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!session) {
    return <div className="flex items-center justify-center min-h-screen">Failed to load session</div>;
  }

  const portfolio = session.portfolio || {};
  const cash = portfolio.cash || 0;
  const totalValue = portfolio.total_value || 0;
  const holdings = portfolio.holdings || {};

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">{session.market.toUpperCase()} Trading - {session.strategy}</h1>
            <p className="text-slate-400">Status: {session.status}</p>
          </div>
          <Link href="/dashboard/games/paper-trading/results" className="px-4 py-2 bg-slate-600 rounded-lg hover:bg-slate-700">
            View Results
          </Link>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800 p-4 rounded-lg">
            <span className="text-slate-400">Cash Available</span>
            <p className="text-2xl font-bold">{cash.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
          </div>
          <div className="bg-slate-800 p-4 rounded-lg">
            <span className="text-slate-400">Portfolio Value</span>
            <p className="text-2xl font-bold">{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
          </div>
          <div className="bg-slate-800 p-4 rounded-lg">
            <span className="text-slate-400">P&L</span>
            <p className={`text-2xl font-bold ${(session.metrics?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {(session.metrics?.total_pnl || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </p>
          </div>
          <div className="bg-slate-800 p-4 rounded-lg">
            <span className="text-slate-400">Holdings</span>
            <p className="text-2xl font-bold">{Object.keys(holdings).length}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Trade Executor */}
            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-bold mb-4">Execute Trade</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Symbol</label>
                  <input
                    type="text"
                    placeholder="e.g., RELIANCE.NS or AAPL"
                    value={selectedSymbol}
                    onChange={e => setSelectedSymbol(e.target.value.toUpperCase())}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Qty</label>
                    <input
                      type="number"
                      value={quantity}
                      onChange={e => setQuantity(Math.max(1, Number(e.target.value)))}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Price</label>
                    <input
                      type="number"
                      value={price}
                      onChange={e => setPrice(Math.max(0, Number(e.target.value)))}
                      step="0.01"
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Total</label>
                    <div className="px-4 py-2 bg-slate-700 border border-slate-600 rounded">
                      {(quantity * price).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setTradeMode('buy')}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-semibold"
                  >
                    BUY
                  </button>
                  <button
                    onClick={() => setTradeMode('sell')}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded font-semibold"
                  >
                    SELL
                  </button>
                </div>
              </div>
            </div>

            {/* Holdings Table */}
            {Object.keys(holdings).length > 0 && (
              <div className="bg-slate-800 p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Your Holdings</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b border-slate-600">
                      <tr>
                        <th className="text-left py-2">Symbol</th>
                        <th className="text-right py-2">Qty</th>
                        <th className="text-right py-2">Entry</th>
                        <th className="text-right py-2">Current</th>
                        <th className="text-right py-2">P&L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(holdings).map(([symbol, holding]: [string, any]) => (
                        <tr key={symbol} className="border-b border-slate-700">
                          <td className="py-2">{symbol}</td>
                          <td className="text-right">{holding.quantity}</td>
                          <td className="text-right">{holding.entry_price.toFixed(2)}</td>
                          <td className="text-right">{holding.current_price.toFixed(2)}</td>
                          <td className={`text-right ${holding.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {holding.pnl_percentage.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Trade Modal */}
            {tradeMode && (
              <div className="bg-slate-800 p-6 rounded-lg border-2 border-yellow-500">
                <h3 className="text-lg font-bold mb-4">Confirm {tradeMode.toUpperCase()}</h3>
                <div className="space-y-2 text-sm mb-4">
                  <p>Symbol: <span className="font-semibold">{selectedSymbol}</span></p>
                  <p>Quantity: <span className="font-semibold">{quantity}</span></p>
                  <p>Price: <span className="font-semibold">{price.toFixed(2)}</span></p>
                  <p className="border-t border-slate-600 pt-2 mt-2">
                    Total: <span className="font-bold text-lg">{(quantity * price).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleTrade}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-semibold"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => setTradeMode(null)}
                    className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Quick Stats */}
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="font-bold mb-4">Quick Stats</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span>Max Drawdown:</span>
                  <span className="font-semibold">{(session.metrics?.max_drawdown || 0).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Win Rate:</span>
                  <span className="font-semibold">{(session.metrics?.win_rate || 0).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Help Text */}
        <div className="mt-8 bg-slate-800 p-4 rounded-lg text-sm text-slate-300">
          💡 <strong>Tip:</strong> Use real stock symbols (RELIANCE.NS, TCS.NS for India or AAPL, MSFT for US).
          Enter current prices from live market data for realistic trading experience.
        </div>
      </div>
    </div>
  );
}
