"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { AlertCircle, Loader2 } from 'lucide-react';
import { BudgetOptimizationDashboard } from '@/components/analytics';
import { analyzeBudget } from '@/lib/api/analytics';

export default function BudgetOptimizationPage() {
  const [showCustomizer, setShowCustomizer] = useState(false);
  const [income, setIncome] = useState('50000');
  const [savings, setSavings] = useState('10000');
  const [expenses, setExpenses] = useState({
    housing: '18000',
    utilities: '3000',
    groceries: '7000',
    transportation: '4000',
    insurance: '2000',
    healthcare: '1000',
    restaurants: '5000',
    entertainment: '3000',
    shopping: '2500',
    subscriptions: '1000',
    personal_care: '1500',
  });
  const [manualLoading, setManualLoading] = useState(false);
  const [manualError, setManualError] = useState('');
  const [manualResult, setManualResult] = useState<any>(null);

  const expenseFields = [
    { key: 'housing', label: 'Housing (Rent/EMI)' },
    { key: 'utilities', label: 'Utilities (Electricity/Internet)' },
    { key: 'groceries', label: 'Groceries' },
    { key: 'transportation', label: 'Transportation' },
    { key: 'insurance', label: 'Insurance' },
    { key: 'healthcare', label: 'Healthcare' },
    { key: 'restaurants', label: 'Restaurants & Eating Out' },
    { key: 'entertainment', label: 'Entertainment' },
    { key: 'shopping', label: 'Shopping' },
    { key: 'subscriptions', label: 'Subscriptions' },
    { key: 'personal_care', label: 'Personal Care' },
  ] as const;

  const handleManualAnalyze = async () => {
    const monthlyIncome = Number(income);
    const savingsAmount = Number(savings);
    const parsedExpenses = Object.fromEntries(
      Object.entries(expenses).map(([key, value]) => [key, Number(value || 0)])
    ) as Record<string, number>;
    const expenseValues = Object.values(parsedExpenses);

    if (!monthlyIncome || monthlyIncome <= 0) {
      setManualError('Please enter a valid monthly income.');
      return;
    }

    if ([...expenseValues, savingsAmount].some((n) => n < 0 || Number.isNaN(n))) {
      setManualError('Amounts cannot be negative.');
      return;
    }

    setManualLoading(true);
    setManualError('');

    try {
      const result = await analyzeBudget({
        income: monthlyIncome,
        expenses: parsedExpenses,
        savings: savingsAmount,
      });
      setManualResult(result);
    } catch (error) {
      console.error(error);
      setManualError('Unable to analyze manual budget right now. Please try again.');
    } finally {
      setManualLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl space-y-8">
      {/* Dashboard */}
      <BudgetOptimizationDashboard
        onCustomize={() => setShowCustomizer(!showCustomizer)}
      />

      {showCustomizer && (
        <Card className="p-6 space-y-6 border-cyan-200 bg-cyan-50/30">
          <div>
            <h2 className="text-xl font-bold">Provide Budget Manually</h2>
            <p className="text-sm text-muted-foreground mt-1">
              If you see "No transactions found", enter category-wise monthly expenses here to run analysis instantly.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="income" className="text-sm font-medium">Monthly Income</label>
              <Input
                id="income"
                type="number"
                value={income}
                onChange={(e) => setIncome(e.target.value)}
                placeholder="50000"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="savings" className="text-sm font-medium">Savings (20% target)</label>
              <Input
                id="savings"
                type="number"
                value={savings}
                onChange={(e) => setSavings(e.target.value)}
                placeholder="10000"
              />
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-slate-900">Monthly Expense Categories</h3>
            <p className="text-xs text-muted-foreground">
              Enter actual category amounts. Leave as 0 if not applicable.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {expenseFields.map((field) => (
                <div key={field.key} className="space-y-2">
                  <label htmlFor={field.key} className="text-sm font-medium">{field.label}</label>
                  <Input
                    id={field.key}
                    type="number"
                    value={expenses[field.key]}
                    onChange={(e) =>
                      setExpenses((prev) => ({
                        ...prev,
                        [field.key]: e.target.value,
                      }))
                    }
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
          </div>

          {manualError && (
            <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              <AlertCircle className="w-4 h-4" />
              {manualError}
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <Button onClick={handleManualAnalyze} disabled={manualLoading}>
              {manualLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing Budget...
                </>
              ) : (
                'Analyze My Budget'
              )}
            </Button>
            <Button variant="outline" onClick={() => setShowCustomizer(false)}>
              Close
            </Button>
          </div>

          {manualResult && (
            <Card className="p-4 border-green-200 bg-green-50/40">
              <h3 className="font-semibold text-green-900">Manual Budget Analysis Result</h3>
              <p className="text-sm mt-1 text-green-800">
                Health Score: {Number.isFinite(Number(manualResult.health_score)) ? Math.round(Number(manualResult.health_score)) : 'N/A'}/100
              </p>
              <p className="text-sm text-green-800">
                Savings Rate: {manualResult.summary?.savings_rate_pct ?? 0}%
              </p>
              {Array.isArray(manualResult.recommendations) && manualResult.recommendations.length > 0 && (
                <div className="mt-3 space-y-2">
                  {manualResult.recommendations.slice(0, 3).map((rec: any, idx: number) => (
                    <div key={idx} className="text-sm bg-white/80 border border-green-200 rounded-md px-3 py-2 text-slate-800">
                      <span className="font-medium">{rec.issue}</span>
                      {rec.suggestion ? ` - ${rec.suggestion}` : ''}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}
        </Card>
      )}
    </div>
  );
}

