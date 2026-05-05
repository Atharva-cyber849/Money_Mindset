"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { MarketSimulationDashboard } from '@/components/analytics';
import { AlertCircle, Loader2 } from 'lucide-react';
import { simulateInvestment, simulateMarketCrash } from '@/lib/api/analytics';

export default function MarketSimulationPage() {
  const [showSimulator, setShowSimulator] = useState(false);
  const [initialAmount, setInitialAmount] = useState('100000');
  const [monthlyContribution, setMonthlyContribution] = useState('5000');
  const [years, setYears] = useState('20');
  const [assetClass, setAssetClass] = useState('balanced');
  const [crashYear, setCrashYear] = useState('5');
  const [loadingSim, setLoadingSim] = useState(false);
  const [loadingCrash, setLoadingCrash] = useState(false);
  const [error, setError] = useState('');
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [crashResult, setCrashResult] = useState<any>(null);

  const parseInputs = () => {
    return {
      initial: Number(initialAmount),
      monthly: Number(monthlyContribution),
      yearsValue: Number(years),
      crashYearValue: Number(crashYear),
    };
  };

  const validateInputs = () => {
    const { initial, monthly, yearsValue, crashYearValue } = parseInputs();
    if (!initial || initial <= 0) return 'Initial amount must be greater than 0.';
    if (Number.isNaN(monthly) || monthly < 0) return 'Monthly contribution cannot be negative.';
    if (!Number.isInteger(yearsValue) || yearsValue < 1 || yearsValue > 50) return 'Years must be between 1 and 50.';
    if (!Number.isInteger(crashYearValue) || crashYearValue < 1 || crashYearValue > yearsValue) {
      return 'Crash year must be between 1 and selected years.';
    }
    return '';
  };

  const handleRunSimulation = async () => {
    const validationError = validateInputs();
    if (validationError) {
      setError(validationError);
      return;
    }

    const { initial, monthly, yearsValue } = parseInputs();
    setLoadingSim(true);
    setError('');
    try {
      const data = await simulateInvestment({
        initial_amount: initial,
        monthly_contribution: monthly,
        years: yearsValue,
        asset_class: assetClass,
        num_simulations: 1000,
      });
      setSimulationResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to run investment simulation.');
    } finally {
      setLoadingSim(false);
    }
  };

  const handleRunCrashScenario = async () => {
    const validationError = validateInputs();
    if (validationError) {
      setError(validationError);
      return;
    }

    const { initial, monthly, yearsValue, crashYearValue } = parseInputs();
    setLoadingCrash(true);
    setError('');
    try {
      const data = await simulateMarketCrash({
        initial_amount: initial,
        monthly_contribution: monthly,
        years: yearsValue,
        asset_class: assetClass,
        crash_year: crashYearValue,
        crash_magnitude: -0.3,
      });
      setCrashResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to run crash simulation.');
    } finally {
      setLoadingCrash(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl space-y-8">
      {/* Dashboard */}
      <MarketSimulationDashboard
        onSimulate={() => setShowSimulator(!showSimulator)}
      />

      {showSimulator && (
        <Card className="p-6 space-y-6 border-cyan-200 bg-cyan-50/30">
          <div>
            <h2 className="text-xl font-bold">Detailed Monte Carlo Simulator</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Run direct simulation and crash scenario tests using your own assumptions.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="initial-amount" className="text-sm font-medium">Initial Amount</label>
              <Input
                id="initial-amount"
                type="number"
                value={initialAmount}
                onChange={(e) => setInitialAmount(e.target.value)}
                placeholder="100000"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="monthly-contribution" className="text-sm font-medium">Monthly Contribution</label>
              <Input
                id="monthly-contribution"
                type="number"
                value={monthlyContribution}
                onChange={(e) => setMonthlyContribution(e.target.value)}
                placeholder="5000"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="years" className="text-sm font-medium">Years</label>
              <Input
                id="years"
                type="number"
                min="1"
                max="50"
                value={years}
                onChange={(e) => setYears(e.target.value)}
                placeholder="20"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="asset-class" className="text-sm font-medium">Asset Class</label>
              <select
                id="asset-class"
                value={assetClass}
                onChange={(e) => setAssetClass(e.target.value)}
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="aggressive_stocks">Aggressive Stocks</option>
                <option value="large_cap_stocks">Large Cap Stocks</option>
                <option value="balanced">Balanced</option>
                <option value="conservative">Conservative</option>
                <option value="bonds">Bonds</option>
                <option value="savings">Savings</option>
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="crash-year" className="text-sm font-medium">Crash Year</label>
              <Input
                id="crash-year"
                type="number"
                min="1"
                max={years || '50'}
                value={crashYear}
                onChange={(e) => setCrashYear(e.target.value)}
                placeholder="5"
              />
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <Button onClick={handleRunSimulation} disabled={loadingSim}>
              {loadingSim ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Simulating...
                </>
              ) : (
                'Run Simulation'
              )}
            </Button>
            <Button variant="outline" onClick={handleRunCrashScenario} disabled={loadingCrash}>
              {loadingCrash ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Simulating Crash...
                </>
              ) : (
                'Run Crash Scenario'
              )}
            </Button>
            <Button variant="outline" onClick={() => setShowSimulator(false)}>
              Close
            </Button>
          </div>

          {simulationResult && (
            <Card className="p-4 border-green-200 bg-green-50/40 space-y-2">
              <h3 className="font-semibold text-green-900">Simulation Result</h3>
              <p className="text-sm text-green-800">Asset: {simulationResult.asset_class}</p>
              <p className="text-sm text-green-800">Expected Return: {simulationResult.returns?.expected_return_pct ?? 0}%</p>
              <p className="text-sm text-green-800">Median Final Value: {Number(simulationResult.statistics?.median ?? 0).toLocaleString('en-IN')}</p>
              <p className="text-sm text-green-800">Profit Probability: {simulationResult.probability_analysis?.prob_profit ?? 0}%</p>
            </Card>
          )}

          {crashResult && (
            <Card className="p-4 border-amber-200 bg-amber-50/40 space-y-2">
              <h3 className="font-semibold text-amber-900">Crash Scenario Result</h3>
              <p className="text-sm text-amber-800">
                Final Value with Crash: {Number(crashResult.crash_scenario?.median_value ?? 0).toLocaleString('en-IN')}
              </p>
              <p className="text-sm text-amber-800">
                Final Value without Crash: {Number(crashResult.normal_scenario?.median_value ?? 0).toLocaleString('en-IN')}
              </p>
              <p className="text-sm text-amber-800">Recovery Years: {crashResult.impact_analysis?.years_to_recover ?? 'N/A'}</p>
              <p className="text-sm text-amber-800">Crash Magnitude: {Number(crashResult.crash_scenario?.crash_magnitude_pct ?? -30).toFixed(0)}%</p>
              {crashResult.lesson && (
                <p className="text-sm text-amber-900 bg-white/70 border border-amber-200 rounded-md px-3 py-2 mt-2">
                  {crashResult.lesson}
                </p>
              )}
            </Card>
          )}
        </Card>
      )}
    </div>
  );
}
