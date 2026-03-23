'use client';

import { Card } from '@/components/ui/Card';

interface CareerPathPanelProps {
  state: {
    job_title: string;
    current_salary: number;
    company_size: string;
    years_in_job: number;
    business_status?: string;
    has_mba?: boolean;
  };
}

const formatCurrency = (amount: number) => {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  return `₹${Math.round(amount).toLocaleString()}`;
};

export default function CareerPathPanel({ state }: CareerPathPanelProps) {
  const careerPath = ['Associate', 'Senior Associate', 'Manager', 'Senior Manager', 'Director', 'VP'];
  const currentIndex = Math.floor(state.years_in_job / 3);
  const nextPromotion = Math.ceil((state.years_in_job + 1) / 3) * 3;
  const replayMilestones = Array.from({ length: Math.max(1, currentIndex + 1) }).map((_, idx) => ({
    role: careerPath[Math.min(idx, careerPath.length - 1)],
    year: idx * 3,
    salary: state.current_salary * Math.max(0.45, 0.65 + idx * 0.12),
  }));

  return (
    <Card className="p-6 space-y-6">
      <h3 className="text-xl font-bold">Career Path</h3>

      {/* Current Role */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Current Position</p>
            <p className="text-2xl font-bold text-cyan-600">{state.job_title}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Tenure</p>
            <p className="text-2xl font-bold">{state.years_in_job} yrs</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <span className="px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full">
            {state.company_size === 'startup' ? '🚀 Startup' : state.company_size === 'medium' ? '📊 Mid-size' : '🏢 Large'}
          </span>
          {state.has_mba && (
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
              🎓 MBA
            </span>
          )}
          {state.business_status === 'active' && (
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full">
              💼 Business Owner
            </span>
          )}
        </div>
      </div>

      {/* Salary Information */}
      <div className="bg-gray-50 p-4 rounded-lg space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-gray-600">Annual Salary</p>
          <p className="text-xl font-bold text-green-600">{formatCurrency(state.current_salary)}</p>
        </div>
        <div className="flex items-center justify-between">
          <p className="text-gray-600">Monthly Income</p>
          <p className="text-lg font-semibold">{formatCurrency(state.current_salary / 12)}</p>
        </div>
      </div>

      {/* Career Progression Timeline */}
      <div className="space-y-3">
        <p className="text-sm font-semibold text-gray-700">Career Progression</p>
        <div className="space-y-2">
          {careerPath.map((role, idx) => (
            <div key={idx} className="flex items-center space-x-2">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${idx <= currentIndex ? 'bg-cyan-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                {idx + 1}
              </div>
              <span className={`text-sm ${idx <= currentIndex ? 'font-semibold text-gray-900' : 'text-gray-500'}`}>
                {role}
              </span>
              {idx === currentIndex && (
                <span className="ml-auto text-xs px-2 py-1 bg-cyan-100 text-cyan-700 rounded">
                  Current
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Next Steps */}
      <div className="border-t pt-4">
        <p className="text-sm text-gray-600">
          💡 Keep improving your skills and making good decisions. Next promotion in ~{Math.max(0, nextPromotion - state.years_in_job)} years.
        </p>
      </div>

      <div className="rounded-lg border border-cyan-200 bg-cyan-50 p-4 space-y-2">
        <p className="text-sm font-semibold text-cyan-900">Career Path Replay</p>
        <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
          {replayMilestones.map((m) => (
            <div key={`${m.role}-${m.year}`} className="flex items-center justify-between text-sm">
              <span className="text-gray-700">Year {m.year}: {m.role}</span>
              <span className="font-semibold text-cyan-700">{formatCurrency(m.salary)}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
