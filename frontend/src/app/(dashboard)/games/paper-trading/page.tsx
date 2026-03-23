'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, DollarSign, Target, BarChart3 } from 'lucide-react';
import { api } from '@/lib/api/client';
import {
  TradeExecutor,
  PortfolioOverview,
  HoldingsTable,
  PerformanceAnalytics,
  PortfolioAllocation,
  TradeHistory,
  LearningPanel,
} from './components';

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
      const response = await api.post('/games/paper-trading/create', {
        market,
        strategy,
        initial_capital: capital,
        start_date: isHistorical ? startDate : new Date().toISOString().split('T')[0],
        end_date: isHistorical ? endDate : new Date().toISOString().split('T')[0],
      });

      setSessionId(response.data.session_id);
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
          <div className="inline-block p-3 bg-cyan-100 rounded-full mb-4">
            <TrendingUp className="w-8 h-8 text-cyan-600" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Paper Trading</h1>
          <p className="text-lg text-slate-600">
            Learn stock trading with virtual money. No risk, real lessons!
          </p>
        </div>

        <div className="bg-white rounded-lg shadow border border-slate-200 p-8 space-y-8">
          {/* Market Selection */}
          <div>
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <span className="bg-cyan-100 text-cyan-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">1</span>
              Choose Market
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {MARKETS.map(m => (
                <button
                  key={m.id}
                  onClick={() => setMarket(m.id)}
                  className={`p-4 rounded-lg border-2 transition ${
                    market === m.id
                      ? 'border-cyan-500 bg-cyan-50'
                      : 'border-slate-200 bg-white hover:border-cyan-300'
                  }`}
                >
                  <div className="text-lg font-semibold text-slate-900">{m.label}</div>
                  <div className="text-sm text-slate-600">{m.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Strategy Selection */}
          <div>
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <span className="bg-cyan-100 text-cyan-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">2</span>
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
                      : 'border-slate-200 bg-white hover:border-green-300'
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
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
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
            className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-400 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
          >
            <Target size={20} />
            {stage === 'loading' ? 'Starting Game...' : 'Start Trading'}
          </button>
        </div>

        {/* Info Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow border border-slate-200 hover:border-cyan-300 transition">
            <h3 className="font-semibold text-slate-900 mb-2">📊 Real Market Data</h3>
            <p className="text-sm text-slate-600">
              Live stock prices from yfinance or historical data for backtesting
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border border-slate-200 hover:border-cyan-300 transition">
            <h3 className="font-semibold text-slate-900 mb-2">🎯 Multi-Dimensional Scoring</h3>
            <p className="text-sm text-slate-600">
              Scores on wealth, diversification, risk management, timing, and strategy
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border border-slate-200 hover:border-cyan-300 transition">
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
  const [activeTab, setActiveTab] = useState<'portfolio' | 'holdings' | 'performance' | 'market'>('portfolio');

  // Trade executor state
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState(0);
  const [tradeLoading, setTradeLoading] = useState(false);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState('');
  const [lastQuotedSymbol, setLastQuotedSymbol] = useState('');

  useEffect(() => {
    fetchSession();
    const interval = setInterval(fetchSession, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSession = async () => {
    try {
      const response = await api.get(`/games/paper-trading/${sessionId}`);
      setSession(response.data);
    } catch (err) {
      console.error('Failed to fetch session:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchQuote = async (symbolInput?: string) => {
    const symbol = (symbolInput ?? selectedSymbol).trim().toUpperCase();
    if (!symbol) {
      setQuoteError('');
      return;
    }

    setQuoteLoading(true);
    setQuoteError('');

    try {
      const response = await api.get(`/games/paper-trading/${sessionId}/quote`, {
        params: { symbol },
      });
      const quotePrice = Number(response.data?.price ?? 0);
      if (quotePrice > 0) {
        setPrice(quotePrice);
        setLastQuotedSymbol(symbol);
      } else {
        setQuoteError('Price unavailable for this symbol');
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setQuoteError(typeof detail === 'string' ? detail : 'Failed to fetch live price');
    } finally {
      setQuoteLoading(false);
    }
  };

  useEffect(() => {
    const symbol = selectedSymbol.trim().toUpperCase();

    if (!symbol) {
      setQuoteError('');
      setLastQuotedSymbol('');
      setPrice(0);
      return;
    }

    const timeout = setTimeout(() => {
      fetchQuote(symbol);
    }, 500);

    return () => clearTimeout(timeout);
  }, [selectedSymbol, sessionId]);

  const handleBuy = async () => {
    if (!selectedSymbol || !quantity || !price) return;
    setTradeLoading(true);
    try {
      await api.post(`/games/paper-trading/${sessionId}/trade`, {
        symbol: selectedSymbol,
        quantity,
        price,
        side: 'BUY',
      });
      await fetchSession();
      setSelectedSymbol('');
      setQuantity(1);
      setPrice(0);
    } catch (err) {
      console.error('Trade failed:', err);
    } finally {
      setTradeLoading(false);
    }
  };

  const handleSell = async () => {
    if (!selectedSymbol || !quantity || !price) return;
    setTradeLoading(true);
    try {
      await api.post(`/games/paper-trading/${sessionId}/trade`, {
        symbol: selectedSymbol,
        quantity,
        price,
        side: 'SELL',
      });
      await fetchSession();
      setSelectedSymbol('');
      setQuantity(1);
      setPrice(0);
    } catch (err) {
      console.error('Trade failed:', err);
    } finally {
      setTradeLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading trading session...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <p className="text-red-600">Failed to load session</p>
        </div>
      </div>
    );
  }

  const portfolio = session.portfolio || {};
  const cash = portfolio.cash || 0;
  const totalValue = portfolio.total_value || 0;
  const pnl = (session.metrics?.total_pnl || 0);
  const holdings = portfolio.holdings || {};
  const holdingsCount = Object.keys(holdings).length;
  const winRate = session.metrics?.win_rate || 0;
  const maxDrawdown = session.metrics?.max_drawdown || 0;
  const sharpeRatio = session.metrics?.sharpe_ratio || 0;
  const trades = session.trades || [];

  const tabs = [
    { id: 'portfolio', label: '💼 Portfolio', icon: <TrendingUp size={18} /> },
    { id: 'holdings', label: '📊 Holdings', icon: <BarChart3 size={18} /> },
    { id: 'performance', label: '📈 Performance', icon: <TrendingUp size={18} /> },
    { id: 'market', label: '📝 Trade History', icon: <TrendingUp size={18} /> },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex justify-between items-start">
          <div>
            <Link href="/dashboard/games" className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-4">
              <ArrowLeft size={18} />
              Back to Games
            </Link>
            <h1 className="text-3xl font-bold text-slate-900">{session.market.toUpperCase()} Trading</h1>
            <p className="text-slate-600">Strategy: {session.strategy} • Status: {session.status}</p>
          </div>
          <Link href="/dashboard/games/paper-trading/results" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-semibold">
            View Results
          </Link>
        </div>

        {/* Top Metrics Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-cyan-500">
            <p className="text-sm text-slate-600">Cash</p>
            <p className="text-2xl font-bold text-slate-900">{(cash / 1000).toFixed(1)}k</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <p className="text-sm text-slate-600">Portfolio Value</p>
            <p className="text-2xl font-bold text-slate-900">{(totalValue / 1000).toFixed(1)}k</p>
          </div>
          <div className={`bg-white rounded-lg shadow p-4 border-l-4 ${pnl >= 0 ? 'border-green-500' : 'border-red-500'}`}>
            <p className="text-sm text-slate-600">P&L</p>
            <p className={`text-2xl font-bold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {pnl >= 0 ? '+' : ''}{(pnl / 1000).toFixed(1)}k
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
            <p className="text-sm text-slate-600">Holdings</p>
            <p className="text-2xl font-bold text-slate-900">{holdingsCount}</p>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="bg-white rounded-lg shadow mb-6 border-b border-slate-200">
          <div className="flex overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 px-6 py-4 font-semibold border-b-2 transition flex items-center justify-center gap-2 ${
                  activeTab === tab.id
                    ? 'text-cyan-600 border-cyan-600'
                    : 'text-slate-600 border-transparent hover:text-slate-900'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'portfolio' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <PortfolioOverview
                  cash={cash}
                  totalValue={totalValue}
                  pnl={pnl}
                  holdingsCount={holdingsCount}
                  winRate={winRate}
                  maxDrawdown={maxDrawdown}
                  currency="INR"
                />
                {holdingsCount > 0 && (
                  <PortfolioAllocation holdings={holdings} cashValue={cash} currency="INR" />
                )}
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <TradeExecutor
                  selectedSymbol={selectedSymbol}
                  onSymbolChange={setSelectedSymbol}
                  quantity={quantity}
                  onQuantityChange={setQuantity}
                  price={price}
                  onPriceChange={setPrice}
                  onRefreshQuote={() => fetchQuote()}
                  onBuy={handleBuy}
                  onSell={handleSell}
                  loading={tradeLoading}
                  quoteLoading={quoteLoading}
                  quoteError={quoteError}
                  lastQuotedSymbol={lastQuotedSymbol}
                  availableCash={cash}
                />
              </div>
            </div>
          )}

          {activeTab === 'holdings' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <HoldingsTable holdings={holdings} currency="INR" />
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <TradeExecutor
                  selectedSymbol={selectedSymbol}
                  onSymbolChange={setSelectedSymbol}
                  quantity={quantity}
                  onQuantityChange={setQuantity}
                  price={price}
                  onPriceChange={setPrice}
                  onRefreshQuote={() => fetchQuote()}
                  onBuy={handleBuy}
                  onSell={handleSell}
                  loading={tradeLoading}
                  quoteLoading={quoteLoading}
                  quoteError={quoteError}
                  lastQuotedSymbol={lastQuotedSymbol}
                  availableCash={cash}
                />
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <PerformanceAnalytics
                  winRate={winRate}
                  maxDrawdown={maxDrawdown}
                  sharpeRatio={sharpeRatio}
                  totalTrades={session.metrics?.total_trades || 0}
                  profitableTrades={session.metrics?.profitable_trades || 0}
                />
              </div>
              <LearningPanel
                winRate={winRate}
                maxDrawdown={maxDrawdown}
                totalTrades={session.metrics?.total_trades || 0}
              />
            </div>
          )}

          {activeTab === 'market' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <TradeHistory trades={trades} currency="INR" />
              </div>
              <LearningPanel
                winRate={winRate}
                maxDrawdown={maxDrawdown}
                totalTrades={session.metrics?.total_trades || 0}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
