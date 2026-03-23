'use client';

import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface PricePoint {
  timestamp: string;
  price: number;
  volume?: number;
}

interface StockPriceChartProps {
  symbol: string;
  data: PricePoint[];
  currentPrice: number;
  change: number;
  changePercent: number;
  currency?: 'INR' | 'USD';
}

export function StockPriceChart({
  symbol,
  data,
  currentPrice,
  change,
  changePercent,
  currency = 'INR',
}: StockPriceChartProps) {
  const currencySymbol = currency === 'INR' ? '₹' : '$';
  const isPositive = change >= 0;

  // Prepare data
  const chartData = (data || []).map((point) => ({
    time: new Date(point.timestamp).toLocaleString('en-IN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }),
    price: point.price,
    volume: point.volume,
  }));

  const minPrice = Math.min(...(chartData.map((d) => d.price) || [currentPrice]));
  const maxPrice = Math.max(...(chartData.map((d) => d.price) || [currentPrice]));

  return (
    <ChartWrapper
      title={`${symbol} Price Chart`}
      description={`Current: ${currencySymbol}${currentPrice.toFixed(2)} • ${isPositive ? '+' : ''}${changePercent.toFixed(2)}%`}
      height="h-96"
    >
      <motion.div
        className="h-full"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {chartData.length > 0 ? (
          <>
            {/* TradingView Lightweight Charts placeholder note */}
            <div className="absolute top-2 right-2 hidden md:block text-xs text-gray-400 pointer-events-none">
              <p>💡 Ready for TradingView integration</p>
            </div>

            {/* Chart */}
            <ResponsiveContainer width="100%" height="80%">
              <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={isPositive ? '#10B981' : '#EF4444'} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={isPositive ? '#10B981' : '#EF4444'} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  stroke="#E5E7EB"
                />
                <YAxis
                  domain={[minPrice * 0.95, maxPrice * 1.05]}
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  stroke="#E5E7EB"
                  label={{ value: currencySymbol, angle: -90, position: 'insideLeft', offset: 10 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: `2px solid ${isPositive ? '#10B981' : '#EF4444'}`,
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => [`${currencySymbol}${value.toFixed(2)}`, 'Price']}
                  labelStyle={{ color: '#1F2937' }}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke={isPositive ? '#10B981' : '#EF4444'}
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorPrice)"
                  animationDuration={800}
                  isAnimationActive
                />
              </AreaChart>
            </ResponsiveContainer>

            {/* Stats */}
            <div className="mt-2 flex justify-between text-xs text-gray-600">
              <span>Min: {currencySymbol}{minPrice.toFixed(2)}</span>
              <span>Max: {currencySymbol}{maxPrice.toFixed(2)}</span>
              <span>{chartData.length} data points</span>
            </div>
          </>
        ) : (
          <div className="flex h-full items-center justify-center text-center text-gray-500">
            <div>
              <p className="text-lg font-semibold">No price data available</p>
              <p className="mt-2 text-sm">Historical price data will appear here</p>
            </div>
          </div>
        )}
      </motion.div>
    </ChartWrapper>
  );
}

/*
  NOTE: TradingView Lightweight Charts integration

  To add professional candlestick charts, follow these steps:

  1. Install: npm install lightweight-charts
  2. In your layout or component, add script tag:
     <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
  3. Create a new component: TradingViewChart.tsx
  4. Use this implementation:

     import { useEffect, useRef } from 'react';
     import { createChart } from 'lightweight-charts';

     export function TradingViewChart({ data }) {
       const containerRef = useRef(null);

       useEffect(() => {
         if (!containerRef.current || !data.length) return;

         const chart = createChart(containerRef.current, {
           layout: { background: { color: '#ffffff' } },
           width: containerRef.current.clientWidth,
           height: 400,
           timeScale: { timeVisible: true, secondsVisible: false },
         });

         const candleStickSeries = chart.addCandlestickSeries();
         candleStickSeries.setData(data.map(d => ({
           time: Math.floor(new Date(d.timestamp).getTime() / 1000),
           open: d.open,
           high: d.high,
           low: d.low,
           close: d.close,
         })));

         chart.timeScale().fitContent();

         return () => chart.remove();
       }, [data]);

       return <div ref={containerRef} />;
     }

  Current implementation uses Recharts for immediate functionality.
  Upgrade to TradingView when charting requirements become more sophisticated.
*/
