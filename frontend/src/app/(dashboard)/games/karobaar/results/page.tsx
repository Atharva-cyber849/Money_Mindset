'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, Home, RotateCcw, Share2 } from 'lucide-react';

interface ResultsData {
  session_id: string;
  status: string;
  final_age: number;
  final_scores: {
    career: number;
    financial: number;
    happiness: number;
    overall: number;
  };
  final_net_worth: number;
  final_salary: number;
  decisions_made: number;
  xp_earned: number;
  decision_history: Array<{
    age: number;
    decision_type: string;
    choice: string;
    impacts: {
      salary: number;
      happiness: number;
      career: number;
      wealth: number;
    };
  }>;
}

const formatCurrency = (amount: number) => {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  return `₹${Math.round(amount).toLocaleString()}`;
};

const getScoreBadge = (score: number) => {
  if (score >= 90) return { emoji: '🏆', label: 'Legendary', color: 'from-yellow-400 to-yellow-600' };
  if (score >= 80) return { emoji: '⭐', label: 'Excellent', color: 'from-blue-400 to-blue-600' };
  if (score >= 70) return { emoji: '✨', label: 'Great', color: 'from-purple-400 to-purple-600' };
  if (score >= 60) return { emoji: '👍', label: 'Good', color: 'from-green-400 to-green-600' };
  return { emoji: '📚', label: 'Learning', color: 'from-gray-400 to-gray-600' };
};

export default function KarobarResults({ params }: { params: { session_id: string } }) {
  const router = useRouter();
  const [results, setResults] = useState<ResultsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadResults();
  }, [params.session_id]);

  const loadResults = async () => {
    try {
      const response = await axios.get(`/api/v1/games/karobaar/${params.session_id}`);
      setResults(response.data);
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
          <Button onClick={() => router.push('/games')}>
            Back to Games
          </Button>
        </Card>
      </div>
    );
  }

  const careerBadge = getScoreBadge(results.final_scores.career);
  const financialBadge = getScoreBadge(results.final_scores.financial);
  const happinessBadge = getScoreBadge(results.final_scores.happiness);
  const overallBadge = getScoreBadge(results.final_scores.overall);

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">🎬 Your Story is Complete!</h1>
        <p className="text-xl text-gray-600">
          You've navigated 43 years of financial and personal decisions.
        </p>
        <p className="text-gray-600">
          Here's how your life unfolded from age 22 to {results.final_age}...
        </p>
      </div>

      {/* Overall Score Hero Card */}
      <Card className={`bg-gradient-to-br ${overallBadge.color} text-white p-8 text-center`}>
        <div className="text-6xl mb-4">{overallBadge.emoji}</div>
        <h2 className="text-3xl font-bold mb-2">Overall Life Score</h2>
        <div className="text-7xl font-bold mb-4">{Math.round(results.final_scores.overall)}</div>
        <p className="text-lg opacity-90">{overallBadge.label}</p>
      </Card>

      {/* Three Dimension Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Career Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">{careerBadge.emoji}</div>
          <div>
            <p className="text-gray-600 mb-1">Career Score</p>
            <p className="text-4xl font-bold text-blue-600">{Math.round(results.final_scores.career)}</p>
            <p className="text-sm text-gray-600 mt-1">{careerBadge.label}</p>
          </div>
          <div className="bg-gray-100 p-3 rounded text-sm text-gray-700">
            Final Salary: {formatCurrency(results.final_salary)}
          </div>
        </Card>

        {/* Financial Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">{financialBadge.emoji}</div>
          <div>
            <p className="text-gray-600 mb-1">Financial Score</p>
            <p className="text-4xl font-bold text-green-600">{Math.round(results.final_scores.financial)}</p>
            <p className="text-sm text-gray-600 mt-1">{financialBadge.label}</p>
          </div>
          <div className="bg-gray-100 p-3 rounded text-sm text-gray-700">
            Final Net Worth: {formatCurrency(results.final_net_worth)}
          </div>
        </Card>

        {/* Happiness Score */}
        <Card className="p-6 text-center space-y-4">
          <div className="text-5xl">{happinessBadge.emoji}</div>
          <div>
            <p className="text-gray-600 mb-1">Happiness Score</p>
            <p className="text-4xl font-bold text-purple-600">{Math.round(results.final_scores.happiness)}</p>
            <p className="text-sm text-gray-600 mt-1">{happinessBadge.label}</p>
          </div>
          <div className="bg-gray-100 p-3 rounded text-sm text-gray-700">
            Life Balance Index
          </div>
        </Card>
      </div>

      {/* Statistics */}
      <Card className="p-6 space-y-6">
        <h3 className="text-2xl font-bold">Your Journey in Numbers</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">{results.decisions_made}</p>
            <p className="text-gray-600">Key Decisions Made</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{results.xp_earned}</p>
            <p className="text-gray-600">XP Earned</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-purple-600">43</p>
            <p className="text-gray-600">Years Lived</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-amber-600">{results.decision_history.length}</p>
            <p className="text-gray-600">Milestones Reached</p>
          </div>
        </div>
      </Card>

      {/* Decision Timeline */}
      {results.decision_history.length > 0 && (
        <Card className="p-6 space-y-6">
          <h3 className="text-2xl font-bold">Major Life Decisions</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {results.decision_history.map((decision, idx) => (
              <div key={idx} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-100 text-blue-600 font-bold text-sm">
                    {idx + 1}
                  </span>
                </div>
                <div className="flex-grow">
                  <p className="text-sm font-semibold text-gray-600">Age {decision.age}</p>
                  <p className="font-semibold text-gray-900">{decision.choice}</p>
                  <div className="flex gap-4 mt-2 text-xs">
                    {decision.impacts.salary !== 0 && (
                      <span className={decision.impacts.salary > 0 ? 'text-green-600' : 'text-red-600'}>
                        Salary {decision.impacts.salary > 0 ? '+' : ''}{Math.round(decision.impacts.salary * 100)}%
                      </span>
                    )}
                    {decision.impacts.career !== 0 && (
                      <span className={decision.impacts.career > 0 ? 'text-blue-600' : 'text-red-600'}>
                        Career {decision.impacts.career > 0 ? '+' : ''}{Math.round(decision.impacts.career)}
                      </span>
                    )}
                    {decision.impacts.happiness !== 0 && (
                      <span className={decision.impacts.happiness > 0 ? 'text-purple-600' : 'text-red-600'}>
                        Happiness {decision.impacts.happiness > 0 ? '+' : ''}{Math.round(decision.impacts.happiness)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

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
          onClick={() => router.push('/games/karobaar')}
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Play Again
        </Button>
        <Button
          className="bg-gray-600 hover:bg-gray-700 text-white cursor-not-allowed"
          disabled
        >
          <Share2 className="w-4 h-4 mr-2" />
          Share (Coming Soon)
        </Button>
      </div>

      {/* Insights */}
      <Card className="p-6 bg-blue-50 border border-blue-200 space-y-4">
        <h3 className="text-lg font-bold">💡 Key Insights</h3>
        <ul className="space-y-2 text-sm">
          <li>
            ✓ Your career and financial score reflect the balance between ambition and stability
          </li>
          <li>
            ✓ Happiness depends on more than just wealth - family time and health matter
          </li>
          <li>
            ✓ Early decisions (education, career path) have compounding effects
          </li>
          <li>
            ✓ Try different strategies in your next playthrough to explore alternative paths
          </li>
        </ul>
      </Card>
    </div>
  );
}
