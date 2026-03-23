'use client';

import { Card } from '@/components/ui/Card';
import GameSection from '@/components/dashboard/GameSection';
import { gamesCatalog } from '@/lib/data/games';

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

      {/* Games Grid */}
      <GameSection games={gamesCatalog} />

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
