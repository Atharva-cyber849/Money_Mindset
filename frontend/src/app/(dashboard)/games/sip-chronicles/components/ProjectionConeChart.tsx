'use client';

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '@/components/ui/Card';

interface DataPoint {
  month: number;
  wealth: number;
  age: number;
}

interface ProjectionConeChartProps {
  data: DataPoint[];
  monthlySIP: number;
}

interface ProjectionRow {
  age: number;
  lower: number;
  expected: number;
  upper: number;
}

export default function ProjectionConeChart({ data, monthlySIP }: ProjectionConeChartProps) {
  if (data.length < 3) return null;

  const last = data[data.length - 1];
  const monthsLeft = Math.max(0, 456 - last.month);
  const annualRates = { lower: 0.07, expected: 0.1, upper: 0.13 };

  const futureValue = (principal: number, monthly: number, annualRate: number, months: number) => {
    const r = annualRate / 12;
    if (months <= 0) return principal;
    const growth = Math.pow(1 + r, months);
    const sipFuture = monthly * ((growth - 1) / r);
    return principal * growth + sipFuture;
  };

  const rows: ProjectionRow[] = [];
  const checkpoints = [0, 60, 120, 180, monthsLeft].filter((v, i, arr) => arr.indexOf(v) === i && v >= 0);

  checkpoints.forEach((m) => {
    rows.push({
      age: last.age + Math.floor(m / 12),
      lower: futureValue(last.wealth, monthlySIP, annualRates.lower, m),
      expected: futureValue(last.wealth, monthlySIP, annualRates.expected, m),
      upper: futureValue(last.wealth, monthlySIP, annualRates.upper, m),
    });
  });

  return (
    <Card className="p-6 space-y-4">
      <div>
        <h3 className="text-xl font-bold mb-1">Projection Cone to Age 60</h3>
        <p className="text-sm text-gray-600">Outcome band if you stay consistent with your current SIP pace.</p>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="age" />
          <YAxis tickFormatter={(v) => `₹${Math.round(v / 100000)}L`} />
          <Tooltip
            formatter={(value: number) => `₹${(value / 100000).toFixed(1)}L`}
            labelFormatter={(label) => `Age ${label}`}
          />
          <Area type="monotone" dataKey="upper" stroke="#22c55e" fill="#bbf7d0" fillOpacity={0.5} />
          <Area type="monotone" dataKey="expected" stroke="#0ea5e9" fill="#bae6fd" fillOpacity={0.75} />
          <Area type="monotone" dataKey="lower" stroke="#f97316" fill="#fed7aa" fillOpacity={0.55} />
        </AreaChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-3 text-sm">
        <div className="rounded border border-orange-200 bg-orange-50 p-3">
          <p className="text-gray-600">Conservative</p>
          <p className="font-bold text-orange-700">₹{(rows[rows.length - 1].lower / 100000).toFixed(1)}L</p>
        </div>
        <div className="rounded border border-sky-200 bg-sky-50 p-3">
          <p className="text-gray-600">Expected</p>
          <p className="font-bold text-sky-700">₹{(rows[rows.length - 1].expected / 100000).toFixed(1)}L</p>
        </div>
        <div className="rounded border border-emerald-200 bg-emerald-50 p-3">
          <p className="text-gray-600">Optimistic</p>
          <p className="font-bold text-emerald-700">₹{(rows[rows.length - 1].upper / 100000).toFixed(1)}L</p>
        </div>
      </div>
    </Card>
  );
}
