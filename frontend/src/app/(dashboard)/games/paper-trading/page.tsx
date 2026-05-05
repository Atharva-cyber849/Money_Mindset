'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, DollarSign, Target, BarChart3, Download, WifiOff, Smartphone, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api/client';
import {
  TradeExecutor,
  PortfolioOverview,
  HoldingsTable,
  PerformanceAnalytics,
  PortfolioAllocation,
  TradeHistory,
  LearningPanel,
  StockPriceChart,
} from './components';
import { EnhancedDecisionModal, FinancialLiteracyCard } from '../_lib/SharedComponents';
import { useCompactMarketAnalytics } from '@/lib/api/hooks';

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

const PAPER_TRADING_CACHE_PREFIX = 'money-mindset-paper-trading';

function getCacheKey(sessionId: string) {
  return `${PAPER_TRADING_CACHE_PREFIX}:${sessionId}`;
}

function safeReadCache(sessionId: string) {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(getCacheKey(sessionId));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function safeWriteCache(sessionId: string, payload: Record<string, any>) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(getCacheKey(sessionId), JSON.stringify(payload));
  } catch {
    // Ignore storage failures in private/incognito mode.
  }
}

export default function PaperTradingSetup() {
  const [stage, setStage] = useState<'setup' | 'game' | 'loading'>('setup');
  const [market, setMarket] = useState('india');
  const [strategy, setStrategy] = useState('portfolio_builder');
  const [capital, setCapital] = useState(50000);
  const [isHistorical, setIsHistorical] = useState(false);
  const [compactMode, setCompactMode] = useState(false);
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
      safeWriteCache(response.data.session_id, {
        sessionId: response.data.session_id,
        market,
        strategy,
        capital,
        compactMode,
        createdAt: new Date().toISOString(),
      });
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
          {/* Experience Mode */}
          <div>
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Smartphone size={18} />
              Experience Mode
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setCompactMode(false)}
                className={`p-4 rounded-lg border-2 text-left transition ${
                  !compactMode ? 'border-cyan-500 bg-cyan-50' : 'border-slate-200 bg-white hover:border-cyan-300'
                }`}
              >
                <div className="font-semibold text-slate-900">Full Mode</div>
                <div className="text-sm text-slate-600">All tabs, charts, and detailed trade controls.</div>
              </button>
              <button
                type="button"
                onClick={() => setCompactMode(true)}
                className={`p-4 rounded-lg border-2 text-left transition ${
                  compactMode ? 'border-cyan-500 bg-cyan-50' : 'border-slate-200 bg-white hover:border-cyan-300'
                }`}
              >
                <div className="font-semibold text-slate-900">Quick Play</div>
                <div className="text-sm text-slate-600">Simplified layout for mobile and fast sessions.</div>
              </button>
            </div>
          </div>

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
  type QuotePoint = {
    timestamp: string;
    price: number;
    volume?: number;
  };

  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'portfolio' | 'holdings' | 'performance' | 'market'>('portfolio');
  const [offlineMode, setOfflineMode] = useState(false);
  const [compactMode, setCompactMode] = useState(false);
  const [sessionStart] = useState(() => Date.now());
  const [tradeCount, setTradeCount] = useState(0);
  const [reportStatus, setReportStatus] = useState('');
  const [liveMode, setLiveMode] = useState(true);

  // Trade executor state
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState(0);
  const [tradeLoading, setTradeLoading] = useState(false);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState('');
  const [lastQuotedSymbol, setLastQuotedSymbol] = useState('');
  const [quoteHistoryBySymbol, setQuoteHistoryBySymbol] = useState<Record<string, QuotePoint[]>>({});
  const quoteRequestId = useRef(0);
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'stop_loss' | 'trailing_stop'>('market');
  const [limitPrice, setLimitPrice] = useState(0);
  const [stopPrice, setStopPrice] = useState(0);
  const [trailingStopPct, setTrailingStopPct] = useState(5);
  const [marketState, setMarketState] = useState<any>(null);

  // Portfolio decision state
  const [portfolioDecision, setPortfolioDecision] = useState<any>(null);
  const [showPortfolioDecisionModal, setShowPortfolioDecisionModal] = useState(false);
  const [submittingDecision, setSubmittingDecision] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const cached = safeReadCache(sessionId);
    if (cached?.compactMode !== undefined) {
      setCompactMode(Boolean(cached.compactMode));
    }

    fetchSession();
    const interval = setInterval(fetchSession, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | null = null;

    const fetchMarketState = async () => {
      try {
        const response = await api.get(`/games/paper-trading/${sessionId}/market-state`, {
          params: { limit: 8 },
        });
        if (!cancelled) {
          setMarketState(response.data);
        }
      } catch {
        if (!cancelled) {
          setMarketState(null);
        }
      }
    };

    if (sessionId) {
      fetchMarketState();
      intervalId = setInterval(fetchMarketState, 1500);
    }

    return () => {
      cancelled = true;
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [sessionId]);

  const fetchSession = async () => {
    try {
      const response = await api.get(`/games/paper-trading/${sessionId}`);
      setSession(response.data);
      safeWriteCache(sessionId, {
        ...(safeReadCache(sessionId) || {}),
        session: response.data,
        updatedAt: new Date().toISOString(),
      });
      setOfflineMode(false);

      // Fetch portfolio decision on first load
      if (!portfolioDecision) {
        try {
          const decisionResponse = await api.get(
            `/games/paper-trading/${sessionId}/portfolio-decision`
          );
          if (decisionResponse.data.has_decision) {
            setPortfolioDecision(decisionResponse.data);
            setShowPortfolioDecisionModal(true);
          }
        } catch (err) {
          console.log('No portfolio decision needed');
        }
      }
    } catch (err) {
      console.error('Failed to fetch session:', err);
      const cached = safeReadCache(sessionId);
      if (cached?.session) {
        setSession(cached.session);
        setOfflineMode(true);
      }
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
      const requestId = ++quoteRequestId.current;
      const response = await api.get(`/games/paper-trading/${sessionId}/quote`, {
        params: { symbol },
      });
      if (requestId !== quoteRequestId.current) {
        return;
      }
      const quotePrice = Number(response.data?.price ?? 0);
      if (quotePrice > 0) {
        setPrice(quotePrice);
        setLastQuotedSymbol(symbol);
        setQuoteHistoryBySymbol((prev) => {
          const nextSeries = [...(prev[symbol] || []), {
            timestamp: new Date().toISOString(),
            price: quotePrice,
            volume: Number(response.data?.buy_volume || 0) + Number(response.data?.sell_volume || 0),
          }].slice(-60);
          return {
            ...prev,
            [symbol]: nextSeries,
          };
        });
        setLiveMode(true);
        safeWriteCache(sessionId, {
          ...(safeReadCache(sessionId) || {}),
          lastQuote: {
            symbol,
            price: quotePrice,
            currency: response.data?.currency || 'INR',
            fetchedAt: new Date().toISOString(),
          },
        });
      } else {
        setQuoteError('Price unavailable for this symbol');
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      const cached = safeReadCache(sessionId);
      const cachedPrice = cached?.lastQuote?.symbol === symbol ? cached.lastQuote.price : null;

      if (cachedPrice) {
        setPrice(Number(cachedPrice));
        setLastQuotedSymbol(symbol);
        setQuoteHistoryBySymbol((prev) => {
          const nextSeries = [...(prev[symbol] || []), {
            timestamp: new Date().toISOString(),
            price: Number(cachedPrice),
          }].slice(-60);
          return {
            ...prev,
            [symbol]: nextSeries,
          };
        });
        setLiveMode(false);
        setQuoteError('Live price unavailable, using cached quote');
      } else {
        setQuoteError(typeof detail === 'string' ? detail : 'Failed to fetch live price');
      }
    } finally {
      setQuoteLoading(false);
    }
  };

  const analyticsSymbol = (selectedSymbol || lastQuotedSymbol || '').trim().toUpperCase();
  const compactAnalytics = useCompactMarketAnalytics(
    analyticsSymbol,
    session?.market || 'india',
    {
      period: '1yr',
      filter_type: 'price',
      measure_code: 'EPS',
      period_type: 'Annual',
      data_type: 'Estimates',
      age: 'Current',
    }
  );

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
      const response = await api.post(`/games/paper-trading/${sessionId}/trade`, {
        symbol: selectedSymbol,
        quantity,
        price: orderType === 'limit' && limitPrice > 0 ? limitPrice : price,
        side: 'BUY',
        order_type: orderType,
        limit_price: orderType === 'limit' ? limitPrice : null,
        stop_price: orderType === 'stop_loss' ? stopPrice : null,
        trailing_stop_pct: orderType === 'trailing_stop' ? trailingStopPct : null,
      });
      setTradeCount((count) => count + 1);
      const fill = response.data?.fill;
      if (fill) {
        setReportStatus(
          fill.status === 'partial_fill'
            ? `Partial fill: ${fill.filled_quantity}/${fill.requested_quantity}`
            : fill.status === 'pending'
              ? 'Order placed and waiting for trigger'
              : `Filled ${fill.filled_quantity}/${fill.requested_quantity} at ${Number(fill.execution_price || price).toFixed(2)}`
        );
      }
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
      const response = await api.post(`/games/paper-trading/${sessionId}/trade`, {
        symbol: selectedSymbol,
        quantity,
        price: orderType === 'limit' && limitPrice > 0 ? limitPrice : price,
        side: 'SELL',
        order_type: orderType,
        limit_price: orderType === 'limit' ? limitPrice : null,
        stop_price: orderType === 'stop_loss' ? stopPrice : null,
        trailing_stop_pct: orderType === 'trailing_stop' ? trailingStopPct : null,
      });
      setTradeCount((count) => count + 1);
      const fill = response.data?.fill;
      if (fill) {
        setReportStatus(
          fill.status === 'partial_fill'
            ? `Partial fill: ${fill.filled_quantity}/${fill.requested_quantity}`
            : fill.status === 'pending'
              ? 'Order placed and waiting for trigger'
              : `Filled ${fill.filled_quantity}/${fill.requested_quantity} at ${Number(fill.execution_price || price).toFixed(2)}`
        );
      }
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
  const sessionMinutes = Math.max((Date.now() - sessionStart) / 60000, 0.1);
  const decisionRate = tradeCount / sessionMinutes;
  const learningCurve = Math.min(100, Math.round((winRate * 0.6 + Math.min(decisionRate / 3, 1) * 0.4) * 100));
  const isCompactLayout = compactMode || typeof window !== 'undefined' && window.innerWidth < 768;
  const compactAnalyticsData = compactAnalytics.data?.analytics;
  const marketStatePayload = marketState?.market_state || marketState;
  const chartSymbol = (lastQuotedSymbol || selectedSymbol).trim().toUpperCase();
  const chartData = chartSymbol ? (quoteHistoryBySymbol[chartSymbol] || []) : [];
  const chartCurrentPrice = chartData.length > 0 ? Number(chartData[chartData.length - 1].price || 0) : 0;
  const chartFirstPrice = chartData.length > 0 ? Number(chartData[0].price || chartCurrentPrice || 0) : 0;
  const chartChange = chartCurrentPrice - chartFirstPrice;
  const chartChangePercent = chartFirstPrice > 0 ? (chartChange / chartFirstPrice) * 100 : 0;
  const chartCurrency = chartSymbol.endsWith('.NS') ? 'INR' : 'USD';

  const tabs = [
    { id: 'portfolio', label: '💼 Portfolio', icon: <TrendingUp size={18} /> },
    { id: 'holdings', label: '📊 Holdings', icon: <BarChart3 size={18} /> },
    { id: 'performance', label: '📈 Performance', icon: <TrendingUp size={18} /> },
    { id: 'market', label: '📝 Trade History', icon: <TrendingUp size={18} /> },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:justify-between md:items-start">
          <div>
            <Link href="/dashboard/games" className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-4">
              <ArrowLeft size={18} />
              Back to Games
            </Link>
            <h1 className="text-3xl font-bold text-slate-900">{session.market.toUpperCase()} Trading</h1>
            <p className="text-slate-600">Strategy: {session.strategy} • Status: {session.status}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={async () => {
                try {
                  const response = await api.get(`/analytics/reports/session/paper_trading/${sessionId}`)
                  const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
                  const url = window.URL.createObjectURL(blob)
                  const anchor = document.createElement('a')
                  anchor.href = url
                  anchor.download = `paper-trading-report-${sessionId}.json`
                  anchor.click()
                  window.URL.revokeObjectURL(url)
                  setReportStatus('Report downloaded')
                } catch {
                  setReportStatus('Report export unavailable')
                }
              }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 hover:border-cyan-300 text-slate-700 rounded-lg font-semibold"
            >
              <Download size={16} />
              Export Report
            </button>
            <Link href="/dashboard/games/paper-trading/results" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-semibold">
              View Results
            </Link>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4 border border-slate-200">
            <div className="flex items-center gap-2 text-sm text-slate-600 mb-1">
              {offlineMode ? <WifiOff size={16} /> : <RefreshCw size={16} />}
              {offlineMode ? 'Offline cache active' : liveMode ? 'Live quotes enabled' : 'Cached quote mode'}
            </div>
            <p className="text-lg font-bold text-slate-900">{offlineMode ? 'Using local session cache' : 'Connected to live data'}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border border-slate-200">
            <p className="text-sm text-slate-600 mb-1">Time Spent</p>
            <p className="text-lg font-bold text-slate-900">{sessionMinutes.toFixed(1)} min</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border border-slate-200">
            <p className="text-sm text-slate-600 mb-1">Learning Curve</p>
            <p className="text-lg font-bold text-slate-900">{learningCurve}/100</p>
          </div>
        </div>

        {reportStatus && (
          <div className="mb-4 rounded-lg border border-cyan-200 bg-cyan-50 px-4 py-3 text-sm text-cyan-900">
            {reportStatus}
          </div>
        )}

        {/* Compact Market Analytics */}
        {analyticsSymbol && compactAnalyticsData && (
          <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Trend</p>
              <p className="mt-2 text-lg font-bold text-slate-900 capitalize">{compactAnalyticsData.trend?.direction || 'sideways'}</p>
              <p className="mt-1 text-sm text-slate-600">{compactAnalyticsData.trend?.summary || 'No trend summary available.'}</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Forecast</p>
              <p className="mt-2 text-lg font-bold text-slate-900 capitalize">{compactAnalyticsData.forecast?.direction || 'neutral'}</p>
              <p className="mt-1 text-sm text-slate-600">{compactAnalyticsData.forecast?.summary || 'No forecast available.'}</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">52-Week Context</p>
              <p className="mt-2 text-lg font-bold text-slate-900 capitalize">{compactAnalyticsData.range_52w?.range_state?.replace(/_/g, ' ') || 'mid range'}</p>
              <p className="mt-1 text-sm text-slate-600">
                High {Number(compactAnalyticsData.range_52w?.high || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })} · Low {Number(compactAnalyticsData.range_52w?.low || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        )}

        {/* Live Market State */}
        {marketStatePayload && (
          <div className="mb-6 rounded-lg border border-slate-200 bg-slate-950 p-4 text-slate-100 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-cyan-200">Live Market State</p>
                <p className="text-lg font-semibold capitalize">{String(marketStatePayload.market_regime || 'normal').replace(/_/g, ' ')}</p>
              </div>
              <div className="text-sm text-slate-300">
                Tick {marketStatePayload.tick || 0} · {marketStatePayload.active_event ? marketStatePayload.active_event.event_type.replace(/_/g, ' ') : 'No active shock'}
              </div>
            </div>
          </div>
        )}

        {chartSymbol && (
          <div className="mb-6">
            <StockPriceChart
              symbol={chartSymbol}
              data={chartData}
              currentPrice={chartCurrentPrice}
              change={chartChange}
              changePercent={chartChangePercent}
              currency={chartCurrency}
            />
          </div>
        )}

        {/* Top Metrics Bar */}
        <div className={`grid gap-4 mb-6 ${isCompactLayout ? 'grid-cols-2' : 'grid-cols-2 md:grid-cols-4'}`}>
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
          <div className={`flex overflow-x-auto ${isCompactLayout ? 'text-sm' : ''}`}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 px-6 py-3 font-semibold transition-all flex items-center justify-center gap-2 rounded-t-lg ${
                  activeTab === tab.id
                    ? 'bg-cyan-600 text-white shadow-md '
                    : 'text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className={`space-y-6 ${isCompactLayout ? 'space-y-4' : ''}`}>
          {activeTab === 'portfolio' && (
            <div className={`grid grid-cols-1 gap-6 ${isCompactLayout ? '' : 'lg:grid-cols-3'}`}>
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
              <div className="bg-white p-4 md:p-6 rounded-lg shadow">
                <TradeExecutor
                  selectedSymbol={selectedSymbol}
                  onSymbolChange={setSelectedSymbol}
                  quantity={quantity}
                  onQuantityChange={setQuantity}
                  price={price}
                  onPriceChange={setPrice}
                  orderType={orderType}
                  onOrderTypeChange={setOrderType}
                  limitPrice={limitPrice}
                  onLimitPriceChange={setLimitPrice}
                  stopPrice={stopPrice}
                  onStopPriceChange={setStopPrice}
                  trailingStopPct={trailingStopPct}
                  onTrailingStopPctChange={setTrailingStopPct}
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
            <div className={`grid grid-cols-1 gap-6 ${isCompactLayout ? '' : 'lg:grid-cols-3'}`}>
              <div className="lg:col-span-2">
                <HoldingsTable holdings={holdings} currency="INR" />
              </div>
              <div className="bg-white p-4 md:p-6 rounded-lg shadow">
                <TradeExecutor
                  selectedSymbol={selectedSymbol}
                  onSymbolChange={setSelectedSymbol}
                  quantity={quantity}
                  onQuantityChange={setQuantity}
                  price={price}
                  onPriceChange={setPrice}
                  orderType={orderType}
                  onOrderTypeChange={setOrderType}
                  limitPrice={limitPrice}
                  onLimitPriceChange={setLimitPrice}
                  stopPrice={stopPrice}
                  onStopPriceChange={setStopPrice}
                  trailingStopPct={trailingStopPct}
                  onTrailingStopPctChange={setTrailingStopPct}
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
            <div className={`grid grid-cols-1 gap-6 ${isCompactLayout ? '' : 'lg:grid-cols-3'}`}>
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
            <div className={`grid grid-cols-1 gap-6 ${isCompactLayout ? '' : 'lg:grid-cols-3'}`}>
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

        {showPortfolioDecisionModal && portfolioDecision && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex flex-col items-center justify-center p-4 overflow-y-auto">
            <div className="flex flex-col gap-6 w-full max-w-2xl py-6">
              {error && (
                <div className="p-4 bg-red-100 border border-red-200 text-red-700 rounded-lg">
                  {error}
                </div>
              )}
              <EnhancedDecisionModal
                title={portfolioDecision.decision_title}
                description={portfolioDecision.description}
                event_type="portfolio_setup"
                options={portfolioDecision.options.map((opt: any) => ({
                  index: opt.index,
                  title: opt.title,
                  description: opt.description,
                  risk_level: opt.risk_level,
                  consequences: {},
                  monthly_impact: 0,
                  months: 1,
                  long_term_effect: opt.best_for || '',
                }))}
                onDecide={async (optionIndex: number) => {
                  setSubmittingDecision(true);
                  setError('');
                  try {
                    await api.post(`/games/paper-trading/${sessionId}/portfolio-decision`, {
                      option_index: optionIndex,
                    });
                    setShowPortfolioDecisionModal(false);
                  } catch (error: any) {
                    setError(error?.response?.data?.detail || 'Failed to submit portfolio decision');
                    console.error('Failed to submit portfolio decision:', error);
                  } finally {
                    setSubmittingDecision(false);
                  }
                }}
                isLoading={submittingDecision}
              />
              <FinancialLiteracyCard
                concept="asset_allocation"
                impact_amount={0}
                context="Your portfolio strategy shapes risk exposure and returns"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
