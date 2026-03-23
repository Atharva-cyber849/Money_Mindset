'use client';

import { motion } from 'framer-motion';
import { TimelineEvent } from '@/app/(dashboard)/games/_lib/SharedComponents';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface Trade {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  timestamp: string;
  pnl?: number;
}

interface TradeHistoryProps {
  trades: Trade[];
  currency?: 'INR' | 'USD';
}

export function TradeHistory({ trades, currency = 'INR' }: TradeHistoryProps) {
  const currencySymbol = currency === 'INR' ? '₹' : '$';

  // Sort trades by timestamp (most recent first)
  const sortedTrades = [...trades].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const getTradeIcon = (side: 'BUY' | 'SELL') => {
    return side === 'BUY' ? '📈' : '📉';
  };

  const getTradeVariant = (side: 'BUY' | 'SELL', pnl?: number) => {
    if (side === 'BUY') return 'default';
    if (!pnl) return 'default';
    return pnl >= 0 ? 'success' : 'critical';
  };

  return (
    <ChartWrapper
      title="Trade History"
      description={`${trades.length} total trade${trades.length !== 1 ? 's' : ''}`}
      height="h-96"
      className="overflow-hidden flex flex-col"
    >
      <motion.div
        className="overflow-y-auto flex-1 pr-4 space-y-1"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.05, delayChildren: 0.1 }}
      >
        {sortedTrades.length > 0 ? (
          sortedTrades.map((trade, idx) => (
            <motion.div
              key={trade.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              <TimelineEvent
                icon={getTradeIcon(trade.side)}
                title={`${trade.side} ${trade.quantity} ${trade.symbol}`}
                description={`Executed at ${currencySymbol}${trade.price.toFixed(2)}`}
                timestamp={new Date(trade.timestamp).toLocaleString('en-IN')}
                variant={getTradeVariant(trade.side, trade.pnl)}
                details={[
                  { label: 'Amount', value: `${currencySymbol}${(trade.quantity * trade.price).toLocaleString('en-IN', { maximumFractionDigits: 0 })}` },
                  ...(trade.pnl !== undefined
                    ? [
                        {
                          label: 'P&L',
                          value: `${trade.pnl >= 0 ? '+' : ''}${currencySymbol}${Math.abs(trade.pnl).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
                        },
                      ]
                    : []),
                ]}
                metadata={trade.side}
              />
            </motion.div>
          ))
        ) : (
          <div className="flex h-full items-center justify-center text-center text-gray-500">
            <p>No trades executed yet. Start trading to build your history!</p>
          </div>
        )}
      </motion.div>
    </ChartWrapper>
  );
}
