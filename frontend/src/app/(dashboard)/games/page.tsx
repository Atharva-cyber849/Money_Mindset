'use client';

import { Card } from '@/components/ui/Card';
import GameSection from '@/components/dashboard/GameSection';
import { gamesCatalog } from '@/lib/data/games';

export default function GamesHub() {
  const crossGameHighlights = [
    {
      title: 'Persistent Portfolio',
      description: 'Hold positions across Paper Trading and Dalal Street so one win can carry into the next session.',
    },
    {
      title: 'Career Path Integration',
      description: 'Move from Karobaar to Paper Trading by reinvesting business profits into market learning.',
    },
    {
      title: 'Compound Rewards',
      description: 'XP earned in simulations boosts the visual compound-growth payoff in investing experiences.',
    },
    {
      title: 'Personalization',
      description: 'Games and lessons can suggest scenarios based on your profile and learning gaps.',
    },
    {
      title: 'Achievement-Locked Content',
      description: 'Harder simulations unlock only after you complete the prerequisites and prove consistency.',
    },
    {
      title: 'Session Analytics',
      description: 'Track time spent, decisions made, and learning curves across every session.',
    },
    {
      title: 'Export Reports',
      description: 'Session summaries can be exported for review, reflection, or future PDF output.',
    },
    {
      title: 'Mobile + Offline Ready',
      description: 'Quick-play variants and cached Paper Trading data keep the experience fast and resilient.',
    },
  ]

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

      <Card className="p-8 !bg-slate-950 !text-white !border-slate-700 shadow-2xl ring-1 ring-cyan-500/20">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2 text-cyan-100">Cross-Game Features</h2>
            <p className="text-slate-300 text-sm max-w-3xl">
              These systems connect the games into one progression path instead of isolated mini-apps.
            </p>
          </div>
          <div className="text-sm px-3 py-1 rounded-full bg-cyan-400/15 text-cyan-100 border border-cyan-300/30 shadow-sm">
            Progression enabled
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {crossGameHighlights.map((item) => (
            <div key={item.title} className="rounded-xl border border-cyan-300/20 bg-slate-900/90 p-4 shadow-lg backdrop-blur-sm">
              <h3 className="font-semibold text-lg mb-2 text-cyan-200">{item.title}</h3>
              <p className="text-sm text-slate-200 leading-6">{item.description}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
