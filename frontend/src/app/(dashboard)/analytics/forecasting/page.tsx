"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { forecastCategory } from '@/lib/api/analytics';
import { Loader2, TrendingUp, TrendingDown, Minus, BarChart3 } from 'lucide-react';

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
            {/* Trend Analysis */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                {getTrendIcon(result.trend.trend)}
                Trend Analysis
              </h3>
              <div>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className={`p-4 rounded-lg ${getTrendColor(result.trend.trend)}`}>
                    <div className="text-sm font-medium mb-1">Trend Direction</div>
                    <div className="text-2xl font-bold capitalize">{result.trend.trend}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-muted">
                    <div className="text-sm font-medium mb-1">Monthly Change</div>
                    <div className="text-2xl font-bold">
                      ${Math.abs(result.trend.monthly_change).toFixed(2)}
                      {result.trend.monthly_change >= 0 ? ' ↑' : ' ↓'}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Historical Stats */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-2">Historical Statistics</h3>
              <p className="text-sm text-muted-foreground mb-4">Based on {result.historical_stats.data_points} months</p>
              <div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Average</div>
                    <div className="text-xl font-bold">
                      ${result.historical_stats.average.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Std Dev</div>
                    <div className="text-xl font-bold">
                      ${result.historical_stats.std_dev.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Min</div>
                    <div className="text-xl font-bold text-green-600">
                      ${result.historical_stats.min.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Max</div>
                    <div className="text-xl font-bold text-red-600">
                      ${result.historical_stats.max.toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Predictions */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-2">Forecast Predictions</h3>
              <p className="text-sm text-muted-foreground mb-4">Predicted spending with confidence intervals</p>
              <div>
                <div className="space-y-4">
                  {result.predictions.map((pred: any, idx: number) => (
                    <div key={idx} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <span className="text-sm text-muted-foreground">Month {pred.month}</span>
                        </div>
                        <Badge variant="neutral">{pred.confidence_level}</Badge>
                      </div>
                      
                      <div className="text-center mb-3">
                        <div className="text-3xl font-bold">
                          ${pred.predicted.toLocaleString()}
                        </div>
                        <div className="text-sm text-muted-foreground">Predicted Amount</div>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div className="text-green-600">
                          Low: ${pred.confidence_low.toLocaleString()}
                        </div>
                        <div className="text-red-600">
                          High: ${pred.confidence_high.toLocaleString()}
                        </div>
                      </div>
                      
                      <div className="relative mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="absolute h-full bg-green-300"
                          style={{
                            left: '0%',
                            width: `${((pred.predicted - pred.confidence_low) / (pred.confidence_high - pred.confidence_low)) * 100}%`,
                          }}
                        />
                        <div
                          className="absolute h-full bg-primary"
                          style={{
                            left: `${((pred.predicted - pred.confidence_low) / (pred.confidence_high - pred.confidence_low)) * 100}%`,
                            width: '2px',
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            {/* Recommendation */}
            {result.recommendation && (
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Recommendation
                </h3>
                <div>
                  <p className="text-muted-foreground">{result.recommendation}</p>
                </div>
              </Card>
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
