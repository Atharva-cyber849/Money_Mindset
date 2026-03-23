'use client';

import { Button } from '@/components/ui/Button';
import { Loader2, X } from 'lucide-react';

interface Decision {
  id: string;
  age: number;
  decision_type: string;
  description: string;
  options: Array<{
    id: number;
    text: string;
    salary_impact: number;
    happiness_impact: number;
    career_satisfaction_impact: number;
    wealth_impact: number;
  }>;
}

interface DecisionModalProps {
  decision: Decision;
  onChoose: (choiceIndex: number) => Promise<void>;
  isLoading: boolean;
}

const decisionEmojis: { [key: string]: string } = {
  career_path: '💼',
  mba_education: '🎓',
  relocation: '🌆',
  marriage: '💍',
  first_child: '👶',
  home_purchase: '🏠',
  job_change: '📊',
  business_startup: '🚀',
  investment_aggression: '📈',
  parent_support: '👴',
  retirement_timing: '🎉',
};

export default function DecisionModal({
  decision,
  onChoose,
  isLoading,
}: DecisionModalProps) {
  const emoji = decisionEmojis[decision.decision_type] || '🤔';

  const formatNumber = (num: number) => {
    if (num >= 0) return `+${num}`;
    return `${num}`;
  };

  const formatPercent = (num: number) => {
    const prefix = num >= 0 ? '+' : '';
    return `${prefix}${(Math.round(num * 100) / 100).toFixed(2)}%`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-600 to-cyan-700 text-white p-6 space-y-2">
          <div className="text-4xl mb-2">{emoji}</div>
          <h2 className="text-2xl font-bold">Important Decision Ahead</h2>
          <p className="text-cyan-100">Age {decision.age}</p>
        </div>

        {/* Decision Description */}
        <div className="p-6 bg-cyan-50 border-b border-cyan-200">
          <p className="text-lg text-gray-800">{decision.description}</p>
        </div>

        {/* Options */}
        <div className="p-6 space-y-4">
          <h3 className="font-semibold text-gray-900 mb-4">What will you do?</h3>

          {decision.options.map((option, idx) => (
            <div key={idx} className="space-y-3">
              <button
                onClick={() => onChoose(idx)}
                disabled={isLoading}
                className="w-full text-left p-4 border-2 border-gray-300 rounded-lg hover:border-cyan-500 hover:bg-cyan-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="font-semibold text-lg text-gray-900 mb-3">
                  {option.text}
                </div>

                {/* Impact Preview */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  {option.salary_impact !== 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Salary:</span>
                      <span
                        className={
                          option.salary_impact > 0 ? 'text-green-600 font-semibold' : 'text-red-600'
                        }
                      >
                        {formatPercent(option.salary_impact)}
                      </span>
                    </div>
                  )}

                  {option.career_satisfaction_impact !== 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Career:</span>
                      <span
                        className={
                          option.career_satisfaction_impact > 0
                            ? 'text-green-600 font-semibold'
                            : 'text-red-600'
                        }
                      >
                        {formatNumber(option.career_satisfaction_impact)}
                      </span>
                    </div>
                  )}

                  {option.happiness_impact !== 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Happiness:</span>
                      <span
                        className={
                          option.happiness_impact > 0
                            ? 'text-green-600 font-semibold'
                            : 'text-red-600'
                        }
                      >
                        {formatNumber(option.happiness_impact)}
                      </span>
                    </div>
                  )}

                  {option.wealth_impact !== 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Wealth:</span>
                      <span
                        className={
                          option.wealth_impact > 0
                            ? 'text-green-600 font-semibold'
                            : 'text-red-600'
                        }
                      >
                        {formatNumber(option.wealth_impact)}
                      </span>
                    </div>
                  )}
                </div>
              </button>

              {isLoading && (
                <div className="flex items-center justify-center p-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Note */}
        <div className="p-6 bg-gray-50 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            💡 Each decision affects your future opportunities and outcomes. Think carefully about the long-term consequences.
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Better trade-offs usually balance salary, happiness, and optionality instead of maximizing only one metric.
          </p>
        </div>
      </div>
    </div>
  );
}
