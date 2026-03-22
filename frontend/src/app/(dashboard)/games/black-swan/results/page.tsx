'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, Home, RotateCcw, TrendingUp, TrendingDown } from 'lucide-react';

interface Results {
  session_id: string;
  crisis_type: string;
  scores: {
    antifragility: number;
    overall: number;
    survival: boolean;
  };
  performance: {
    starting_wealth: number;
    trough_wealth: number;
    final_wealth: number;
    max_drawdown_pct: number;
  };
  xp_earned: number;
}

const getAntifragilityBadge = (score: number) => {
  if (score > 50) return { emoji: '🦸', label: 'Opportunist', color: 'from-green-400 to-green-600' };
  if (score > 0) return { emoji: '💪', label: 'Resilient', color: 'from-blue-400 to-blue-600' };
  if (score > -25) return { emoji: '🛡️', label: 'Defensive', color: 'from-purple-400 to-purple-600' };
  if (score > -50) return { emoji: '😤', label: 'Survivor', color: 'from-amber-400 to-amber-600' };
  return { emoji: '📉', label: 'Vulnerable', color: 'from-red-400 to-red-600' };
};

export default function BlackSwanResults() {
  const router = useRouter();
  const params = useSearchParams();
  const sessionId = params?.get('session_id');

  const [results, setResults] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (sessionId) {
      loadResults();
    }
  }, [sessionId]);

  const loadResults = async () => {
    try {
      const response = await axios.get(`/api/v1/games/black-swan/${sessionId}`);
      // Construct results from response
      setResults({
        session_id: sessionId,
        crisis_type: response.data.crisis_type,
        scores: {
          antifragility: response.data.antifragility_score || 0,
          overall: response.data.overall_score || 0,
          survival: response.data.status === 'completed' && response.data.antifragility_score !== undefined,
        },
        performance: {
          starting_wealth: response.data.financial_profile?.assets?.net_worth || 1000000,
          trough_wealth: response.data.quarterly_wealth_history?.[Math.floor(response.data.quarterly_wealth_history.length / 2)] || 500000,
          final_wealth: response.data.quarterly_wealth_history?.[response.data.quarterly_wealth_history.length - 1] || 1000000,
          max_drawdown_pct: 35,
        },
        xp_earned: 0,
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

  const badge = getAntifragilityBadge(results.scores.antifragility);
  const returnPct = ((results.performance.final_wealth - results.performance.starting_wealth) / results.performance.starting_wealth) * 100;
  const drawdownPct = ((results.performance.starting_wealth - results.performance.trough_wealth) / results.performance.starting_wealth) * 100;

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">⚫ Crisis Complete!</h1>
        <p className="text-xl text-gray-600">
          Your antifragility through the {results.crisis_type.replace('_', ' ')} tested
        </p>
      </div>

      {/* Antifragility Score Hero Card */}
      <Card className={`bg-gradient-to-br ${badge.color} text-white p-8 text-center`}>
        <div className="text-6xl mb-4">{badge.emoji}</div>
        <h2 className="text-3xl font-bold mb-2">Antifragility Score</h2>
        <div className="text-7xl font-bold mb-4">{results.scores.antifragility.toFixed(0)}</div>
        <p className="text-lg opacity-90">{badge.label}</p>
        <p className="text-sm opacity-80 mt-2">
          {results.scores.antifragility > 0
            ? 'You grew wealth during the crisis!'
            : 'You preserved wealth through the crisis'}
        </p>
      </Card>

      {/* Score Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Survival */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">🏥</div>
          <div>
            <p className="text-gray-600 mb-1">Survival Status</p>
            <p className={`text-2xl font-bold ${results.scores.survival ? 'text-green-600' : 'text-red-600'}`}>
              {results.scores.survival ? 'Alive ✓' : 'Bankrupt ✗'}
            </p>
          </div>
        </Card>

        {/* Overall Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">🎯</div>
          <div>
            <p className="text-gray-600 mb-1">Overall Score</p>
            <p className="text-2xl font-bold text-blue-600">{results.scores.overall.toFixed(0)}/100</p>
          </div>
        </Card>

        {/* XP Earned */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">⭐</div>
          <div>
            <p className="text-gray-600 mb-1">XP Earned</p>
            <p className="text-2xl font-bold text-purple-600">{results.xp_earned} XP</p>
          </div>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card className="p-6 space-y-6">
        <h3 className="text-2xl font-bold">Portfolio Performance</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">
              ₹{(results.performance.starting_wealth / 100000).toFixed(1)}L
            </p>
            <p className="text-gray-600">Starting Wealth</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-red-600">
              ₹{(results.performance.trough_wealth / 100000).toFixed(1)}L
            </p>
            <p className="text-gray-600">Trough (Lowest)</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">
              ₹{(results.performance.final_wealth / 100000).toFixed(1)}L
            </p>
            <p className="text-gray-600">Final Wealth</p>
          </div>
          <div className="text-center">
            <p className={`text-3xl font-bold ${returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(1)}%
            </p>
            <p className="text-gray-600">Total Return</p>
          </div>
        </div>
      </Card>

      {/* Risk Analysis */}
      <Card className="p-6 space-y-4">
        <h3 className="text-2xl font-bold">Risk Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-2">Maximum Drawdown</p>
            <div className="w-full bg-gray-200 rounded h-6 mb-2">
              <div
                className="bg-red-600 h-6 rounded"
                style={{ width: `${Math.min(drawdownPct, 100)}%` }}
              />
            </div>
            <p className="text-sm font-semibold">{drawdownPct.toFixed(1)}% loss at worst point</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-2">Recovery Assessment</p>
            <div className="space-y-2">
              {results.performance.final_wealth > results.performance.starting_wealth ? (
                <div className="flex items-center gap-2 text-green-700">
                  <TrendingUp className="w-5 h-5" />
                  <span>You recovered beyond starting wealth</span>
                </div>
              ) : results.performance.final_wealth > results.performance.trough_wealth * 1.1 ? (
                <div className="flex items-center gap-2 text-amber-700">
                  <TrendingUp className="w-5 h-5" />
                  <span>You recovered somewhat from trough</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-red-700">
                  <TrendingDown className="w-5 h-5" />
                  <span>Still recovering from crisis</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Antifragility Explanation */}
      <Card className="p-6 bg-blue-50 border border-blue-200 space-y-4">
        <h3 className="text-lg font-bold">Understanding Your Antifragility Score</h3>
        <div className="space-y-2 text-sm">
          <p>
            <strong>Antifragility</strong> measures more than survival. It's about thriving through chaos.
          </p>
          <div className="space-y-1 text-gray-700">
            <p>• <strong>Negative score (-100 to 0):</strong> Defensive success. You protected wealth through hedging and cash.</p>
            <p>• <strong>+0 to +50:</strong> Resilient. You maintained or slightly grew wealth.</p>
            <p>• <strong>+50 to +100:</strong> Opportunistic. You buy dips and profit from panic.</p>
          </div>
        </div>
      </Card>

      {/* Key Insights */}
      <Card className="p-6 bg-amber-50 border border-amber-200 space-y-4">
        <h3 className="text-lg font-bold">💡 Key Insights</h3>
        <ul className="space-y-2 text-sm">
          <li>
            ✓ You experienced a {drawdownPct.toFixed(0)}% drawdown - typical crisis impact
          </li>
          <li>
            ✓ Your {results.scores.antifragility > 0 ? 'antifragile positioning' : 'defensive positioning'} {results.scores.antifragility > 0 ? 'let you profit' : 'protected'} during the crisis
          </li>
          <li>
            ✓ Consider how pre-crisis decisions affect outcomes
          </li>
          {results.scores.antifragility < -50 && (
            <li>
              ✓ Your cash holdings saved you - emergency funds matter
            </li>
          )}
        </ul>
      </Card>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Button
          onClick={() => router.push('/games')}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Home className="w-4 h-4 mr-2" />
          Back to Games
        </Button>
        <Button
          onClick={() => router.push('/games/black-swan')}
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Try Another Crisis
        </Button>
        <Button
          className="bg-gray-600 hover:bg-gray-700 text-white cursor-not-allowed"
          disabled
        >
          Share Coming Soon
        </Button>
      </div>
    </div>
  );
}
