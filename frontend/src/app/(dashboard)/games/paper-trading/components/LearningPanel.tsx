'use client';

import { motion } from 'framer-motion';
import { InfoCard } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface LearningPanelProps {
  winRate?: number;
  totalTrades?: number;
  maxDrawdown?: number;
}

export function LearningPanel({
  winRate = 0,
  totalTrades = 0,
  maxDrawdown = 0,
}: LearningPanelProps) {
  const tips = [
    {
      title: 'Diversification',
      description:
        'Spread your capital across multiple stocks and sectors. This reduces risk by ensuring no single stock tanks your portfolio.',
      variant: 'info',
      icon: '📊',
      condition: totalTrades > 0,
    },
    {
      title: 'Risk Management',
      description:
        'Never risk more than 2% of your portfolio on a single trade. Use stop losses to limit downside.',
      variant: 'warning',
      icon: '⚠️',
      condition: true,
    },
    {
      title: 'Entry & Exit Strategy',
      description:
        'Plan your exit BEFORE entering. Know your profit target and stop loss prices upfront.',
      variant: 'info',
      icon: '🎯',
      condition: true,
    },
    {
      title: 'Emotional Discipline',
      description:
        'The biggest killer of portfolio returns is panic selling. Stick to your strategy even when markets dip.',
      variant: 'warning',
      icon: '🧠',
      condition: maxDrawdown > 15,
    },
  ];

  // Dynamic tips based on performance
  const dynamicTips = [];

  if (winRate > 0 && winRate < 30) {
    dynamicTips.push({
      title: 'Improve Your Win Rate',
      description:
        'Your win rate is below 30%. Consider using technical analysis or fundamental analysis to improve entry points.',
      variant: 'warning' as const,
      icon: '📉',
    });
  }

  if (winRate > 60) {
    dynamicTips.push({
      title: 'Consistency is Key',
      description: `Great win rate (${winRate.toFixed(0)}%)! Now focus on position sizing and scaling your success without taking excessive risks.`,
      variant: 'success' as const,
      icon: '🎉',
    });
  }

  if (maxDrawdown > 50) {
    dynamicTips.push({
      title: 'High Volatility Alert',
      description:
        'Your max drawdown exceeds 50%. This is very high risk. Consider tighter stop losses and smaller position sizes.',
      variant: 'warning' as const,
      icon: '⛔',
    });
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <h3 className="mb-6 text-lg font-semibold text-gray-900">📚 Learning Hub</h3>

      <motion.div className="space-y-4" variants={containerVariants}>
        {/* Static Tips */}
        {tips
          .filter((tip) => tip.condition)
          .map((tip, idx) => (
            <motion.div key={idx} variants={itemVariants}>
              <InfoCard
                icon={tip.icon}
                title={tip.title}
                description={tip.description}
                variant={tip.variant as 'default' | 'success' | 'warning' | 'info'}
              />
            </motion.div>
          ))}

        {/* Dynamic Tips */}
        {dynamicTips.map((tip, idx) => (
          <motion.div key={`dynamic-${idx}`} variants={itemVariants}>
            <InfoCard
              icon={tip.icon}
              title={tip.title}
              description={tip.description}
              variant={tip.variant}
            />
          </motion.div>
        ))}

        {/* General Market Lesson */}
        <motion.div variants={itemVariants}>
          <div className="rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 p-4">
            <p className="mb-2 font-semibold text-purple-900">💡 Daily Market Lesson</p>
            <p className="text-sm text-purple-800">
              Remember: In stock markets, time in the market beats timing the market. Even legendary investors rarely time the market perfectly.
            </p>
          </div>
        </motion.div>
      </motion.div>

      {/* Stats Summary */}
      {totalTrades > 0 && (
        <motion.div
          className="mt-6 rounded-lg bg-blue-50 border border-blue-200 p-4"
          variants={itemVariants}
        >
          <p className="mb-3 font-semibold text-blue-900">Your Progress</p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-blue-700">Total Trades</p>
              <p className="mt-1 text-lg font-bold text-blue-900">{totalTrades}</p>
            </div>
            <div>
              <p className="text-blue-700">Win Rate</p>
              <p className="mt-1 text-lg font-bold text-blue-900">{winRate.toFixed(1)}%</p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
