'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, TrendingUp, TrendingDown, Home } from 'lucide-react';

interface Era {
  id: string;
  name: string;
  dateRange: string;
  narrative: string;
  difficulty: string;
  capital: string;
  stocks: string;
  emoji: string;
}

interface GameSession {
  session_id: string;
  status: string;
  era: string;
  current_quarter: number;
  portfolio_value: number;
  cash: number;
  holdings_value: number;
  market_index: number;
  news_event?: any;
}

interface Stock {
  symbol: string;
  name: string;
  current_price: number;
  trend: string;
  sector: string;
}

const ERAS: Era[] = [
  {
    id: "liberalization_1991_1996",
    name: "🎪 Liberalization Dawn",
    dateRange: "(1991-1996)",
    narrative: "The Indian economy opens to foreign investment. New opportunities emerge for retail investors.",
    difficulty: "⭐ Beginner",
    capital: "₹10,000",
    stocks: "10 stocks",
    emoji: "🎪",
  },
  {
    id: "dotcom_1997_2002",
    name: "💻 Dot-Com Bubble",
    dateRange: "(1997-2002)",
    narrative: "The IT boom drives valuations to unprecedented heights. Tech stocks soar but cracks form beneath the surface.",
    difficulty: "⭐⭐ Intermediate",
    capital: "Inherited",
    stocks: "20 stocks",
    emoji: "💻",
  },
  {
    id: "bull_crash_2003_2008",
    name: "📈 Bull Run & Crisis",
    dateRange: "(2003-2008)",
    narrative: "A powerful bull market drives valuations higher, but the 2008 financial crisis crashes everything.",
    difficulty: "⭐⭐ Intermediate",
    capital: "Inherited",
    stocks: "25 stocks",
    emoji: "📈",
  },
  {
    id: "recovery_2009_2014",
    name: "🔧 Recovery & Regulation",
    dateRange: "(2009-2014)",
    narrative: "Markets recover slowly from the 2008 crisis. Regulatory reforms strengthen the system.",
    difficulty: "⭐⭐⭐ Advanced",
    capital: "₹1,00,000",
    stocks: "30 stocks",
    emoji: "🔧",
  },
  {
    id: "modern_2015_2020",
    name: "🌍 Modern Era",
    dateRange: "(2015-2020)",
    narrative: "Markets ride through demonetization, GST, and COVID-19. Resilience becomes key.",
    difficulty: "⭐⭐⭐ Expert",
    capital: "Inherited",
    stocks: "40 stocks",
    emoji: "🌍",
  },
];

