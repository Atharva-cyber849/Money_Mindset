'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface Option {
  action: string;
  description: string;
  consequence: string;
}

interface InterruptionModalProps {
  interruption: {
    month: number;
    age: number;
    type: string;
    description: string;
    options: Option[];
  };
  onResponse: (action: string) => void;
  disabled: boolean;
}

const EVENT_ICONS: Record<string, string> = {
  salary_increase: '💰',
  market_crash: '📉',
  emergency_withdrawal: '🚨',
  pause_sip: '⏸️',
  job_loss: '💼',
  bull_run: '🚀',
};

export default function InterruptionModal({
  interruption,
  onResponse,
  disabled,
}: InterruptionModalProps) {
  const icon = EVENT_ICONS[interruption.type] || '⚡';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="p-8 max-w-2xl w-full">
        <div className="text-center mb-6">
          <div className="text-6xl mb-4">{icon}</div>
          <h2 className="text-2xl font-bold mb-2">Life Interruption!</h2>
          <p className="text-lg text-gray-700 mb-4">{interruption.description}</p>
          <p className="text-xs text-gray-600">Age {interruption.age} · Month {interruption.month}</p>
        </div>

        {/* Options */}
        <div className="space-y-4 mb-6">
          {interruption.options.map((option, idx) => (
            <div key={idx} className="border-2 border-gray-200 rounded-lg p-4 hover:border-cyan-400 transition">
              <p className="font-semibold text-sm mb-2">{option.description}</p>
              <p className="text-xs text-gray-600">💡 {option.consequence}</p>
              <Button
                onClick={() => onResponse(option.action)}
                disabled={disabled}
                className="w-full mt-3 text-sm"
              >
                Choose: {option.action}
              </Button>
            </div>
          ))}
        </div>

        <p className="text-xs text-gray-500 text-center">
          Your decision will affect your wealth trajectory. Choose wisely!
        </p>
      </Card>
    </div>
  );
}
