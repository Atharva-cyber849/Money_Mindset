'use client';

import { Card } from '@/components/ui/Card';

interface GameHeaderProps {
  title: string;
  gameMonth: number;
  totalMonths: number;
  description?: string;
}

export default function GameHeader({
  title,
  gameMonth,
  totalMonths,
  description,
}: GameHeaderProps) {
  const safeGameMonth = Number.isFinite(gameMonth) ? gameMonth : 0;
  const safeTotalMonths = Number.isFinite(totalMonths) && totalMonths > 0 ? totalMonths : 12;
  const progress = Math.min(100, Math.max(0, (safeGameMonth / safeTotalMonths) * 100));
  const yearsComplete = safeGameMonth / 12;
  const yearsTotal = safeTotalMonths / 12;
  const currentYearOfLife = 22 + Math.floor(yearsComplete);

  return (
    <Card className="p-6 bg-gradient-to-r from-blue-50 to-cyan-50">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">{title}</h1>
          {description && (
            <p className="text-gray-600">{description}</p>
          )}
        </div>
        <div className="text-right">
          <p className="text-4xl font-bold text-indigo-600">
            {yearsComplete.toFixed(1)}y / {yearsTotal}y
          </p>
          <p className="text-sm text-gray-600">Year {currentYearOfLife} of life</p>
        </div>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className="bg-gradient-to-r from-cyan-500 to-indigo-600 h-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex justify-between text-sm text-gray-600 mt-2">
        <span>Start (Age 22)</span>
        <span>{Math.round(progress)}% Complete</span>
        <span>Retirement (Age 32)</span>
      </div>

      <div className="mt-4 p-3 bg-cyan-100 text-cyan-900 rounded text-sm">
        <p>
          Month {safeGameMonth + 1} of {safeTotalMonths} • Focus on cash flow, resilience, and long-term wealth
        </p>
      </div>
    </Card>
  );
}
