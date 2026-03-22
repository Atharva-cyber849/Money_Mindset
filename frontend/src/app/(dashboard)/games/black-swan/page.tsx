'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, TrendingDown, AlertCircle, Home } from 'lucide-react';

interface CrisisOption {
  id: string;
  name: string;
  emoji: string;
  year: number;
  description: string;
}

interface ProfileOption {
  id: string;
  name: string;
  emoji: string;
  description: string;
}

interface GameSession {
  session_id: string;
  status: string;
  crisis_type: string;
  profile_type: string;
  difficulty: string;
  current_quarter: number;
  current_phase: string;
  starting_wealth: number;
  wealth: number;
  financial_profile: any;
  crisis_name: string;
  crisis_description: string;
}

const CRISES: CrisisOption[] = [
  { id: 'demonetization_2016', name: '₹2000 Demonetization', emoji: '💸', year: 2016, description: '86% of currency invalidated overnight' },
  { id: 'covid_2020', name: 'COVID-19 Pandemic', emoji: '🦠', year: 2020, description: 'Global pandemic, market crash, job losses' },
  { id: 'il_fs_2021', name: 'IL&FS Credit Crisis', emoji: '🏢', year: 2021, description: 'Shadow banking system freezes' },
  { id: 'yes_bank_2021', name: 'Yes Bank Crisis', emoji: '🏦', year: 2021, description: 'Major bank liquidity crisis' },
  { id: 'crypto_2022', name: 'Crypto Winter', emoji: '₿', year: 2022, description: 'Digital asset collapse' },
  { id: 'shadow_banking_2023', name: 'NBFC Crisis', emoji: '📉', year: 2023, description: 'Shadow banking cascade' },
  { id: 'rupee_2024', name: 'Rupee Crisis', emoji: '🔴', year: 2024, description: 'Currency depreciation' },
];

const PROFILES: ProfileOption[] = [
  {
    id: 'conservative',
    name: '🛡️ Conservative',
    emoji: '🛡️',
    description: 'High savings, low risk. FDs, insurance, minimal equity exposure.',
  },
  {
    id: 'moderate',
    name: '⚖️ Moderate',
    emoji: '⚖️',
    description: 'Balanced portfolio. Equity, real estate, and some debt instruments.',
  },
  {
    id: 'aggressive',
    name: '🚀 Aggressive',
    emoji: '🚀',
    description: 'High exposure to equities and crypto. Growth-focused, high volatility.',
  },
  {
    id: 'unprepared',
    emoji: '⚠️',
    name: '⚠️ Unprepared',
    description: 'Limited savings, high debt. No emergency fund or hedges.',
  },
];

