"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Pill';
import { analyzeBudget } from '@/lib/api/analytics';
import { Loader2, AlertTriangle, CheckCircle, TrendingUp, Target, Wallet, PiggyBank, Zap, DollarSign, BarChart3, Lightbulb } from 'lucide-react';
import { BudgetBreakdownDonut, CircularHealthScore, StatisticsPulse, InsightCard, ExplanationCard, HowItWorks, ExampleShowcase, ConceptInfographic } from '@/components/analytics';

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
    if (score >= 75) return 'text-cyan-600';
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

      {/* Educational Infographics Section */}
      <div className="mb-12 space-y-6">
        {/* Explanation */}
        <ExplanationCard
          icon={Target}
          title="What is Budget Optimization?"
          description="The 50/30/20 rule is a proven budgeting framework that helps you allocate income across three categories: needs, wants, and savings. Our AI analyzes your spending to show how well you're aligned with this proven financial strategy."
          keyPoints={[
            '50% of income should go to needs (housing, food, utilities)',
            '30% should go to wants (entertainment, dining, hobbies)',
            '20% should go to savings and debt repayment',
            'Helps identify overspending areas and savings opportunities',
          ]}
          color="teal"
          example="If you earn $5,000/month: $2,500 needs, $1,500 wants, $1,000 savings"
        />

        {/* How It Works */}
        <HowItWorks
          title="How Budget Analysis Works"
          steps={[
            {
              number: 1,
              title: 'Enter Your Income & Expenses',
              description: 'Input your monthly income and breakdown your expenses by category (housing, food, entertainment, etc.)',
              icon: DollarSign,
            },
            {
              number: 2,
              title: 'AI Categorizes Your Spending',
              description: 'Our algorithm automatically categorizes your expenses into Needs (50%), Wants (30%), and Savings (20%)',
              icon: BarChart3,
            },
            {
              number: 3,
              title: 'Health Score Analysis',
              description: 'We calculate your Budget Health Score (0-100) based on how well you follow the 50/30/20 rule',
              icon: Target,
            },
            {
              number: 4,
              title: 'Get Recommendations',
              description: 'Receive personalized recommendations to optimize your budget and increase savings potential',
              icon: Lightbulb,
            },
          ]}
          color="teal"
        />

        {/* Visual Concept */}
        <ConceptInfographic
          title="The 50/30/20 Budget Rule Explained"
          subtitle="How your ideal budget should be allocated"
          type="50-30-20"
          segments={[
            {
              label: 'Needs',
              percentage: 50,
              color: '#0891B2',
              description: 'Essential expenses',
            },
            {
              label: 'Wants',
              percentage: 30,
              color: '#8B5CF6',
              description: 'Lifestyle choices',
            },
            {
              label: 'Savings',
              percentage: 20,
              color: '#10B981',
              description: 'Financial security',
            },
          ]}
        />

        {/* Example */}
        <ExampleShowcase
          title="Budget Optimization Example"
          description="See how our analysis helps you understand your spending"
          inputExample={[
            { label: 'Monthly Income', value: '$5,000', highlight: true },
            { label: 'Housing Expenses', value: '$1,250' },
            { label: 'Food & Groceries', value: '$400' },
            { label: 'Entertainment', value: '$400' },
            { label: 'Current Savings', value: '$800' },
          ]}
          outputExample={[
            {
              label: 'Health Score',
              value: '78/100',
              highlight: true,
            },
            { label: 'Needs Allocation', value: '52%' },
            { label: 'Savings Rate', value: '18%' },
            {
              label: 'Optimization Potential',
              value: '+$200/month',
              highlight: true,
            },
          ]}
          color="teal"
        />
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
            {/* Health Score - Circular Visualization */}
            <CircularHealthScore
              score={result.health_score.score}
              rating={result.health_score.rating}
              factors={result.health_score.factors}
            />

            {/* Budget Breakdown Donut */}
            <BudgetBreakdownDonut
              budget_breakdown={{ needs: 50, wants: 30, savings: 20 }}
              actual={{
                needs: result.fifty_thirty_twenty.needs?.percentage || 0,
                wants: result.fifty_thirty_twenty.wants?.percentage || 0,
                savings: result.fifty_thirty_twenty.savings?.percentage || 0,
              }}
              compliance={result.fifty_thirty_twenty.overall_compliance?.compliance == true}
            />

            {/* Key Statistics */}
            <StatisticsPulse
              stats={[
                {
                  label: 'Savings Rate',
                  value: result.health_score.factors.savings_rate,
                  icon: PiggyBank,
                  color: 'green',
                },
                {
                  label: 'Current Score',
                  value: result.health_score.score,
                  icon: Target,
                  color: 'teal',
                },
                {
                  label: 'Monthly Income',
                  value: parseFloat(income) || 0,
                  icon: TrendingUp,
                  color: 'cyan',
                },
                {
                  label: 'Monthly Savings',
                  value: parseFloat(savings) || 0,
                  icon: Wallet,
                  color: 'purple',
                },
              ]}
            />

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Optimization Recommendations</h3>
                <div className="space-y-3">
                  {result.recommendations.map((rec: any, idx: number) => (
                    <InsightCard
                      key={idx}
                      icon={rec.priority === 'high' ? AlertTriangle : CheckCircle}
                      title={rec.issue}
                      description={rec.suggestion}
                      color={rec.priority === 'high' ? 'red' : rec.priority === 'medium' ? 'yellow' : 'green'}
                    />
                  ))}
                </div>
              </Card>
            )}

            {/* Optimization Potential */}
            {result.optimization_potential && (
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Optimization Potential</h3>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-2xl font-bold text-green-600">
                      ${result.optimization_potential.potential_additional_savings.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      Potential Monthly Savings
                    </div>
                  </div>
                  <div className="text-center p-4 bg-cyan-50 rounded-lg border border-cyan-200">
                    <div className="text-2xl font-bold text-cyan-600">
                      {result.optimization_potential.potential_savings_rate}%
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      Potential Savings Rate
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-4">
                  By optimizing expenses to recommended levels, you could increase your savings
                  rate by {result.optimization_potential.improvement}%.
                </p>
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
