'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import GameHeader from '../_lib/GameHeader';
import FinancialMetricsPanel from '../_lib/FinancialMetricsPanel';
import CompoundGraph from './components/CompoundGraph';
import InterruptionModal from './components/InterruptionModal';
import ProjectionConeChart from './components/ProjectionConeChart';
import StrategyComparison from './components/StrategyComparison';
import { Loader2, Play, Pause, Zap } from 'lucide-react';

interface SIPSession {
  session_id: string;
  current_month: number;
  current_age: number;
  status: string;
  accumulated_wealth: number;
  total_contributions: number;
  monthly_sip: number;
  sip_type: string;
}

interface Interruption {
  month: number;
  age: number;
  type: string;
  description: string;
  options: Array<{ action: string; description: string; consequence: string }>;
}

interface InterruptionDecision {
  month: number;
  age: number;
  type: string;
  action: string;
  consequence: string;
}

export default function SIPChroniclesGame() {
  const router = useRouter();
  const [session, setSession] = useState<SIPSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [gameStarted, setGameStarted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<'manual' | 'slow' | 'fast'>('manual');
  const [wealthHistory, setWealthHistory] = useState<Array<{ month: number; wealth: number; age: number }>>([]);
  const [interruption, setInterruption] = useState<Interruption | null>(null);
  const [showInterruptionModal, setShowInterruptionModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [sipType, setSIPType] = useState('nifty_50');
  const [interruptionHistory, setInterruptionHistory] = useState<InterruptionDecision[]>([]);
  const [activeStage, setActiveStage] = useState<'overview' | 'analysis' | 'actions'>('overview');

  useEffect(() => {
    loadSession();
  }, []);

  // Auto-progression when playing
  useEffect(() => {
    if (!isPlaying || !session) return;

    const interval = setInterval(() => {
      progressMonth();
    }, playbackSpeed === 'fast' ? 200 : playbackSpeed === 'slow' ? 2000 : Infinity);

    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, session]);

  const loadSession = async () => {
    try {
      const response = await api.get('/games/sip/user/sessions');
      const sessions = response.data.sessions;

      if (sessions.length > 0) {
        const lastSession = sessions[0];
        if (lastSession.status === 'active') {
          const sessionDetails = await api.get(`/games/sip/${lastSession.session_id}`);
          setSession(sessionDetails.data);
          setGameStarted(true);

          // Load wealth history
          const snapshots = sessionDetails.data.monthly_snapshots || [];
          setWealthHistory(snapshots.map((s: any) => ({ month: s.month, wealth: s.wealth, age: s.age })));
        }
      }
    } catch (error) {
      console.log('No active SIP session found');
    } finally {
      setLoading(false);
    }
  };

  const createNewGame = async () => {
    try {
      setSubmitting(true);
      const response = await api.post('/games/sip/create', {
        sip_type: sipType,
      });

      setSession(response.data);
      setGameStarted(true);
      setWealthHistory([{ month: 0, wealth: 0, age: 22 }]);
      setIsPlaying(false);
    } catch (error) {
      console.error('Failed to create game:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const progressMonth = async () => {
    if (!session) return;

    try {
      const response = await api.post(
        `/games/sip/${session.session_id}/progress`,
        { fast_forward_months: 1 }
      );

      // Update session
      setSession({
        ...session,
        current_month: response.data.current_month,
        current_age: response.data.current_age,
        accumulated_wealth: response.data.accumulated_wealth,
        total_contributions: response.data.total_contributions,
        monthly_sip: response.data.monthly_sip,
      });

      // Add to wealth history
      setWealthHistory((prev) => [
        ...prev,
        {
          month: response.data.current_month,
          wealth: response.data.accumulated_wealth,
          age: response.data.current_age,
        },
      ]);

      // Show interrupt if present
      if (response.data.interruption) {
        setInterruption(response.data.interruption);
        setShowInterruptionModal(true);
        setIsPlaying(false);
      }

      // Check if game complete (456 months = age 60)
      if (response.data.current_month >= 456) {
        setIsPlaying(false);
        completeGame();
      }
    } catch (error) {
      console.error('Failed to progress:', error);
      setIsPlaying(false);
    }
  };

  const handleInterruptionResponse = async (action: string) => {
    if (!session || !interruption) return;

    try {
      setSubmitting(true);
      await api.post(
        `/games/sip/${session.session_id}/progress`,
        {
          fast_forward_months: 1,
          interruption_response: action,
        }
      );

      const selected = interruption.options.find((o) => o.action === action);
      setInterruptionHistory((prev) => [
        ...prev,
        {
          month: interruption.month,
          age: interruption.age,
          type: interruption.type,
          action,
          consequence: selected?.consequence || 'Outcome applied to your compounding path.',
        },
      ]);

      setShowInterruptionModal(false);
      setInterruption(null);

      // Auto-continue if not paused
      if (playbackSpeed !== 'manual') {
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Failed to respond to interruption:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const completeGame = async () => {
    try {
      const response = await api.post(`/games/sip/${session?.session_id}/complete`);
      router.push(`/games/sip-chronicles/results?session_id=${session?.session_id}`);
    } catch (error) {
      console.error('Failed to complete game:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  // Game setup screen
  if (!gameStarted) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card className="p-8 text-center">
          <h1 className="text-4xl font-bold mb-4">📈 SIP Chronicles</h1>
          <p className="text-lg text-gray-600 mb-8">The Journey from ₹500/month to ₹1 Crore</p>
          <p className="text-gray-700 mb-8">
            Watch your wealth compound over 38 years. Starting with just ₹500/month SIP at age 22,
            navigate life interruptions and see how small consistent actions lead to massive wealth.
          </p>

          <div className="mb-8">
            <label className="block text-sm font-medium mb-2">Choose Your Investment</label>
            <select
              value={sipType}
              onChange={(e) => setSIPType(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option value="nifty_50">Nifty 50 (10% CAGR)</option>
              <option value="midcap_150">Midcap 150 (12% CAGR)</option>
              <option value="elss">ELSS (10% CAGR + Tax Benefit)</option>
              <option value="gold">Gold (5% CAGR)</option>
            </select>
          </div>

          <Button onClick={createNewGame} disabled={submitting} className="w-full py-3 text-lg">
            {submitting ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : null}
            Start Your SIP Journey
          </Button>
        </Card>
      </div>
    );
  }

  // Active game screen
  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <GameHeader
        title="📈 SIP Chronicles"
        gameMonth={session?.current_month || 0}
        totalMonths={456}
        description="From ₹500/month to financial freedom"
      />

      <FinancialMetricsPanel
        netWorth={session?.accumulated_wealth || 0}
        monthlyIncome={session?.monthly_sip || 0}
        savingsRate={100}
      />

      <div className="bg-white rounded-lg border border-slate-200 p-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          onClick={() => setActiveStage('overview')}
          className={`px-4 py-2 rounded-md font-semibold text-sm transition ${
            activeStage === 'overview' ? 'bg-cyan-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
          }`}
        >
          Stage 1: Wealth Overview
        </button>
        <button
          onClick={() => setActiveStage('analysis')}
          className={`px-4 py-2 rounded-md font-semibold text-sm transition ${
            activeStage === 'analysis' ? 'bg-cyan-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
          }`}
        >
          Stage 2: Analysis
        </button>
        <button
          onClick={() => setActiveStage('actions')}
          className={`px-4 py-2 rounded-md font-semibold text-sm transition ${
            activeStage === 'actions' ? 'bg-cyan-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
          }`}
        >
          Stage 3: Actions
        </button>
      </div>

      {/* Wealth counter */}
      {activeStage === 'overview' && (
        <>
          <Card className="p-8 bg-gradient-to-r from-green-50 to-emerald-50 text-center">
            <p className="text-sm text-gray-600 mb-2">Current Wealth (Age {session?.current_age})</p>
            <p className="text-5xl font-bold text-green-600 mb-2">
              ₹{((session?.accumulated_wealth || 0) / 100000).toFixed(1)}L
            </p>
            <p className="text-sm text-gray-600">
              Contributed: ₹{((session?.total_contributions || 0) / 100000).toFixed(1)}L ·
              Multiplier: {((session?.accumulated_wealth || 1) / (session?.total_contributions || 1)).toFixed(1)}x
            </p>
          </Card>

          {wealthHistory.length > 1 && (
            <CompoundGraph data={wealthHistory} />
          )}
        </>
      )}

      {activeStage === 'analysis' && (
        <>
          {wealthHistory.length > 2 && (
            <ProjectionConeChart
              data={wealthHistory}
              monthlySIP={session?.monthly_sip || 5000}
            />
          )}

          <StrategyComparison monthlySIP={session?.monthly_sip || 5000} />

          {interruptionHistory.length > 0 && (
            <Card className="p-6 space-y-4">
              <h3 className="text-xl font-bold">Interruption Consequence Replay</h3>
              <p className="text-sm text-gray-600">Your major decisions and how each one impacted long-term wealth compounding.</p>
              <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
                {interruptionHistory.slice(-8).reverse().map((event, idx) => (
                  <div key={`${event.month}-${idx}`} className="rounded border border-gray-200 bg-gray-50 p-3">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-gray-900">{event.type.replace('_', ' ').toUpperCase()} • Age {event.age}</p>
                      <p className="text-xs text-gray-600">Month {event.month}</p>
                    </div>
                    <p className="text-sm text-cyan-700 mt-1">You chose: {event.action}</p>
                    <p className="text-sm text-gray-700 mt-1">Consequence: {event.consequence}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}

      {activeStage === 'actions' && (
        <Card className="p-6">
          <div className="flex gap-4 items-center justify-center">
            <Button
              onClick={() => setIsPlaying(!isPlaying)}
              disabled={session?.current_month >= 456}
              className={isPlaying ? 'bg-red-600 hover:bg-red-700' : ''}
            >
              {isPlaying ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Play
                </>
              )}
            </Button>

            <Button
              onClick={() => progressMonth()}
              disabled={session?.current_month >= 456 || isPlaying}
              variant="outline"
            >
              Next Month
            </Button>

            <select
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(e.target.value as any)}
              className="p-2 border rounded"
            >
              <option value="manual">Manual</option>
              <option value="slow">Slow (1 month / 2s)</option>
              <option value="fast">Fast (1 month / 200ms)</option>
            </select>
          </div>
        </Card>
      )}

      {session?.current_month >= 456 && (
        <Button onClick={completeGame} className="w-full py-4 text-lg bg-green-600 hover:bg-green-700">
          See Results & Final Score
        </Button>
      )}

      {showInterruptionModal && interruption && (
        <InterruptionModal
          interruption={interruption}
          onResponse={handleInterruptionResponse}
          disabled={submitting}
        />
      )}
    </div>
  );
}
