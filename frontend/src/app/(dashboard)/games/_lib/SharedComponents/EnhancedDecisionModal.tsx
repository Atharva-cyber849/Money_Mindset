/**
 * EnhancedDecisionModal - Advanced decision interface with learning
 * Shows multiple options with consequences, risk levels, and educational content
 */

'use client';

import React, { useState } from 'react';
import { AlertCircle, Check, Zap, TrendingUp, Target, Lightbulb } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface DecisionOption {
  index: number;
  title: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high';
  consequences: Record<string, number>;
  monthly_impact?: number;
  months?: number;
  long_term_effect: string;
}

interface DecisionModalProps {
  title: string;
  description: string;
  event_type: string;
  options: DecisionOption[];
  onDecide: (optionIndex: number) => void;
  isLoading?: boolean;
}

const getDecisionTheme = (eventType: string) => {
  const themes: Record<string, { label: string; guidance: string }> = {
    portfolio_setup: {
      label: 'Asset Allocation',
      guidance: 'Match risk to your time horizon. A better portfolio is usually the one you can hold through volatility.',
    },
    market_crash: {
      label: 'Risk Management',
      guidance: 'Your goal is not perfect timing. Your goal is survival, liquidity, and the ability to buy quality assets when fear is high.',
    },
    salary_increase: {
      label: 'Opportunity Cost',
      guidance: 'A raise can build wealth or lifestyle inflation. The difference usually comes from what you do with the surplus cash flow.',
    },
    emergency_withdrawal: {
      label: 'Emergency Fund',
      guidance: 'Liquidity protects compounding. Cash reserves buy you time and better choices when life gets noisy.',
    },
    default: {
      label: 'Financial Literacy',
      guidance: 'Pause, compare downside, and prefer choices that preserve future options instead of only optimizing the next step.',
    },
  };

  return themes[eventType] || themes.default;
};

const getRiskColor = (level: string) => {
  switch (level) {
    case 'low':
      return 'bg-green-50 border-green-200 text-green-800';
    case 'medium':
      return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    case 'high':
      return 'bg-red-50 border-red-200 text-red-800';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
};

const getRiskIcon = (level: string) => {
  switch (level) {
    case 'low':
      return <Check className="w-4 h-4" />;
    case 'medium':
      return <Zap className="w-4 h-4" />;
    case 'high':
      return <AlertCircle className="w-4 h-4" />;
    default:
      return null;
  }
};

const ConsequenceItem: React.FC<{ label: string; amount: number }> = ({ label, amount }) => {
  const isPositive = amount >= 0;
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-gray-700">{label}</span>
      <span className={`font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? '+' : ''}₹{Math.abs(amount).toLocaleString()}
      </span>
    </div>
  );
};

const OptionCard: React.FC<{
  option: DecisionOption;
  isSelected: boolean;
  onSelect: (index: number) => void;
}> = ({ option, isSelected, onSelect }) => {
  return (
    <Card
      className={`p-4 cursor-pointer transition-all ${
        isSelected
          ? 'ring-2 ring-blue-500 shadow-lg'
          : 'hover:shadow-md hover:border-blue-300'
      }`}
      onClick={() => onSelect(option.index)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-bold text-gray-900">{option.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{option.description}</p>
        </div>
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full border ${getRiskColor(option.risk_level)}`}>
          {getRiskIcon(option.risk_level)}
          <span className="text-xs font-medium capitalize">{option.risk_level}</span>
        </div>
      </div>

      {/* Consequences */}
      <div className="bg-gray-50 rounded p-3 mb-3 space-y-2">
        <h5 className="text-xs font-semibold text-gray-700 uppercase">Immediate Impact</h5>
        {Object.entries(option.consequences || {}).map(([key, value]) => (
          <ConsequenceItem
            key={key}
            label={key.replace(/_/g, ' ').toUpperCase()}
            amount={value}
          />
        ))}
        {option.monthly_impact && (
          <div className="pt-2 border-t border-gray-300 flex items-center gap-2 text-xs text-orange-600">
            <TrendingUp className="w-3 h-3" />
            <span>₹{Math.abs(option.monthly_impact).toLocaleString()}/month × {option.months} months</span>
          </div>
        )}
      </div>

      {/* Long-term Effect */}
      {option.long_term_effect && (
        <div className="flex gap-2 p-2 bg-blue-50 rounded border border-blue-200">
          <Lightbulb className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-blue-900">{option.long_term_effect}</p>
        </div>
      )}

      {/* Selection Indicator */}
      {isSelected && (
        <div className="mt-3 flex items-center gap-2 text-blue-600 font-semibold">
          <Check className="w-4 h-4" />
          Selected
        </div>
      )}
    </Card>
  );
};

