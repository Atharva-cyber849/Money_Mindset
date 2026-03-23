'use client';

import { motion } from 'framer-motion';

interface ComparisonItem {
  label: string;
  value: string | number;
  variant?: 'neutral' | 'good' | 'bad' | 'warning';
}

interface ComparisonStrategy {
  name: string;
  description?: string;
  items: ComparisonItem[];
  highlighted?: boolean;
}

interface ComparisonPanelProps {
  strategies: ComparisonStrategy[];
  title?: string;
  className?: string;
}

export function ComparisonPanel({
  strategies,
  title = 'Strategy Comparison',
  className = '',
}: ComparisonPanelProps) {
  const variantColors = {
    neutral: 'text-gray-600 bg-gray-50',
    good: 'text-green-700 bg-green-50',
    bad: 'text-red-700 bg-red-50',
    warning: 'text-amber-700 bg-amber-50',
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0 },
  };

  return (
    <div className={`rounded-lg border border-gray-200 bg-white p-6 ${className}`}>
      {title && <h3 className="mb-6 text-lg font-semibold text-gray-900">{title}</h3>}

      <motion.div
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {strategies.map((strategy, idx) => (
          <motion.div
            key={idx}
            variants={itemVariants}
            className={`rounded-lg p-4 transition-all duration-300 ${
              strategy.highlighted ? 'border-2 border-cyan-400 bg-cyan-50 ring-2 ring-cyan-100' : 'border border-gray-200 bg-white hover:shadow-md'
            }`}
          >
            <h4 className="font-semibold text-gray-900">{strategy.name}</h4>
            {strategy.description && <p className="mt-1 text-xs text-gray-600">{strategy.description}</p>}

            <div className="mt-4 space-y-2">
              {strategy.items.map((item, itemIdx) => (
                <div key={itemIdx} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{item.label}</span>
                  <span
                    className={`rounded px-2 py-1 text-xs font-semibold ${variantColors[item.variant || 'neutral']}`}
                  >
                    {item.value}
                  </span>
                </div>
              ))}
            </div>

            {strategy.highlighted && (
              <div className="mt-3 border-t border-cyan-200 pt-3">
                <p className="text-xs font-semibold text-cyan-700">✓ Recommended</p>
              </div>
            )}
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
