'use client';

import { motion } from 'framer-motion';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface TreemapChartProps {
  jars: {
    emergency: number;
    insurance: number;
    short_term: number;
    long_term: number;
    gold: number;
  };
}

const JAR_INFO = {
  emergency: {
    color: 'bg-red-100 border-red-300',
    textColor: 'text-red-700',
    icon: '🚨',
    label: 'Emergency Fund',
    description: '6 months of expenses',
  },
  insurance: {
    color: 'bg-orange-100 border-orange-300',
    textColor: 'text-orange-700',
    icon: '🛡️',
    label: 'Insurance',
    description: 'Health & Life Coverage',
  },
  short_term: {
    color: 'bg-amber-100 border-amber-300',
    textColor: 'text-amber-700',
    icon: '🎯',
    label: 'Short-term Goals',
    description: 'Within 2 years',
  },
  long_term: {
    color: 'bg-green-100 border-green-300',
    textColor: 'text-green-700',
    icon: '🏢',
    label: 'Long-term Wealth',
    description: '10+ years, Retirement',
  },
  gold: {
    color: 'bg-yellow-100 border-yellow-300',
    textColor: 'text-yellow-700',
    icon: '👑',
    label: 'Gold & Hedge',
    description: 'Cultural & Hedge',
  },
};

export function TreemapChart({ jars }: TreemapChartProps) {
  const total = Object.values(jars).reduce((a, b) => a + b, 0);

  // Sort jars by value (largest first)
  const sortedJars = Object.entries(jars)
    .sort(([, a], [, b]) => b - a)
    .map(([key]) => key as keyof typeof jars);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  };

  return (
    <ChartWrapper
      title="Jar Composition"
      description={`Total: ₹${total.toLocaleString()}`}
      height="h-96"
    >
      <motion.div
        className="h-full flex flex-col gap-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Tree Map Grid */}
        <div className="flex-1 grid grid-cols-2 gap-3 auto-rows-fr">
          {sortedJars.map((jar) => {
            const amount = jars[jar];
            const percentage = total > 0 ? ((amount / total) * 100).toFixed(1) : '0';
            const jarInfo = JAR_INFO[jar];

            return (
              <motion.div
                key={jar}
                variants={itemVariants}
                className={`rounded-lg border-2 p-4 flex flex-col justify-between transition-all hover:shadow-lg ${jarInfo.color}`}
              >
                <div>
                  <div className="text-3xl mb-2">{jarInfo.icon}</div>
                  <h4 className={`font-bold ${jarInfo.textColor}`}>{jarInfo.label}</h4>
                  <p className={`text-xs opacity-75 ${jarInfo.textColor}`}>{jarInfo.description}</p>
                </div>

                <div className="mt-3 pt-3 border-t-2 border-current">
                  <p className={`text-2xl font-bold ${jarInfo.textColor}`}>
                    ₹{(amount / 1000).toFixed(0)}K
                  </p>
                  <p className={`text-sm font-semibold ${jarInfo.textColor}`}>
                    {percentage}% of total
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Summary Stats */}
        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg p-4 border border-cyan-200"
        >
          <p className="text-sm text-gray-600">Total Jar Balance</p>
          <p className="text-3xl font-bold text-cyan-600">₹{total.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">
            💡 A diversified jar strategy protects your wealth across multiple goals
          </p>
        </motion.div>
      </motion.div>
    </ChartWrapper>
  );
}
