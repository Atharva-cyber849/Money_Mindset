'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import GameHeader from '../_lib/GameHeader';
import DecisionModal from './components/DecisionModal';
import LifeState from './components/LifeState';
import MetricsPanel from './components/MetricsPanel';
import CareerPathPanel from './components/CareerPathPanel';
import { EnhancedDecisionModal, FinancialLiteracyCard } from '../_lib/SharedComponents';
import { Loader2, Play, ChevronRight } from 'lucide-react';

interface KarobarSession {
  session_id: string;
  current_age: number;
  current_month: number;
  current_year: number;
  status: string;
  gender: string;
  city: string;
  education: string;
  starting_job?: string;
  current_state?: any;
}

interface Decision {
  id: string;
  age: number;
  decision_type: string;
  description: string;
  options: Array<{
    id: number;
    text: string;
    salary_impact: number;
    happiness_impact: number;
    career_satisfaction_impact: number;
    wealth_impact: number;
  }>;
}

export default function KarobarGame() {
  const router = useRouter();
  const [setupScreen, setSetupScreen] = useState(true);
  const [session, setSession] = useState<KarobarSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [currentDecision, setCurrentDecision] = useState<Decision | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [activeStage, setActiveStage] = useState<'overview' | 'decisions' | 'metrics'>('overview');

  // Business decision state
  const [businessDecision, setBusinessDecision] = useState<any>(null);
  const [showBusinessDecisionModal, setShowBusinessDecisionModal] = useState(false);
  const [submittingBusinessDecision, setSubmittingBusinessDecision] = useState(false);

  // Setup form state
  const [gender, setGender] = useState('female');
  const [city, setCity] = useState('bangalore');
  const [education, setEducation] = useState('ug');
  const [startingJob, setStartingJob] = useState('salaried');

  const normalizeSession = (rawSession: any): KarobarSession => {
    const state = rawSession?.current_state && typeof rawSession.current_state === 'object'
      ? rawSession.current_state
      : {};

    const currentAge = Number(rawSession?.current_age ?? state?.age ?? 22);
    const currentMonth = Number(rawSession?.current_month ?? state?.current_month ?? 0);
    const currentYear = Number(rawSession?.current_year ?? state?.current_year ?? 0);

    return {
      ...rawSession,
      current_age: Number.isFinite(currentAge) ? currentAge : 22,
      current_month: Number.isFinite(currentMonth) ? currentMonth : 0,
      current_year: Number.isFinite(currentYear) ? currentYear : 0,
      status: rawSession?.status === 'created' ? 'active' : (rawSession?.status || 'active'),
      current_state: state,
    };
  };

  useEffect(() => {
    loadSession();
  }, []);

  const loadSession = async () => {
    try {
      const response = await api.get('/games/karobaar/user/sessions');
      const sessions = response.data.sessions;

      if (sessions.length > 0) {
        const lastSession = sessions[0];
        if (lastSession.status === 'active') {
          const sessionDetails = await api.get(`/games/karobaar/${lastSession.session_id}`);
          setSession(normalizeSession(sessionDetails.data));
          setSetupScreen(false);
        }
      }
    } catch (error) {
      console.log('No active Karobaar session found');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGame = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/games/karobaar/create', {
        gender,
        city,
        education,
        starting_job: startingJob,
      });

      setSession(normalizeSession(response.data));
      setSetupScreen(false);
      
      // Fetch business decision after game starts
      await fetchBusinessDecision(response.data.session_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  const fetchBusinessDecision = async (sessionId: string) => {
    try {
      const response = await api.get(`/games/karobaar/${sessionId}/business-decision`);
      if (response.data.has_decision) {
        setBusinessDecision(response.data);
        setShowBusinessDecisionModal(true);
      }
    } catch (error) {
      console.error('Failed to fetch business decision:', error);
    }
  };

  const handleProgress = async () => {
    if (!session) return;
    setSubmitting(true);
    try {
      const response = await api.post(`/games/karobaar/${session.session_id}/progress`);
      setSession(normalizeSession(response.data));

      // If there's a pending decision, show modal
      if (response.data.pending_decision) {
        setCurrentDecision(response.data.pending_decision);
        setShowDecisionModal(true);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to progress game');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDecision = async (choiceIndex: number) => {
    if (!session || !currentDecision) return;
    setSubmitting(true);
    try {
      const response = await api.post(
        `/games/karobaar/${session.session_id}/decide`,
        {
          decision_id: currentDecision.id,
          choice_index: choiceIndex,
        }
      );

      setSession(normalizeSession(response.data));
      setShowDecisionModal(false);

      // Check if game should continue
      if (response.data.current_age >= 65) {
        router.push(`/games/karobaar/results?session_id=${session.session_id}`);
      } else if (response.data.next_decision) {
        setCurrentDecision(response.data.next_decision);
        setShowDecisionModal(true);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to make decision');
    } finally {
      setSubmitting(false);
    }
  };

  const handleComplete = async () => {
    if (!session) return;
    setSubmitting(true);
    try {
      await api.post(`/games/karobaar/${session.session_id}/complete`);
      router.push(`/games/karobaar/results?session_id=${session.session_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete game');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  // Setup Screen
  if (setupScreen) {
    return (
      <div className="max-w-2xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-3">
          <h1 className="text-4xl font-bold">💼 Karobaar: The Business of Life</h1>
          <p className="text-gray-600">
            Navigate 43 years of financial and personal decisions. Your choices shape your career, family, and wealth.
          </p>
        </div>

        <Card className="p-8 space-y-6">
          <h2 className="text-2xl font-bold">Create Your Character</h2>

          {error && (
            <div className="p-4 bg-red-100 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {/* Gender Selection */}
          <div className="space-y-3">
            <label className="block font-semibold">Gender</label>
            <div className="grid grid-cols-2 gap-4">
              {['female', 'male'].map((g) => (
                <button
                  key={g}
                  onClick={() => setGender(g)}
                  className={`p-4 border-2 rounded-lg transition ${
                    gender === g
                      ? 'border-cyan-500 bg-cyan-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="font-semibold capitalize">{g}</div>
                  <div className="text-sm text-gray-600">
                    {g === 'female' ? '👩 Woman' : '👨 Man'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* City Selection */}
          <div className="space-y-3">
            <label className="block font-semibold">Starting City</label>
            <div className="grid grid-cols-2 gap-4">
              {[
                { id: 'mumbai', label: 'Mumbai', emoji: '🏙️' },
                { id: 'bangalore', label: 'Bangalore', emoji: '🌆' },
                { id: 'delhi', label: 'Delhi', emoji: '🏛️' },
                { id: 'tier2', label: 'Tier-2 City', emoji: '🏘️' },
              ].map((c) => (
                <button
                  key={c.id}
                  onClick={() => setCity(c.id)}
                  className={`p-4 border-2 rounded-lg transition ${
                    city === c.id
                      ? 'border-cyan-500 bg-cyan-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="text-2xl">{c.emoji}</div>
                  <div className="font-semibold">{c.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Education Selection */}
          <div className="space-y-3">
            <label className="block font-semibold">Education</label>
            <div className="grid grid-cols-3 gap-4">
              {[
                { id: 'ug', label: 'Bachelor (UG)' },
                { id: 'pg', label: 'Masters (PG)' },
                { id: 'iit', label: 'IIT' },
              ].map((e) => (
                <button
                  key={e.id}
                  onClick={() => setEducation(e.id)}
                  className={`p-4 border-2 rounded-lg transition ${
                    education === e.id
                      ? 'border-cyan-500 bg-cyan-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="font-semibold">{e.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Starting Job */}
          <div className="space-y-3">
            <label className="block font-semibold">Starting Career Path</label>
            <div className="grid grid-cols-3 gap-4">
              {[
                { id: 'salaried', label: 'Salaried (Stable)' },
                { id: 'freelance', label: 'Freelance (Flexible)' },
                { id: 'business', label: 'Business (Risky)' },
              ].map((j) => (
                <button
                  key={j.id}
                  onClick={() => setStartingJob(j.id)}
                  className={`p-4 border-2 rounded-lg transition text-sm ${
                    startingJob === j.id
                      ? 'border-cyan-500 bg-cyan-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="font-semibold">{j.label}</div>
                </button>
              ))}
            </div>
          </div>

          <Button
            onClick={handleCreateGame}
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-blue-700 text-white py-3"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating Your Story...
              </>
            ) : (
              <>
                Begin Your 43-Year Journey
                <ChevronRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </Card>
      </div>
    );
  }

  // Game Screen
  if (!session) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <GameHeader
        title="💼 Karobaar"
        gameMonth={session.current_month || 0}
        totalMonths={516}
        description={`Age ${session.current_age} • Year ${session.current_year}`}
      />

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-3 grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          onClick={() => setActiveStage('overview')}
          className={`px-4 py-3 rounded-lg font-semibold text-sm transition-all ${
            activeStage === 'overview' ? 'bg-cyan-600 text-white shadow-md ring-2 ring-cyan-300' : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          👤 Life State
        </button>
        <button
          onClick={() => setActiveStage('decisions')}
          className={`px-4 py-3 rounded-lg font-semibold text-sm transition-all ${
            activeStage === 'decisions' ? 'bg-cyan-600 text-white shadow-md ring-2 ring-cyan-300' : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          🎯 Decision
        </button>
        <button
          onClick={() => setActiveStage('metrics')}
          className={`px-4 py-3 rounded-lg font-semibold text-sm transition-all ${
            activeStage === 'metrics' ? 'bg-cyan-600 text-white shadow-md ring-2 ring-cyan-300' : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          📊 Metrics
        </button>
      </div>

      {activeStage === 'overview' && session.current_state && (
        <div className="space-y-6">
          <LifeState state={session.current_state} />
          <CareerPathPanel state={session.current_state} />
        </div>
      )}

      {activeStage === 'decisions' && (
        <Card className="p-6 space-y-4">
          <h3 className="font-semibold text-lg">What's Next?</h3>
          <div className="space-y-3">
            <Button
              onClick={handleProgress}
              disabled={submitting || session.status !== 'active'}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 transition-all"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Progressing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Continue to Next Year →
                </>
              )}
            </Button>

            {session.current_age >= 65 && (
              <Button
                onClick={handleComplete}
                disabled={submitting}
                className="w-full bg-cyan-600 hover:bg-blue-700 text-white"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Completing...
                  </>
                ) : (
                  'See Final Results'
                )}
              </Button>
            )}
          </div>
        </Card>
      )}

      {activeStage === 'metrics' && session.current_state && (
        <MetricsPanel state={session.current_state} />
      )}

      {/* Decision Modal */}
      {showDecisionModal && currentDecision && (
        <DecisionModal
          decision={currentDecision}
          onChoose={handleDecision}
          isLoading={submitting}
        />
      )}

      {showBusinessDecisionModal && businessDecision && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex flex-col items-center justify-center p-4 overflow-y-auto">
          <div className="flex flex-col gap-6 w-full max-w-2xl py-6">
            <EnhancedDecisionModal
              title={businessDecision.decision_title}
              description={businessDecision.description}
              event_type={businessDecision.event_type}
              options={businessDecision.options.map((opt: any) => ({
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
                setSubmittingBusinessDecision(true);
                setError('');
                try {
                  const response = await api.post(`/games/karobaar/${session?.session_id}/business-decision`, {
                    option_index: optionIndex,
                  });

                  if (response.data?.current_state && session) {
                    setSession({
                      ...session,
                      current_state: response.data.current_state,
                    });
                  }

                  setShowBusinessDecisionModal(false);
                } catch (error: any) {
                  setError(error?.response?.data?.detail || 'Failed to submit business decision');
                  console.error('Failed to submit business decision:', error);
                } finally {
                  setSubmittingBusinessDecision(false);
                }
              }}
              isLoading={submittingBusinessDecision}
            />
            <FinancialLiteracyCard
              concept="opportunity_cost"
              impact_amount={0}
              context="Your career and life decisions compound over 43 years. Choose wisely."
            />
          </div>
        </div>
      )}
    </div>
  );
}
