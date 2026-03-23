'use client';

import { motion } from 'framer-motion';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface WaterfallChartProps {
  income: number;
  expenses: number;
  jars: {
    emergency: number;
    insurance: number;
    short_term: number;
    long_term: number;
    gold: number;
  };
}

export function WaterfallChart({ income, expenses, jars }: WaterfallChartProps) {
  const surplus = Math.max(0, income - expenses);
  const totalJars = Object.values(jars).reduce((a, b) => a + b, 0);

  // Calculate flow stages
  const stages = [
    { label: 'Income', value: income, color: 'bg-green-500', type: 'positive' },
    { label: 'Expenses', value: -expenses, color: 'bg-red-500', type: 'negative' },
    { label: 'Surplus', value: surplus, color: 'bg-blue-500', type: 'positive', highlight: true },
    { label: 'Emergency', value: jars.emergency, color: 'bg-red-400', type: 'allocation' },
    { label: 'Insurance', value: jars.insurance, color: 'bg-orange-400', type: 'allocation' },
    { label: 'Short-term', value: jars.short_term, color: 'bg-amber-400', type: 'allocation' },
    { label: 'Long-term', value: jars.long_term, color: 'bg-green-400', type: 'allocation' },
    { label: 'Gold', value: jars.gold, color: 'bg-yellow-400', type: 'allocation' },
  ];

  const maxValue = Math.max(...stages.map((s) => s.value));
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.2 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <ChartWrapper
      title="Money Flow - Where Your Income Goes"
      description="Waterfall view of financial allocation"
      height="h-96"
    >
      <motion.div
        className="h-full flex flex-col justify-between"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Waterfall Flow */}
        <div className="flex-1 flex gap-2 items-flex-end justify-between px-2">
          {stages.map((stage, idx) => {
            const barHeight = (Math.abs(stage.value) / maxValue) * 100;
            const isAllocation = stage.type === 'allocation';

            return (
              <motion.div
                key={idx}
                variants={itemVariants}
                className="flex-1 flex flex-col items-center gap-2"
              >
                {/* Bar */}
                <div className="w-full flex flex-col items-center gap-1">
                  <motion.div
                    className={`w-full ${stage.color} rounded-t transition-all hover:shadow-lg`}
                    style={{ height: `${Math.max(barHeight, 5)}px` }}
                    whileHover={{ scaleY: 1.05 }}
                  />

                  {/* Value Label */}
                  <div className="text-xs font-bold text-gray-900 text-center">
                    ₹{(stage.value / 1000).toFixed(0)}K
                  </div>
                </div>

                {/* Stage Label */}
                <p className="text-xs font-semibold text-gray-700 text-center w-full break-words">
                  {stage.label}
                </p>

                {/* Percentage for allocations */}
                {isAllocation && (
                  <p className="text-xs text-gray-500">
                    {((stage.value / surplus) * 100).toFixed(0)}% of surplus
                  </p>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Key Insights */}
        <motion.div
          variants={itemVariants}
          className="mt-6 grid grid-cols-3 gap-3 pt-4 border-t border-gray-200"
        >
          <div className="bg-green-50 p-3 rounded border border-green-200">
            <p className="text-xs text-gray-600">Income</p>
            <p className="font-bold text-green-700">₹{income.toLocaleString()}</p>
          </div>

          <div className="bg-red-50 p-3 rounded border border-red-200">
            <p className="text-xs text-gray-600">Expenses</p>
            <p className="font-bold text-red-700">₹{expenses.toLocaleString()}</p>
          </div>

          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <p className="text-xs text-gray-600">Allocated</p>
            <p className="font-bold text-blue-700">₹{totalJars.toLocaleString()}</p>
          </div>
        </motion.div>
      </motion.div>
    </ChartWrapper>
  );
}
