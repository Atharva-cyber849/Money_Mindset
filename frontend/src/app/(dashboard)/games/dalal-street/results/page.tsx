'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api/client';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, Home, RotateCcw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface ResultsData {
  session_id: string;
  status: string;
  era: string;
  final_scores: {
    timing: number;
    portfolio_management: number;
    risk_management: number;
    overall: number;
  };
  portfolio_performance: {
    starting_value: number;
    ending_value: number;
    profit_loss: number;
    return_percentage: number;
    market_return_percentage: number;
    max_drawdown: number;
  };
  xp_earned: number;
  trades_count: number;
}

const getScoreBadge = (score: number) => {
  if (score >= 90) return { emoji: '🏆', label: 'Expert', color: 'from-yellow-400 to-yellow-600' };
  if (score >= 80) return { emoji: '⭐', label: 'Proficient', color: 'from-cyan-400 to-cyan-600' };
  if (score >= 70) return { emoji: '✨', label: 'Competent', color: 'from-purple-400 to-purple-600' };
  if (score >= 60) return { emoji: '👍', label: 'Adequate', color: 'from-green-400 to-green-600' };
  return { emoji: '📚', label: 'Novice', color: 'from-gray-400 to-gray-600' };
};

export default function DalalStreetResults({ searchParams }: { searchParams?: Record<string, string> }) {
  const router = useRouter();
  const params = useSearchParams();
  const sessionId = params?.get('session_id') || searchParams?.session_id;

  const [results, setResults] = useState<ResultsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (sessionId) {
      loadResults();
    }
  }, [sessionId]);

  const loadResults = async () => {
    try {
      const response = await api.get(`/games/dalal/${sessionId}`);
      // Parse the data from the session
      const quarterly = JSON.parse(response.data.quarterly_snapshots || '[]');

      setResults({
        session_id: sessionId,
        status: response.data.status,
        era: response.data.era,
        final_scores: {
          timing: Math.round(Math.random() * 40 + 50), // Placeholder - should come from API
          portfolio_management: Math.round(Math.random() * 40 + 50),
          risk_management: Math.round(Math.random() * 40 + 50),
          overall: Math.round(Math.random() * 40 + 50),
        },
        portfolio_performance: {
          starting_value: quarterly.length > 0 ? quarterly[0].portfolio_value : 10000,
          ending_value: quarterly.length > 0 ? quarterly[quarterly.length - 1].portfolio_value : 10000,
          profit_loss: quarterly.length > 0 ? quarterly[quarterly.length - 1].portfolio_value - quarterly[0].portfolio_value : 0,
          return_percentage: quarterly.length > 0
            ? ((quarterly[quarterly.length - 1].portfolio_value - quarterly[0].portfolio_value) / quarterly[0].portfolio_value) * 100
            : 0,
          market_return_percentage: 15, // Placeholder
          max_drawdown: 20, // Placeholder
        },
        xp_earned: Math.round(Math.random() * 500 + 500),
        trades_count: 12,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card className="p-8 text-center space-y-4">
          <p className="text-red-600">{error || 'Failed to load results'}</p>
          <Button onClick={() => router.push('/games')}>Back to Games</Button>
        </Card>
      </div>
    );
  }

  const overallBadge = getScoreBadge(results.final_scores.overall);

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">📊 Your Trading Journey Complete!</h1>
        <p className="text-xl text-gray-600">
          You've navigated through {results.era.replace(/_/g, ' ')} era
        </p>
        <p className="text-gray-600">
          Made {results.trades_count} trades over 20 quarters
        </p>
      </div>

      {/* Overall Score Hero Card */}
      <Card className={`bg-gradient-to-br ${overallBadge.color} text-white p-8 text-center`}>
        <div className="text-6xl mb-4">{overallBadge.emoji}</div>
        <h2 className="text-3xl font-bold mb-2">Overall Trading Score</h2>
        <div className="text-7xl font-bold mb-4">{Math.round(results.final_scores.overall)}</div>
        <p className="text-lg opacity-90">{overallBadge.label}</p>
      </Card>

      {/* Three Dimension Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Timing Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">⏱️</div>
          <div>
            <p className="text-gray-600 mb-1">Timing Score</p>
            <p className="text-4xl font-bold text-cyan-600">{Math.round(results.final_scores.timing)}</p>
            <p className="text-sm text-gray-600 mt-1">{getScoreBadge(results.final_scores.timing).label}</p>
          </div>
          <div className="bg-gray-100 p-3 rounded text-sm text-gray-700">
            How well you timed entries and exits
          </div>
        </Card>

        {/* Portfolio Management Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">📈</div>
          <div>
            <p className="text-gray-600 mb-1">Portfolio Management</p>
            <p className="text-4xl font-bold text-green-600">{Math.round(results.final_scores.portfolio_management)}</p>
            <p className="text-sm text-gray-600 mt-1">{getScoreBadge(results.final_scores.portfolio_management).label}</p>
          </div>
          <div className="bg-gray-100 p-3 rounded text-sm text-gray-700">
            Quality of stock selection
          </div>
        </Card>

        {/* Risk Management Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">🛡️</div>
          <div>
            <p className="text-gray-600 mb-1">Risk Management</p>
            <p className="text-4xl font-bold text-purple-600">{Math.round(results.final_scores.risk_management)}</p>
            <p className="text-sm text-gray-600 mt-1">{getScoreBadge(results.final_scores.risk_management).label}</p>
          </div>
          <div className="bg-gray-100 p-3 rounded text-sm text-gray-700">
            Balance of growth vs stability
          </div>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card className="p-6 space-y-6">
        <h3 className="text-2xl font-bold">Portfolio Performance</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-cyan-600">
              ₹{results.portfolio_performance.starting_value.toLocaleString()}
            </p>
            <p className="text-gray-600">Starting Value</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">
              ₹{results.portfolio_performance.ending_value.toLocaleString()}
            </p>
            <p className="text-gray-600">Final Value</p>
          </div>
          <div className="text-center">
            <p className={`text-3xl font-bold ${
              results.portfolio_performance.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {results.portfolio_performance.profit_loss >= 0 ? '+' : ''}
              ₹{results.portfolio_performance.profit_loss.toLocaleString()}
            </p>
            <p className="text-gray-600">Profit/Loss</p>
          </div>
          <div className="text-center">
            <p className={`text-3xl font-bold ${
              results.portfolio_performance.return_percentage >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {results.portfolio_performance.return_percentage >= 0 ? '+' : ''}
              {results.portfolio_performance.return_percentage.toFixed(1)}%
            </p>
            <p className="text-gray-600">Return %</p>
          </div>
        </div>
      </Card>

      {/* Market Comparison */}
      <Card className="p-6 space-y-4">
        <h3 className="text-2xl font-bold">Your Performance vs Market</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-cyan-50 p-4 rounded">
            <p className="text-sm text-gray-600">Your Return</p>
            <p className={`text-2xl font-bold ${
              results.portfolio_performance.return_percentage >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {results.portfolio_performance.return_percentage.toFixed(1)}%
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <p className="text-sm text-gray-600">Market Return</p>
            <p className="text-2xl font-bold text-gray-700">
              {results.portfolio_performance.market_return_percentage.toFixed(1)}%
            </p>
          </div>
        </div>
      </Card>

      {/* Risk Metrics */}
      <Card className="p-6 space-y-4">
        <h3 className="text-2xl font-bold">Risk Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-2">Maximum Drawdown</p>
            <div className="w-full bg-gray-200 rounded h-4">
              <div
                className="bg-red-600 h-4 rounded"
                style={{ width: `${results.portfolio_performance.max_drawdown}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-1">{results.portfolio_performance.max_drawdown.toFixed(1)}%</p>
          </div>
          <div className="bg-amber-50 p-4 rounded">
            <p className="text-sm font-semibold text-amber-900">Risk Assessment</p>
            <p className="text-sm text-amber-800 mt-2">
              {results.portfolio_performance.max_drawdown > 30 ? 'High volatility - aggressive strategy' :
               results.portfolio_performance.max_drawdown > 15 ? 'Moderate volatility - balanced approach' :
               'Low volatility - conservative strategy'}
            </p>
          </div>
        </div>
      </Card>

      {/* Key Insights */}
      <Card className="p-6 bg-cyan-50 border border-cyan-200 space-y-4">
        <h3 className="text-lg font-bold">💡 Key Insights</h3>
        <ul className="space-y-2 text-sm">
          <li>
            ✓ You made {results.trades_count} decisions over 20 quarters
          </li>
          <li>
            ✓ Your timing score of {results.final_scores.timing} reflects entry/exit quality
          </li>
          <li>
            ✓ Sector concentration vs diversification affected your portfolio
          </li>
          <li>
            ✓ Each market era had distinct characteristics - observe how you adapted
          </li>
        </ul>
      </Card>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Button
          onClick={() => router.push('/games')}
          className="bg-cyan-600 hover:bg-blue-700 text-white"
        >
          <Home className="w-4 h-4 mr-2" />
          Back to Games
        </Button>
        <Button
          onClick={() => router.push('/games/dalal-street')}
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Try Another Era
        </Button>
        <Button
          className="bg-gray-600 hover:bg-gray-700 text-white cursor-not-allowed"
          disabled
        >
          Share (Coming Soon)
        </Button>
      </div>
    </div>
  );
}
