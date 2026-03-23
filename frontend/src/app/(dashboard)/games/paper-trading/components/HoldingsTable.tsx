'use client';

import { motion } from 'framer-motion';
import { LineChart, Line, ResponsiveContainer } from 'recharts';

interface Holding {
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  pnl: number;
  pnl_percentage: number;
  priceHistory?: number[]; // For sparkline
}

interface HoldingsTableProps {
  holdings: Record<string, Holding>;
  currency?: 'INR' | 'USD';
  onSellClick?: (symbol: string) => void;
}

export function HoldingsTable({
  holdings,
  currency = 'INR',
  onSellClick,
}: HoldingsTableProps) {
  if (Object.keys(holdings).length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-8 text-center"
      >
        <p className="text-lg font-semibold text-gray-600">📂 No Holdings Yet</p>
        <p className="mt-2 text-sm text-gray-500">
          Execute your first trade to start building your portfolio
        </p>
      </motion.div>
    );
  }

  const currencySymbol = currency === 'INR' ? '₹' : '$';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm"
    >
      {/* Header */}
      <div className="border-b border-gray-200 bg-gray-50 px-6 py-4">
        <h3 className="font-semibold text-gray-900">Your Holdings</h3>
        <p className="mt-1 text-xs text-gray-600">
          {Object.keys(holdings).length} position{Object.keys(holdings).length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-gray-200 bg-white">
            <tr>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Symbol</th>
              <th className="px-6 py-3 text-right font-semibold text-gray-700">Qty</th>
              <th className="px-6 py-3 text-right font-semibold text-gray-700">Entry Price</th>
              <th className="px-6 py-3 text-right font-semibold text-gray-700">Current Price</th>
              <th className="px-6 py-3 text-center font-semibold text-gray-700">Sparkline</th>
              <th className="px-6 py-3 text-right font-semibold text-gray-700">P&L</th>
              <th className="px-6 py-3 text-right font-semibold text-gray-700">Return %</th>
              <th className="px-6 py-3 text-center font-semibold text-gray-700">Action</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(holdings).map(([symbol, holding], idx) => {
              const isProfit = holding.pnl_percentage >= 0;
              const sparklineData = holding.priceHistory
                ? holding.priceHistory.map((price) => ({ value: price }))
                : [];

              return (
                <motion.tr
                  key={symbol}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  {/* Symbol */}
                  <td className="px-6 py-4 font-semibold text-gray-900">{symbol}</td>

                  {/* Quantity */}
                  <td className="px-6 py-4 text-right text-gray-600">{holding.quantity}</td>

                  {/* Entry Price */}
                  <td className="px-6 py-4 text-right text-gray-600">
                    {currencySymbol}{holding.entry_price.toFixed(2)}
                  </td>

                  {/* Current Price */}
                  <td className="px-6 py-4 text-right font-semibold text-gray-900">
                    {currencySymbol}{holding.current_price.toFixed(2)}
                  </td>

                  {/* Sparkline */}
                  <td className="px-6 py-4 text-center">
                    {sparklineData.length > 0 ? (
                      <ResponsiveContainer width={60} height={30}>
                        <LineChart data={sparklineData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke={isProfit ? '#10B981' : '#EF4444'}
                            dot={false}
                            strokeWidth={2}
                            isAnimationActive={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <span className="text-xs text-gray-400">—</span>
                    )}
                  </td>

                  {/* P&L */}
                  <td className={`px-6 py-4 text-right font-semibold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                    {currencySymbol}{Math.abs(holding.pnl).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>

                  {/* Return % */}
                  <td className={`px-6 py-4 text-right font-semibold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                    {isProfit ? '+' : ''}{holding.pnl_percentage.toFixed(2)}%
                  </td>

                  {/* Action */}
                  <td className="px-6 py-4 text-center">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => onSellClick?.(symbol)}
                      className="inline-flex items-center gap-1 rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-100 transition-colors"
                    >
                      📉 Sell
                    </motion.button>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
