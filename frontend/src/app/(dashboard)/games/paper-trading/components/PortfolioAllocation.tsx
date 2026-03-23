'use client';

import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface HoldingData {
  symbol: string;
  value: number;
}

interface PortfolioAllocationProps {
  holdings: Record<string, { quantity: number; current_price: number }>;
  cashValue: number;
  currency?: 'INR' | 'USD';
}

const COLORS = [
  '#06B6D4',
  '#0891B2',
  '#10B981',
  '#F59E0B',
  '#EF4444',
  '#8B5CF6',
  '#EC4899',
  '#14B8A6',
];

export function PortfolioAllocation({
  holdings,
  cashValue,
  currency = 'INR',
}: PortfolioAllocationProps) {
  // Calculate holdings values
  const holdingsData: HoldingData[] = Object.entries(holdings)
    .map(([symbol, holding]) => ({
      symbol,
      value: holding.quantity * holding.current_price,
    }))
    .sort((a, b) => b.value - a.value);

  // Prepare data for pie chart
  const chartData = [
    ...holdingsData.slice(0, 6), // Top 6 holdings
    ...(holdingsData.length > 6
      ? [
          {
            symbol: 'Others',
            value: holdingsData.slice(6).reduce((sum, h) => sum + h.value, 0),
          },
        ]
      : []),
    ...(cashValue > 0 ? [{ symbol: 'Cash', value: cashValue }] : []),
  ];

  const totalValue = chartData.reduce((sum, item) => sum + item.value, 0);

  const currencySymbol = currency === 'INR' ? '₹' : '$';

  const renderCustomLabel = (entry: any) => {
    if (entry.value === 0) return '';
    const percentage = ((entry.value / totalValue) * 100).toFixed(1);
    return percentage + '%';
  };

  return (
    <ChartWrapper
      title="Portfolio Allocation"
      description={`Total Value: ${currencySymbol}${totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
      height="h-96"
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="h-full flex flex-col items-center justify-center"
      >
        {chartData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomLabel}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={800}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => `${currencySymbol}${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Legend with custom styling */}
            <div className="mt-4 flex flex-wrap justify-center gap-4 text-xs">
              {chartData.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="text-gray-700">
                    {item.symbol}: {((item.value / totalValue) * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center text-gray-500">
            <p>No holding data available</p>
          </div>
        )}
      </motion.div>
    </ChartWrapper>
  );
}
