'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface JarAllocationProps {
  currentJars: {
    emergency: number;
    insurance: number;
    short_term: number;
    long_term: number;
    gold: number;
  };
  monthlyIncome: number;
  monthlyExpenses: number;
  onSubmitAllocation: (allocation: any) => void;
  disabled: boolean;
}

const JAR_COLORS = {
  emergency: '#ef4444',
  insurance: '#f97316',
  short_term: '#eab308',
  long_term: '#22c55e',
  gold: '#eab308',
};

const JAR_DESCRIPTIONS = {
  emergency: '6 months of expenses for emergencies',
  insurance: 'Health & life insurance coverage',
  short_term: 'Goals within 2 years (wedding, car, etc)',
  long_term: 'Retirement & wealth building (10+ years)',
  gold: 'Gold hedge & cultural investment',
};

export default function JarAllocation({
  currentJars,
  monthlyIncome,
  monthlyExpenses,
  onSubmitAllocation,
  disabled,
}: JarAllocationProps) {
  const surplus = Math.max(0, monthlyIncome - monthlyExpenses);
  const optimalAllocation = {
    emergency: surplus * 0.25,
    insurance: surplus * 0.15,
    short_term: surplus * 0.15,
    long_term: surplus * 0.35,
    gold: surplus * 0.10,
  };

  const roundedOptimal = {
    emergency: Math.round(optimalAllocation.emergency),
    insurance: Math.round(optimalAllocation.insurance),
    short_term: Math.round(optimalAllocation.short_term),
    long_term: Math.round(optimalAllocation.long_term),
    gold: Math.round(optimalAllocation.gold),
  };

  const [allocation, setAllocation] = useState({
    emergency: roundedOptimal.emergency,
    insurance: roundedOptimal.insurance,
    short_term: roundedOptimal.short_term,
    long_term: roundedOptimal.long_term,
    gold: roundedOptimal.gold,
  });

  useEffect(() => {
    setAllocation(roundedOptimal);
  }, [
    roundedOptimal.emergency,
    roundedOptimal.insurance,
    roundedOptimal.short_term,
    roundedOptimal.long_term,
    roundedOptimal.gold,
  ]);

  const totalAllocated = Object.values(allocation).reduce((a, b) => a + b, 0);

  const chartData = [
    {
      name: 'Current',
      emergency: Math.round(allocation.emergency),
      insurance: Math.round(allocation.insurance),
      short_term: Math.round(allocation.short_term),
      long_term: Math.round(allocation.long_term),
      gold: Math.round(allocation.gold),
    },
    {
      name: 'Optimal',
      emergency: Math.round(optimalAllocation.emergency),
      insurance: Math.round(optimalAllocation.insurance),
      short_term: Math.round(optimalAllocation.short_term),
      long_term: Math.round(optimalAllocation.long_term),
      gold: Math.round(optimalAllocation.gold),
    },
  ];

  const handleJarChange = (jar: string, value: number) => {
    setAllocation({
      ...allocation,
      [jar]: Math.max(0, value),
    });
  };

  const useOptimalAllocation = () => {
    setAllocation(roundedOptimal);
  };

  const handleSubmit = () => {
    onSubmitAllocation(allocation);
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Monthly Allocation</h2>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-sm text-gray-600">Monthly Income</p>
            <p className="text-2xl font-bold">₹{monthlyIncome.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Monthly Expenses</p>
            <p className="text-2xl font-bold">₹{monthlyExpenses.toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-cyan-50 p-4 rounded mb-6">
          <p className="text-lg font-semibold">Available Surplus</p>
          <p className="text-3xl font-bold text-cyan-600">₹{surplus.toLocaleString()}</p>
          <p className="text-sm text-gray-600 mt-2">
            Allocate your surplus across 5 jars to teach your money where to go
          </p>
        </div>

        <div className="space-y-6">
          {Object.entries(allocation).map(([jar, amount]) => (
            <div key={jar}>
              <div className="flex justify-between items-center mb-2">
                <label className="font-semibold capitalize">{jar.replace('_', ' ')}</label>
                <span className="text-sm text-gray-600">₹{amount.toLocaleString()}</span>
              </div>
              <p className="text-xs text-gray-500 mb-2">{JAR_DESCRIPTIONS[jar as keyof typeof JAR_DESCRIPTIONS]}</p>
              <input
                type="range"
                min="0"
                max={Math.max(
                  Math.round(surplus),
                  Math.round((surplus / 2)),
                  1000
                )}
                value={amount}
                onChange={(e) => handleJarChange(jar, Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>₹0</span>
                <span>Optimal: ₹{Math.round(optimalAllocation[jar as keyof typeof optimalAllocation]).toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-gray-50 p-4 rounded mt-6">
          <p className="text-sm text-gray-600">Total Monthly Allocation</p>
          <p className="text-2xl font-bold">₹{totalAllocated.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">
            {totalAllocated > surplus
              ? `⚠️ Over allocation by ₹${(totalAllocated - surplus).toLocaleString()}`
              : `✓ Allocation healthy`}
          </p>
        </div>

        <div className="bg-slate-50 border border-slate-200 p-4 rounded mt-4">
          <p className="text-sm font-semibold text-slate-800 mb-2">Current Jar Balances</p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs text-slate-700">
            <div>Emergency: ₹{Math.round(currentJars.emergency).toLocaleString()}</div>
            <div>Insurance: ₹{Math.round(currentJars.insurance).toLocaleString()}</div>
            <div>Short-term: ₹{Math.round(currentJars.short_term).toLocaleString()}</div>
            <div>Long-term: ₹{Math.round(currentJars.long_term).toLocaleString()}</div>
            <div>Gold: ₹{Math.round(currentJars.gold).toLocaleString()}</div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            onClick={useOptimalAllocation}
            variant="outline"
            className="flex-1"
          >
            Use Optimal Allocation
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={disabled || totalAllocated === 0}
            className="flex-1"
          >
            Allocate & Next Month
          </Button>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4">Allocation Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
            <Legend />
            <Bar dataKey="emergency" fill="#ef4444" name="Emergency Fund" />
            <Bar dataKey="insurance" fill="#f97316" name="Insurance" />
            <Bar dataKey="short_term" fill="#eab308" name="Short-term" />
            <Bar dataKey="long_term" fill="#22c55e" name="Long-term" />
            <Bar dataKey="gold" fill="#fbbf24" name="Gold" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
