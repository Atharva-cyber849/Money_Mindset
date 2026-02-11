"use client";

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ArrowRight, Brain, TrendingUp, Target, BarChart3, Sparkles } from 'lucide-react';
import Link from 'next/link';

const features = [
  {
    title: 'Expense Classification',
    description: 'Supervised learning categorizes expenses automatically',
    icon: Brain,
    color: 'text-yellow-600 bg-yellow-50',
    link: '/analytics/expense-classification',
    details: 'AI-powered categorization using machine learning to automatically classify your transactions with confidence scores.',
  },
  {
    title: 'Market Simulation',
    description: 'Historical data-based simulations visualize risk vs return',
    icon: TrendingUp,
    color: 'text-red-600 bg-red-50',
    link: '/analytics/market-simulation',
    details: 'Monte Carlo simulations based on historical market data to understand investment outcomes and probabilities.',
  },
  {
    title: 'Budget Optimization',
    description: 'Rule-based heuristics analyze savings and expense ratios',
    icon: Target,
    color: 'text-orange-600 bg-orange-50',
    link: '/analytics/budget-optimization',
    details: 'Get actionable recommendations using proven financial rules like the 50/30/20 guideline and industry benchmarks.',
  },
  {
    title: 'Forecasting Models',
    description: 'Time-series analysis predicts spending trends',
    icon: BarChart3,
    color: 'text-pink-600 bg-pink-50',
    link: '/analytics/forecasting',
    details: 'Predict future spending patterns using exponential smoothing and trend analysis with confidence intervals.',
  },
];

export default function AnalyticsPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="w-8 h-8 text-primary" />
          <h1 className="text-5xl font-bold">AI-Powered Analytics</h1>
        </div>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Advanced financial intelligence powered by machine learning, statistical analysis,
          and proven financial principles
        </p>
      </div>

      {/* Feature Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {features.map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <Card key={idx} hover className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${feature.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-2">{feature.title}</h3>
              <p className="text-base text-muted-foreground mb-3">
                {feature.description}
              </p>
              <p className="text-sm text-muted-foreground mb-4">{feature.details}</p>
              <Link href={feature.link}>
                <Button className="w-full group">
                  Try It Now
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </Card>
          );
        })}
      </div>

      {/* How It Works Section */}
      <Card className="bg-gradient-to-br from-primary/5 to-primary/10 p-8 mb-8">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold mb-2">How Our AI Analytics Work</h2>
          <p className="text-base text-muted-foreground">
            Combining multiple approaches for comprehensive financial insights
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
              <span className="text-2xl font-bold text-primary">1</span>
            </div>
            <h3 className="font-semibold mb-2">Data Collection</h3>
            <p className="text-sm text-muted-foreground">
              Your transactions, budgets, and financial goals provide the foundation
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
              <span className="text-2xl font-bold text-primary">2</span>
            </div>
            <h3 className="font-semibold mb-2">Analysis</h3>
            <p className="text-sm text-muted-foreground">
              ML models and statistical algorithms process your data
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
              <span className="text-2xl font-bold text-primary">3</span>
            </div>
            <h3 className="font-semibold mb-2">Insights</h3>
            <p className="text-sm text-muted-foreground">
              Generate predictions, classifications, and recommendations
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
              <span className="text-2xl font-bold text-primary">4</span>
            </div>
            <h3 className="font-semibold mb-2">Action</h3>
            <p className="text-sm text-muted-foreground">
              Take informed decisions based on data-driven guidance
            </p>
          </div>
        </div>
      </Card>

      {/* Info Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-bold mb-2">Accurate Predictions</h3>
          <p className="text-sm text-muted-foreground">
            Our models are trained on extensive financial data and validated against real-world
            outcomes to ensure reliability.
          </p>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-bold mb-2">Actionable Insights</h3>
          <p className="text-sm text-muted-foreground">
            Every analysis comes with clear recommendations and next steps you can implement
            immediately.
          </p>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-bold mb-2">Privacy First</h3>
          <p className="text-sm text-muted-foreground">
            Your financial data is encrypted and processed securely. We never share your
            information with third parties.
          </p>
        </Card>
      </div>
    </div>
  );
}