export default function DalalStreetGame() {
  const router = useRouter();
  const [gameStarted, setGameStarted] = useState(false);
  const [showOpeningScene, setShowOpeningScene] = useState(false);
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState<GameSession | null>(null);
  const [selectedEra, setSelectedEra] = useState<Era | null>(null);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [showStockList, setShowStockList] = useState(false);
  const [tradeSymbol, setTradeSymbol] = useState('');
  const [tradeType, setTradeType] = useState('hold');
  const [tradeQuantity, setTradeQuantity] = useState(1);
  const [tradeError, setTradeError] = useState('');
  const [tradeMessage, setTradeMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Load existing session on mount
  useEffect(() => {
    loadExistingSession();
  }, []);

  const loadExistingSession = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/games/dalal/user/sessions');
      if (response.data.sessions && response.data.sessions.length > 0) {
        const active = response.data.sessions.find((s: any) => s.status === 'active');
        if (active) {
          // Load the active session
          const sessionData = await axios.get(`/api/v1/games/dalal/${active.session_id}`);
          setSession({
            session_id: active.session_id,
            status: active.status,
            era: active.era,
            current_quarter: active.current_quarter,
            portfolio_value: sessionData.data.portfolio?.cash || 0,
            cash: sessionData.data.portfolio?.cash || 0,
            holdings_value: 0,
            market_index: 100,
          });
          setGameStarted(true);
          // Load stocks
          loadAvailableStocks(active.session_id);
        }
      }
    } catch (err) {
      // No existing session, that's fine
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGame = async () => {
    if (!selectedEra) {
      setError('Please select an era');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('/api/v1/games/dalal/create', {
        era: selectedEra.id,
      });

      setSession(response.data);
      setShowOpeningScene(true);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create game session');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableStocks = async (sessionId: string) => {
    try {
      const response = await axios.get(`/api/v1/games/dalal/${sessionId}/available-stocks`);
      setStocks(response.data.stocks);
    } catch (err) {
      console.error('Failed to load stocks:', err);
    }
  };

  const handleAdvanceQuarter = async () => {
    if (!session) return;

    try {
      setSubmitting(true);
      const response = await axios.post(`/api/v1/games/dalal/${session.session_id}/advance-quarter`);

      setSession(prev => prev ? {
        ...prev,
        current_quarter: response.data.current_quarter,
        portfolio_value: response.data.portfolio_value,
        cash: response.data.cash,
        holdings_value: response.data.holdings_value,
        market_index: response.data.market_index,
        news_event: response.data.news_event,
      } : null);

      // Reload stocks
      await loadAvailableStocks(session.session_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to advance quarter');
    } finally {
      setSubmitting(false);
    }
  };

  const handleExecuteTrade = async () => {
    if (!session || !tradeSymbol) {
      setTradeError('Please select a stock');
      return;
    }

    if (tradeType !== 'hold' && tradeQuantity <= 0) {
      setTradeError('Quantity must be greater than 0');
      return;
    }

    try {
      setSubmitting(true);
      const response = await axios.post(`/api/v1/games/dalal/${session.session_id}/trade`, {
        symbol: tradeSymbol,
        trade_type: tradeType,
        quantity: tradeQuantity,
      });

      setSession(prev => prev ? {
        ...prev,
        portfolio_value: response.data.portfolio_value,
        cash: response.data.cash,
        holdings_value: response.data.holdings_value,
      } : null);

      setTradeMessage(response.data.message);
      setTradeError('');
      setTradeSymbol('');
      setTradeQuantity(1);

      setTimeout(() => setTradeMessage(''), 3000);
    } catch (err: any) {
      setTradeError(err.response?.data?.detail || 'Trade failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCompleteGame = async () => {
    if (!session) return;

    try {
      setSubmitting(true);
      await axios.post(`/api/v1/games/dalal/${session.session_id}/complete`);
      router.push(`/games/dalal-street/results?session_id=${session.session_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete game');
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (loading && !gameStarted) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  // Era Selection Screen
  if (!gameStarted) {
    return (
      <div className="max-w-6xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">🏛️ Dalal Street Trading Simulation</h1>
          <p className="text-xl text-gray-600">
            Navigate 5 historical Indian stock market eras
          </p>
          <p className="text-gray-600">
            From liberalization to the digital age - experience market cycles, crises, and opportunities
          </p>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Choose Your Era</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ERAS.map((era) => (
              <Card
                key={era.id}
                className={`p-6 cursor-pointer transition ${
                  selectedEra?.id === era.id
                    ? 'border-2 border-blue-500 bg-blue-50'
                    : 'border border-gray-200 hover:border-blue-300'
                }`}
                onClick={() => setSelectedEra(era)}
              >
                <div className="space-y-3">
                  <div className="text-4xl">{era.emoji}</div>
                  <h3 className="text-lg font-bold">{era.name}</h3>
                  <p className="text-sm text-gray-600">{era.dateRange}</p>
                  <p className="text-sm text-gray-700 line-clamp-2">{era.narrative}</p>
                  <div className="space-y-1 text-xs text-gray-600 pt-2 border-t">
                    <p><span className="font-semibold">{era.difficulty}</span></p>
                    <p>Capital: {era.capital}</p>
                    <p>Stocks: {era.stocks}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {error && (
          <Card className="p-4 bg-red-50 border border-red-200">
            <p className="text-red-700">{error}</p>
          </Card>
        )}

        <Button
          onClick={handleCreateGame}
          disabled={!selectedEra || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
          Start Trading
        </Button>
      </div>
    );
  }

  // Opening Scene
  if (showOpeningScene) {
    const era = ERAS.find((e) => e.id === session?.era);
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-6">
          <div className="text-6xl">{era?.emoji}</div>
          <h1 className="text-4xl font-bold">{era?.name}</h1>
          <p className="text-xl text-gray-600">{era?.narrative}</p>
        </div>

        <Card className="p-8 bg-gradient-to-r from-blue-50 to-indigo-50 space-y-4">
          <h2 className="text-2xl font-bold">Starting Conditions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Starting Capital</p>
              <p className="text-2xl font-bold text-blue-600">₹{session?.portfolio_value.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Available Stocks</p>
              <p className="text-2xl font-bold text-green-600">{stocks.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Time Frame</p>
              <p className="text-2xl font-bold text-purple-600">20 Quarters</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Market Index</p>
              <p className="text-2xl font-bold text-amber-600">100.0</p>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-amber-50 border border-amber-200 space-y-2">
          <p className="font-semibold text-amber-900">💡 How to Play</p>
          <ul className="space-y-1 text-sm text-amber-900">
            <li>• Advance through quarters to see market movements and news events</li>
            <li>• Buy stocks you believe will perform well</li>
            <li>• Sell stocks to lock in profits or cut losses</li>
            <li>• Make strategic decisions at key moments</li>
            <li>• Complete 20 quarters to see your final results</li>
          </ul>
        </Card>

        <Button
          onClick={() => {
            setShowOpeningScene(false);
            setGameStarted(true);
            if (session) loadAvailableStocks(session.session_id);
          }}
          className="w-full bg-green-600 hover:bg-green-700 text-white py-3 text-lg"
        >
          Begin Trading
        </Button>
      </div>
    );
  }

  // Active Game Screen
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">📊 Dalal Street Trading</h1>
          <p className="text-gray-600">Quarter {session?.current_quarter} of 20</p>
        </div>
        <Link href="/games" className="text-blue-600 hover:underline flex items-center gap-2">
          <Home className="w-4 h-4" />
          Back to Games
        </Link>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar: Portfolio */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="p-6 space-y-4">
            <h3 className="text-lg font-bold">Portfolio</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-3xl font-bold text-blue-600">
                  ₹{(session?.portfolio_value || 0).toLocaleString('en-IN', {
                    maximumFractionDigits: 0,
                  })}
                </p>
              </div>
              <div className="bg-gray-50 p-3 rounded space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Cash</span>
                  <span className="font-semibold">₹{(session?.cash || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Holdings</span>
                  <span className="font-semibold">₹{(session?.holdings_value || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4 space-y-2">
            <p className="text-sm text-gray-600">Market Index</p>
            <p className="text-2xl font-bold text-green-600">{(session?.market_index || 100).toFixed(1)}</p>
          </Card>

          <Button
            onClick={handleAdvanceQuarter}
            disabled={submitting || !session || session.current_quarter >= 20}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Next Quarter
          </Button>

          {session && session.current_quarter >= 20 && (
            <Button
              onClick={handleCompleteGame}
              className="w-full bg-green-600 hover:bg-green-700 text-white"
            >
              View Results
            </Button>
          )}
        </div>

        {/* Center: Game Board */}
        <div className="lg:col-span-2 space-y-4">
          {/* News Feed */}
          {session?.news_event && (
            <Card className="p-4 border-l-4 border-amber-500 bg-amber-50">
              <p className="font-semibold text-amber-900">📰 {session.news_event.headline}</p>
              <p className="text-sm text-amber-800 mt-1">{session.news_event.description}</p>
            </Card>
          )}

          {/* Trade Status */}
          {tradeMessage && (
            <Card className="p-4 bg-green-50 border border-green-200">
              <p className="text-green-700">{tradeMessage}</p>
            </Card>
          )}

          {tradeError && (
            <Card className="p-4 bg-red-50 border border-red-200">
              <p className="text-red-700">{tradeError}</p>
            </Card>
          )}

          {/* Trade Execution Panel */}
          <Card className="p-6 space-y-4">
            <h3 className="text-lg font-bold">Execute Trade</h3>

            <div>
              <label className="block text-sm font-medium mb-2">Stock Symbol</label>
              <div className="relative">
                <input
                  type="text"
                  value={tradeSymbol}
                  onChange={(e) => setTradeSymbol(e.target.value.toUpperCase())}
                  placeholder="e.g., INFY, TCS"
                  className="w-full px-3 py-2 border rounded"
                />
                <button
                  onClick={() => setShowStockList(!showStockList)}
                  className="absolute right-2 top-2 text-gray-600 hover:text-gray-900"
                >
                  ▼
                </button>
              </div>

              {showStockList && stocks.length > 0 && (
                <div className="mt-2 border rounded bg-white max-h-48 overflow-y-auto">
                  {stocks.slice(0, 10).map((stock) => (
                    <div
                      key={stock.symbol}
                      onClick={() => {
                        setTradeSymbol(stock.symbol);
                        setShowStockList(false);
                      }}
                      className="p-2 hover:bg-gray-100 cursor-pointer text-sm"
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-semibold">{stock.symbol}</span>
                        <div className="flex items-center gap-2">
                          <span>₹{stock.current_price.toFixed(0)}</span>
                          {stock.trend === 'up' ? (
                            <TrendingUp className="w-4 h-4 text-green-600" />
                          ) : stock.trend === 'down' ? (
                            <TrendingDown className="w-4 h-4 text-red-600" />
                          ) : null}
                        </div>
                      </div>
                      <p className="text-xs text-gray-600">{stock.sector}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Action</label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setTradeType('buy')}
                  className={`p-2 rounded ${
                    tradeType === 'buy'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  BUY
                </button>
                <button
                  onClick={() => setTradeType('sell')}
                  className={`p-2 rounded ${
                    tradeType === 'sell'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  SELL
                </button>
                <button
                  onClick={() => setTradeType('hold')}
                  className={`p-2 rounded ${
                    tradeType === 'hold'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  HOLD
                </button>
              </div>
            </div>

            {tradeType !== 'hold' && (
              <div>
                <label className="block text-sm font-medium mb-2">Quantity</label>
                <input
                  type="number"
                  value={tradeQuantity}
                  onChange={(e) => setTradeQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
            )}

            <Button
              onClick={handleExecuteTrade}
              disabled={submitting || !tradeSymbol}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Execute Trade
            </Button>
          </Card>
        </div>

        {/* Right Sidebar: Stock List */}
        <div className="lg:col-span-1">
          <Card className="p-4 space-y-3">
            <h3 className="text-lg font-bold">Market Prices</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {stocks.slice(0, 15).map((stock) => (
                <div
                  key={stock.symbol}
                  onClick={() => setTradeSymbol(stock.symbol)}
                  className="p-2 hover:bg-gray-100 rounded cursor-pointer"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-sm">{stock.symbol}</span>
                    <span className="text-sm text-gray-600">₹{stock.current_price.toFixed(0)}</span>
                  </div>
                  {stock.trend === 'up' ? (
                    <p className="text-xs text-green-600">📈 Trending up</p>
                  ) : stock.trend === 'down' ? (
                    <p className="text-xs text-red-600">📉 Trending down</p>
                  ) : (
                    <p className="text-xs text-gray-600">➡️ Stable</p>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {error && (
        <Card className="p-4 bg-red-50 border border-red-200">
          <p className="text-red-700">{error}</p>
        </Card>
      )}
    </div>
  );
}
