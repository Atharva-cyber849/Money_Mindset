"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { forecastCategory } from '@/lib/api/analytics';
import { Loader2, TrendingUp, TrendingDown, Minus, BarChart3, TrendingUpIcon, Lightbulb, Calendar, Clock, AlertCircle } from 'lucide-react';
import { ForecastLineChart, StatisticsPulse, InsightCard, ExplanationCard, HowItWorks, ExampleShowcase } from '@/components/analytics';

export default function ForecastingPage() {
  const [category, setCategory] = useState('groceries');
  const [historicalData, setHistoricalData] = useState('500,520,480,510,495,530');
  const [monthsAhead, setMonthsAhead] = useState('3');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleForecast = async () => {
    setLoading(true);
    try {
      const amounts = historicalData.split(',').map((val) => parseFloat(val.trim())).filter((val) => !isNaN(val));
      
      if (amounts.length < 2) {
        alert('Please enter at least 2 historical data points');
        setLoading(false);
        return;
      }

      const data = await forecastCategory({
        category,
        historical_amounts: amounts,
        months_ahead: parseInt(monthsAhead),
      });
      setResult(data);
    } catch (error) {
      console.error('Forecast failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'increasing') return <TrendingUp className="w-5 h-5 text-red-600" />;
    if (trend === 'decreasing') return <TrendingDown className="w-5 h-5 text-green-600" />;
    return <Minus className="w-5 h-5 text-gray-600" />;
  };

  const getTrendColor = (trend: string) => {
    if (trend === 'increasing') return 'text-red-600 bg-red-50';
    if (trend === 'decreasing') return 'text-green-600 bg-green-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Spending Forecasting</h1>
        <p className="text-muted-foreground">
          Time-series analysis to predict future spending trends
        </p>
      </div>

      {/* Educational Infographics */}
      <div className="mb-12 space-y-6">
        {/* Explanation */}
        <ExplanationCard
          icon={TrendingUp}
          title="What is Spending Forecasting?"
          description="Forecasting predicts future spending patterns by analyzing your historical spending data. Using time-series analysis, we identify trends and project what you'll likely spend in upcoming months."
          keyPoints={[
            'Analyzes your historical spending data across months',
            'Identifies increasing or decreasing trends in your expenses',
            'Projects future spending with confidence intervals',
            'Helps you plan budgets and anticipate financial needs',
            'More data points = more accurate predictions',
          ]}
          color="blue"
          example="If you spent $500, $520, $480, $510 on groceries, we predict next month will be around $505 ± $25"
        />

        {/* How It Works */}
        <HowItWorks
          title="How Spending Forecast Works"
          steps={[
            {
              number: 1,
              title: 'Input Historical Data',
              description: 'Enter your monthly spending amounts for a specific category (e.g., groceries, entertainment). More months of data = better accuracy.',
              icon: Calendar,
            },
            {
              number: 2,
              title: 'Analyze Trends',
              description: 'Our algorithm identifies if your spending is increasing, decreasing, or staying stable over time.',
              icon: TrendingUp,
            },
            {
              number: 3,
              title: 'Calculate Statistics',
              description: 'We compute average spending, variation (std dev), and identify minimum/maximum spending months.',
              icon: BarChart3,
            },
            {
              number: 4,
              title: 'Generate Forecast',
              description: 'We project future spending for your chosen months with confidence intervals showing likely range.',
              icon: Clock,
            },
          ]}
          color="blue"
        />

        {/* Example */}
        <ExampleShowcase
          title="Forecasting Example"
          description="See how we predict your future spending based on history"
          inputExample={[
            { label: 'Category', value: 'Restaurants' },
            { label: 'Historical Data (6 months)', value: '$300-400', highlight: true },
            { label: 'Months to Forecast', value: '3 months' },
            { label: 'Average Monthly', value: '$350' },
          ]}
          outputExample={[
            { label: 'Month 1 Prediction', value: '$355' },
            { label: 'Confidence Range', value: '$320-390', highlight: true },
            { label: 'Trend Direction', value: 'Stable' },
            { label: 'Recommendation', value: 'Budget $380' },
          ]}
          color="blue"
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <Card className="lg:col-span-1 p-6">
          <h3 className="text-lg font-bold mb-2">Forecast Parameters</h3>
          <p className="text-sm text-muted-foreground mb-4">Enter historical spending data</p>
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="category" className="text-sm font-medium">Category</label>
              <Input
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g., groceries, restaurants"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="months" className="text-sm font-medium">Months to Forecast</label>
              <Input
                id="months"
                type="number"
                min="1"
                max="12"
                value={monthsAhead}
                onChange={(e) => setMonthsAhead(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="historical" className="text-sm font-medium">Historical Data (comma-separated)</label>
              <textarea
                id="historical"
                className="w-full min-h-[100px] p-3 border rounded-md text-sm"
                value={historicalData}
                onChange={(e) => setHistoricalData(e.target.value)}
                placeholder="500, 520, 480, 510, 495..."
              />
              <p className="text-xs text-muted-foreground">
                Enter monthly amounts separated by commas. More data = better accuracy.
              </p>
            </div>

            <Button onClick={handleForecast} disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Forecasting...
                </>
              ) : (
                'Generate Forecast'
              )}
            </Button>
          </div>
        </Card>

        {/* Results Panel */}
        {result && (
          <div className="lg:col-span-2 space-y-6">
            {/* Forecast Line Chart */}
            <ForecastLineChart
              historicalData={result.historical_data?.map((val: number, idx: number) => ({
                month: `Month ${idx + 1}`,
                value: Math.round(val),
              })) || []}
              predictions={result.predictions?.map((pred: any) => ({
                month: `M${pred.month}`,
                value: Math.round(pred.predicted),
                low: Math.round(pred.confidence_low),
                high: Math.round(pred.confidence_high),
              })) || []}
              months={result.predictions?.length || 0}
            />

            {/* Key Statistics */}
            <StatisticsPulse
              stats={[
                {
                  label: 'Average',
                  value: Math.round(result.historical_stats.average),
                  icon: BarChart3,
                  color: 'teal',
                },
                {
                  label: 'Min',
                  value: Math.round(result.historical_stats.min),
                  icon: TrendingDown,
                  color: 'green',
                },
                {
                  label: 'Max',
                  value: Math.round(result.historical_stats.max),
                  icon: TrendingUp,
                  color: 'red',
                },
                {
                  label: 'Std Dev',
                  value: Math.round(result.historical_stats.std_dev),
                  icon: BarChart3,
                  color: 'cyan',
                },
              ]}
            />

            {/* Trend Analysis with Insight */}
            <InsightCard
              icon={result.trend.trend === 'increasing' ? TrendingUp : result.trend.trend === 'decreasing' ? TrendingDown : Minus}
              title={`Spending Trend: ${result.trend.trend.charAt(0).toUpperCase() + result.trend.trend.slice(1)}`}
              description={`Monthly change: ${result.trend.monthly_change >= 0 ? '+' : ''}$${Math.abs(result.trend.monthly_change).toFixed(2)}`}
              color={result.trend.trend === 'increasing' ? 'red' : result.trend.trend === 'decreasing' ? 'green' : 'yellow'}
            />

            {/* Recommendation */}
            {result.recommendation && (
              <InsightCard
                icon={Lightbulb}
                title="Forecast Insight"
                description={result.recommendation}
                color="cyan"
                featured
              />
            )}
          </div>
        )}

        {/* Placeholder */}
        {!result && !loading && (
          <Card className="lg:col-span-2 p-6">
            <div className="flex flex-col items-center justify-center py-12">
              <BarChart3 className="w-16 h-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Ready to Forecast</h3>
              <p className="text-muted-foreground text-center max-w-md">
                Enter your historical spending data to generate predictions using time-series
                analysis. The more data you provide, the more accurate the forecast.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
