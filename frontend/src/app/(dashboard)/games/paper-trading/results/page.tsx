'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Trophy, TrendingUp, Award } from 'lucide-react';
import { api } from '@/lib/api/client';

export default function PaperTradingResults({ params }: { params: { sessionId: string } }) {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSession();
  }, []);

  const fetchSession = async () => {
    try {
      const response = await api.get(`/games/paper-trading/${params.sessionId}`);
      setSession(response.data);
    } catch (err) {
      console.error('Failed to fetch session:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading results...</div>;
  }

  if (!session) {
    return <div className="flex items-center justify-center min-h-screen">Failed to load results</div>;
  }

  const pnl = session.total_pnl || 0;
  const pnlPct = session.pnl_percentage || 0;
  const scores = session.scores || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <Link href="/dashboard/games" className="mb-6 flex items-center gap-2 w-fit text-slate-600 hover:text-slate-900">
        <ArrowLeft size={20} />
        Back to Games
      </Link>

      <div className="max-w-4xl mx-auto">
        {/* Header with Trophy */}
        <div className="text-center mb-12">
          <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Trading Session Complete!</h1>
          <p className="text-lg text-slate-600">
            {session.market.toUpperCase()} Market • {session.strategy} Strategy
          </p>
        </div>

        {/* Performance Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Wealth */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-600 font-medium">Final Wealth</span>
              <DollarIcon />
            </div>
            <p className="text-3xl font-bold text-slate-900">{session.final_wealth?.toLocaleString()}</p>
            <p className="text-sm text-slate-500 mt-2">Vs. {session.initial_capital} initial</p>
          </div>

          {/* P&L */}
          <div className={`bg-white p-6 rounded-lg shadow-lg ${pnl >= 0 ? 'border-2 border-green-500' : 'border-2 border-red-500'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-600 font-medium">Profit/Loss</span>
              <TrendingUp className={pnl >= 0 ? 'text-green-500' : 'text-red-500'} />
            </div>
            <p className={`text-3xl font-bold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {pnl >= 0 ? '+' : ''}{pnl.toLocaleString()}
            </p>
            <p className={`text-sm mt-2 ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%
            </p>
          </div>

          {/* Total Score */}
          <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 text-white p-6 rounded-lg shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Trading Score</span>
              <Award />
            </div>
            <p className="text-3xl font-bold">{Math.round(scores.total_score || 0)}/100</p>
            <p className="text-sm mt-2 text-cyan-100">Your performance rating</p>
          </div>
        </div>

        {/* Detailed Scores */}
        <div className="bg-white p-8 rounded-lg shadow-lg mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Score Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ScoreCard
              title="Portfolio Score"
              score={Math.round(scores.portfolio_score || 0)}
              maxScore={30}
              description="Wealth generation vs initial capital"
            />
            <ScoreCard
              title="Diversification Score"
              score={Math.round(scores.diversification_score || 0)}
              maxScore={25}
              description="Sector and asset balance"
            />
            <ScoreCard
              title="Risk-Adjusted Score"
              score={Math.round(scores.risk_adjusted_score || 0)}
              maxScore={20}
              description="Performance per unit of risk"
            />
            <ScoreCard
              title="Timing Score"
              score={Math.round(scores.timing_score || 0)}
              maxScore={15}
              description="Trade win rate and execution"
            />
            <ScoreCard
              title="Adherence Score"
              score={Math.round(scores.adherence_score || 0)}
              maxScore={10}
              description="Consistency with strategy"
            />
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-cyan-50 border border-cyan-200 p-6 rounded-lg mb-8">
          <h3 className="font-bold text-cyan-900 mb-4">📚 Learning Recommendations</h3>
          <ul className="space-y-2 text-cyan-800 text-sm">
            {pnl < 0 && <li>• Focus on risk management: Consider using stop-losses to limit downside</li>}
            {scores.diversification_score < 15 && <li>• Improve diversification: Spread across more sectors and asset classes</li>}
            {scores.timing_score < 10 && <li>• Work on entry/exit timing: Study market patterns and technical analysis</li>}
            <li>• Try a different strategy to expand your trading skills</li>
            <li>• Compare your performance: Play again and track your improvement</li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/dashboard/games"
            className="px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-semibold text-center"
          >
            Back to Games
          </Link>
          <Link
            href="/dashboard/games/paper-trading"
            className="px-6 py-3 bg-cyan-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-center"
          >
            Try Again
          </Link>
        </div>
      </div>
    </div>
  );
}

function ScoreCard({
  title,
  score,
  maxScore,
  description,
}: {
  title: string;
  score: number;
  maxScore: number;
  description: string;
}) {
  const percentage = (score / maxScore) * 100;
  const color = percentage >= 75 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <h4 className="font-semibold text-slate-900">{title}</h4>
        <span className="text-lg font-bold text-slate-900">
          {score}/{maxScore}
        </span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full ${color} transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-slate-600">{description}</p>
    </div>
  );
}

function DollarIcon() {
  return <span className="text-2xl">💰</span>;
}
