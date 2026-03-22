'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

const games = [
  {
    id: 'gullak',
    title: 'Gullak - The Piggy Bank',
    emoji: '🏺',
    description: 'Learn smart financial allocation through a 10-year life simulation. Divide your monthly surplus into 5 jars and navigate real Indian financial scenarios.',
    difficulty: 'Beginner',
    playtime: '30-40 min',
    type: 'Educational Simulation',
    features: ['Family dynamics', 'Regional variations', 'Real events'],
    getStartedUrl: '/games/gullak',
    comingSoon: false,
  },
  {
    id: 'sip-chronicles',
    title: 'SIP Chronicles',
    emoji: '📈',
    description: 'Watch your wealth compound in real-time as you start a ₹500/month SIP at age 22. Navigate life interruptions that threaten your investment discipline.',
    difficulty: 'Beginner',
    playtime: '15-20 min',
    type: 'Idle Game',
    features: ['Idle gameplay', 'Historical returns', 'Hindsight mechanic'],
    getStartedUrl: '/games/sip-chronicles',
    comingSoon: false,
  },
  {
    id: 'paper-trading',
    title: 'Paper Trading',
    emoji: '💹',
    description: 'Learn stock trading with virtual money. Trade Indian or US stocks with real prices. Practice portfolio diversification, market timing, and risk management without real capital at risk.',
    difficulty: 'Intermediate',
    playtime: '20-60 min',
    type: 'Trading Simulator',
    features: ['Real-time prices', 'Dual markets (India/US)', 'Multi-dimensional scoring', 'Historical backtesting'],
    getStartedUrl: '/games/paper-trading',
    comingSoon: false,
  },
  {
    id: 'karobaar',
    title: 'Karobaar - The Business of Life',
    emoji: '💼',
    description: 'Navigate 40 years of financial life as a professional. Make career, marriage, home, and investment decisions with real long-term consequences.',
    difficulty: 'Intermediate',
    playtime: '60+ min',
    type: 'Life Simulation RPG',
    features: ['Decision tree', 'Career paths', 'Family dynamics'],
    getStartedUrl: '/games/karobaar',
    comingSoon: false,
  },
  {
    id: 'dalal-street',
    title: 'Dalal Street: The Floor',
    emoji: '📊',
    description: 'Trade on BSE across 5 historical eras. Learn market cycles, fraud detection, and the evolution of Indian financial regulation.',
    difficulty: 'Advanced',
    playtime: '45+ min',
    type: 'Strategy Simulation',
    features: ['Historical periods', 'Real stocks', 'SEBI mechanics'],
    getStartedUrl: '/games/dalal-street',
    comingSoon: false,
  },
  {
    id: 'black-swan',
    title: 'Black Swan - Crisis Survival',
    emoji: '⚫',
    description: 'Each session is different. Given a random financial profile and crisis scenario, demonstrate antifragility and build wealth through crises.',
    difficulty: 'Advanced',
    playtime: '30 min',
    type: 'Crisis Simulation',
    features: ['Randomization', 'Hindsight replay', 'Resilience scoring'],
    getStartedUrl: '/games/black-swan',
    comingSoon: false,
  },
];

export default function GamesHub() {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-12">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">🎮 Learn Money Through Games</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Five uniquely Indian financial games that teach real-world money management through interactive storytelling.
          Each game tackles a different aspect of personal finance in the context of Indian financial life.
        </p>
      </div>

      {/* Active Games */}
      <div>
        <h2 className="text-2xl font-bold mb-6">Just Launched 🎉</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {games.filter(game => !game.comingSoon).map((game) => (
            <Card key={game.id} className="overflow-hidden border-2 border-blue-500 hover:shadow-lg transition-shadow">
              <div className="p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="text-5xl">{game.emoji}</div>
                  <span className="bg-green-100 text-green-700 text-xs font-semibold px-3 py-1 rounded-full">
                    Active
                  </span>
                </div>

                <div>
                  <h3 className="text-2xl font-bold">{game.title}</h3>
                  <p className="text-gray-600 text-sm">{game.type} • {game.difficulty}</p>
                </div>

                <p className="text-gray-700">{game.description}</p>

                <div className="space-y-2">
                  <p className="text-xs font-semibold text-gray-600">Key Features:</p>
                  <div className="flex flex-wrap gap-2">
                    {game.features.map((feature) => (
                      <span
                        key={feature}
                        className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm pt-2">
                  <span className="text-gray-600">⏱️ {game.playtime}</span>
                </div>

                <Link href={game.getStartedUrl} className="block">
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    Play Now
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Upcoming Games */}
      <div>
        <h2 className="text-2xl font-bold mb-6">Coming Soon</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {games.filter(game => game.comingSoon).map((game) => (
            <Card key={game.id} className="p-6 flex flex-col h-full hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="text-5xl">{game.emoji}</div>
                <span className="bg-gray-200 text-gray-700 text-xs font-semibold px-3 py-1 rounded-full">
                  Coming Soon
                </span>
              </div>

              <h3 className="text-xl font-bold mb-2">{game.title}</h3>
              <p className="text-sm text-gray-600 mb-4">{game.type} • {game.difficulty}</p>

              <p className="text-gray-700 mb-4 flex-grow">{game.description}</p>

              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Playtime</span>
                  <span className="font-semibold">{game.playtime}</span>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-semibold text-gray-600">Key Features:</p>
                  <div className="flex flex-wrap gap-2">
                    {game.features.map((feature) => (
                      <span
                        key={feature}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                <Button variant="outline" disabled className="w-full mt-4">
                  Coming Soon
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Educational Value */}
      <Card className="p-8 bg-gradient-to-r from-indigo-50 to-blue-50">
        <h2 className="text-2xl font-bold mb-6">Why These Games Matter</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <h3 className="font-bold text-lg mb-2">🇮🇳 Culturally Rooted</h3>
            <p className="text-gray-700">
              Authentic Indian financial scenarios (demonetization, chit funds, joint family dynamics)
              that Western games never cover.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2">📊 Historically Accurate</h3>
            <p className="text-gray-700">
              Real events, real crashes, real recovery patterns from India's financial history.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2">🧠 Behavioral Learning</h3>
            <p className="text-gray-700">
              Learn through lived experience rather than textbooks. Make mistakes in a safe space.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2">💰 Wealth Building</h3>
            <p className="text-gray-700">
              See compound interest, tax optimization, and diversification in action over decades.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2">🎯 Decision Making</h3>
            <p className="text-gray-700">
              Practice financial decisions with real consequences without risking real money.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2">🏆 Gamified Progress</h3>
            <p className="text-gray-700">
              Earn XP, unlock badges, and build streaks. Make learning engaging and habit-forming.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
