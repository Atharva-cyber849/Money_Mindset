'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api/client';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { Loader2 } from 'lucide-react';

interface GameResults {
  final_corpus: number;
  final_age: number;
  total_contributions: number;
  total_months: number;
  multiplier: number;
  financial_discipline_score: number;
  tax_savings: number;
  interruptions_count: number;
  xp_earned: number;
  interruptions_log: Array<{ month: number; age: number; type: string; description: string }>;
}

export default function SIPChronclesResults() {
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

        const response = await api.get(`/games/sip/${sessionId}`);
        const data = response.data;

        // Need to get the complete results - call completion endpoint instead
        const completeResponse = await api.post(`/games/sip/${sessionId}/complete`);
        setResults(completeResponse.data);
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
          <Link href="/games/sip-chronicles">
            <Button>Back to Game</Button>
          </Link>
        </Card>
      </div>
    );
  }

  const getDisciplineEmoji = (score: number) => {
    if (score >= 90) return '🏆';
    if (score >= 75) return '🎯';
    if (score >= 50) return '📈';
    if (score >= 25) return '💪';
    return '📚';
  };

  const getMultiplierColor = (multiplier: number) => {
    if (multiplier >= 4) return 'text-green-600';
    if (multiplier >= 3) return 'text-cyan-600';
    if (multiplier >= 2) return 'text-amber-600';
    return 'text-gray-600';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Final Score */}
      <Card className="p-8 bg-gradient-to-r from-green-50 to-emerald-50">
        <div className="text-center space-y-4">
          <div className="text-7xl">{getDisciplineEmoji(results.financial_discipline_score)}</div>
          <h1 className="text-4xl font-bold">Congratulations!</h1>
          <p className="text-xl font-semibold">Your SIP Journey is Complete</p>

          <div className="space-y-2">
            <p className="text-6xl font-bold">
              <span className={getMultiplierColor(results.multiplier)}>
                {results.multiplier.toFixed(1)}x
              </span>
            </p>
            <p className="text-gray-600">Your wealth multiplier from ₹500/month</p>
          </div>

          <div className="bg-white rounded p-4 mt-4">
            <p className="text-sm text-gray-600">Discipline Score</p>
            <p className="text-3xl font-bold">{results.financial_discipline_score.toFixed(0)} / 100</p>
          </div>

          <div className="space-y-1 text-sm">
            <p>
              <span className="font-semibold">+{results.xp_earned} XP</span> earned
            </p>
            <p className="text-gray-600">
              Navigated {results.interruptions_count} life interruptions
            </p>
          </div>
        </div>
      </Card>

      {/* Final Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <p className="text-sm text-gray-600 mb-1">Final Corpus</p>
          <p className="text-3xl font-bold">₹{(results.final_corpus / 100000).toFixed(1)}L</p>
          <p className="text-xs text-gray-500 mt-2">Age {results.final_age}</p>
        </Card>

        <Card className="p-6">
          <p className="text-sm text-gray-600 mb-1">Total Contributed</p>
          <p className="text-3xl font-bold">₹{(results.total_contributions / 100000).toFixed(1)}L</p>
          <p className="text-xs text-gray-500 mt2">{results.total_months} months</p>
        </Card>

        <Card className="p-6">
          <p className="text-sm text-gray-600 mb-1">Wealth Gained</p>
          <p className="text-3xl font-bold text-green-600">
            ₹{((results.final_corpus - results.total_contributions) / 100000).toFixed(1)}L
          </p>
          <p className="text-xs text-gray-500 mt-2">From compounding</p>
        </Card>
      </div>

      {/* Tax Benefit (ELSS) */}
      {results.tax_savings > 0 && (
        <Card className="p-6 bg-cyan-50">
          <h3 className="font-bold mb-2">💰 Tax Savings (ELSS Benefit)</h3>
          <p className="text-2xl font-bold text-cyan-600">₹{results.tax_savings.toLocaleString()}</p>
          <p className="text-sm text-gray-600 mt-2">Additional savings from 80C deduction</p>
        </Card>
      )}

      {/* Interruptions Encountered */}
      {results.interruptions_log.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Life Interruptions You Faced</h3>
          <div className="space-y-3">
            {results.interruptions_log.map((interrupt, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded flex justify-between">
                <div>
                  <p className="font-semibold text-sm">Month {interrupt.month}</p>
                  <p className="text-xs text-gray-600">{interrupt.description}</p>
                </div>
                <span className="text-xs text-gray-500 whitespace-nowrap ml-4">Age {interrupt.age}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Call to Action */}
      <div className="flex gap-4">
        <Link href="/games/sip-chronicles" className="flex-1">
          <Button className="w-full py-3 text-lg">Play Again</Button>
        </Link>
        <Link href="/games" className="flex-1">
          <Button variant="outline" className="w-full py-3 text-lg">
            Try Other Games
          </Button>
        </Link>
      </div>

      {/* Educational Note */}
      <Card className="p-6 bg-amber-50">
        <h4 className="font-bold mb-2">💡 Key Learning</h4>
        <p className="text-sm text-gray-700">
          Over {results.total_months} months, your ₹500/month SIP became ₹{(results.final_corpus / 100000).toFixed(1)}L through the
          power of compounding. Every interruption you faced tested your discipline. This is why SIP consistency matters!
        </p>
      </Card>
    </div>
  );
}
