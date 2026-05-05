"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { getSpendingTrends } from '@/lib/api/analytics';
import { 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  BarChart3,
  Loader2,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  Clock,
  Lightbulb,
  TrendingDown,
  Minus
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ForecastingDashboardProps {
  onForecast?: () => void;
}

export function ForecastingDashboard({
  onForecast,
}: ForecastingDashboardProps) {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [months, setMonths] = useState(6);

  useEffect(() => {
    fetchTrends();
  }, [months]);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      const data = await getSpendingTrends(months);
      setTrends(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load spending trends');
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

  if (error || !trends) {
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

  const getTrendIcon = (direction: string) => {
    if (direction === 'increasing') return <ArrowUpRight className="w-5 h-5 text-red-600" />;
    if (direction === 'decreasing') return <ArrowDownLeft className="w-5 h-5 text-green-600" />;
    return <Minus className="w-5 h-5 text-gray-600" />;
  };

  const getTrendColor = (direction: string) => {
    if (direction === 'increasing') return 'text-red-600';
    if (direction === 'decreasing') return 'text-green-600';
    return 'text-gray-600';
  };

  // Prepare chart data
  const chartData = (trends.monthly_data || []).map((month: any) => ({
    month: new Date(month.month + '-01T00:00:00').toLocaleDateString('en-US', { month: 'short' }),
    total: month.total,
  }));

  const forecastData = [
    ...chartData,
    ...(trends.forecasts || []).map((forecast: any) => ({
      month: new Date(forecast.month + '-01T00:00:00').toLocaleDateString('en-US', { month: 'short' }),
      forecast: forecast.predicted_spend,
      confidence: forecast.confidence,
    })),
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div>
          <h1 className="text-3xl font-bold">Spending Forecasts & Trend Analysis</h1>
          <p className="text-muted-foreground mt-1">
            Analyze historical spending patterns and predict future trends.
          </p>
        </div>

        {/* Period Selector */}
        <div className="flex items-center gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Historical Period (Months)</label>
            <Input
              type="number"
              value={months}
              onChange={(e) => setMonths(parseInt(e.target.value))}
              placeholder="6"
              min="3"
              max="24"
              className="w-32"
            />
          </div>
          <Button onClick={fetchTrends} variant="outline" className="mt-7">
            Update
          </Button>
          <Button onClick={onForecast} className="mt-7">
            Open Forecast Tool
          </Button>
        </div>
      </div>

      {/* Trend Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Trend Direction</p>
              <p className="text-2xl font-bold capitalize mt-1">{trends.trend.direction}</p>
            </div>
            {getTrendIcon(trends.trend.direction)}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Change Rate</p>
              <p className={`text-2xl font-bold mt-1 ${getTrendColor(trends.trend.direction)}`}>
                {trends.trend.change_percentage > 0 ? '+' : ''}{trends.trend.change_percentage}%
              </p>
            </div>
            <BarChart3 className="w-10 h-10 opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Highest Category</p>
              <p className="text-2xl font-bold capitalize mt-1">
                {trends.highest_category ? trends.highest_category.replace(/_/g, ' ') : 'N/A'}
              </p>
            </div>
            {trends.highest_category && trends.highest_category !== 'N/A' && (
              <Badge variant="outline">{trends.highest_category.replace(/_/g, ' ')}</Badge>
            )}
          </div>
        </Card>
      </div>

      {/* Historical Data Chart */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4">Spending History ({months} Months)</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecastData}>
              <defs>
                <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0891B2" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#0891B2" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value) => formatCurrency(value as number)}
                labelFormatter={(label) => `${label}`}
              />
              <Area
                type="monotone"
                dataKey="total"
                stroke="#0891B2"
                fillOpacity={1}
                fill="url(#colorSpend)"
                name="Monthly Spending"
              />
              <Area
                type="monotone"
                dataKey="forecast"
                stroke="#F59E0B"
                strokeDasharray="5 5"
                fillOpacity={0}
                name="Predicted Spending"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="p-4 bg-muted rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Average</p>
            <p className="text-lg font-bold mt-1">
              {formatCurrency(
                chartData.length ? chartData.reduce((sum: number, d: any) => sum + d.total, 0) / chartData.length : 0
              )}
            </p>
          </div>
          <div className="p-4 bg-muted rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Highest</p>
            <p className="text-lg font-bold mt-1">
              {formatCurrency(chartData.length ? Math.max(...chartData.map((d: any) => d.total)) : 0)}
            </p>
          </div>
          <div className="p-4 bg-muted rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Lowest</p>
            <p className="text-lg font-bold mt-1">
              {formatCurrency(chartData.length ? Math.min(...chartData.map((d: any) => d.total)) : 0)}
            </p>
          </div>
        </div>
      </Card>

      {/* Forecast */}
      {trends.forecasts && trends.forecasts.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">3-Month Forecast</h2>
          
          <div className="space-y-4 mb-6">
            {trends.forecasts.map((forecast: any, idx: number) => (
              <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-blue-600" />
                    <span className="font-semibold text-gray-900">{forecast.month}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-blue-600">
                      {formatCurrency(forecast.predicted_spend)}
                    </span>
                    <Badge variant="outline">
                      {Math.round(forecast.confidence * 100)}% confidence
                    </Badge>
                  </div>
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${forecast.confidence * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Insights */}
      <Card className="p-6 bg-gradient-to-br from-emerald-50 to-transparent border-emerald-200">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-emerald-900">Spending Insight</h3>
            <p className="text-sm text-emerald-800 mt-2">
              Your spending is currently <span className="font-semibold">{trends.trend.direction}</span> by{' '}
              <span className="font-semibold">{Math.abs(trends.trend.change_percentage)}%</span>.{' '}
              {trends.trend.direction === 'increasing'
                ? 'Consider reviewing your discretionary expenses to get spending under control.'
                : 'Great job! Your spending habits show positive control.'}
            </p>
          </div>
        </div>
      </Card>

      {/* Action Items */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-primary" />
          Recommended Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
            <p className="font-semibold text-gray-900">Track by Category</p>
            <p className="text-sm text-muted-foreground mt-1">
              Monitor {trends.highest_category ? trends.highest_category.replace(/_/g, ' ') : 'top'} expenses more closely
            </p>
          </div>
          <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
            <p className="font-semibold text-gray-900">Set Budget Limits</p>
            <p className="text-sm text-muted-foreground mt-1">
              Create alerts for categories exceeding forecast amounts
            </p>
          </div>
          <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
            <p className="font-semibold text-gray-900">Review Trends</p>
            <p className="text-sm text-muted-foreground mt-1">
              Check monthly breakdowns to identify spending patterns
            </p>
          </div>
          <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
            <p className="font-semibold text-gray-900">Plan Ahead</p>
            <p className="text-sm text-muted-foreground mt-1">
              Use forecasts to budget for upcoming months
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
