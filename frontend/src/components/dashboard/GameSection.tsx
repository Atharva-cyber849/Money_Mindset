'use client';

import { motion } from 'framer-motion';
import GameCard from './GameCard';

interface GameSectionProps {
  games?: Array<{
    id: string;
    title: string;
    emoji: string;
    description: string;
    difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
    playtime: string;
    xpReward: number;
    accentColor: string;
    featured?: boolean;
    locked?: boolean;
    unlockAt?: number;
    getStartedUrl: string;
  }>;
  title?: string;
  description?: string;
}

export default function GameSection({
  games = [],
  title = '🎮 Games',
  description = 'Learn finance through interactive gameplay',
}: GameSectionProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  const unlockedCount = games.filter((g) => !g.locked).length;
  const lockedCount = games.filter((g) => g.locked).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
        <div className="text-sm font-semibold px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full">
          {unlockedCount} Unlocked{lockedCount > 0 && ` • ${lockedCount} Locked`}
        </div>
      </div>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {games.map((game) => (
          <motion.div key={game.id} variants={cardVariants}>
            <GameCard
              id={game.id}
              icon={game.emoji}
              name={game.title}
              description={game.description}
              difficulty={game.difficulty}
              xpReward={game.xpReward}
              playtime={game.playtime}
              locked={game.locked || false}
              unlockAt={game.unlockAt}
              featured={game.featured}
              href={game.getStartedUrl}
              accentColor={game.accentColor}
            />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
