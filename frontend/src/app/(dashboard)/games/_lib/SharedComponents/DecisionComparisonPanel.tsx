/**
 * DecisionComparisonPanel - Shows side-by-side outcomes of different decisions
 * Educational tool to understand consequences of financial choices
 */

'use client';

import React from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { Card } from '@/components/ui/Card';

interface MetricComparison {
  label: string;
  units: string;
  choices: Array<{
    name: string;
    value: number;
    isOptimal: boolean;
  }>;
}

interface DecisionOutcome {
  option_name: string;
  immediate_impact: number;
  long_term_impact: number;
  wealth_at_end: number;
  health_score: number;
  stress_level: number;
}

interface DecisionComparisonPanelProps {
  decision_title: string;
  outcomes: Record<string, DecisionOutcome>;
  metrics: MetricComparison[];
  lesson?: string;
}

const formatCurrency = (amount: number): string => {
  if (Math.abs(amount) >= 10000000) {
    return `₹${(amount / 10000000).toFixed(1)}Cr`;
  }
  if (Math.abs(amount) >= 100000) {
    return `₹${(amount / 100000).toFixed(1)}L`;
  }
  if (Math.abs(amount) >= 1000) {
    return `₹${(amount / 1000).toFixed(1)}K`;
  }
  return `₹${amount.toFixed(0)}`;
};

const OutcomeCard: React.FC<{
  option_name: string;
  outcome: DecisionOutcome;
  is_optimal: boolean;
}> = ({ option_name, outcome, is_optimal }) => {
  return (
    <Card className={`p-4 ${is_optimal ? 'ring-2 ring-green-500 shadow-lg' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <h3 className="font-bold text-lg text-gray-900">{option_name}</h3>
        {is_optimal && (
          <div className="flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-semibold">
            <CheckCircle className="w-4 h-4" />
            Best Choice
          </div>
        )}
      </div>

      <div className="space-y-4">
        {/* Immediate Impact */}
        <div>
          <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Immediate Impact</p>
          <p className={`text-2xl font-bold ${outcome.immediate_impact > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {outcome.immediate_impact > 0 ? '+' : ''}{formatCurrency(outcome.immediate_impact)}
          </p>
        </div>

        {/* Long-term Impact */}
        <div>
          <p className="text-xs font-semibold text-gray-600 uppercase mb-2">10-Year Wealth Impact</p>
          <p className={`text-2xl font-bold ${outcome.long_term_impact > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {outcome.long_term_impact > 0 ? '+' : ''}{formatCurrency(outcome.long_term_impact)}
          </p>
        </div>

        {/* Final Wealth */}
        <div className="bg-gray-50 p-3 rounded">
          <p className="text-xs font-semibold text-gray-600 mb-1">Projected Wealth at Goal Age</p>
          <p className="text-xl font-bold text-gray-900">{formatCurrency(outcome.wealth_at_end)}</p>
        </div>

        {/* Quality of Life Metrics */}
        <div className="space-y-3">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-xs font-medium text-gray-700">Financial Health</span>
              <span className="text-xs font-bold text-gray-700">{outcome.health_score.toFixed(0)}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{ width: `${outcome.health_score}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="text-xs font-medium text-gray-700">Stress Level</span>
              <span className="text-xs font-bold text-gray-700">{outcome.stress_level.toFixed(0)}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="h-full bg-orange-500 rounded-full"
                style={{ width: `${outcome.stress_level}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export const DecisionComparisonPanel: React.FC<DecisionComparisonPanelProps> = ({
  decision_title,
  outcomes,
  metrics,
  lesson,
}) => {
  // Find optimal choice (highest wealth_at_end)
  const optimalOption = Object.entries(outcomes).reduce((a, b) =>
    a[1].wealth_at_end > b[1].wealth_at_end ? a : b
  )[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{decision_title} - Outcome Comparison</h2>
        <p className="text-gray-600 mt-2">See how each decision affects your financial journey</p>
      </div>

      {/* Learning Lesson */}
      {lesson && (
        <Card className="bg-blue-50 border-blue-200 p-4">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900">Key Learning</h3>
              <p className="text-sm text-blue-800 mt-2">{lesson}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Outcome Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(outcomes).map(([optionName, outcome]) => (
          <OutcomeCard
            key={optionName}
            option_name={optionName}
            outcome={outcome}
            is_optimal={optionName === optimalOption}
          />
        ))}
      </div>

      {/* Metrics Comparison */}
      {metrics.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Detailed Metrics</h3>
          <div className="space-y-8">
            {metrics.map((metric) => (
              <div key={metric.label}>
                <h4 className="font-semibold text-gray-900 mb-3">{metric.label}</h4>
                <div className="space-y-3">
                  {metric.choices.map((choice) => (
                    <div key={choice.name} className="flex justify-between items-center">
                      <span className={`text-sm ${choice.isOptimal ? 'font-bold' : ''}`}>{choice.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{choice.value.toFixed(1)}</span>
                        {choice.isOptimal && <CheckCircle className="w-4 h-4 text-green-600" />}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Summary Insight */}
      <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200 p-6">
        <h3 className="font-bold text-gray-900 mb-3">💡 The Impact of Discipline</h3>
        <p className="text-sm text-gray-700">
          The difference between the best and worst choice in this scenario could be{' '}
          <span className="font-bold text-purple-600">
            {formatCurrency(
              Math.max(...Object.values(outcomes).map((o) => o.wealth_at_end)) -
                Math.min(...Object.values(outcomes).map((o) => o.wealth_at_end))
            )}
          </span>{' '}
          at retirement. This shows how financial discipline in your 20s and 30s creates compounding effects by your
          60s.
        </p>
      </Card>
    </div>
  );
};
