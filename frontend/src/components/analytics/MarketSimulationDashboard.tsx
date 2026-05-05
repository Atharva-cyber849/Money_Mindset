"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { getPortfolioSimulationAnalysis } from '@/lib/api/analytics';
import { 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  BarChart3,
  Loader2,
  ArrowUpRight,
  ArrowDownLeft,
  DollarSign
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

interface MarketSimulationDashboardProps {
  onSimulate?: () => void;
}

export function MarketSimulationDashboard({
  onSimulate,
}: MarketSimulationDashboardProps) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [params, setParams] = useState({
    initial_amount: 100000,
    monthly_contribution: 5000,
    years: 20,
  });

  useEffect(() => {
    fetchAnalysis();
  }, [params]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const data = await getPortfolioSimulationAnalysis(params);
      setAnalysis(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load simulation analysis');
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
    }).format(value);
  };

  // Prepare comparison data
  const comparisonData = Object.entries(analysis.scenarios).map(([assetClass, metrics]: any) => ({
    name: assetClass.replace(/_/g, ' ').toUpperCase(),
    mean: metrics.mean,
    percentile_25: metrics.percentile_25,
    percentile_75: metrics.percentile_75,
    min: metrics.min,
    max: metrics.max,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div>
          <h1 className="text-3xl font-bold">Market Simulation & Portfolio Analysis</h1>
          <p className="text-muted-foreground mt-1">
            Monte Carlo simulations showing investment growth across different asset classes.
          </p>
        </div>

        <div>
          <Button onClick={onSimulate}>Open Detailed Simulator</Button>
        </div>

        {/* Parameters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Initial Amount (₹)</label>
            <Input
              type="number"
              value={params.initial_amount}
              onChange={(e) => setParams({...params, initial_amount: parseFloat(e.target.value)})}
              placeholder="100000"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Monthly Contribution (₹)</label>
            <Input
              type="number"
              value={params.monthly_contribution}
              onChange={(e) => setParams({...params, monthly_contribution: parseFloat(e.target.value)})}
              placeholder="5000"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Years</label>
            <Input
              type="number"
              value={params.years}
              onChange={(e) => setParams({...params, years: parseInt(e.target.value)})}
              placeholder="20"
              min="1"
              max="50"
            />
          </div>
          <div className="flex items-end">
            <Button onClick={fetchAnalysis} className="w-full">
              Recalculate
            </Button>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Initial Investment</p>
              <p className="text-2xl font-bold">{formatCurrency(analysis.parameters.initial_amount)}</p>
            </div>
            <DollarSign className="w-10 h-10 text-blue-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Contributed</p>
              <p className="text-2xl font-bold">{formatCurrency(analysis.parameters.total_contributed)}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Time Horizon</p>
              <p className="text-2xl font-bold">{analysis.parameters.years} Years</p>
            </div>
            <BarChart3 className="w-10 h-10 text-purple-500 opacity-20" />
          </div>
        </Card>
      </div>

      {/* Asset Class Comparison */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4">Final Portfolio Value Comparison (Median Outcomes)</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value) => formatCurrency(value as number)}
                labelFormatter={(label) => `${label}`}
              />
              <Legend />
              <Bar dataKey="mean" fill="#0891B2" name="Expected (Mean)" />
              <Bar dataKey="percentile_25" fill="#F59E0B" name="25th Percentile" />
              <Bar dataKey="percentile_75" fill="#10B981" name="75th Percentile" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Risk vs Return Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Best Case Scenarios */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Best Case Scenarios (90th Percentile)</h2>
          <div className="space-y-3">
            {comparisonData.map((item, idx) => (
              <div key={idx} className="p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-gray-900">{item.name}</span>
                  <span className="text-sm font-bold text-green-600">
                    {formatCurrency(analysis.scenarios[item.name.toLowerCase().replace(/ /g, '_')].percentile_90)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{
                        width: `${Math.min((analysis.scenarios[item.name.toLowerCase().replace(/ /g, '_')].percentile_90 / 
                          Math.max(...comparisonData.map(d => analysis.scenarios[d.name.toLowerCase().replace(/ /g, '_')].percentile_90)) * 100), 100)}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Worst Case Scenarios */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Worst Case Scenarios (10th Percentile)</h2>
          <div className="space-y-3">
            {comparisonData.map((item, idx) => (
              <div key={idx} className="p-3 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-gray-900">{item.name}</span>
                  <span className="text-sm font-bold text-red-600">
                    {formatCurrency(analysis.scenarios[item.name.toLowerCase().replace(/ /g, '_')].percentile_10)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div
                      className="h-full bg-red-500 rounded-full"
                      style={{
                        width: `${Math.min((analysis.scenarios[item.name.toLowerCase().replace(/ /g, '_')].percentile_10 / 
                          Math.max(...comparisonData.map(d => analysis.scenarios[d.name.toLowerCase().replace(/ /g, '_')].percentile_90)) * 100), 100)}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Risk Metrics */}
      <Card className="p-6">
        <h2 className="text-lg font-bold mb-4">Risk Metrics (Standard Deviation)</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {comparisonData.map((item, idx) => (
            <div key={idx} className="p-4 bg-muted rounded-lg text-center">
              <p className="text-xs text-muted-foreground mb-2">{item.name}</p>
              <p className="text-lg font-bold">
                {formatCurrency(analysis.scenarios[item.name.toLowerCase().replace(/ /g, '_')].std_dev)}
              </p>
              <p className="text-xs text-muted-foreground mt-2">Volatility</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Insights */}
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-transparent border-blue-200">
        <div className="flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900">Investment Recommendation</h3>
            <p className="text-sm text-blue-800 mt-2">
              Based on your {analysis.parameters.years}-year timeline, a balanced portfolio offers optimal risk-adjusted returns. 
              Regular monthly contributions of {formatCurrency(analysis.parameters.monthly_contribution)} will compound significantly over time.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
