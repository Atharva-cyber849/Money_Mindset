'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '@/components/ui/Card';

interface DataPoint {
  month: number;
  wealth: number;
  age: number;
}

interface CompoundGraphProps {
  data: DataPoint[];
}

export default function CompoundGraph({ data }: CompoundGraphProps) {
  if (data.length < 2) return null;

  // Format data for chart
  const chartData = data.map((point) => ({
    month: point.month,
    age: point.age,
    wealth: Math.round(point.wealth / 100000), // Convert to lakhs
  }));

  // Calculate multiplier
  const initialContribution = 500 * 1; // First month
  const finalWealth = data[data.length - 1].wealth;
  const multiplier = finalWealth > 0 ? (finalWealth / (500 * data.length)) : 1;

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div>
          <h3 className="text-xl font-bold mb-2">Your Wealth Growth</h3>
          <p className="text-sm text-gray-600">Watch your ₹500/month SIP compound over time</p>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="age"
              label={{ value: 'Age', position: 'insideBottomRight', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Wealth (₹L)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={(value) => `₹${value}L`}
              labelFormatter={(label) => `Age: ${label}`}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ddd' }}
            />
            <Line
              type="monotone"
              dataKey="wealth"
              stroke="#22c55e"
              dot={false}
              strokeWidth={2}
              name="Your Wealth"
            />
          </LineChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded">
          <div>
            <p className="text-xs text-gray-600">Total Contributed</p>
            <p className="text-lg font-bold">₹{(500 * data.length / 100000).toFixed(1)}L</p>
          </div>
          <div>
            <p className="text-xs text-gray-600">Current Wealth</p>
            <p className="text-lg font-bold">₹{(finalWealth / 100000).toFixed(1)}L</p>
          </div>
          <div>
            <p className="text-xs text-gray-600">Multiplier</p>
            <p className="text-lg font-bold text-green-600">{multiplier.toFixed(1)}x</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