export const EnhancedDecisionModal: React.FC<DecisionModalProps> = ({
  title,
  description,
  event_type,
  options,
  onDecide,
  isLoading = false,
}) => {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const decisionTheme = getDecisionTheme(event_type);

  const handleDecide = () => {
    if (selectedOption !== null) {
      onDecide(selectedOption);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white">
          <h2 className="text-2xl font-bold">{title}</h2>
          <p className="text-blue-100 mt-2">{description}</p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Alert Box */}
          <div className="bg-amber-50 border-l-4 border-amber-500 p-4 flex gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-900">Decision Impact</p>
              <p className="text-sm text-amber-800 mt-1">
                Your choice will affect your finances and long-term wealth. Consider the immediate costs and future
                consequences before deciding.
              </p>
              <p className="text-xs text-amber-700 mt-2 font-semibold uppercase tracking-wide">
                {decisionTheme.label}
              </p>
            </div>
          </div>

          <Card className="bg-slate-50 border-slate-200 p-4">
            <div className="flex items-start gap-3">
              <Target className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-slate-900">How to think about it</h4>
                <p className="text-sm text-slate-700 mt-1">{decisionTheme.guidance}</p>
              </div>
            </div>
          </Card>

          {/* Options Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {options.map((option) => (
              <OptionCard
                key={option.index}
                option={option}
                isSelected={selectedOption === option.index}
                onSelect={setSelectedOption}
              />
            ))}
          </div>

          {/* Learning Section */}
          <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200 p-4">
            <div className="flex gap-3">
              <Lightbulb className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-purple-900">Financial Literacy Lesson</h4>
                <p className="text-sm text-purple-800 mt-2">
                  {getFinancialLesson(event_type, selectedOption !== null ? options[selectedOption] : null)}
                </p>
              </div>
            </div>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t">
            <Button
              variant="outline"
              disabled={isLoading}
              onClick={() => setSelectedOption(null)}
            >
              Clear Selection
            </Button>
            <Button
              disabled={selectedOption === null || isLoading}
              onClick={handleDecide}
            >
              {isLoading ? 'Processing...' : 'Confirm Decision'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

/**
 * Get contextual financial literacy lesson based on event type and decision
 */
function getFinancialLesson(eventType: string, _selectedOption: DecisionOption | null): string {
  const lessons: Record<string, string> = {
    car_accident:
      'This scenario teaches emergency management. Good financial planning means having an emergency fund to handle unexpected expenses without derailing your investments.',
    medical_emergency:
      'Health emergencies remind us why insurance is critical. A good insurance policy protects your wealth from unexpected medical costs.',
    job_loss_signal:
      'Job loss is a financial stress test. Maintaining an emergency fund (6 months of expenses) gives you options when income is uncertain.',
    education_expense:
      'Education is an investment in your future earning potential. Consider the ROI: does the course justify its cost relative to salary increase?',
    wedding:
      'Weddings are celebrations, but also major financial decisions. Balancing celebration with long-term wealth is key to financial maturity.',
    bonus:
      "Sudden windfalls test your discipline. Will you spend it immediately, or invest it for future wealth? Remember: investing ₹100K today could be ₹500K+ in 20 years.",
    market_crash:
      'Market crashes are inevitable. Those who stay invested during crashes get rewarded when markets recover. This is the real test of investment discipline.',
    salary_increase:
      'A salary increase is your chance to accelerate wealth building. Many people spend raises immediately (lifestyle inflation) instead of investing them.',
    default:
      'Every financial decision has tradeoffs. Consider both immediate comfort and long-term wealth.',
  };

  return lessons[eventType] || lessons.default;
}
