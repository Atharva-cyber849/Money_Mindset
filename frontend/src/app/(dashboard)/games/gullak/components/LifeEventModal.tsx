'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface LifeEventModalProps {
  event: {
    month: number;
    type: string;
    description: string;
    impact_amount: number;
  };
  onClose: () => void;
}

const EVENT_ICONS: Record<string, string> = {
  medical_emergency: '🏥',
  job_loss_signal: '💼',
  wedding: '💒',
  bonus: '💰',
  market_correction: '📉',
  demonetization: '🪙',
  salary_increase: '📈',
  car_accident: '🚗',
  education_expense: '📚',
  home_repair: '🏠',
  festival_bonus: '🎉',
  inflation_spike: '📊',
};

const EVENT_SEVERITY: Record<string, 'high' | 'medium' | 'low'> = {
  medical_emergency: 'high',
  job_loss_signal: 'high',
  wedding: 'high',
  bonus: 'low',
  market_correction: 'medium',
  demonetization: 'high',
  salary_increase: 'low',
  car_accident: 'medium',
  education_expense: 'medium',
  home_repair: 'medium',
  festival_bonus: 'low',
  inflation_spike: 'medium',
};

const SEVERITY_COLORS = {
  high: 'bg-red-100 border-red-300',
  medium: 'bg-yellow-100 border-yellow-300',
  low: 'bg-green-100 border-green-300',
};

export default function LifeEventModal({ event, onClose }: LifeEventModalProps) {
  const severity = EVENT_SEVERITY[event.type] || 'medium';
  const icon = EVENT_ICONS[event.type] || '⚡';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className={`p-8 max-w-md ${SEVERITY_COLORS[severity]} border-2`}>
        <div className="text-center">
          <div className="text-6xl mb-4">{icon}</div>

          <h2 className="text-2xl font-bold mb-2">Life Event!</h2>
          <p className="text-gray-700 mb-6">{event.description}</p>

          <div className="bg-white rounded p-4 mb-6">
            <p className="text-sm text-gray-600">Financial Impact</p>
            <p className="text-2xl font-bold text-red-600">
              ₹{event.impact_amount.toLocaleString()}
            </p>
          </div>

          <div className="bg-white rounded p-4 mb-6 text-left">
            <h3 className="font-semibold mb-2">How Your Jars Help:</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              {event.type === 'medical_emergency' && (
                <>
                  <li>✓ Insurance jar covers 70% of medical costs</li>
                  <li>✓ Short-term jar fills the remaining gap</li>
                  <li>✓ This is why emergency planning matters</li>
                </>
              )}
              {event.type === 'wedding' && (
                <>
                  <li>✓ Short-term jar was built for this occasion</li>
                  <li>✓ Long-term jar can support if needed</li>
                  <li>✓ Plan ahead for predictable life events</li>
                </>
              )}
              {event.type === 'job_loss_signal' && (
                <>
                  <li>⚠️ Emergency fund becomes critical now</li>
                  <li>⚠️ Reduce spending, preserve cash</li>
                  <li>✓ This is why 6 months buffer matters</li>
                </>
              )}
              {event.type === 'market_correction' && (
                <>
                  <li>📉 Long-term investments declined</li>
                  <li>💡 This is normal - stay invested!</li>
                  <li>🎯 Your SIP keeps buying at lower prices</li>
                </>
              )}
              {event.type === 'demonetization' && (
                <>
                  <li>🪙 Cash in emergency jar devalued</li>
                  <li>✓ Digital savings unaffected</li>
                  <li>💡 Keep some emergency fund digital</li>
                </>
              )}
              {(event.type === 'bonus' || event.type === 'salary_increase') && (
                <>
                  <li>💰 Great news! Additional income</li>
                  <li>✓ Allocate across jars as planned</li>
                  <li>🎯 Let growth compound over time</li>
                </>
              )}
            </ul>
          </div>

          <Button onClick={onClose} className="w-full py-2 text-lg">
            Continue Playing
          </Button>
        </div>
      </Card>
    </div>
  );
}
