"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { analyzeBudget } from '@/lib/api/analytics';
import { Loader2, AlertTriangle, CheckCircle, TrendingUp, Target } from 'lucide-react';

export default function BudgetOptimizationPage() {
  const [income, setIncome] = useState('5000');
  const [savings, setSavings] = useState('1000');
  const [expenses, setExpenses] = useState({
    housing: '1250',
    transportation: '500',
    groceries: '400',
    restaurants: '300',
    utilities: '150',
    entertainment: '200',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const expenseValues: Record<string, number> = {};
      Object.entries(expenses).forEach(([key, value]) => {
        expenseValues[key] = parseFloat(value) || 0;
      });

      const data = await analyzeBudget({
        income: parseFloat(income),
        expenses: expenseValues,
        savings: parseFloat(savings),
      });
      setResult(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateExpense = (category: string, value: string) => {
    setExpenses({ ...expenses, [category]: value });
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getPriorityIcon = (priority: string) => {
    if (priority === 'high') return <AlertTriangle className="w-4 h-4 text-red-600" />;
    if (priority === 'medium') return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
    return <CheckCircle className="w-4 h-4 text-green-600" />;
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Budget Optimization</h1>
        <p className="text-muted-foreground">
          Rule-based heuristics to analyze savings and expense ratios
        </p>
      </div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* Input Panel */}
        <Card className="lg:col-span-2 p-6">
          <h3 className="text-lg font-bold mb-2">Budget Details</h3>
          <p className="text-sm text-muted-foreground mb-4">Enter your monthly income and expenses</p>
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="income" className="text-sm font-medium">Monthly Income</label>
              <Input
                id="income"
                type="number"
                value={income}
                onChange={(e) => setIncome(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="savings" className="text-sm font-medium">Monthly Savings</label>
              <Input
                id="savings"
                type="number"
                value={savings}
                onChange={(e) => setSavings(e.target.value)}
              />
            </div>

            <div className="border-t pt-4 mt-4">
              <label className="text-base font-medium mb-3 block">Monthly Expenses</label>
              <div className="space-y-3">
                {Object.entries(expenses).map(([category, value]) => (
                  <div key={category} className="space-y-1">
                    <label htmlFor={category} className="text-sm font-medium capitalize">
                      {category.replace('_', ' ')}
                    </label>
                    <Input
                      id={category}
                      type="number"
                      value={value}
                      onChange={(e) => updateExpense(category, e.target.value)}
                    />
                  </div>
                ))}
              </div>
            </div>

            <Button onClick={handleAnalyze} disabled={loading} className="w-full mt-4">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Budget'
              )}
            </Button>
          </div>
        </Card>

        {/* Results Panel */}
        {result && (
          <div className="lg:col-span-3 space-y-6">
            {/* Health Score */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Budget Health Score
              </h3>
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className={`text-5xl font-bold ${getScoreColor(result.health_score.score)}`}>
                      {result.health_score.score}
                    </div>
                    <div className="text-2xl font-semibold text-muted-foreground mt-1">
                      {result.health_score.rating}
                    </div>
                  </div>
                  <div className="text-right space-y-2">
                    <div className="text-sm text-muted-foreground">Savings Rate</div>
                    <div className="text-2xl font-bold">
                      {result.health_score.factors.savings_rate}%
                    </div>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-primary h-3 rounded-full" style={{width: `${result.health_score.score}%`}}></div>
                </div>
              </div>
            </Card>

            {/* 50/30/20 Analysis */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-2">50/30/20 Rule Analysis</h3>
              <p className="text-sm text-muted-foreground mb-4">Recommended budget framework</p>
              <div className="space-y-4">
                {Object.entries(result.fifty_thirty_twenty).map(([key, data]: [string, any]) => {
                  if (key === 'overall_compliance') return null;
                  
                  const percentage = data.percentage;
                  const target = data.target;
                  const status = data.status;
                  
                  return (
                    <div key={key} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="font-semibold capitalize">{key}</span>
                          <span className="text-sm text-muted-foreground ml-2">
                            ${data.amount.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={status === 'on_track' ? 'success' : 'danger'}>
                            {percentage}% / {target}%
                          </Badge>
                        </div>
                      </div>
                      <div className="relative">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{width: `${percentage}%`}}></div>
                        </div>
                        <div
                          className="absolute top-0 h-2 w-0.5 bg-primary"
                          style={{ left: `${target}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
                
                {result.fifty_thirty_twenty.overall_compliance && (
                  <div className="pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">Overall Score</span>
                      <Badge variant="neutral" className="text-lg">
                        {result.fifty_thirty_twenty.overall_compliance.grade}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">
                      {result.fifty_thirty_twenty.overall_compliance.message}
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Optimization Recommendations
                </h3>
                <div className="space-y-3">
                  {result.recommendations.map((rec: any, idx: number) => (
                    <div key={idx} className="flex gap-3 p-3 border rounded-lg">
                      {getPriorityIcon(rec.priority)}
                      <div className="flex-1">
                        <div className="font-semibold text-sm mb-1">{rec.issue}</div>
                        <div className="text-sm text-muted-foreground">{rec.suggestion}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Optimization Potential */}
            {result.optimization_potential && (
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Optimization Potential</h3>
                <div>
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <div className="text-2xl font-bold">
                        ${result.optimization_potential.potential_additional_savings.toLocaleString()}
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        Potential Monthly Savings
                      </div>
                    </div>
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {result.optimization_potential.potential_savings_rate}%
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        Potential Savings Rate
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4">
                    By optimizing expenses to recommended levels, you could increase your savings
                    rate by {result.optimization_potential.improvement}%.
                  </p>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Placeholder */}
        {!result && !loading && (
          <Card className="lg:col-span-3 p-6">
            <div className="flex flex-col items-center justify-center py-12">
              <Target className="w-16 h-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Ready to Optimize</h3>
              <p className="text-muted-foreground text-center max-w-md">
                Enter your income, expenses, and savings to get personalized optimization
                recommendations based on proven financial rules.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
