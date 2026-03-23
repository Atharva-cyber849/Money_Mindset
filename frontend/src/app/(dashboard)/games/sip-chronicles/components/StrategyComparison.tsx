'use client';

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '@/components/ui/Card';

interface StrategyComparisonProps {
  monthlySIP: number;
}

const STRATEGIES = [
  { id: 'nifty_50', label: 'Nifty 50', cagr: 0.1 },
  { id: 'midcap_150', label: 'Midcap 150', cagr: 0.12 },
  { id: 'elss', label: 'ELSS', cagr: 0.105 },
  { id: 'gold', label: 'Gold', cagr: 0.05 },
];

export default function StrategyComparison({ monthlySIP }: StrategyComparisonProps) {
  const years = 38;
  const months = years * 12;

  const fv = (monthly: number, annualRate: number) => {
    const r = annualRate / 12;
    const growth = Math.pow(1 + r, months);
    return monthly * ((growth - 1) / r);
  };

  const data = STRATEGIES.map((s) => ({
    name: s.label,
    wealth: fv(monthlySIP, s.cagr),
    cagr: `${Math.round(s.cagr * 100)}%`,
  }));

  return (
    <Card className="p-6 space-y-4">
      <div>
        <h3 className="text-xl font-bold mb-1">Strategy Comparison (38-Year Horizon)</h3>
        <p className="text-sm text-gray-600">Same monthly SIP, different long-term outcomes due to return profile.</p>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={(v) => `₹${Math.round(v / 100000)}L`} />
          <Tooltip
            formatter={(value: number) => `₹${(value / 100000).toFixed(1)}L`}
          />
          <Bar dataKey="wealth" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      <div className="rounded border border-cyan-200 bg-cyan-50 p-3 text-sm text-cyan-900">
        Rate differences seem small year-to-year, but over decades compounding creates large gaps.
      </div>
    </Card>
  );
}
