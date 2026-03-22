'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import JarAllocation from './components/JarAllocation';
import LifeEventModal from './components/LifeEventModal';
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
}

interface MonthlyEvent {
  month: number;
  type: string;
  description: string;
  impact_amount: number;
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

  // Configuration options for new game
  const [incomeType, setIncomeType] = useState('salaried');
  const [stateLocation, setStateLocation] = useState('maharashtra');

  useEffect(() => {
    // Load any existing session
    loadSession();
  }, []);

  const loadSession = async () => {
    try {
      const response = await axios.get('/api/v1/games/gullak/user/sessions');
      const sessions = response.data.sessions;

      if (sessions.length > 0) {
        const lastSession = sessions[0];
        if (lastSession.status === 'active') {
          // Load active session
          const sessionDetails = await axios.get(`/api/v1/games/gullak/${lastSession.session_id}`);
          setSession(sessionDetails.data);
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
      const response = await axios.post('/api/v1/games/gullak/create', {
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

      const response = await axios.post(
        `/api/v1/games/gullak/${initialSession.session_id}/allocate`,
        allocation
      );

      setMonthlyIncome(response.data.income);
      setMonthlyExpenses(response.data.expenses);

      if (response.data.event) {
        setLifeEvent(response.data.event);
        setShowEventModal(true);
      }

      const updated = await axios.get(`/api/v1/games/gullak/${initialSession.session_id}`);
      setSession(updated.data);

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

      const response = await axios.post(
        `/api/v1/games/gullak/${session.session_id}/allocate`,
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
      const updated = await axios.get(`/api/v1/games/gullak/${session.session_id}`);
      setSession(updated.data);

    } catch (error) {
      console.error('Failed to simulate month:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAllocationSubmit = async (allocation: any) => {
    try {
      setSubmitting(true);

      const response = await axios.post(
        `/api/v1/games/gullak/${session?.session_id}/allocate`,
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
      const updated = await axios.get(`/api/v1/games/gullak/${session?.session_id}`);
      setSession(updated.data);

    } catch (error) {
      console.error('Failed to allocate:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const completeGame = async () => {
    try {
      setSubmitting(true);

      const response = await axios.post(
        `/api/v1/games/gullak/${session?.session_id}/complete`
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

      {session && (
        <>
          <JarAllocation
            currentJars={session.current_jars}
            monthlyIncome={monthlyIncome}
            monthlyExpenses={monthlyExpenses}
            onSubmitAllocation={handleAllocationSubmit}
            disabled={submitting}
          />

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
