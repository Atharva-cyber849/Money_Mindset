'use client';

import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ChartWrapper } from '@/app/(dashboard)/games/_lib/SharedComponents';

interface JarGrowthChartProps {
  month: number;
  jars: {
    emergency: number;
    insurance: number;
    short_term: number;
    long_term: number;
    gold: number;
  };
}

export function JarGrowthChart({ month, jars }: JarGrowthChartProps) {
  // Simulate historical jar growth data (simplified - in reality this would come from API)
  // This is a demo showing growth progression
  const generateHistoricalData = (currentMonth: number) => {
    const data = [];
    const monthInterval = Math.max(5, Math.floor(currentMonth / 12)); // Data points every 5-12 months

    for (let m = monthInterval; m <= currentMonth; m += monthInterval) {
      const progress = m / currentMonth;
      data.push({
        month: m,
        year: Math.floor(m / 12),
        emergency: Math.round(jars.emergency * (progress * 0.8 + 0.2)),
        insurance: Math.round(jars.insurance * (progress * 0.6 + 0.4)),
        short_term: Math.round(jars.short_term * (progress * 0.9 + 0.1)),
        long_term: Math.round(jars.long_term * Math.pow(progress, 1.2) * 1.3), // Compound growth
        gold: Math.round(jars.gold * progress),
      });
    }

    // Add current month
    if (currentMonth % monthInterval !== 0) {
      data.push({
        month: currentMonth,
        year: Math.floor(currentMonth / 12),
        emergency: jars.emergency,
        insurance: jars.insurance,
        short_term: jars.short_term,
        long_term: jars.long_term,
        gold: jars.gold,
      });
    }

    return data;
  };

  const data = generateHistoricalData(Math.max(1, month || 1));

  return (
    <ChartWrapper
      title="Jar Growth Trajectory"
      description={`Month ${month} of 120 (Year ${Math.floor(month / 12)})`}
      height="h-80"
    >
      <motion.div
        className="h-full"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey="month"
                label={{ value: 'Months', position: 'insideBottomRight', offset: -5 }}
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <YAxis
                label={{ value: '₹ Amount', angle: -90, position: 'insideLeft' }}
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => `₹${value.toLocaleString()}`}
                labelFormatter={(label) => `Month ${label}`}
              />
              <Legend
                verticalAlign="top"
                height={36}
                wrapperStyle={{ paddingBottom: '10px' }}
              />

              <Line
                type="monotone"
                dataKey="emergency"
                stroke="#EF4444"
                strokeWidth={2}
                dot={false}
                name="Emergency Fund"
              />
              <Line
                type="monotone"
                dataKey="insurance"
                stroke="#F97316"
                strokeWidth={2}
                dot={false}
                name="Insurance"
              />
              <Line
                type="monotone"
                dataKey="short_term"
                stroke="#EAB308"
                strokeWidth={2}
                dot={false}
                name="Short-term"
              />
              <Line
                type="monotone"
                dataKey="long_term"
                stroke="#22C55E"
                strokeWidth={3}
                dot={false}
                name="Long-term (Wealth)"
              />
              <Line
                type="monotone"
                dataKey="gold"
                stroke="#FBBF24"
                strokeWidth={2}
                dot={false}
                name="Gold"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>Starting your journey... data will appear as months progress</p>
          </div>
        )}
      </motion.div>
    </ChartWrapper>
  );
}
