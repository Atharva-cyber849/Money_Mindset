'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

interface PortfolioOverviewProps {
  cash: number;
  totalValue: number;
  pnl: number;
  holdingsCount: number;
  winRate: number;
  maxDrawdown: number;
  currency?: 'INR' | 'USD';
}

export function PortfolioOverview({
  cash,
  totalValue,
  pnl,
  holdingsCount,
  winRate,
  maxDrawdown,
  currency = 'INR',
}: PortfolioOverviewProps) {
  const [pnlPercentage, setPnlPercentage] = useState(0);

  useEffect(() => {
    if (totalValue > 0) {
      setPnlPercentage((pnl / (totalValue - pnl)) * 100);
    }
  }, [pnl, totalValue]);

  const currencySymbol = currency === 'INR' ? '₹' : '$';
  const invested = totalValue - cash;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const cards = [
    {
      title: 'Cash Available',
      value: cash,
      icon: '💰',
      color: 'blue',
      tooltip: 'Uninvested capital available for trades',
    },
    {
      title: 'Portfolio Value',
      value: totalValue,
      icon: '📊',
      color: 'cyan',
      tooltip: 'Total value of cash + holdings',
    },
    {
      title: 'P&L',
      value: pnl,
      icon: pnl >= 0 ? '📈' : '📉',
      color: pnl >= 0 ? 'green' : 'red',
      isGain: pnl >= 0,
      tooltip: 'Profit or loss on investments',
    },
    {
      title: 'Holdings',
      value: holdingsCount,
      icon: '📂',
      color: 'amber',
      isCount: true,
      tooltip: 'Number of different stocks held',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    cyan: 'bg-cyan-50 border-cyan-200 text-cyan-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    amber: 'bg-amber-50 border-amber-200 text-amber-700',
  };

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {cards.map((card, idx) => (
        <motion.div
          key={idx}
          variants={cardVariants}
          className={`group relative rounded-xl border-2 p-6 transition-all hover:shadow-md ${colorClasses[card.color as keyof typeof colorClasses]}`}
          title={card.tooltip}
        >
          {/* Icon */}
          <div className="mb-4 text-3xl">{card.icon}</div>

          {/* Label */}
          <p className="text-sm font-medium opacity-70">{card.title}</p>

          {/* Value */}
          <p className="mt-2 text-2xl font-bold">
            {card.isCount
              ? card.value
              : `${card.isGain !== false ? (card.value >= 0 ? '+' : '') : ''}${currencySymbol}${(!card.isCount ? card.value.toLocaleString('en-IN', { maximumFractionDigits: 0 }) : card.value)}`}
          </p>

          {/* Percentage for P&L */}
          {card.title === 'P&L' && pnl !== 0 && (
            <p className={`mt-1 text-xs font-semibold ${pnl >= 0 ? 'text-green-700' : 'text-red-700'}`}>
              {pnl >= 0 ? '+' : ''}{pnlPercentage.toFixed(2)}%
            </p>
          )}

          {/* Tooltip on hover */}
          <div className="absolute inset-x-0 bottom-full mb-2 hidden group-hover:block">
            <div className="rounded-lg bg-gray-900 px-2 py-1 text-xs text-white whitespace-nowrap">
              {card.tooltip}
            </div>
          </div>
        </motion.div>
      ))}

      {/* Performance Metrics (Secondary Row) */}
      <motion.div
        variants={cardVariants}
        className="col-span-1 md:col-span-2 lg:col-span-4 grid grid-cols-2 gap-4"
      >
        <div className="rounded-xl border-2 border-purple-200 bg-purple-50 p-4 text-purple-700">
          <p className="text-sm font-medium opacity-70">Win Rate</p>
          <p className="mt-1 text-2xl font-bold">{winRate.toFixed(1)}%</p>
        </div>
        <div className="rounded-xl border-2 border-orange-200 bg-orange-50 p-4 text-orange-700">
          <p className="text-sm font-medium opacity-70">Max Drawdown</p>
          <p className="mt-1 text-2xl font-bold">{maxDrawdown.toFixed(2)}%</p>
        </div>
      </motion.div>
    </motion.div>
  );
}
