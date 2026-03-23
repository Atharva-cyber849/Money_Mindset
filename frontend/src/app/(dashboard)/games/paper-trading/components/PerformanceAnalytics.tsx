'use client';

import { motion } from 'framer-motion';
import { MetricGauge } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface PerformanceAnalyticsProps {
  winRate: number;
  maxDrawdown: number;
  sharpeRatio?: number;
  totalTrades?: number;
  profitableTrades?: number;
}

export function PerformanceAnalytics({
  winRate,
  maxDrawdown,
  sharpeRatio = 0,
  totalTrades = 0,
  profitableTrades = 0,
}: PerformanceAnalyticsProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: { opacity: 1, scale: 1 },
  };

  return (
    <motion.div
      className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <h3 className="mb-6 text-lg font-semibold text-gray-900">Performance Analytics</h3>

      {/* Gauge Grid */}
      <motion.div className="grid grid-cols-1 md:grid-cols-3 gap-8" variants={containerVariants}>
        <motion.div variants={itemVariants} className="flex flex-col items-center">
          <MetricGauge
            value={winRate}
            max={100}
            title="Win Rate"
            unit="%"
            color="green"
            size="md"
            description="% of profitable trades"
            thresholds={{ good: 50, warning: 30 }}
          />
        </motion.div>

        <motion.div variants={itemVariants} className="flex flex-col items-center">
          <MetricGauge
            value={Math.abs(maxDrawdown)}
            max={100}
            title="Max Drawdown"
            unit="%"
            color="red"
            size="md"
            description="Largest peak-to-trough decline"
            thresholds={{ good: 10, warning: 20 }}
          />
        </motion.div>

        <motion.div variants={itemVariants} className="flex flex-col items-center">
          <MetricGauge
            value={Math.max(0, Math.min(sharpeRatio * 10, 100))}
            max={100}
            title="Sharpe Ratio"
            unit="×10"
            color="cyan"
            size="md"
            description="Risk-adjusted returns"
          />
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        className="mt-8 grid grid-cols-2 gap-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div
          variants={itemVariants}
          className="rounded-lg bg-blue-50 p-4 border border-blue-200"
        >
          <p className="text-sm text-blue-700 font-medium">Total Trades</p>
          <p className="mt-2 text-2xl font-bold text-blue-900">{totalTrades}</p>
        </motion.div>

        <motion.div
          variants={itemVariants}
          className="rounded-lg bg-green-50 p-4 border border-green-200"
        >
          <p className="text-sm text-green-700 font-medium">Profitable Trades</p>
          <p className="mt-2 text-2xl font-bold text-green-900">
            {profitableTrades}
            <span className="text-sm ml-2">{totalTrades > 0 ? `(${((profitableTrades / totalTrades) * 100).toFixed(0)}%)` : ''}</span>
          </p>
        </motion.div>
      </motion.div>

      {/* Educational Insights */}
      <motion.div
        className="mt-6 space-y-3 rounded-lg bg-amber-50 p-4 border border-amber-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p className="text-sm font-semibold text-amber-900">📊 Performance Insights:</p>
        <ul className="text-xs text-amber-800 space-y-1">
          <li>
            • <strong>Win Rate:</strong> {winRate > 50 ? '✓ Above 50% is excellent for long-term profitability' : '⚠ Focus on improving entry/exit timing'}
          </li>
          <li>
            • <strong>Max Drawdown:</strong> {Math.abs(maxDrawdown) < 20 ? '✓ Good risk management' : '⚠ Consider tighter stop losses'}
          </li>
          <li>
            • <strong>Sharpe Ratio:</strong> {sharpeRatio > 1 ? '✓ Strong risk-adjusted returns' : '⚠ Need more consistency'}
          </li>
        </ul>
      </motion.div>
    </motion.div>
  );
}
