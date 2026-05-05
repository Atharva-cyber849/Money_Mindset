"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Pill';
import { getCurrentBudgetAnalysis } from '@/lib/api/analytics';
import { 
  Target, 
  AlertCircle, 
  CheckCircle, 
  TrendingUp,
  Loader2,
  Wallet,
  PiggyBank,
  Zap,
  DollarSign,
  BarChart3,
  Lightbulb
} from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

const COLORS = ['#06B6D4', '#F97316', '#10B981'];

interface BudgetOptimizationDashboardProps {
  onCustomize?: () => void;
}

export function BudgetOptimizationDashboard({
  onCustomize,
}: BudgetOptimizationDashboardProps) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const data = await getCurrentBudgetAnalysis();
      setAnalysis(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load budget analysis');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <Card className="p-6 border-red-200 bg-red-50">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-800">{error || 'No data available'}</p>
        </div>
      </Card>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const pieData = [
    { name: 'Needs (50%)', value: analysis.budget_breakdown.needs.percentage, color: '#06B6D4' },
    { name: 'Wants (30%)', value: analysis.budget_breakdown.wants.percentage, color: '#F97316' },
    { name: 'Savings (20%)', value: analysis.budget_breakdown.savings.percentage, color: '#10B981' },
  ];

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div>
          <h1 className="text-3xl font-bold">Budget Optimization & Financial Health</h1>
          <p className="text-muted-foreground mt-1">
            Analyze your spending against the 50/30/20 rule and get personalized recommendations.
          </p>
        </div>

        <div className="flex gap-2">
          <Button onClick={fetchAnalysis} variant="outline">
            Refresh Analysis
          </Button>
          <Button onClick={onCustomize}>
            Customize Budget
          </Button>
        </div>
      </div>

      {/* Health Score */}
      <Card className="p-6 bg-gradient-to-br from-purple-50 to-transparent border-purple-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-purple-900">Financial Health Score</p>
            <p className="text-4xl font-bold text-purple-900 mt-1">
              {Math.round(analysis.health_score)}/100
            </p>
            <p className="text-xs text-purple-700 mt-2">
              {analysis.health_score >= 80
                ? '✨ Excellent budget management'
                : analysis.health_score >= 60
                ? '👍 Good spending habits'
                : analysis.health_score >= 40
                ? '⚠️ Room for improvement'
                : '🔴 Needs attention'}
            </p>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-24 h-24 rounded-full relative flex items-center justify-center">
              <svg className="w-24 h-24" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={
                    analysis.health_score >= 80
                      ? '#10B981'
                      : analysis.health_score >= 60
                      ? '#F59E0B'
                      : analysis.health_score >= 40
                      ? '#F97316'
                      : '#EF4444'
                  }
                  strokeWidth="8"
                  strokeDasharray={`${(analysis.health_score / 100) * 282.7} 282.7`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <span className="absolute text-lg font-bold">
                {Math.round(analysis.health_score)}%
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Budget Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Spending Distribution (50/30/20 Rule)</h2>
          <div className="h-80">
            {analysis.total_spent === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground bg-muted/20 rounded-lg">
                <BarChart3 className="w-16 h-16 opacity-20 mb-4" />
                <p className="font-medium">No transactions found</p>
                <p className="text-sm mt-1">Add some expenses in the last 30 days to see your budget distribution.</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={(entry) => `${entry.value.toFixed(1)}%`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        {/* Budget Breakdown Details */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Budget Categories</h2>
          <div className="space-y-6">
            <BudgetCategoryCard
              label="Needs"
              description="Essential expenses"
              amount={analysis.budget_breakdown.needs.amount}
              percentage={analysis.budget_breakdown.needs.percentage}
              target={analysis.budget_breakdown.needs.target}
              status={analysis.budget_breakdown.needs.status}
              icon={Wallet}
              color="bg-cyan-500"
            />

            <BudgetCategoryCard
              label="Wants"
              description="Discretionary spending"
              amount={analysis.budget_breakdown.wants.amount}
              percentage={analysis.budget_breakdown.wants.percentage}
              target={analysis.budget_breakdown.wants.target}
              status={analysis.budget_breakdown.wants.status}
              icon={Zap}
              color="bg-orange-500"
            />

            <BudgetCategoryCard
              label="Savings"
              description="Emergency & investments"
              amount={analysis.budget_breakdown.savings.amount}
              percentage={analysis.budget_breakdown.savings.percentage}
              target={analysis.budget_breakdown.savings.target}
              status={analysis.budget_breakdown.savings.status}
              icon={PiggyBank}
              color="bg-green-500"
            />
          </div>
        </Card>
      </div>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <Card className="p-6 bg-gradient-to-br from-amber-50 to-transparent border-amber-200">
          <div className="flex items-start gap-3 mb-4">
            <Lightbulb className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-amber-900">Recommendations</h3>
              <p className="text-sm text-amber-800">Actionable insights to improve your financial health</p>
            </div>
          </div>

          <div className="space-y-3">
            {analysis.recommendations.map((rec: any, idx: number) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border-l-4 ${
                  rec.priority === 'high'
                    ? 'bg-red-50 border-red-400'
                    : 'bg-yellow-50 border-yellow-400'
                }`}
              >
                <p className="text-sm font-semibold text-gray-900">{rec.title}</p>
                <p className="text-xs text-gray-700 mt-1">{rec.message}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Total Spent */}
      <Card className="p-6 border-b-4 border-primary">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Spent (Last 30 Days)</p>
            <p className="text-4xl font-bold text-primary mt-1">
              {formatCurrency(analysis.total_spent)}
            </p>
          </div>
          <BarChart3 className="w-16 h-16 text-primary opacity-20" />
        </div>
      </Card>
    </div>
  );
}

interface BudgetCategoryCardProps {
  label: string;
  description: string;
  amount: number;
  percentage: number;
  target: number;
  status: string;
  icon: any;
  color: string;
}

function BudgetCategoryCard({
  label,
  description,
  amount,
  percentage,
  target,
  status,
  icon: Icon,
  color,
}: BudgetCategoryCardProps) {
  const isGood = status === 'good';
  const isHigh = status === 'high';

  return (
    <div className="flex items-start gap-4">
      <div className={`p-3 rounded-lg ${color} text-white`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <div>
            <p className="font-semibold text-gray-900">{label}</p>
            <p className="text-xs text-muted-foreground">{description}</p>
          </div>
          {isGood ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : isHigh ? (
            <AlertCircle className="w-5 h-5 text-red-600" />
          ) : null}
        </div>

        <div className="mt-2">
          <div className="flex justify-between text-sm mb-1">
            <span className="font-semibold">{percentage.toFixed(1)}%</span>
            <span className="text-muted-foreground">Target: {target}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all ${color}`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
