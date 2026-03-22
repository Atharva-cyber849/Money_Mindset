'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { Loader2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface GameResults {
  resilience_score: number;
  resilience_breakdown: {
    wealth_score: number;
    emergency_score: number;
    diversification_score: number;
    long_term_score: number;
    gold_score: number;
    total: number;
  };
  summary: {
    total_months: number;
    final_age: number;
    final_wealth: number;
    final_allocation: {
      emergency: number;
      insurance: number;
      short_term: number;
      long_term: number;
      gold: number;
    };
    total_events: number;
    average_monthly_income: number;
    events_log: Array<{
      month: number;
      type: string;
      description: string;
    }>;
  };
  xp_earned: number;
}

export default function GullakResults() {
  const searchParams = useSearchParams();
  const sessionId = searchParams?.get('session_id');
  const [results, setResults] = useState<GameResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadResults = async () => {
      try {
        if (!sessionId) {
          setError('No session found');
          return;
        }

        // Get session details
        const sessionResponse = await axios.get(`/api/v1/games/gullak/${sessionId}`);
        const data = sessionResponse.data;

        // Parse stored JSON data
        const resilience_breakdown = data.financial_health_index ? JSON.parse(data.financial_health_index) : {};
        const current_jars = data.current_jars;
        const events_log = data.events_log ? JSON.parse(data.events_log) : [];

        // Calculate total wealth
        const final_wealth = Object.values(current_jars as Record<string, number>).reduce((a: number, b: number) => a + b, 0);

        // Transform to match GameResults interface
        const results = {
          resilience_score: data.resilience_score,
          resilience_breakdown,
          summary: {
            total_months: data.current_month,
            final_age: 22 + Math.floor(data.current_month / 12),
            final_wealth,
            final_allocation: current_jars,
            total_events: events_log.length,
            average_monthly_income: 40000,
            events_log,
          },
          xp_earned: 0,
        };

        setResults(results as GameResults);
      } catch (err) {
        setError('Failed to load results');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card className="p-8 text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600 mb-8">{error || 'Failed to load results'}</p>
          <Link href="/games/gullak">
            <Button>Back to Game</Button>
          </Link>
        </Card>
      </div>
    );
  }

  const allocationData = [
    {
      name: 'Emergency Fund',
      value: results.summary.final_allocation.emergency,
      color: '#ef4444',
    },
    {
      name: 'Insurance',
      value: results.summary.final_allocation.insurance,
      color: '#f97316',
    },
    {
      name: 'Short-term',
      value: results.summary.final_allocation.short_term,
      color: '#eab308',
    },
    {
      name: 'Long-term',
      value: results.summary.final_allocation.long_term,
      color: '#22c55e',
    },
    {
      name: 'Gold',
      value: results.summary.final_allocation.gold,
      color: '#fbbf24',
    },
  ];

  const scoreData = [
    {
      name: 'Wealth',
      score: results.resilience_breakdown.wealth_score,
      max: 30,
    },
    {
      name: 'Emergency',
      score: results.resilience_breakdown.emergency_score,
      max: 25,
    },
    {
      name: 'Diversification',
      score: results.resilience_breakdown.diversification_score,
      max: 20,
    },
    {
      name: 'Long-term',
      score: results.resilience_breakdown.long_term_score,
      max: 15,
    },
    {
      name: 'Gold',
      score: results.resilience_breakdown.gold_score,
      max: 10,
    },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getScoreEmoji = (score: number) => {
    if (score >= 85) return '🚀';
    if (score >= 75) return '🎯';
    if (score >= 65) return '📈';
    if (score >= 50) return '💪';
    return '📚';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Final Score */}
      <Card className="p-8 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="text-center space-y-4">
          <div className="text-7xl">{getScoreEmoji(results.resilience_score)}</div>
          <h1 className="text-4xl font-bold">Game Complete!</h1>
          <div className="space-y-2">
            <p className="text-6xl font-bold">
              <span className={getScoreColor(results.resilience_score)}>
                {results.resilience_score.toFixed(1)}
              </span>
              <span className="text-3xl text-gray-600"> / 100</span>
            </p>
            <p className="text-xl font-semibold">Financial Wellbeing Index</p>
          </div>

          <div className="bg-blue-100 text-blue-900 p-4 rounded mt-4">
            {results.resilience_score >= 80 && (
              <p>Excellent work! Your balanced approach to financial planning sets you up for long-term success.</p>
            )}
            {results.resilience_score >= 70 && results.resilience_score < 80 && (
              <p>Great job! You demonstrated good financial discipline and planning.</p>
            )}
            {results.resilience_score >= 60 && results.resilience_score < 70 && (
              <p>Good progress! Continue refining your allocation strategy.</p>
            )}
            {results.resilience_score < 60 && (
              <p>You learned valuable lessons! Review your allocation decisions and try again.</p>
            )}
          </div>

          <div className="space-y-2 mt-4">
            <p className="text-lg">
              <span className="font-semibold">+{results.xp_earned} XP</span> earned
            </p>
            <p className="text-sm text-gray-600">
              Age {results.summary.final_age} • {results.summary.total_months} months completed
            </p>
          </div>
        </div>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <p className="text-sm text-gray-600 mb-1">Final Wealth</p>
          <p className="text-3xl font-bold">₹{(results.summary.final_wealth / 100000).toFixed(1)}L</p>
          <p className="text-xs text-gray-500 mt-2">
            Avg monthly income: ₹{(results.summary.average_monthly_income / 1000).toFixed(0)}K
          </p>
        </Card>

        <Card className="p-6">
          <p className="text-sm text-gray-600 mb-1">Life Events</p>
          <p className="text-3xl font-bold">{results.summary.total_events}</p>
          <p className="text-xs text-gray-500 mt-2">
            Challenges navigated
          </p>
        </Card>

        <Card className="p-6">
          <p className="text-sm text-gray-600 mb-1">Time Horizon</p>
          <p className="text-3xl font-bold">{results.summary.final_age - 22} years</p>
          <p className="text-xs text-gray-500 mt-2">
            Age {22} → {results.summary.final_age}
          </p>
        </Card>
      </div>

      {/* Allocation Pie Chart */}
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Final Jar Allocation</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) =>
                    `${name}: ₹${(value / 100000).toFixed(0)}L`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `₹${(value / 100000).toFixed(1)}L`} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-3">
            {allocationData.map((item) => (
              <div key={item.name} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="font-medium">{item.name}</span>
                </div>
                <span className="text-lg font-bold">₹{(item.value / 100000).toFixed(1)}L</span>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Score Breakdown */}
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Financial Wellbeing Breakdown</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={scoreData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="score" fill="#3b82f6" name="Your Score" />
            <Bar dataKey="max" fill="#d1d5db" name="Max Points" />
          </BarChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          {scoreData.map((item) => (
            <div key={item.name} className="p-4 bg-gray-50 rounded">
              <p className="font-semibold">{item.name}</p>
              <p className="text-2xl font-bold">
                {item.score.toFixed(0)} / {item.max}
              </p>
              <div className="bg-gray-300 h-2 rounded mt-2 overflow-hidden">
                <div
                  className="bg-blue-500 h-full"
                  style={{ width: `${(item.score / item.max) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Events Encountered */}
      {results.summary.events_log.length > 0 && (
        <Card className="p-6">
          <h2 className="text-2xl font-bold mb-4">Life Events You Navigated</h2>
          <div className="space-y-2">
            {results.summary.events_log.slice(0, 10).map((event, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded flex justify-between items-start">
                <div>
                  <p className="font-semibold">Month {event.month}</p>
                  <p className="text-sm text-gray-600">{event.description}</p>
                </div>
                <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                  {event.type.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
            ))}
            {results.summary.events_log.length > 10 && (
              <p className="text-sm text-gray-600 text-center mt-4">
                +{results.summary.events_log.length - 10} more events
              </p>
            )}
          </div>
        </Card>
      )}

      {/* Call to Action */}
      <div className="flex gap-4">
        <Link href="/games/gullak" className="flex-1">
          <Button className="w-full py-3 text-lg">Play Again</Button>
        </Link>
        <Link href="/games" className="flex-1">
          <Button variant="outline" className="w-full py-3 text-lg">
            See Other Games
          </Button>
        </Link>
      </div>
    </div>
  );
}
