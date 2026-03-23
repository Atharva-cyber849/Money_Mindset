'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import JarAllocation from './components/JarAllocation';
import LifeEventModal from './components/LifeEventModal';
import { TreemapChart, WaterfallChart, JarGrowthChart, ConsequencePanel, DecisionTimeline } from './components';
import GameHeader from '../_lib/GameHeader';
import FinancialMetricsPanel from '../_lib/FinancialMetricsPanel';
import { Loader2 } from 'lucide-react';

interface GameSession {
  session_id: string;
  current_month: number;
  status: string;
  current_jars: {
    emergency: number;
    insurance: number;
    short_term: number;
    long_term: number;
    gold: number;
  };
  income_type: string;
  state_location: string;
  decisions_made?: Array<Record<string, any>>;
  events_log?: Array<Record<string, any>>;
}

interface MonthlyEvent {
  month: number;
  type: string;
  description: string;
  impact_amount: number;
}

interface AllocationRecord {
  month: number;
  emergency: number;
  insurance: number;
  short_term: number;
  long_term: number;
  gold: number;
  totalAllocated: number;
  totalAssets: number;
}

export default function GullakGame() {
  const router = useRouter();
  const [session, setSession] = useState<GameSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [gameStarted, setGameStarted] = useState(false);
  const [monthlyIncome, setMonthlyIncome] = useState(0);
  const [monthlyExpenses, setMonthlyExpenses] = useState(0);
  const [lifeEvent, setLifeEvent] = useState<MonthlyEvent | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [allocationHistory, setAllocationHistory] = useState<AllocationRecord[]>([]);
  const [activeStage, setActiveStage] = useState<'allocate' | 'insights' | 'timeline'>('allocate');

  // Configuration options for new game
  const [incomeType, setIncomeType] = useState('salaried');
  const [stateLocation, setStateLocation] = useState('maharashtra');

  useEffect(() => {
    // Load any existing session
    loadSession();
  }, []);

  const mapSessionHistory = (sessionData: GameSession): AllocationRecord[] => {
    const fromDecisions = Array.isArray(sessionData.decisions_made) ? sessionData.decisions_made : [];

    const parsed = fromDecisions
      .map((entry, idx) => {
        const jars = entry.current_jars || entry.allocation || entry.jars || {};
        const emergency = Number(jars.emergency || 0);
        const insurance = Number(jars.insurance || 0);
        const short_term = Number(jars.short_term || 0);
        const long_term = Number(jars.long_term || 0);
        const gold = Number(jars.gold || 0);
        const totalAllocated = emergency + insurance + short_term + long_term + gold;

        return {
          month: Number(entry.month || entry.current_month || idx + 1),
          emergency,
          insurance,
          short_term,
          long_term,
          gold,
          totalAllocated,
          totalAssets: Number(entry.total_assets || totalAllocated),
        };
      })
      .filter((r) => r.totalAllocated > 0);

    if (parsed.length > 0) return parsed;

    const jars = sessionData.current_jars;
    const total = Object.values(jars || {}).reduce((a: number, b: number) => a + b, 0);
    if (total <= 0) return [];

    return [
      {
        month: sessionData.current_month || 1,
        emergency: Number(jars.emergency || 0),
        insurance: Number(jars.insurance || 0),
        short_term: Number(jars.short_term || 0),
        long_term: Number(jars.long_term || 0),
        gold: Number(jars.gold || 0),
        totalAllocated: total,
        totalAssets: total,
      },
    ];
  };

  const estimateMonthlyBase = (incomeType: string) => {
    if (incomeType === 'business') {
      return { income: 50000, expenses: 36000 };
    }
    if (incomeType === 'gig_work') {
      return { income: 38000, expenses: 29000 };
    }
    return { income: 40000, expenses: 30000 };
  };

  const loadSession = async () => {
    try {
      const response = await api.get('/games/gullak/user/sessions');
      const sessions = response.data.sessions;

      if (sessions.length > 0) {
        const lastSession = sessions[0];
        if (lastSession.status === 'active') {
          // Load active session
          const sessionDetails = await api.get(`/games/gullak/${lastSession.session_id}`);
          setSession(sessionDetails.data);
          setAllocationHistory(mapSessionHistory(sessionDetails.data));
          const latestDecision = (sessionDetails.data?.decisions_made || []).slice(-1)[0];
          if (latestDecision) {
            setMonthlyIncome(Number(latestDecision.income || 0));
            setMonthlyExpenses(Number(latestDecision.expenses || 0));
          } else {
            const base = estimateMonthlyBase(sessionDetails.data?.income_type || 'salaried');
            setMonthlyIncome(base.income);
            setMonthlyExpenses(base.expenses);
          }
          setGameStarted(true);
        }
      }
    } catch (error) {
      console.log('No active session found');
    } finally {
      setLoading(false);
    }
  };

  const createNewGame = async () => {
    try {
      setSubmitting(true);
      const response = await api.post('/games/gullak/create', {
        income_type: incomeType,
        state_location: stateLocation,
      });

      const newSession = response.data;
      setSession(newSession);
      setGameStarted(true);

      // Simulate first month with new session data
      await simulateFirstMonth(newSession);
    } catch (error) {
      console.error('Failed to create game:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const simulateFirstMonth = async (initialSession: GameSession) => {
    try {
      setLoading(true);

      const allocation = {
        emergency: initialSession.current_jars.emergency || 25000,
        insurance: initialSession.current_jars.insurance || 15000,
        short_term: initialSession.current_jars.short_term || 15000,
        long_term: initialSession.current_jars.long_term || 35000,
        gold: initialSession.current_jars.gold || 10000,
      };

      const response = await api.post(
        `/games/gullak/${initialSession.session_id}/allocate`,
        allocation
      );

      setMonthlyIncome(response.data.income);
      setMonthlyExpenses(response.data.expenses);

      if (response.data.event) {
        setLifeEvent(response.data.event);
        setShowEventModal(true);
      }

      const updated = await api.get(`/games/gullak/${initialSession.session_id}`);
      setSession(updated.data);
      setAllocationHistory(mapSessionHistory(updated.data));

    } catch (error) {
      console.error('Failed to simulate month:', error);
    } finally {
      setLoading(false);
    }
  };

  const simulateMonth = async () => {
    if (!session) return;

    try {
      setLoading(true);

      // Get current jars from session
      const jars = session.current_jars;

      // For the first month, use default allocation
      const allocation = {
        emergency: jars.emergency || 50000,
        insurance: jars.insurance || 10000,
        short_term: jars.short_term || 10000,
        long_term: jars.long_term || 20000,
        gold: jars.gold || 10000,
      };

      const response = await api.post(
        `/games/gullak/${session.session_id}/allocate`,
        allocation
      );

      // Update session data
      setMonthlyIncome(response.data.income);
      setMonthlyExpenses(response.data.expenses);

      if (response.data.event) {
        setLifeEvent(response.data.event);
        setShowEventModal(true);
      }

      // Refresh session
      const updated = await api.get(`/games/gullak/${session.session_id}`);
      setSession(updated.data);
      setAllocationHistory(mapSessionHistory(updated.data));

    } catch (error) {
      console.error('Failed to simulate month:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAllocationSubmit = async (allocation: any) => {
    try {
      setSubmitting(true);

      const response = await api.post(
        `/games/gullak/${session?.session_id}/allocate`,
        allocation
      );

      // Update state
      setMonthlyIncome(response.data.income);
      setMonthlyExpenses(response.data.expenses);

      if (response.data.event) {
        setLifeEvent(response.data.event);
        setShowEventModal(true);
      }

      // Refresh session
      const updated = await api.get(`/games/gullak/${session?.session_id}`);
      setSession(updated.data);
      setAllocationHistory(mapSessionHistory(updated.data));

    } catch (error) {
      console.error('Failed to allocate:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const completeGame = async () => {
    try {
      setSubmitting(true);

      const response = await api.post(
        `/games/gullak/${session?.session_id}/complete`
      );

      // Navigate to results
      router.push(`/games/gullak/results?session_id=${session?.session_id}`);

    } catch (error) {
      console.error('Failed to complete game:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  // Game selection screen
  if (!gameStarted) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card className="p-8 text-center">
          <h1 className="text-4xl font-bold mb-4">🏺 Gullak</h1>
          <p className="text-lg text-gray-600 mb-8">The Piggy Bank Game</p>
          <p className="text-gray-700 mb-8">
            Learn smart financial allocation through a 10-year life simulation.
            Divide your monthly surplus into 5 jars and navigate real Indian financial scenarios.
          </p>

          <div className="space-y-4 mb-8">
            <div>
              <label className="block text-sm font-medium mb-2">Income Type</label>
              <select
                value={incomeType}
                onChange={(e) => setIncomeType(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="salaried">Salaried Job</option>
                <option value="gig_work">Gig Work</option>
                <option value="business">Business</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">State Location</label>
              <select
                value={stateLocation}
                onChange={(e) => setStateLocation(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="maharashtra">Maharashtra</option>
                <option value="tamil_nadu">Tamil Nadu</option>
                <option value="karnataka">Karnataka</option>
                <option value="delhi">Delhi</option>
                <option value="punjab">Punjab</option>
                <option value="telangana">Telangana</option>
                <option value="rajasthan">Rajasthan</option>
                <option value="uttar_pradesh">Uttar Pradesh</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <Button
            onClick={createNewGame}
            disabled={submitting}
            className="w-full py-3 text-lg"
          >
            {submitting ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : null}
            Start Game
          </Button>
        </Card>
      </div>
    );
  }

  // Active game screen
  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <GameHeader
        title="🏺 Gullak - The Piggy Bank"
        gameMonth={session?.current_month || 0}
        totalMonths={120}
      />

      <FinancialMetricsPanel
        netWorth={session?.current_jars
          ? Object.values(session.current_jars).reduce((a: number, b: number) => a + b, 0)
          : 0}
        monthlyIncome={monthlyIncome}
        monthlyExpenses={monthlyExpenses}
      />

      <div className="bg-white rounded-lg border border-slate-200 p-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          onClick={() => setActiveStage('allocate')}
          className={`px-4 py-2 rounded-md font-semibold text-sm transition ${
            activeStage === 'allocate' ? 'bg-cyan-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
          }`}
        >
          Stage 1: Allocation
        </button>
        <button
          onClick={() => setActiveStage('insights')}
          className={`px-4 py-2 rounded-md font-semibold text-sm transition ${
            activeStage === 'insights' ? 'bg-cyan-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
          }`}
        >
          Stage 2: Insights
        </button>
        <button
          onClick={() => setActiveStage('timeline')}
          className={`px-4 py-2 rounded-md font-semibold text-sm transition ${
            activeStage === 'timeline' ? 'bg-cyan-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
          }`}
        >
          Stage 3: Timeline
        </button>
      </div>

      {session && (
        <>
          {activeStage === 'allocate' && (
            <>
              <JarAllocation
                currentJars={session.current_jars}
                monthlyIncome={monthlyIncome}
                monthlyExpenses={monthlyExpenses}
                onSubmitAllocation={handleAllocationSubmit}
                disabled={submitting}
              />

              <Card className="p-5 bg-cyan-50 border border-cyan-200">
                <h3 className="font-semibold text-cyan-900 mb-2">How to use this stage</h3>
                <p className="text-sm text-cyan-800">
                  Adjust sliders to allocate jars for the upcoming month, then submit. If income/expenses start at 0,
                  run one month first and values will populate from simulation output.
                </p>
              </Card>
            </>
          )}

          {activeStage === 'insights' && (
            <>
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-2">
                  <JarGrowthChart
                    month={session.current_month || 1}
                    jars={session.current_jars}
                  />
                </div>
                <TreemapChart jars={session.current_jars} />
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <WaterfallChart
                  income={monthlyIncome || 50000}
                  expenses={monthlyExpenses || 30000}
                  jars={session.current_jars}
                />
                <ConsequencePanel
                  emergencyFund={session.current_jars.emergency || 0}
                  monthlyExpenses={monthlyExpenses || 30000}
                  insurance={session.current_jars.insurance || 0}
                  totalJars={Object.values(session.current_jars || {}).reduce((a: number, b: number) => a + b, 0)}
                />
              </div>

              <Card className="p-5 bg-indigo-50 border border-indigo-200">
                <h3 className="font-semibold text-indigo-900 mb-2">Choice Consequences Snapshot</h3>
                <p className="text-sm text-indigo-800">
                  Every monthly jar split changes your resilience profile. Higher emergency and insurance allocations reduce downside risk,
                  while long-term and gold allocations improve wealth growth and inflation protection.
                </p>
              </Card>
            </>
          )}

          {activeStage === 'timeline' && (
            <DecisionTimeline
              allocationHistory={allocationHistory}
              currentMonth={session.current_month || 0}
            />
          )}

          {session.current_month >= 120 && (
            <Button
              onClick={completeGame}
              disabled={submitting}
              className="w-full py-4 text-lg bg-green-600 hover:bg-green-700"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : null}
              Complete Game & See Results
            </Button>
          )}
        </>
      )}

      {showEventModal && lifeEvent && (
        <LifeEventModal
          event={lifeEvent}
          onClose={() => setShowEventModal(false)}
        />
      )}
    </div>
  );
}
