"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { simulateInvestment, getAssetClasses } from '@/lib/api/analytics';
import { Loader2, TrendingUp, DollarSign } from 'lucide-react';

export default function MarketSimulationPage() {
  const [assetClasses, setAssetClasses] = useState<any>({});
  const [formData, setFormData] = useState({
    initial_amount: '10000',
    monthly_contribution: '500',
    years: '10',
    asset_class: 'balanced',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    loadAssetClasses();
  }, []);

  const loadAssetClasses = async () => {
    try {
      const data = await getAssetClasses();
      setAssetClasses(data);
    } catch (error) {
      console.error('Failed to load asset classes:', error);
    }
  };

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const data = await simulateInvestment({
        initial_amount: parseFloat(formData.initial_amount),
        monthly_contribution: parseFloat(formData.monthly_contribution),
        years: parseInt(formData.years),
        asset_class: formData.asset_class,
        num_simulations: 1000,
      });
      setResult(data);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Market Simulation</h1>
        <p className="text-muted-foreground">
          Historical data-based Monte Carlo simulations to visualize risk vs return
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <Card className="lg:col-span-1 p-6">
          <h3 className="text-lg font-bold mb-2">Simulation Parameters</h3>
          <p className="text-sm text-muted-foreground mb-4">Configure your investment scenario</p>
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="initial" className="text-sm font-medium">Initial Investment</label>
              <Input
                id="initial"
                type="number"
                value={formData.initial_amount}
                onChange={(e) =>
                  setFormData({ ...formData, initial_amount: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="monthly" className="text-sm font-medium">Monthly Contribution</label>
              <Input
                id="monthly"
                type="number"
                value={formData.monthly_contribution}
                onChange={(e) =>
                  setFormData({ ...formData, monthly_contribution: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="years" className="text-sm font-medium">Time Horizon (Years)</label>
              <Input
                id="years"
                type="number"
                min="1"
                max="50"
                value={formData.years}
                onChange={(e) => setFormData({ ...formData, years: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="asset" className="text-sm font-medium">Asset Class</label>
              <select
                id="asset"
                className="w-full p-2 border rounded-md text-sm"
                value={formData.asset_class}
                onChange={(e) =>
                  setFormData({ ...formData, asset_class: e.target.value })
                }
              >
                {Object.entries(assetClasses).map(([key, value]: [string, any]) => (
                  <option key={key} value={key}>
                    {value.name}
                  </option>
                ))}
              </select>
              {assetClasses[formData.asset_class] && (
                <p className="text-xs text-muted-foreground">
                  {assetClasses[formData.asset_class].description}
                </p>
              )}
            </div>

            <Button onClick={handleSimulate} disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Simulating...
                </>
              ) : (
                'Run Simulation'
              )}
            </Button>
          </div>
        </Card>

        {/* Results Panel */}
        {result && (
          <div className="lg:col-span-2 space-y-6">
            {/* Summary Cards */}
            <div className="grid sm:grid-cols-2 gap-4">
              <Card className="p-6">
                <div className="text-sm font-medium text-muted-foreground mb-3">
                  Total Invested
                </div>
                <div className="text-2xl font-bold">
                  {formatCurrency(result.total_invested)}
                </div>
              </Card>

              <Card className="p-6">
                <div className="text-sm font-medium text-muted-foreground mb-3">
                  Expected Value
                </div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(result.statistics.median)}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatCurrency(result.returns.expected_gain)} gain
                </p>
              </Card>
            </div>

            {/* Percentile Ranges */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-2">Potential Outcomes</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Distribution of {result.simulations_run.toLocaleString()} simulations
              </p>
              <div className="space-y-4">
                {[
                  { label: '10th Percentile (Pessimistic)', value: result.percentiles.p10, percent: 10 },
                  { label: '25th Percentile', value: result.percentiles.p25, percent: 25 },
                  { label: '50th Percentile (Median)', value: result.percentiles.p50, percent: 50 },
                  { label: '75th Percentile', value: result.percentiles.p75, percent: 75 },
                  { label: '90th Percentile (Optimistic)', value: result.percentiles.p90, percent: 90 },
                ].map((item, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between text-sm mb-2">
                      <span>{item.label}</span>
                      <span className="font-semibold">{formatCurrency(item.value)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{width: `${item.percent}%`}}></div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Probability Analysis */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Probability Analysis
              </h3>
                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-3xl font-bold text-green-600">
                      {result.probability_analysis.prob_profit}%
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">Chance of Profit</div>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-600">
                      {result.probability_analysis.prob_double}%
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Chance to Double
                    </div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-3xl font-bold text-red-600">
                      {result.probability_analysis.prob_loss}%
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">Risk of Loss</div>
                  </div>
                </div>
            </Card>

            {/* Key Statistics */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4">Statistical Summary</h3>
                <dl className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm text-muted-foreground">Mean Outcome</dt>
                    <dd className="text-lg font-semibold">{formatCurrency(result.statistics.mean)}</dd>
                  </div>
                  <div>
                    <dt className="text-sm text-muted-foreground">Standard Deviation</dt>
                    <dd className="text-lg font-semibold">{formatCurrency(result.statistics.std_dev)}</dd>
                  </div>
                  <div>
                    <dt className="text-sm text-muted-foreground">Best Case</dt>
                    <dd className="text-lg font-semibold text-green-600">
                      {formatCurrency(result.statistics.max)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-muted-foreground">Worst Case</dt>
                    <dd className="text-lg font-semibold text-red-600">
                      {formatCurrency(result.statistics.min)}
                    </dd>
                  </div>
                </dl>
            </Card>
          </div>
        )}

        {/* Placeholder when no results */}
        {!result && !loading && (
          <Card className="lg:col-span-2 p-6">
            <div className="flex flex-col items-center justify-center py-12">
              <DollarSign className="w-16 h-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Ready to Simulate</h3>
              <p className="text-muted-foreground text-center max-w-md">
                Configure your investment parameters and click "Run Simulation" to see
                potential outcomes based on historical market data.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
