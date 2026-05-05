/**
 * FinancialLiteracyCard - Educational overlay for teaching financial concepts during gameplay
 * Shows real-world implications and connections to financial principles
 */

'use client';

import React from 'react';
import { Lightbulb, BookOpen, TrendingUp, BarChart3, PieChart, Target, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/Card';

export type LiteracyConceptType =
  | 'compound_interest'
  | 'diversification'
  | 'emergency_fund'
  | 'risk_management'
  | 'inflation'
  | 'tax_efficiency'
  | 'dollar_cost_averaging'
  | 'asset_allocation'
  | 'opportunity_cost'
  | 'life_insurance';

interface FinancialLiteracyCardProps {
  concept: LiteracyConceptType;
  context?: string;
  impact_amount?: number;
  impact_percentage?: number;
  example?: string;
}

const conceptData: Record<LiteracyConceptType, { title: string; description: string; key_points: string[]; action_tip: string }> = {
  compound_interest: {
    title: 'Power of Compound Interest',
    description:
      'Your money grows on your money. Interest earned reinvests to generate even more interest - like a snowball rolling downhill, getting bigger with each turn.',
    key_points: [
      'Doubling time: ₹100 at 10% annual return doubles every 7.2 years',
      'Starting early matters most: ₹100 invested at age 25 is worth more than ₹10,000 invested at age 45',
      'Interruptions are costly: A 5-year pause in investing costs 30-40% of final wealth',
    ],
    action_tip: 'Automate your investments so compounding works without constant willpower.',
  },
  diversification: {
    title: 'Don\'t Put All Eggs in One Basket',
    description:
      'Spreading investments across different asset classes reduces risk. When one sector crashes, others may be stable or growing.',
    key_points: [
      'Portfolio with 5+ sectors has 70% less volatility than single stock',
      'Correlation matters: Stocks + bonds + gold don\'t move together',
      'Rebalancing forces you to "buy low, sell high" automatically',
    ],
    action_tip: 'Use a mix of asset classes so one bad year doesn\'t reset your entire plan.',
  },
  emergency_fund: {
    title: 'Emergency Fund: Your Financial Airbag',
    description:
      'Unexpected expenses happen. An emergency fund lets you handle crises without derailing your long-term investments or taking expensive loans.',
    key_points: [
      'Target: 6 months of living expenses, kept in liquid savings',
      'Without it: A ₹100K emergency can force you to withdraw ₹500K from investments (5+ year cost)',
      'Psychological benefit: Reduces financial stress and sleep-interrupting anxiety',
    ],
    action_tip: 'Keep emergency money separate and easy to access, not in volatile assets.',
  },
  risk_management: {
    title: 'Risk Management - The Foundation',
    description:
      'Understand the risks you\'re taking and have plans to handle them. Insurance, diversification, and emergency funds are your tools.',
    key_points: [
      'Insurable risks (health, life, property): Transfer to insurance companies',
      'Market risks: Diversify across sectors and geographies',
      'Personal risks (job loss): Build emergency fund',
    ],
    action_tip: 'Protect the downside first, then chase returns with the remainder.',
  },
  inflation: {
    title: 'Inflation Erodes Your Purchasing Power',
    description:
      'Inflation means ₹100 today might only buy ₹80 worth of goods in 10 years. You need growth to stay ahead of inflation.',
    key_points: [
      'Historical Indian inflation: 4-6% annually',
      'Keeping money in savings account (3-4% returns) = losing 1-3% annually to inflation',
      'Equity investments (10%+ returns) beat inflation with 6%+ real growth',
    ],
    action_tip: 'Hold enough growth assets to keep your real purchasing power intact.',
  },
  tax_efficiency: {
    title: 'Reduce Taxes Legally',
    description:
      'Different investments have different tax treatments. ELSS, EPF, and tax-loss harvesting can save 10-30% more wealth.',
    key_points: [
      'ELSS: ₹1.5L can save ₹45,900 in taxes (30% of investment) + growth',
      'EPF: ₹150K annual contribution saves ₹45,000+ while building wealth',
      'Tax-loss harvesting: Sell losing positions to offset gains',
    ],
    action_tip: 'Choose the same return after tax, not just the highest headline return.',
  },
  dollar_cost_averaging: {
    title: 'Regular Investments Beat Timing',
    description:
      'Investing fixed amounts regularly (like SIPs) buys more units when prices are low and fewer when prices are high - a simple but powerful strategy.',
    key_points: [
      'SIP ₹10K/month beats lump-sum investing once yearly - 20%+ advantage over time',
      'Market timing fails: Most professionals can\'t time the market',
      'Removes emotion: No need to guess when to buy or sell',
    ],
    action_tip: 'Invest on schedule so market noise does not control your decisions.',
  },
  asset_allocation: {
    title: 'Asset Allocation: Your Wealth Blueprint',
    description:
      'Your mix of stocks, bonds, gold, and cash should match your age, goals, and risk tolerance. It determines 90% of your returns.',
    key_points: [
      'Age 25: 80% stocks, 15% bonds, 5% gold = growth-focused',
      'Age 45: 60% stocks, 25% bonds, 15% gold = balanced',
      'Age 60: 30% stocks, 40% bonds, 30% gold = preservation-focused',
    ],
    action_tip: 'Revisit allocation when goals change, not only when markets move.',
  },
  opportunity_cost: {
    title: 'Opportunity Cost: What You Gave Up',
    description:
      'When you choose one thing, you give up another. ₹1 not invested today is ₹10 given up in 20 years (at 10% returns).',
    key_points: [
      'Taking a ₹1L consumer loan = losing ₹500K+ in wealth gains over 20 years',
      'Delaying a ₹100K investment for 5 years costs ₹160K in compounding',
      'Every financial decision has a long-term cost',
    ],
    action_tip: 'Before spending, compare the future value of investing the same amount.',
  },
  life_insurance: {
    title: 'Life Insurance: Protecting Your Family\'s Future',
    description:
      'Term insurance is cheap and covers your family\'s financial needs if you pass away. It\'s not an investment - it\'s protection.',
    key_points: [
      '₹50L coverage costs only ₹500-800/year for a 30-year-old',
      'Liabilities: Home loan, children\'s education, spouse\'s 20-year expenses',
      'Protects your family from financial ruin while you build wealth',
    ],
    action_tip: 'Insure income first if dependents rely on it.',
  },
};

const getConceptIcon = (concept: LiteracyConceptType) => {
  const icons: Record<LiteracyConceptType, React.ReactNode> = {
    compound_interest: <TrendingUp className="w-5 h-5" />,
    diversification: <PieChart className="w-5 h-5" />,
    emergency_fund: <AlertCircle className="w-5 h-5" />,
    risk_management: <BarChart3 className="w-5 h-5" />,
    inflation: <TrendingUp className="w-5 h-5" />,
    tax_efficiency: <Target className="w-5 h-5" />,
    dollar_cost_averaging: <BookOpen className="w-5 h-5" />,
    asset_allocation: <PieChart className="w-5 h-5" />,
    opportunity_cost: <Lightbulb className="w-5 h-5" />,
    life_insurance: <AlertCircle className="w-5 h-5" />,
  };
  return icons[concept];
};

const getConceptColor = (concept: LiteracyConceptType) => {
  const colors: Record<LiteracyConceptType, string> = {
    compound_interest: 'from-green-50 to-emerald-50 text-green-700 border-green-200',
    diversification: 'from-blue-50 to-cyan-50 text-blue-700 border-blue-200',
    emergency_fund: 'from-red-50 to-rose-50 text-red-700 border-red-200',
    risk_management: 'from-purple-50 to-pink-50 text-purple-700 border-purple-200',
    inflation: 'from-orange-50 to-amber-50 text-orange-700 border-orange-200',
    tax_efficiency: 'from-yellow-50 to-lime-50 text-yellow-700 border-yellow-200',
    dollar_cost_averaging: 'from-indigo-50 to-blue-50 text-indigo-700 border-indigo-200',
    asset_allocation: 'from-teal-50 to-cyan-50 text-teal-700 border-teal-200',
    opportunity_cost: 'from-pink-50 to-red-50 text-pink-700 border-pink-200',
    life_insurance: 'from-violet-50 to-purple-50 text-violet-700 border-violet-200',
  };
  return colors[concept];
};

export const FinancialLiteracyCard: React.FC<FinancialLiteracyCardProps> = ({
  concept,
  context,
  impact_amount,
  impact_percentage,
  example,
}) => {
  const data = conceptData[concept];
  const colorClass = getConceptColor(concept);
  const icon = getConceptIcon(concept);
  const impactMagnitude = Math.abs(Number(impact_amount || 0));
  const impactDirection = Number(impact_amount || 0) >= 0 ? 'positive' : 'negative';

  return (
    <Card
      className={`bg-gradient-to-br ${colorClass} border-2 p-6 space-y-4`}
    >
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-1">{icon}</div>
        <div className="flex-1">
          <h3 className="text-lg font-bold">{data.title}</h3>
          {context && <p className="text-sm opacity-90 mt-1">{context}</p>}
        </div>
      </div>

      {/* Main Description */}
      <p className="text-sm leading-relaxed">{data.description}</p>

      <div className="bg-white bg-opacity-60 rounded p-3 space-y-1">
        <p className="text-xs font-semibold opacity-75 uppercase">Actionable Rule</p>
        <p className="text-sm font-medium">{data.action_tip}</p>
      </div>

      {/* Impact Display */}
      {(impact_amount !== undefined || impact_percentage !== undefined) && (
        <div className="bg-white bg-opacity-60 rounded p-3 space-y-1">
          <p className="text-xs font-semibold opacity-75 uppercase">Impact in This Decision</p>
          {impact_amount !== undefined && (
            <p className={`text-lg font-bold ${impactDirection === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
              {impact_amount > 0 ? '+' : ''}₹{impactMagnitude.toLocaleString()}
            </p>
          )}
          {impact_percentage !== undefined && (
            <p className="text-sm font-semibold opacity-90">{impact_percentage > 0 ? '+' : ''}{impact_percentage.toFixed(1)}% impact</p>
          )}
        </div>
      )}

      {/* Key Points */}
      <div className="space-y-2">
        <p className="text-xs font-semibold opacity-75 uppercase">Key Takeaways</p>
        <ul className="space-y-2">
          {data.key_points.map((point, idx) => (
            <li key={idx} className="text-sm flex gap-2">
              <span className="font-bold opacity-75">•</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Example */}
      {example && (
        <div className="bg-white bg-opacity-40 rounded p-3 text-sm italic">
          <span className="font-semibold">Example: </span>
          {example}
        </div>
      )}

      {/* Action Prompt */}
      <div className="text-xs opacity-75 border-t border-current pt-3 mt-3">
        💡 <span className="font-semibold">Think about:</span> How does this concept apply to your financial decisions?
      </div>
    </Card>
  );
};

/**
 * Get relevant literacy concept based on game event
 */
export function getRelevantConcept(eventType: string): LiteracyConceptType {
  const mapping: Record<string, LiteracyConceptType> = {
    market_crash: 'diversification',
    emergency_withdrawal: 'emergency_fund',
    salary_increase: 'opportunity_cost',
    market_crash_sip: 'dollar_cost_averaging',
    portfolio_setup: 'asset_allocation',
    job_loss: 'risk_management',
    inflation_alert: 'inflation',
    tax_planning: 'tax_efficiency',
    insurance_decision: 'life_insurance',
    compound_growth: 'compound_interest',
    default: 'compound_interest',
  };

  return mapping[eventType] || mapping.default;
}
