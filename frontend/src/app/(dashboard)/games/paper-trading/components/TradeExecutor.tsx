'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

interface TradeExecutorProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  quantity: number;
  onQuantityChange: (qty: number) => void;
  price: number;
  onPriceChange: (price: number) => void;
  onRefreshQuote?: () => void;
  onBuy: () => void;
  onSell: () => void;
  loading?: boolean;
  quoteLoading?: boolean;
  quoteError?: string;
  lastQuotedSymbol?: string;
  availableCash?: number;
}

export function TradeExecutor({
  selectedSymbol,
  onSymbolChange,
  quantity,
  onQuantityChange,
  price,
  onPriceChange,
  onRefreshQuote,
  onBuy,
  onSell,
  loading = false,
  quoteLoading = false,
  quoteError = '',
  lastQuotedSymbol = '',
  availableCash = 0,
}: TradeExecutorProps) {
  const [tradeType, setTradeType] = useState<'buy' | 'sell' | null>(null);
  const totalCost = quantity * price;
  const canAfford = totalCost <= availableCash;
  const canTrade = selectedSymbol.trim().length > 0 && quantity > 0 && price > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <h3 className="mb-6 text-lg font-semibold text-gray-900">Execute Trade</h3>

      <div className="space-y-4">
        {/* Symbol Input */}
        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="block text-sm font-medium text-gray-700">
              Stock Symbol
            </label>
            <button
              type="button"
              onClick={onRefreshQuote}
              disabled={loading || quoteLoading || !selectedSymbol.trim()}
              className="rounded-md border border-cyan-200 bg-cyan-50 px-2.5 py-1 text-xs font-semibold text-cyan-700 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {quoteLoading ? 'Fetching...' : 'Get Price'}
            </button>
          </div>
          <input
            type="text"
            placeholder="e.g., RELIANCE.NS or AAPL"
            value={selectedSymbol}
            onChange={(e) => onSymbolChange(e.target.value.toUpperCase())}
            disabled={loading}
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 disabled:bg-gray-50 disabled:text-gray-500"
          />
          {quoteError && (
            <p className="mt-1.5 text-xs text-red-600">{quoteError}</p>
          )}
        </div>

        {/* Quantity & Price */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => onQuantityChange(Math.max(1, Number(e.target.value)))}
              disabled={loading}
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 disabled:bg-gray-50 disabled:text-gray-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Price
            </label>
            <input
              type="number"
              value={price}
              onChange={(e) => onPriceChange(Math.max(0, Number(e.target.value)))}
              step="0.01"
              disabled={loading}
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 disabled:bg-gray-50 disabled:text-gray-500"
            />
            {lastQuotedSymbol && lastQuotedSymbol === selectedSymbol && (
              <p className="mt-1.5 text-xs text-emerald-700">Live quote loaded from API</p>
            )}
          </div>
        </div>

        {/* Total Cost */}
        <div className="rounded-lg bg-gray-50 p-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Cost:</span>
            <span className="text-lg font-bold text-gray-900">
              {totalCost.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
            </span>
          </div>
          {availableCash > 0 && (
            <div className="mt-2 text-xs text-gray-600">
              Available Cash: {availableCash.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              {!canAfford && (
                <p className="mt-1 text-red-600">Insufficient funds for BUY</p>
              )}
            </div>
          )}
        </div>

        {/* Trade Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onBuy}
            disabled={loading || !canAfford || !canTrade}
            className="rounded-lg bg-gradient-to-r from-green-500 to-green-600 px-4 py-2.5 font-semibold text-white shadow-md transition-all hover:shadow-lg disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? '⏳ Trading...' : '📈 BUY'}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onSell}
            disabled={loading || !canTrade}
            className="rounded-lg bg-gradient-to-r from-red-500 to-red-600 px-4 py-2.5 font-semibold text-white shadow-md transition-all hover:shadow-lg disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? '⏳ Trading...' : '📉 SELL'}
          </motion.button>
        </div>

        {/* Tips */}
        <div className="rounded-lg bg-blue-50 p-3 text-xs text-blue-700">
          💡 Use real stock symbols: RELIANCE.NS, TCS.NS (India) or AAPL, MSFT (US)
        </div>
      </div>
    </motion.div>
  );
}
