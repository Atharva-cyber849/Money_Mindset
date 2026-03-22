'use client';

import { Card } from '@/components/ui/Card';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface FinancialMetricsPanelProps {
  netWorth: number;
  monthlyIncome?: number;
  monthlyExpenses?: number;
  savingsRate?: number;
  resilience_score?: number;
}

export default function FinancialMetricsPanel({
  netWorth,
  monthlyIncome = 0,
  monthlyExpenses = 0,
  savingsRate,
  resilience_score,
}: FinancialMetricsPanelProps) {
  const calculatedSavingsRate = monthlyIncome > 0
    ? ((monthlyIncome - monthlyExpenses) / monthlyIncome * 100)
    : savingsRate || 0;

  const surplus = monthlyIncome - monthlyExpenses;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="p-4">
        <p className="text-sm text-gray-600 mb-1">Net Worth</p>
        <p className="text-3xl font-bold text-indigo-600">
          ₹{(netWorth / 100000).toFixed(1)}L
        </p>
        <div className="flex items-center mt-2 text-xs text-green-600">
          <TrendingUp className="w-3 h-3 mr-1" />
          Growing your wealth
        </div>
      </Card>

      <Card className="p-4">
        <p className="text-sm text-gray-600 mb-1">Monthly Income</p>
        <p className="text-3xl font-bold">
          ₹{(monthlyIncome / 1000).toFixed(0)}K
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Your earning capacity
        </p>
      </Card>

      <Card className="p-4">
        <p className="text-sm text-gray-600 mb-1">Monthly Surplus</p>
        <p className={`text-3xl font-bold ${surplus > 0 ? 'text-green-600' : 'text-red-600'}`}>
          ₹{(surplus / 1000).toFixed(0)}K
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Available to allocate
        </p>
      </Card>

      <Card className="p-4">
        <p className="text-sm text-gray-600 mb-1">Savings Rate</p>
        <p className="text-3xl font-bold text-blue-600">
          {calculatedSavingsRate.toFixed(0)}%
        </p>
        <p className="text-xs text-gray-500 mt-2">
          {calculatedSavingsRate > 50 ? '✓ Excellent' : calculatedSavingsRate > 30 ? '✓ Good' : '⚠️ Improve'}
        </p>
      </Card>

      {resilience_score !== undefined && (
        <Card className="p-4 md:col-span-2 lg:col-span-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600 mb-1">Financial Wellbeing Index</p>
              <p className="text-2xl font-bold">{resilience_score.toFixed(1)} / 100</p>
            </div>
            <div className="text-right">
              <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center">
                <span className="text-2xl font-bold">
                  {resilience_score > 75 ? '🚀' : resilience_score > 50 ? '📈' : '💪'}
                </span>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