export default function BlackSwanGame() {
  const router = useRouter();
  const [screen, setScreen] = useState<'crisis-select' | 'profile-select' | 'difficulty-select' | 'opening' | 'game'>('crisis-select');
  const [selectedCrisis, setSelectedCrisis] = useState<CrisisOption | null>(null);
  const [selectedProfile, setSelectedProfile] = useState<ProfileOption | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [session, setSession] = useState<GameSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentAsset, setCurrentAsset] = useState('');
  const [currentAction, setCurrentAction] = useState('');

  const handleCreateGame = async () => {
    if (!selectedCrisis || !selectedProfile) {
      setError('Please select a crisis and profile');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('/api/v1/games/black-swan/create', {
        crisis_type: selectedCrisis.id,
        profile_type: selectedProfile.id,
        difficulty: selectedDifficulty,
      });

      setSession(response.data);
      setScreen('opening');
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  const handleAdvanceQuarter = async () => {
    if (!session) return;

    try {
      setLoading(true);
      const response = await axios.post(`/api/v1/games/black-swan/${session.session_id}/advance-quarter`);

      setSession(prev => prev ? {
        ...prev,
        current_quarter: response.data.current_quarter,
        current_phase: response.data.phase,
        wealth: response.data.wealth,
      } : null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to advance quarter');
    } finally {
      setLoading(false);
    }
  };

  const handleMakeDecision = async () => {
    if (!session || !currentAsset || !currentAction) {
      setError('Please select an action and asset');
      return;
    }

    try {
      setLoading(true);
      await axios.post(`/api/v1/games/black-swan/${session.session_id}/make-decision`, {
        decision_type: currentAction,
        asset_class: currentAsset,
        amount: Math.random() * 100000, // Placeholder amount
      });

      setCurrentAsset('');
      setCurrentAction('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to make decision');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!session) return;

    try {
      setLoading(true);
      await axios.post(`/api/v1/games/black-swan/${session.session_id}/complete`);
      router.push(`/games/black-swan/results?session_id=${session.session_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete game');
    } finally {
      setLoading(false);
    }
  };

  // Crisis Selection Screen
  if (screen === 'crisis-select') {
    return (
      <div className="max-w-6xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">⚫ Black Swan Crisis Simulation</h1>
          <p className="text-xl text-gray-600">
            Face unexpected financial crises with randomized scenarios
          </p>
          <p className="text-gray-600">
            Test your antifragility - can you thrive through chaos?
          </p>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Choose Your Crisis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {CRISES.map((crisis) => (
              <Card
                key={crisis.id}
                className={`p-6 cursor-pointer transition ${
                  selectedCrisis?.id === crisis.id
                    ? 'border-2 border-red-500 bg-red-50'
                    : 'border border-gray-200 hover:border-red-300'
                }`}
                onClick={() => setSelectedCrisis(crisis)}
              >
                <div className="space-y-3">
                  <div className="text-4xl">{crisis.emoji}</div>
                  <h3 className="text-lg font-bold">{crisis.name}</h3>
                  <p className="text-sm text-gray-600">{crisis.year}</p>
                  <p className="text-sm text-gray-700">{crisis.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        <Button
          onClick={() => setScreen('profile-select')}
          disabled={!selectedCrisis}
          className="w-full bg-red-600 hover:bg-red-700 text-white py-3 text-lg"
        >
          Next: Select Profile
        </Button>
      </div>
    );
  }

  // Profile Selection Screen
  if (screen === 'profile-select') {
    return (
      <div className="max-w-6xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">Choose Your Financial Profile</h1>
          <p className="text-gray-600">
            Different profiles face different challenges. Each will generate a random portfolio.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PROFILES.map((profile) => (
            <Card
              key={profile.id}
              className={`p-6 cursor-pointer transition ${
                selectedProfile?.id === profile.id
                  ? 'border-2 border-blue-500 bg-blue-50'
                  : 'border border-gray-200 hover:border-blue-300'
              }`}
              onClick={() => setSelectedProfile(profile)}
            >
              <div className="text-5xl mb-4">{profile.emoji}</div>
              <h3 className="text-lg font-bold">{profile.name}</h3>
              <p className="text-sm text-gray-700 mt-2">{profile.description}</p>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Button
            onClick={() => setScreen('crisis-select')}
            variant="secondary"
            className="py-3"
          >
            Back
          </Button>
          <Button
            onClick={() => setScreen('difficulty-select')}
            disabled={!selectedProfile}
            className="bg-blue-600 hover:bg-blue-700 text-white py-3"
          >
            Next: Choose Difficulty
          </Button>
        </div>
      </div>
    );
  }

  // Difficulty Selection Screen
  if (screen === 'difficulty-select') {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">Choose Difficulty</h1>
          <p className="text-gray-600">
            Affects how much time you have to prepare before the crisis hits
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card
            className={`p-6 cursor-pointer transition ${
              selectedDifficulty === 'easy'
                ? 'border-2 border-green-500 bg-green-50'
                : 'border border-gray-200'
            }`}
            onClick={() => setSelectedDifficulty('easy')}
          >
            <div className="text-4xl mb-3">⭐</div>
            <h3 className="font-bold mb-2">Easy</h3>
            <p className="text-sm text-gray-600">12 quarters to prepare. Gentle crisis.</p>
          </Card>

          <Card
            className={`p-6 cursor-pointer transition ${
              selectedDifficulty === 'medium'
                ? 'border-2 border-orange-500 bg-orange-50'
                : 'border border-gray-200'
            }`}
            onClick={() => setSelectedDifficulty('medium')}
          >
            <div className="text-4xl mb-3">⭐⭐</div>
            <h3 className="font-bold mb-2">Medium</h3>
            <p className="text-sm text-gray-600">10 quarters to prepare. Standard crisis.</p>
          </Card>

          <Card
            className={`p-6 cursor-pointer transition ${
              selectedDifficulty === 'hard'
                ? 'border-2 border-red-500 bg-red-50'
                : 'border border-gray-200'
            }`}
            onClick={() => setSelectedDifficulty('hard')}
          >
            <div className="text-4xl mb-3">⭐⭐⭐</div>
            <h3 className="font-bold mb-2">Hard</h3>
            <p className="text-sm text-gray-600">6 quarters to prepare. Rapid onset.</p>
          </Card>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Button
            onClick={() => setScreen('profile-select')}
            variant="secondary"
            className="py-3"
          >
            Back
          </Button>
          <Button
            onClick={handleCreateGame}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white py-3"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Start Crisis Simulation
          </Button>
        </div>

        {error && <p className="text-red-600">{error}</p>}
      </div>
    );
  }

  // Opening Scene
  if (screen === 'opening' && session) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        <div className="text-center space-y-6">
          <div className="text-6xl">{selectedCrisis?.emoji}</div>
          <h1 className="text-4xl font-bold">{session.crisis_name}</h1>
          <p className="text-xl text-gray-600">{session.crisis_description}</p>
        </div>

        <Card className="p-8 bg-gradient-to-r from-red-50 to-orange-50 space-y-4">
          <h2 className="text-2xl font-bold">Your Financial Profile</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Profile Type</p>
              <p className="text-lg font-bold capitalize">{session.profile_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Difficulty</p>
              <p className="text-lg font-bold capitalize">{session.difficulty}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Starting Wealth</p>
              <p className="text-lg font-bold">₹{(session.starting_wealth / 100000).toFixed(1)}L</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Quarters</p>
              <p className="text-lg font-bold">20 📅</p>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-amber-50 border border-amber-200 space-y-2">
          <div className="flex gap-2">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-900">Your Mission</p>
              <p className="text-sm text-amber-800 mt-1">
                Pre-crisis: Build defenses or double down. Crisis: Navigate the trough. Recovery: Capitalize on opportunities.
              </p>
            </div>
          </div>
        </Card>

        <Button
          onClick={() => setScreen('game')}
          className="w-full bg-red-600 hover:bg-red-700 text-white py-3 text-lg"
        >
          Face the Crisis
        </Button>
      </div>
    );
  }

  // Active Game Screen
  if (screen === 'game' && session) {
    const assetClasses = ['cash', 'equity', 'real_estate', 'fds', 'gold', 'crypto'];
    const actions = ['hold', 'sell', 'rebalance', 'buy_dip'];
    const phaseEmoji: Record<string, string> = {
      'pre_crisis': '📝',
      'onset': '⚠️',
      'trough': '🔴',
      'recovery': '✅',
    };

    return (
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">⚫ Black Swan Crisis</h1>
            <p className="text-gray-600">Quarter {session.current_quarter} • Phase: {phaseEmoji[session.current_phase]}</p>
          </div>
          <Link href="/games" className="text-blue-600 hover:underline flex items-center gap-2">
            <Home className="w-4 h-4" />
            Back to Games
          </Link>
        </div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left: Portfolio Status */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="p-6 space-y-4">
              <h3 className="text-lg font-bold">Portfolio Wealth</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Current Value</p>
                  <p className="text-3xl font-bold text-blue-600">
                    ₹{(session.wealth / 100000).toFixed(1)}L
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded space-y-2">
                  <p className="text-sm font-semibold text-gray-700">Phase Status:</p>
                  <p className="text-sm">{phaseEmoji[session.current_phase]} {session.current_phase.replace('_', ' ').toUpperCase()}</p>
                </div>
              </div>
            </Card>

            <Button
              onClick={handleAdvanceQuarter}
              disabled={loading || session.current_quarter >= 20}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Next Quarter
            </Button>

            {session.current_quarter >= 20 && (
              <Button
                onClick={handleComplete}
                className="w-full bg-green-600 hover:bg-green-700 text-white"
              >
                View Results
              </Button>
            )}
          </div>

          {/* Center: Decision Making */}
          <div className="lg:col-span-2 space-y-4">
            {/* Phase Info */}
            <Card className="p-4 bg-gradient-to-r from-red-50 to-orange-50 border-l-4 border-red-500">
              <p className="font-semibold text-red-900">
                {phaseEmoji[session.current_phase]} {session.current_phase === 'pre_crisis' ? 'Prepare now while you can' : 'Crisis is underway - make tough choices'}
              </p>
            </Card>

            {/* Decision Panel */}
            <Card className="p-6 space-y-4">
              <h3 className="text-lg font-bold">Make a Decision</h3>

              <div>
                <label className="block text-sm font-medium mb-2">Asset Class</label>
                <div className="grid grid-cols-2 gap-2">
                  {assetClasses.map((asset) => (
                    <button
                      key={asset}
                      onClick={() => setCurrentAsset(asset)}
                      className={`p-2 rounded text-sm font-medium transition ${
                        currentAsset === asset
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                      }`}
                    >
                      {asset}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Action</label>
                <div className="grid grid-cols-2 gap-2">
                  {actions.map((action) => (
                    <button
                      key={action}
                      onClick={() => setCurrentAction(action)}
                      className={`p-2 rounded text-sm font-medium transition ${
                        currentAction === action
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                      }`}
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleMakeDecision}
                disabled={!currentAsset || !currentAction}
                className="w-full bg-green-600 hover:bg-green-700 text-white"
              >
                Execute Decision
              </Button>
            </Card>
          </div>

          {/* Right: Crisis Status */}
          <div className="lg:col-span-1">
            <Card className="p-4 space-y-4">
              <h3 className="text-lg font-bold">Crisis Timeline</h3>
              <div className="space-y-3">
                <div className="p-3 bg-red-50 rounded">
                  <p className="text-xs font-semibold text-red-900">ONSET</p>
                  <p className="text-sm text-red-800">Q11-12: Crisis begins</p>
                </div>
                <div className="p-3 bg-orange-50 rounded">
                  <p className="text-xs font-semibold text-orange-900">TROUGH</p>
                  <p className="text-sm text-orange-800">Q12-13: Worst phase</p>
                </div>
                <div className="p-3 bg-green-50 rounded">
                  <p className="text-xs font-semibold text-green-900">RECOVERY</p>
                  <p className="text-sm text-green-800">Q14+: Opportunities emerge</p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {error && (
          <Card className="p-4 bg-red-50 border border-red-200">
            <p className="text-red-700">{error}</p>
          </Card>
        )}
      </div>
    );
  }

  return null;
}
