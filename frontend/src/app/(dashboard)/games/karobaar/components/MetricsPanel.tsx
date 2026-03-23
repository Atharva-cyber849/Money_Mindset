'use client';

import { Card } from '@/components/ui/Card';
import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer } from 'recharts';

interface MetricsPanelProps {
  state: {
    career_satisfaction: number;
    family_happiness: number;
    work_life_balance: number;
    health_score: number;
  };
}

interface MetricProps {
  label: string;
  value: number;
  emoji: string;
  barColor: string;
  description: string;
}

function MetricBar({ label, value, emoji, barColor, description }: MetricProps) {
  const getStatus = (val: number) => {
    if (val >= 80) return 'Excellent';
    if (val >= 60) return 'Good';
    if (val >= 40) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{emoji}</span>
          <div>
            <p className="font-semibold">{label}</p>
            <p className="text-xs text-gray-500">{getStatus(value)}</p>
          </div>
        </div>
        <p className="text-2xl font-bold text-gray-900">{Math.round(value)}</p>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full transition-all ${barColor}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>

      <p className="text-xs text-gray-600">{description}</p>
    </div>
  );
}

export default function MetricsPanel({ state }: MetricsPanelProps) {
  // Calculate overall scores
  const careerScore = state.career_satisfaction;
  const financialScore = 70; // Would come from state, hardcoded for now
  const happinessScore = (state.family_happiness + state.work_life_balance + state.health_score) / 3;

  const overallScore = careerScore * 0.35 + financialScore * 0.40 + happinessScore * 0.25;
  const radarData = [
    { metric: 'Career', score: careerScore },
    { metric: 'Finance', score: financialScore },
    { metric: 'Family', score: state.family_happiness },
    { metric: 'Balance', score: state.work_life_balance },
    { metric: 'Health', score: state.health_score },
  ];

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <Card className="p-6 bg-gradient-to-br from-cyan-500 to-cyan-600 text-white space-y-3">
        <h3 className="font-semibold text-lg">Life Score</h3>
        <div className="text-5xl font-bold">{Math.round(overallScore)}</div>
        <div className="text-cyan-100">
          <p className="text-sm">Overall well-being index</p>
          <p className="text-xs mt-1">
            Based on career, finances & happiness
          </p>
        </div>
      </Card>

      {/* Individual Metrics */}
      <Card className="p-6 space-y-6">
        <h3 className="font-semibold text-lg">Life Dimensions</h3>

        <MetricBar
          label="Career Satisfaction"
          value={careerScore}
          emoji="💼"
          barColor="bg-cyan-600"
          description="Job satisfaction and career growth"
        />

        <MetricBar
          label="Financial Health"
          value={financialScore}
          emoji="💰"
          barColor="bg-green-600"
          description="Net worth and financial stability"
        />

        <MetricBar
          label="Happiness Index"
          value={happinessScore}
          emoji="😊"
          barColor="bg-purple-600"
          description="Family, balance, and health combined"
        />

        <MetricBar
          label="Work-Life Balance"
          value={state.work_life_balance}
          emoji="⚖️"
          barColor="bg-amber-600"
          description="Time for family and personal pursuits"
        />

        <MetricBar
          label="Health Score"
          value={state.health_score}
          emoji="🏥"
          barColor="bg-red-600"
          description="Physical and mental well-being"
        />
      </Card>

      <Card className="p-6 space-y-4">
        <div>
          <h3 className="font-semibold text-lg">Life Radar</h3>
          <p className="text-xs text-gray-600">Balanced progress across dimensions is more durable than one-dimensional growth.</p>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#0891b2"
              fill="#06b6d4"
              fillOpacity={0.5}
            />
          </RadarChart>
        </ResponsiveContainer>
      </Card>

      {/* Tips Card */}
      <Card className="p-4 bg-cyan-50 border border-cyan-200 space-y-2">
        <p className="font-semibold text-sm">💡 Pro Tip</p>
        <p className="text-sm text-gray-700">
          Balance all three dimensions. A high career score but low happiness indicates burnout.
        </p>
      </Card>
    </div>
  );
}
