"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ForecastingDashboard } from '@/components/analytics';
import { detectAnomalies, forecastCategory } from '@/lib/api/analytics';
import { AlertCircle, Loader2 } from 'lucide-react';

export default function ForecastingPage() {
  const [showForecastTool, setShowForecastTool] = useState(false);
  const [category, setCategory] = useState('groceries');
  const [monthsAhead, setMonthsAhead] = useState('3');
  const [amountsInput, setAmountsInput] = useState('12000, 13500, 12800, 14200, 15000, 14750');
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [loadingAnomalies, setLoadingAnomalies] = useState(false);
  const [error, setError] = useState('');
  const [forecastResult, setForecastResult] = useState<any>(null);
  const [anomalyResult, setAnomalyResult] = useState<any>(null);

  const parseAmounts = () => {
    return amountsInput
      .split(',')
      .map((item) => Number(item.trim()))
      .filter((value) => Number.isFinite(value) && value >= 0);
  };

  const handleCategoryForecast = async () => {
    const amounts = parseAmounts();
    const ahead = Number(monthsAhead);

    if (!category.trim()) {
      setError('Please enter a category name.');
      return;
    }

    if (amounts.length < 2) {
      setError('Enter at least 2 valid historical amounts.');
      return;
    }

    if (!Number.isInteger(ahead) || ahead < 1 || ahead > 12) {
      setError('Months ahead must be between 1 and 12.');
      return;
    }

    setLoadingForecast(true);
    setError('');

    try {
      const data = await forecastCategory({
        category: category.trim(),
        historical_amounts: amounts,
        months_ahead: ahead,
      });
      setForecastResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to run category forecast.');
    } finally {
      setLoadingForecast(false);
    }
  };

  const handleDetectAnomalies = async () => {
    const amounts = parseAmounts();
    if (amounts.length < 2) {
      setError('Enter at least 2 valid historical amounts.');
      return;
    }

    setLoadingAnomalies(true);
    setError('');

    try {
      const data = await detectAnomalies(amounts, 2.0);
      setAnomalyResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to detect anomalies.');
    } finally {
      setLoadingAnomalies(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl space-y-8">
      {/* Dashboard */}
      <ForecastingDashboard
        onForecast={() => setShowForecastTool(!showForecastTool)}
      />

      {showForecastTool && (
        <Card className="p-6 space-y-5 border-cyan-200 bg-cyan-50/30">
          <div>
            <h2 className="text-xl font-bold">Manual Forecast Tool</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Provide category-wise historical monthly amounts to generate a focused forecast and anomaly signal.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="forecast-category" className="text-sm font-medium">Category</label>
              <Input
                id="forecast-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="groceries"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="months-ahead" className="text-sm font-medium">Months Ahead (1-12)</label>
              <Input
                id="months-ahead"
                type="number"
                min="1"
                max="12"
                value={monthsAhead}
                onChange={(e) => setMonthsAhead(e.target.value)}
                placeholder="3"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="historical-amounts" className="text-sm font-medium">Historical Amounts (comma-separated)</label>
            <Input
              id="historical-amounts"
              value={amountsInput}
              onChange={(e) => setAmountsInput(e.target.value)}
              placeholder="12000, 13500, 12800, 14200"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <Button onClick={handleCategoryForecast} disabled={loadingForecast}>
              {loadingForecast ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Forecasting...
                </>
              ) : (
                'Run Category Forecast'
              )}
            </Button>
            <Button variant="outline" onClick={handleDetectAnomalies} disabled={loadingAnomalies}>
              {loadingAnomalies ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Detecting...
                </>
              ) : (
                'Detect Anomalies'
              )}
            </Button>
            <Button variant="outline" onClick={() => setShowForecastTool(false)}>
              Close
            </Button>
          </div>

          {forecastResult && (
            <Card className="p-4 border-green-200 bg-green-50/40 space-y-2">
              <h3 className="font-semibold text-green-900">Forecast Result</h3>
              <p className="text-sm text-green-800">Trend: {forecastResult.trend_analysis?.trend ?? 'N/A'}</p>
              <p className="text-sm text-green-800">
                Historical Average: {Number.isFinite(Number(forecastResult.historical_stats?.average))
                  ? Number(forecastResult.historical_stats.average).toLocaleString('en-IN')
                  : 'N/A'}
              </p>
              {Array.isArray(forecastResult.predictions) && forecastResult.predictions.length > 0 && (
                <div className="space-y-2 mt-2">
                  {forecastResult.predictions.map((item: any, idx: number) => (
                    <div key={idx} className="text-sm bg-white/80 border border-green-200 rounded-md px-3 py-2 text-slate-800">
                      Month {item.month}: {Number(item.predicted).toLocaleString('en-IN')} ({item.confidence_low} - {item.confidence_high})
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}

          {anomalyResult && (
            <Card className="p-4 border-amber-200 bg-amber-50/40 space-y-2">
              <h3 className="font-semibold text-amber-900">Anomaly Result</h3>
              <p className="text-sm text-amber-800">
                Anomalies Found: {Array.isArray(anomalyResult.anomalies) ? anomalyResult.anomalies.length : 0}
              </p>
              {Array.isArray(anomalyResult.anomalies) && anomalyResult.anomalies.length > 0 && (
                <div className="space-y-2 mt-2">
                  {anomalyResult.anomalies.map((item: any, idx: number) => (
                    <div key={idx} className="text-sm bg-white/80 border border-amber-200 rounded-md px-3 py-2 text-slate-800">
                      Index {item.index}: value {Number(item.value).toLocaleString('en-IN')} (z-score {Number(item.z_score).toFixed(2)})
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
