"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Pill';
import { getTransactionAnalytics, TransactionAnalytics } from '@/lib/api/analytics';
import { 
  Calendar, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  PieChart as PieChartIcon,
  Loader2,
  ArrowUpRight,
  ArrowDownLeft,
  Edit2
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
  ProgressBar,
} from 'recharts';

const COLORS = [
  '#06B6D4', // cyan
  '#F97316', // orange
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#14B8A6', // teal
  '#F59E0B', // amber
  '#06B6D4', // cyan
  '#6366F1', // indigo
  '#10B981', // emerald
];

interface ExpenseClassificationDashboardProps {
  days?: number;
  onViewFullHistory?: () => void;
  onAnalyzeMore?: () => void;
}

export function ExpenseClassificationDashboard({
  days = 30,
  onViewFullHistory,
  onAnalyzeMore,
}: ExpenseClassificationDashboardProps) {
  const [analytics, setAnalytics] = useState<TransactionAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showFullHistory, setShowFullHistory] = useState(false);
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: '',
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const data = await getTransactionAnalytics(days);
        setAnalytics(data);

        // Format date range
        const startDate = new Date(data.period.start_date);
        const endDate = new Date(data.period.end_date);
        setDateRange({
          start: startDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          }),
          end: endDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          }),
        });
      } catch (err) {
        console.error(err);
        setError('Failed to load expense analytics');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [days]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-800">{error || 'No data available'}</p>
        </div>
      </Card>
    );
  }

  const pieData = Object.entries(analytics.spending_breakdown)
    .map(([category, data]) => ({
      name: category.replace('_', ' ').charAt(0).toUpperCase() + category.replace('_', ' ').slice(1),
      value: data.amount,
      percentage: data.percentage,
    }))
    .sort((a, b) => b.value - a.value);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
    }).format(value);
  };

  const visibleTransactions = showFullHistory
    ? analytics.recent_transactions
    : analytics.recent_transactions.slice(0, 10);

  const handleViewFullHistory = () => {
    if (onViewFullHistory) {
      onViewFullHistory();
      return;
    }
    setShowFullHistory((prev) => !prev);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">Expense Classification Analytics</h1>
            <p className="text-muted-foreground mt-1">
              Analyze categorized expenses and improve AI learning by correcting errors.
            </p>
          </div>
        </div>

        {/* Date Range Selector */}
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              Last {days} Days ({dateRange.start} - {dateRange.end})
            </span>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleViewFullHistory}
            >
              {showFullHistory ? 'Show Latest 10' : 'View Full Expense History'}
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={onAnalyzeMore}
            >
              Add/Classify Expense
            </Button>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Overall Spending Breakdown */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">
            Overall Spending Breakdown ({dateRange.start} - {dateRange.end})
          </h2>
          <div className="flex items-center justify-center min-h-[300px]">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="value"
                  label={(entry) => `${entry.percentage}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => formatCurrency(Number(value))}
                  labelFormatter={(label) => (
                    <span className="text-sm font-medium">{label}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="mt-6 grid grid-cols-2 gap-3 text-sm">
            {pieData.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                />
                <span className="text-muted-foreground">{item.name} ({item.percentage}%)</span>
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="mt-6 pt-4 border-t">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-muted-foreground">Total Expenses:</span>
              <span className="text-2xl font-bold">
                {formatCurrency(analytics.summary.total_spent)}
              </span>
            </div>
          </div>
        </Card>

        {/* Budget Adherence: 50/30/20 Rule */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Budget Adherence: 50/30/20 Rule</h2>
          <div className="space-y-6">
            {/* Needs */}
            <BudgetCategoryRow
              label="Needs (Target 50%)"
              amount={analytics.budget_adherence.needs.amount}
              percentage={analytics.budget_adherence.needs.percentage}
              target={analytics.budget_adherence.needs.target}
              status={analytics.budget_adherence.needs.status}
              color="bg-teal-500"
            />

            {/* Wants */}
            <BudgetCategoryRow
              label="Wants (Target 30%)"
              amount={analytics.budget_adherence.wants.amount}
              percentage={analytics.budget_adherence.wants.percentage}
              target={analytics.budget_adherence.wants.target}
              status={analytics.budget_adherence.wants.status}
              color="bg-red-500"
            />

            {/* Savings */}
            <BudgetCategoryRow
              label="Savings (Target 20%)"
              amount={analytics.budget_adherence.savings.amount}
              percentage={analytics.budget_adherence.savings.percentage}
              target={analytics.budget_adherence.savings.target}
              status={analytics.budget_adherence.savings.status}
              color="bg-green-500"
            />
          </div>
        </Card>
      </div>

      {/* Quick Analysis Insights */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4">Quick Analysis Insights</h2>
        {analytics.insights.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analytics.insights.map((insight, idx) => (
              <div
                key={idx}
                className="p-4 border rounded-lg bg-gradient-to-br from-blue-50 to-transparent"
              >
                <div className="flex items-start gap-3">
                  {insight.type.includes('high') ? (
                    <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <TrendingUp className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900">{insight.title}</p>
                    {insight.percentage !== undefined && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {insight.percentage}%
                        {insight.target && ` (Target: ${insight.target}%)`}
                      </p>
                    )}
                    {insight.recommendation && (
                      <p className="text-xs text-muted-foreground mt-2 italic">
                        💡 {insight.recommendation}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No insights available yet.</p>
        )}
      </Card>

      {/* Recent Classified Transactions */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">
            Recent Classified Transactions (For Manual Correction & Teach AI)
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left py-3 px-4 font-semibold">Date</th>
                <th className="text-left py-3 px-4 font-semibold">Description</th>
                <th className="text-left py-3 px-4 font-semibold">System-Assigned Category</th>
                <th className="text-right py-3 px-4 font-semibold">Amount</th>
                <th className="text-center py-3 px-4 font-semibold">Correct?</th>
                <th className="text-center py-3 px-4 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {visibleTransactions.map((txn, idx) => (
                <tr key={idx} className="border-b hover:bg-muted/50 transition-colors">
                  <td className="py-3 px-4 text-xs text-muted-foreground">
                    {new Date(txn.date).toLocaleDateString('en-US', {
                      month: 'numeric',
                      day: 'numeric',
                    })}
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-medium text-gray-900">{txn.description}</span>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant="outline" className="capitalize">
                      {txn.category.replace('_', ' ')}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-right font-medium">
                    {formatCurrency(txn.amount)}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <CheckCircle className="w-5 h-5 text-green-600 inline-block" />
                  </td>
                  <td className="py-3 px-4 text-center">
                    <button className="text-blue-600 hover:text-blue-700 transition-colors p-1">
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {analytics.recent_transactions.length > 10 && (
          <div className="mt-4 text-center">
            <Button variant="outline" onClick={handleViewFullHistory}>
              {showFullHistory
                ? 'Show Latest 10'
                : `View All Transactions (${analytics.recent_transactions.length})`}
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}

interface BudgetCategoryRowProps {
  label: string;
  amount: number;
  percentage: number;
  target: number;
  status: string;
  color: string;
}

function BudgetCategoryRow({
  label,
  amount,
  percentage,
  target,
  status,
  color,
}: BudgetCategoryRowProps) {
  const isGood = status === 'good';
  const isHigh = status === 'high';

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">
            {formatCurrency(amount)} (Target {target}%)
          </span>
          {isGood ? (
            <CheckCircle className="w-4 h-4 text-green-600" />
          ) : isHigh ? (
            <AlertCircle className="w-4 h-4 text-red-600" />
          ) : null}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full transition-all ${color}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      <div className="flex justify-between mt-1">
        <span className="text-xs text-muted-foreground">{percentage.toFixed(1)}% Spent</span>
        <span className="text-xs text-muted-foreground">{target}% Target</span>
      </div>
    </div>
  );
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    notation: 'compact',
    maximumFractionDigits: 0,
  }).format(value);
}
