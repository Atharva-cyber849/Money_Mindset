'use client';

import { Card } from '@/components/ui/Card';

interface LifeStateProps {
  state: {
    age: number;
    job_title: string;
    current_salary: number;
    marital_status: string;
    num_children: number;
    net_worth: number;
    outstanding_debt: number;
    emergency_fund: number;
  };
}

const formatCurrency = (amount: number) => {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  return `₹${Math.round(amount).toLocaleString()}`;
};

export default function LifeState({ state }: LifeStateProps) {
  return (
    <Card className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Your Current Life</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Salary */}
        <div className="space-y-1">
          <p className="text-sm text-gray-600">Annual Salary</p>
          <p className="text-2xl font-bold text-blue-600">{formatCurrency(state.current_salary)}</p>
          <p className="text-xs text-gray-500">{state.job_title}</p>
        </div>

        {/* Net Worth */}
        <div className="space-y-1">
          <p className="text-sm text-gray-600">Net Worth</p>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(state.net_worth)}</p>
          <p className="text-xs text-gray-500">
            {state.net_worth > 0 ? '+' : ''}{((state.net_worth / (state.current_salary * 43)) * 100).toFixed(0)}% of lifetime earn
          </p>
        </div>

        {/* Debt */}
        <div className="space-y-1">
          <p className="text-sm text-gray-600">Outstanding Debt</p>
          <p className={`text-2xl font-bold ${state.outstanding_debt > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {formatCurrency(state.outstanding_debt)}
          </p>
          <p className="text-xs text-gray-500">Home loan, education loan</p>
        </div>

        {/* Emergency Fund */}
        <div className="space-y-1">
          <p className="text-sm text-gray-600">Emergency Fund</p>
          <p className="text-2xl font-bold text-amber-600">{formatCurrency(state.emergency_fund)}</p>
          <p className="text-xs text-gray-500">
            {state.emergency_fund > 0 ? '✓ Prepared' : '✗ Build it up'}
          </p>
        </div>
      </div>

      {/* Family Status */}
      <div className="border-t pt-4">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">
              {state.marital_status === 'married' ? '💍' : '🎓'}
            </span>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="font-semibold capitalize">{state.marital_status}</p>
            </div>
          </div>

          {state.num_children > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-2xl">👶</span>
              <div>
                <p className="text-sm text-gray-600">Children</p>
                <p className="font-semibold">{state.num_children}</p>
              </div>
            </div>
          )}

          <div className="flex items-center space-x-2">
            <span className="text-2xl">📅</span>
            <div>
              <p className="text-sm text-gray-600">Age</p>
              <p className="font-semibold">{state.age} years</p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
