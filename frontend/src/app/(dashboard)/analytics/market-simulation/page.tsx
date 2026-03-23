"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { simulateInvestment, getAssetClasses } from '@/lib/api/analytics';
import { Loader2, TrendingUp, DollarSign, TrendingDown, BarChart3, Zap, TrendingUpIcon, PieChart } from 'lucide-react';
import { DistributionBellCurve, StatisticsPulse, ExplanationCard, HowItWorks, ExampleShowcase, ConceptInfographic } from '@/components/analytics';

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

      {/* Educational Infographics */}
      <div className="mb-12 space-y-6">
        {/* Explanation */}
        <ExplanationCard
          icon={TrendingUpIcon}
          title="What is Market Simulation?"
          description="Monte Carlo simulations run 1000+ virtual market scenarios using historical asset class data to show possible investment outcomes. This helps you see the range of possible results and understand investment risk vs. reward."
          keyPoints={[
            'Based on 20+ years of historical market data',
            'Runs 1000 simulations to cover market scenarios',
            'Shows percentile ranges (P10 to P90) of possible outcomes',
            'Calculates probability of profit, loss, and wealth doubling',
            'Helps set realistic expectations for your investments',
          ]}
          color="purple"
          example="Investing $10K initial + $500/month for 10 years typically results in $85K-$220K depending on market conditions"
        />

        {/* How It Works */}
        <HowItWorks
          title="How Market Simulation Works"
          steps={[
            {
              number: 1,
              title: 'Enter Investment Parameters',
              description: 'Specify your initial investment, monthly contribution, investment time horizon (years), and asset class (stocks, bonds, balanced).',
              icon: DollarSign,
            },
            {
              number: 2,
              title: 'Run 1000 Simulations',
              description: 'Our algorithm randomly samples historical returns to simulate 1000 potential market scenarios over your time period.',
              icon: Zap,
            },
            {
              number: 3,
              title: 'Calculate Distribution',
              description: 'We analyze all 1000 outcomes to determine percentiles (10th, 25th, 50th, 75th, 90th) showing the range of possible results.',
              icon: BarChart3,
            },
            {
              number: 4,
              title: 'Compute Probabilities',
              description: 'We calculate the likelihood of profit, doubling your investment, and experiencing losses. See your risk profile clearly.',
              icon: TrendingUp,
            },
          ]}
          color="purple"
        />

        {/* Visual Concept */}
        <ConceptInfographic
          title="Understanding Bell Curve Distribution"
          subtitle="What the percentiles mean for your investment"
          type="bars"
          segments={[
            {
              label: 'P10 (Pessimistic)',
              percentage: 10,
              color: '#EF4444',
              description: 'Worst 10% case',
            },
            {
              label: 'P25',
              percentage: 25,
              color: '#F59E0B',
              description: 'Below average',
            },
            {
              label: 'P50 (Median)',
              percentage: 50,
              color: '#0891B2',
              description: 'Most likely outcome',
            },
            {
              label: 'P75',
              percentage: 75,
              color: '#06B6D4',
              description: 'Above average',
            },
            {
              label: 'P90 (Optimistic)',
              percentage: 90,
              color: '#10B981',
              description: 'Best 10% case',
            },
          ]}
        />

        {/* Example */}
        <ExampleShowcase
          title="Market Simulation Example"
          description="See possible outcomes for your investment strategy"
          inputExample={[
            { label: 'Initial Investment', value: '$10,000', highlight: true },
            { label: 'Monthly Contribution', value: '$500' },
            { label: 'Time Horizon', value: '10 years' },
            { label: 'Asset Class', value: 'Balanced' },
          ]}
          outputExample={[
            { label: 'P50 (Median)', value: '$125,000', highlight: true },
            { label: 'P10 (Pessimistic)', value: '$85,000' },
            { label: 'P90 (Optimistic)', value: '$180,000' },
            { label: 'Profit Probability', value: '87%', highlight: true },
          ]}
          color="purple"
        />
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
                <div className="text-sm font-medium text-gray-600 mb-3">
                  Total Invested
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatCurrency(result.total_invested)}
                </div>
              </Card>

              <Card className="p-6">
                <div className="text-sm font-medium text-gray-600 mb-3">
                  Expected Value (Median)
                </div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(result.statistics.median)}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {formatCurrency(result.returns.expected_gain)} gain
                </p>
              </Card>
            </div>

            {/* Distribution Bell Curve */}
            <DistributionBellCurve
              percentiles={{
                p10: result.percentiles.p10,
                p25: result.percentiles.p25,
                p50: result.percentiles.p50,
                p75: result.percentiles.p75,
                p90: result.percentiles.p90,
              }}
              probability={{
                profit: result.probability_analysis.prob_profit,
                double: result.probability_analysis.prob_double,
                loss: result.probability_analysis.prob_loss,
              }}
            />

            {/* Key Statistics */}
            <StatisticsPulse
              stats={[
                {
                  label: 'Mean Outcome',
                  value: Math.round(result.statistics.mean),
                  icon: BarChart3,
                  color: 'teal',
                },
                {
                  label: 'Std Dev',
                  value: Math.round(result.statistics.std_dev),
                  icon: BarChart3,
                  color: 'cyan',
                },
                {
                  label: 'Best Case',
                  value: Math.round(result.statistics.max),
                  icon: TrendingUp,
                  color: 'green',
                },
                {
                  label: 'Worst Case',
                  value: Math.round(result.statistics.min),
                  icon: TrendingDown,
                  color: 'red',
                },
              ]}
            />
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
