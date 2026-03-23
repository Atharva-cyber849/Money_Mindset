'use client';

import { motion } from 'framer-motion';
import { useMemo } from 'react';

interface MetricGaugeProps {
  value: number;
  max?: number;
  title: string;
  unit?: string;
  color?: 'blue' | 'green' | 'amber' | 'red' | 'cyan';
  size?: 'sm' | 'md' | 'lg';
  description?: string;
  thresholds?: {
    good: number;
    warning: number;
  };
}

export function MetricGauge({
  value,
  max = 100,
  title,
  unit,
  color = 'blue',
  size = 'md',
  description,
  thresholds,
}: MetricGaugeProps) {
  const percentage = Math.min((value / max) * 100, 100);

  const thresholdPercentage = thresholds ? (thresholds.good / max) * 100 : 66;

  // Determine gauge color based on value or manual color
  const getGaugeColor = (val: number) => {
    if (!thresholds) {
      const colorMap = {
        blue: 'from-blue-400 to-blue-600',
        green: 'from-green-400 to-green-600',
        amber: 'from-amber-400 to-amber-600',
        red: 'from-red-400 to-red-600',
        cyan: 'from-cyan-400 to-cyan-600',
      };
      return colorMap[color];
    }

    if (val >= thresholds.good) return 'from-green-400 to-green-600';
    if (val >= thresholds.warning) return 'from-amber-400 to-amber-600';
    return 'from-red-400 to-red-600';
  };

  const sizeConfig = {
    sm: { container: 'w-20 h-20', text: 'text-lg', labelText: 'text-xs' },
    md: { container: 'w-32 h-32', text: 'text-3xl', labelText: 'text-sm' },
    lg: { container: 'w-48 h-48', text: 'text-5xl', labelText: 'text-base' },
  };

  const config = sizeConfig[size];
  const gaugeGradient = getGaugeColor(value);

  return (
    <div className="text-center">
      <h4 className="mb-2 text-sm font-semibold text-gray-900">{title}</h4>
      {description && <p className="mb-4 text-xs text-gray-600">{description}</p>}

      {/* Gauge Container */}
      <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }} className="mx-auto">
        <div className={`relative ${config.container} mx-auto`}>
          {/* Background circle */}
          <svg viewBox="0 0 120 120" className="absolute inset-0 h-full w-full">
            <circle cx="60" cy="60" r="55" fill="none" stroke="#E5E7EB" strokeWidth="8" />

            {/* Progress circle */}
            <motion.circle
              cx="60"
              cy="60"
              r="55"
              fill="none"
              strokeWidth="8"
              strokeDasharray={`${2 * Math.PI * 55}`}
              strokeDashoffset={`${2 * Math.PI * 55 * (1 - percentage / 100)}`}
              strokeLinecap="round"
              className={`bg-gradient-to-b ${gaugeGradient}`}
              stroke={`url(#gaugeGradient${value})`}
              initial={{ strokeDashoffset: 2 * Math.PI * 55 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 55 * (1 - percentage / 100) }}
              transition={{ duration: 1, delay: 0.3, ease: 'easeOut' }}
            />

            {/* Gradient definition */}
            <defs>
              <linearGradient id={`gaugeGradient${value}`} x1="0%" y1="0%" x2="0%" y2="100%">
                <stop
                  offset="0%"
                  stopColor={
                    color === 'blue'
                      ? '#60A5FA'
                      : color === 'green'
                        ? '#4ADE80'
                        : color === 'amber'
                          ? '#FBBF24'
                          : color === 'red'
                            ? '#F87171'
                            : '#06D6FF'
                  }
                />
                <stop
                  offset="100%"
                  stopColor={
                    color === 'blue'
                      ? '#2563EB'
                      : color === 'green'
                        ? '#15803D'
                        : color === 'amber'
                          ? '#D97706'
                          : color === 'red'
                            ? '#DC2626'
                            : '#0891B2'
                  }
                />
              </linearGradient>
            </defs>
          </svg>

          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className={`${config.text} font-bold text-gray-900`}
            >
              {value.toFixed(value > 10 ? 0 : 1)}
            </motion.div>
            {unit && <div className={`${config.labelText} text-gray-600`}>{unit}</div>}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
